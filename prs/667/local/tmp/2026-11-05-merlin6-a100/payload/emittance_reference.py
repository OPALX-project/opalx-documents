#!/usr/bin/env python3
"""Matched local RMS emittances from saved native ten-metre bend data.

No native tracking is launched. Transverse momenta are mechanical p/(mc),
projected onto each particle's local radial/vertical axes. Longitudinal
emittance uses (s, delta kinetic energy), not a momentum approximation.
"""
from pathlib import Path
import hashlib
import json

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RADIUS = 2.
FIELDS = ['emit_n_u_m', 'emit_n_y_m', 'emit_sE_m_eV']


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            digest.update(block)
    return digest.hexdigest()


def rms_area(q, p):
    """Mean-subtracted area, stable even for a nearly linear cold beam."""
    q = q-q.mean()
    p = p-p.mean()
    q2 = np.mean(q*q)
    if q2 == 0.:
        return 0.
    residual = p-np.mean(q*p)/q2*q
    return float(np.sqrt(q2*np.mean(residual*residual)))


def covariance_area(row, i, j):
    a, b, c = [float(row[f'native_cov_{x}{y}']) for x, y in [(i, i), (j, j), (i, j)]]
    determinant = a*b-c*c
    tolerance = 256*np.finfo(float).eps*max(a*b, c*c, np.finfo(float).tiny)
    assert determinant >= -tolerance, (i, j, determinant, tolerance)
    return float(np.sqrt(max(0., determinant)))


def particle_emittances(position, momentum, phase, p0, mass_eV):
    radial_distance = np.hypot(position[:, 0]+RADIUS, position[:, 2])
    theta = np.arctan2(position[:, 2], position[:, 0]+RADIUS)
    s = RADIUS*np.arctan2(np.sin(theta-phase), np.cos(theta-phase))
    u = radial_distance-RADIUS
    radial_p = ((position[:, 0]+RADIUS)*momentum[:, 0]
                + position[:, 2]*momentum[:, 2])/radial_distance
    p2 = np.einsum('ij,ij->i', momentum, momentum)
    # Exact gamma-gamma0 through a difference of squares avoids gamma-1 loss.
    delta_energy = mass_eV*(p2-p0*p0)/(np.sqrt(1+p2)+np.sqrt(1+p0*p0))
    return dict(zip(FIELDS, [rms_area(u, radial_p),
                            rms_area(position[:, 1], momentum[:, 1]),
                            rms_area(s, delta_energy)]))


def global_snapshot(group):
    reference_p = np.asarray(group.attrs['RefPartP'], float)
    angle = np.arctan2(-reference_p[0], reference_p[2])
    co, si = np.cos(angle), np.sin(angle)
    basis = np.array([[co, 0., -si], [0., 1., 0.], [si, 0., co]])
    position = np.column_stack([group[k][:] for k in ['x', 'y', 'z']])@basis.T
    position += np.asarray(group.attrs['RefPartR'], float)
    momentum = np.column_stack([group[k][:] for k in ['px', 'py', 'pz']])@basis.T
    return position, momentum


def collect():
    selected = json.loads((ROOT/'analysis/selection.json').read_text())
    rows, controls, provenance = [], [], []
    for item in selected:
        manifest_path = Path(item['manifest'])
        assert sha(manifest_path) == item['manifest_sha256']
        manifest = json.loads(manifest_path.read_text())
        source = manifest['source']
        assert sha(source['npz']) == item['source_sha256']
        p0 = source['momentum_betagamma']
        directory = manifest_path.parent
        moments_path = directory/'moments.csv'
        assert sha(moments_path) == item['moment_csv_sha256']
        moments = pd.read_csv(moments_path, float_precision='round_trip')
        assert moments.step.tolist() == list(range(11))
        code, mode = item['code'], item['mode']
        if code == 'OPALX 2D5':
            mass_eV = 938272088.16
            with np.load(source['npz']) as source_data:
                values = particle_emittances(source_data['cartesian_m'],
                    source_data['momenta_betagamma'], 0., p0, mass_eV)
            rows.append(dict(code=code, zero_sc=mode=='ZeroSC', step=0, advance_m=0., **values))
            native = directory/'track.h5'
            with h5py.File(native) as handle:
                groups = sorted(handle, key=lambda k: int(k.split('#')[-1]))
                assert len(groups) == 10
                for step, key in enumerate(groups, 1):
                    position, momentum = global_snapshot(handle[key])
                    assert len(position) == 1048576
                    phase = moments.loc[moments.step==step, 'reference_phase_rad'].iloc[0]
                    values = particle_emittances(position, momentum, phase, p0, mass_eV)
                    rows.append(dict(code=code, zero_sc=mode=='ZeroSC', step=step,
                                     advance_m=float(step), **values))
            provenance.append(dict(code=code, mode=mode, native=str(native), sha256=sha(native)))
        else:
            for _, row in moments.iterrows():
                values = dict(zip(FIELDS, [p0*covariance_area(row, 0, 1),
                    p0*covariance_area(row, 2, 3), 1e9*covariance_area(row, 4, 5)]))
                rows.append(dict(code=code, zero_sc=mode=='ZeroSC', step=int(row.step),
                                 advance_m=float(row.nominal_design_advance_m), **values))
            provenance.append(dict(code=code, mode=mode, native=str(moments_path), sha256=sha(moments_path)))

        # Independent endpoint representation: final physical/native NPZ.
        with np.load(directory/'final-particles.npz') as data:
            mass_eV = 938272088.16 if code == 'OPALX 2D5' else manifest['mass_GeV']*1e9
            kinetic0_eV = mass_eV*p0*p0/(np.sqrt(1+p0*p0)+1)
            # A cold native dE=0 becomes tiny roundoff spread after Cartesian
            # p reconstruction. Bound that control by energy precision times
            # bunch length; this never changes or floors a plotted emittance.
            energy_area_roundoff = 64*np.finfo(float).eps*kinetic0_eV*float(moments.sigma_frenet_s_m.iloc[-1])
            if code == 'OPALX 2D5':
                expected = particle_emittances(data['positions_m'], data['momenta_betagamma'],
                    float(data['reference_phase_rad']), p0, 938272088.16)
            else:
                native = data['native_state']
                expected = dict(zip(FIELDS, [p0*rms_area(native[:, 0], native[:, 1]),
                    p0*rms_area(native[:, 2], native[:, 3]),
                    1e9*rms_area(native[:, 4], native[:, 5])]))
                # Check the physical Cartesian momentum embedding as well.
                physical = particle_emittances(data['positions_m'], data['momenta_betagamma'],
                                               5., p0, manifest['mass_GeV']*1e9)
                for field in FIELDS:
                    absolute_tolerance = energy_area_roundoff if field == 'emit_sE_m_eV' else 1e-18
                    assert np.isclose(physical[field], expected[field], rtol=1e-7, atol=absolute_tolerance), (code, mode, field, physical[field], expected[field])
        measured = rows[-1]
        for field in FIELDS:
            assert np.isclose(measured[field], expected[field], rtol=1e-7, atol=1e-18), (code, mode, field)
        controls.append(dict(code=code, mode=mode, endpoint_npz_check_passed=True,
                             cold_energy_area_roundoff_control_m_eV=energy_area_roundoff,
                             endpoint_npz_emittances=expected))
    result = pd.DataFrame(rows)
    assert len(result) == 44 and np.isfinite(result[FIELDS]).all().all()
    result.to_csv(ROOT/'analysis/emittance.csv', index=False, float_format='%.17g')
    check = dict(passed=True, native_tracking_rerun=False, records=len(result),
        definition_transverse='sqrt(Var(q)*Var(p_q/(mc))-Cov(q,p_q/(mc))^2), mean-subtracted, particle-local radial/vertical mechanical momentum',
        definition_longitudinal='sqrt(Var(s)*Var(delta kinetic energy[eV])-Cov(s,delta kinetic energy[eV])^2)',
        plotted_units=['mm mrad', 'mm mrad', 'mm eV'],
        plotted_scale_factors=[1e6, 1e6, 1e3],
        longitudinal_conversion='No linearized momentum conversion; energy emittance from exact OPALX kinetic energy and native PyORBIT delta energy.',
        zero_sc_floor='ZeroSC radial projected RMS area can be nonzero in nonlinear curved coordinates; no subtraction or forced-zero correction.',
        endpoint_controls=controls, native_provenance=provenance, script_sha256=sha(__file__))
    (ROOT/'analysis/emittance-checks.json').write_text(json.dumps(check, indent=2)+'\n')
    return result


def plot(data, colors, save):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8))
    fig.subplots_adjust(left=.09, right=.99, top=.80, bottom=.35, wspace=.42)
    titles = [r'$\epsilon_{n,u}$', r'$\epsilon_{n,y}$', r'$\epsilon_{s,E}$']
    for ax, field, title, factor, unit in zip(axes, FIELDS, titles,
            [1e6, 1e6, 1e3], ['mm mrad', 'mm mrad', 'mm eV']):
        for code, color in colors.items():
            for zero in [True, False]:
                selected = data[(data.code==code)&(data.zero_sc==zero)].sort_values('step')
                ax.plot(selected.advance_m, selected[field]*factor, color=color,
                    ls='--' if zero else '-', alpha=.65 if zero else 1,
                    marker=None if zero else ('o' if code=='OPALX 2D5' else 's'),
                    ms=3, mfc='white', label=code+(' ZeroSC' if zero else ' 10 pC'))
        ax.axhline(0, color='.55', lw=.65)
        ax.grid(alpha=.15)
        ax.set(xlim=(0, 10), ylim=(0, None), xlabel=r'$s$ (m)',
               title=title, ylabel=f'RMS emittance ({unit})')
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5,.01),
               ncol=2, frameon=False, fontsize=7)
    fig.suptitle('$R=2$ m bend: 10 m, 10 steps; local RMS emittances', fontsize=10)
    save(fig, 'emittance-10m')


if __name__ == '__main__':
    data = collect()
    print(data[data.step==10].to_string(index=False))
