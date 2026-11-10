"""Audit native pipe snapshots and compare against the independent Gauss-law reference."""
from pathlib import Path
import hashlib
import json
import os
import sys

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
STUDY = Path('/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe')
sys.path.insert(0, str(STUDY / 'analytic-audit'))
from analytic import Benchmark

CASE = Benchmark()
POINTS = pd.read_csv(STUDY / 'common/probes.csv', float_precision='round_trip')
OUT = HERE / 'analysis'


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            result.update(chunk)
    return result.hexdigest()


def native_read(manifest, points, wall=False):
    m = json.loads(manifest.read_text())
    for filename, key in [(m['binary'], 'binary_sha256'),
                          (m['distribution'], 'distribution_sha256'),
                          (m['reference_path'], 'reference_path_sha256')]:
        assert sha(filename) == m[key], (filename, key)
    assert sha(manifest.parent / 'triangle.in') == m['input_sha256']
    assert m['returncode'] == 0
    cfg = m['config']
    macrocharge = cfg['macrocharge_C'] if wall else m['source']['macrocharge_C']
    source_count = cfg['source_particles'] if wall else m['source']['source_particles']
    offset = 0 if m['companion'] else source_count
    check = dict(case=manifest.parent.name, manifest=str(manifest), manifest_sha256=sha(manifest))
    with h5py.File(m['h5']) as handle:
        assert list(handle) == ['Step#0']
        units = {'ExUnit': 'V/m', 'EyUnit': 'V/m', 'EzUnit': 'V/m',
                 'xUnit': 'm', 'yUnit': 'm', 'zUnit': 'm', 'qUnit': 'C'}
        for key, expected in units.items():
            assert np.asarray(handle.attrs[key]).item().decode() == expected
        g = handle['Step#0']
        ids = g['id'][:].astype(np.int64)
        assert len(ids) == m['expected_particles']
        order = np.argsort(ids)
        assert np.array_equal(ids[order], np.arange(len(ids)))
        q = g['q'][:]
        assert np.isfinite(q).all() and np.allclose(q, macrocharge, rtol=1e-11, atol=0)
        charge = float(np.asarray(g.attrs['CHARGE']).ravel()[0])
        assert np.isclose(charge, m['charge_C'], rtol=1e-11, atol=0)
        assert np.isclose(q.sum(), charge, rtol=1e-11, atol=0)
        time = float(np.asarray(g.attrs['TIME']).ravel()[0])
        assert np.isclose(time, cfg['dt_s'], rtol=1e-10, atol=1e-30)
        refp = np.asarray(g.attrs['RefPartP'], dtype=float)
        refr = np.asarray(g.attrs['RefPartR'], dtype=float)
        tangent = refp / np.linalg.norm(refp)
        assert tangent[2] > 0 and np.max(np.abs(tangent[:2])) < 1e-10
        e1 = np.array([tangent[2], 0., -tangent[0]])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(tangent, e1)
        basis = np.column_stack((e1, e2, tangent))
        gamma2 = 1. + float(refp @ refp)
        assert np.isclose(np.sqrt(gamma2), cfg['gamma'], rtol=1e-9)

        def selected(keys, wanted_ids):
            rows = order[wanted_ids]
            sorted_rows = np.argsort(rows)
            back = np.argsort(sorted_rows)
            return np.column_stack([g[k][rows[sorted_rows]][back] for k in keys])

        wanted = offset + np.arange(len(points))
        field = selected(['Ex', 'Ey', 'Ez'], wanted) @ basis.T
        position = selected(['x', 'y', 'z'], wanted) @ basis.T + refr
        nominal = points[['x_m', 'y_m', 's_m']].to_numpy()
        drift = np.array([0., 0., cfg['beta'] * 299792458. * time])
        motion = float(np.linalg.norm(position - nominal - drift, axis=1).max())
        assert motion < 1e-10 and np.isfinite(field).all()
        for key in ['px', 'py', 'pz', 'Bx', 'By', 'Bz']:
            assert np.isfinite(selected([key], wanted)).all()
        check.update(particles=len(ids), source_particles=offset, assigned_charge_C=charge,
                     source_charge_C=offset * macrocharge, macrocharge_C=macrocharge,
                     q_sum_C=float(q.sum()), time_s=time, gamma_squared=gamma2,
                     max_probe_motion_residual_m=motion, units_pass=True,
                     exact_ids_pass=True, q_count_charge_pass=True, reference_frame_pass=True)
        if offset and not wall:
            assert sha(m['source']['npz']) == m['source']['npz_sha256']
            with np.load(m['source']['npz']) as source:
                ss, xy = source['s_nodes_m'], source['cross_xy_m']
                sample_ids = np.unique(np.linspace(0, offset - 1, 2049, dtype=np.int64))
                expected = np.column_stack((xy[sample_ids % len(xy)], ss[sample_ids // len(xy)]))
                actual = selected(['x', 'y', 'z'], sample_ids) @ basis.T + refr
                residual = float(np.linalg.norm(actual - expected - drift, axis=1).max())
                assert residual < 1e-10
                check.update(sampled_source_ids=len(sample_ids),
                             max_source_sample_motion_residual_m=residual,
                             source_tensor_geometry_pass=True, source_npz_sha256=m['source']['npz_sha256'])
    check['h5_sha256'] = sha(m['h5'])
    return field, check, m


def opalx():
    full, check, m = native_read(HERE/'opalx/runs/pipe256-final703/manifest.json', POINTS)
    probe, pcheck, companion = native_read(HERE/'opalx/runs/pipe256-final703-probes/manifest.json', POINTS)
    for key in ['mesh', 'binary_sha256', 'reference_path_sha256', 'physical_pipe_radius_m', 'longitudinal_mode']:
        assert m[key] == companion[key]
    assert np.isclose(companion['charge_C']/companion['expected_particles'], m['source']['macrocharge_C'], rtol=1e-12)
    probe[:, 2] *= pcheck['gamma_squared'] / check['gamma_squared']
    d = POINTS.copy()
    d[['Ex_V_m', 'Ey_V_m', 'Es_V_m']] = full - probe
    d['case'] = 'opalx-pipe256'; d['code'] = 'OPALX'; d['model'] = 'CIRCULAR_UNIFORM'
    d['mpi_size'] = 1
    d['nx'], d['ny'], d['nz'] = m['mesh']
    d['source_particles'] = m['source']['source_particles']
    return [d], [check, pcheck], m


def pyorbit():
    frames, checks = [], []
    for directory in sorted((HERE/'pyorbit/runs').glob('*')):
        metas = [json.loads(p.read_text()) for p in sorted(directory.glob('manifest-rank*.json'))]
        if not metas:
            raise ValueError('Incomplete case: '+str(directory))
        m = metas[0]
        assert len(metas) == m['mpi_size']
        assert {x['rank'] for x in metas} == set(range(m['mpi_size']))
        for x in metas:
            source = x['argv'][x['argv'].index('--source')+1]
            assert sha(source) == x['source_sha256']
            assert sha(STUDY/'common/probes.csv') == x['probe_input_sha256']
            assert x['zero_probe_weights'] and x['probe_positions_unchanged']
            assert x['native_weight_sum_global'] == 1e14
            assert x['native_source_count_global'] == x['source_particles_global']
            assert x['native_total_count_global'] == x['source_particles_global']+len(POINTS)+6
        d = pd.concat([pd.read_csv(p, float_precision='round_trip') for p in sorted(directory.glob('probes-rank*.csv'))], ignore_index=True)
        assert len(d) == len(POINTS) and not d.probe_id.duplicated().any()
        d = d.rename(columns={'probe_id': 'point_id'}).merge(POINTS[['point_id', 'kind']], on='point_id', validate='one_to_one')
        coordinates = d.merge(POINTS, on='point_id', suffixes=('_got', '_input'), validate='one_to_one')
        for key in ['x_m', 'y_m', 's_m']:
            assert np.allclose(coordinates[key+'_got'], coordinates[key+'_input'], rtol=0, atol=2e-14)
        assert np.isfinite(d.Es_V_m).all()
        assert np.allclose(d.Es_V_m, d.dE_GeV*1e9/m['kick_length_m'], rtol=2e-15, atol=1e-10)
        d['case'] = 'pyorbit-'+directory.name; d['code'] = 'PyORBIT'; d['model'] = m['model']
        d['mpi_size'] = m['mpi_size']; d['nx'] = m['nx']; d['ny'] = m['ny']; d['nz'] = m['nz']
        d['source_particles'] = m['source_particles_global']
        frames.append(d)
        checks.append(dict(case=directory.name, ranks=m['mpi_size'], exact_probe_ids_pass=True,
                           native_source_particles=m['native_source_count_global'],
                           native_protons=m['native_weight_sum_global'], zero_probe_charge_pass=True,
                           fixed_positions_frame_pass=True, source_sha256=m['source_sha256'],
                           harness_sha256=m['harness_sha256'], pyorbit_revision=m['pyorbit_revision']))
    return frames, checks


def wall():
    fixture = Path('/Users/adelmann/git/regression-tests-x/RegressionTests/FFT2D5-TriangularPipe')
    points = pd.read_csv(fixture/'probes.csv', float_precision='round_trip').rename(columns={'probe_id': 'point_id'})
    full, fcheck, m = native_read(HERE/'wall-final703/full/manifest.json', points, wall=True)
    probe, pcheck, _ = native_read(HERE/'wall-final703/probes/manifest.json', points, wall=True)
    probe[:, 2] *= pcheck['gamma_squared']/fcheck['gamma_squared']
    points['r_m'] = np.hypot(points.x_m, points.y_m)
    points['Es_V_m'] = full[:, 2] - probe[:, 2]
    points['probe_only_Es_V_m'] = probe[:, 2]
    points['analytic_Es_V_m'] = CASE.longitudinal_field(points.s_m.to_numpy(), points.r_m.to_numpy())
    mask = points.r_m < CASE.pipe_radius_m
    points['error_percent'] = np.where(mask, 100*(points.Es_V_m/points.analytic_Es_V_m-1), np.nan)
    maximum = float(points.loc[mask, 'error_percent'].abs().max())
    maximum_wall = float(points.loc[~mask, 'Es_V_m'].abs().max())
    assert maximum < 1.0 and maximum_wall < 1e-4
    points.to_csv(OUT/'wall-fields.csv', index=False)
    result = dict(case='native-annulus-wall', source_particles=m['config']['source_particles'],
                  mesh=m['config']['mesh'], numerical_width_m=m['config']['numerical_width_m'],
                  max_nonzero_relative_error_percent=maximum,
                  max_wall_absolute_field_V_m=maximum_wall,
                  max_probe_only_absolute_Es_V_m=float(np.abs(probe[:, 2]).max()), passed=True)
    return points, result, [fcheck, pcheck]


def plot(d, wall_data):
    os.environ.setdefault('MPLCONFIGDIR', str(HERE/'.matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.labelsize': 10,
                         'legend.fontsize': 8, 'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.dpi': 400, 'pdf.fonttype': 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), constrained_layout=True)
    reference_s = np.r_[np.linspace(-5., -.001, 300), np.nan, np.linspace(.001, 5., 300)]
    axes[0].plot(reference_s, CASE.longitudinal_field(reference_s)/1e3, color='black', lw=1.4, label='Analytic uniform-disk pipe')
    styles = [('opalx-pipe256', '#0072B2', 'o', 'OPALX $256^3$'),
              ('pyorbit-slice-r1', '#D55E00', 's', 'PyORBIT slices'),
              ('pyorbit-rb-r1', '#009E73', '^', 'PyORBIT Baartman')]
    for name, color, marker, label in styles:
        a = d[(d.case==name)&(d.kind=='axis')].sort_values('s_m')
        axes[0].plot(a.s_m, a.Es_V_m/1e3, color=color, marker=marker, ms=2.3,
                     lw=.6, markevery=5, label=label)
    axes[0].set(xlabel='$s$ [m]', ylabel='$E_s$ [kV/m]', xlim=(-5.15, 5.15))
    axes[0].axhline(0, color='.7', lw=.6)
    axes[0].legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, 1.01),
                   ncol=2, fontsize=7, columnspacing=1.0)
    rr = np.linspace(0, CASE.pipe_radius_m, 500)
    axes[1].plot(rr*1e3, CASE.longitudinal_field(np.full_like(rr, 2.5), rr)/1e3,
                 color='black', lw=1.4, label='Analytic, $s=2.5$ m')
    for name, color, marker, label in styles:
        a = d[(d.case==name)&(d.kind=='radial')&(d.s_m>0)&(d.x_m>=0)].sort_values('x_m')
        axes[1].plot(a.x_m*1e3, a.Es_V_m/1e3, color=color, marker=marker, ms=2.4,
                     lw=.6, markevery=3, label=label)
    w = wall_data[wall_data.s_m>0]
    axes[1].scatter(w.r_m*1e3, w.Es_V_m/1e3, marker='x', color='#0072B2', s=25,
                    label='OPALX annulus/wall control', zorder=5)
    axes[1].axvline(5, color='.7', ls=':', lw=.8)
    axes[1].set(xlabel='$r$ [mm]', ylabel='$E_s$ [kV/m]', xlim=(0, 20.5), ylim=(0, None))
    axes[1].legend(frameon=False, fontsize=7, loc='upper right')
    for ax in axes: ax.grid(alpha=.16)
    for extension in ['png', 'pdf']:
        fig.savefig(OUT/f'straight-pipe-control.{extension}')
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    frames, checks, native_manifest = opalx()
    pyframes, pychecks = pyorbit()
    d = pd.concat(frames+pyframes, ignore_index=True)
    d['r_m'] = np.hypot(d.x_m, d.y_m)
    d['analytic_Es_V_m'] = CASE.longitudinal_field(d.s_m.to_numpy(), d.r_m.to_numpy())
    d['acceptance'] = CASE.acceptance_mask(d.s_m.to_numpy())
    d['error_percent'] = 100*(d.Es_V_m/d.analytic_Es_V_m-1)
    d['axis_scale_error_percent'] = 100*(d.Es_V_m-d.analytic_Es_V_m)/(CASE.longitudinal_base*CASE.g_axis)
    rows = []
    for name, data in d.groupby('case'):
        a = data[data.acceptance&(data.kind=='axis')]
        r = data[data.acceptance&(data.kind=='radial')]
        row = data.iloc[0]
        rows.append(dict(case=name, code=row.code, model=row.model, mpi_size=int(row.mpi_size),
                         nx=int(row.nx), ny=int(row.ny), nz=int(row.nz), source_particles=int(row.source_particles),
                         axis_points=len(a), radial_points=len(r),
                         max_axis_relative_error_percent=float(a.error_percent.abs().max()),
                         max_radial_relative_error_percent=float(r.error_percent.abs().max()),
                         passed=bool(a.error_percent.abs().max()<1 and r.error_percent.abs().max()<1)))
    summary = pd.DataFrame(rows)
    assert summary.passed.all()
    controls = []
    for first, second, label in [('pyorbit-slice-r1', 'pyorbit-slice-r2', 'slice MPI repeat'),
                                  ('pyorbit-rb-r1', 'pyorbit-rb-r2', 'Baartman MPI repeat'),
                                  ('opalx-pipe256', 'pyorbit-slice-r1', 'OPALX vs PyORBIT slices'),
                                  ('opalx-pipe256', 'pyorbit-rb-r1', 'OPALX vs PyORBIT Baartman')]:
        pair = d[(d.case==first)&d.acceptance].merge(d[(d.case==second)&d.acceptance], on='point_id', suffixes=('_a', '_b'), validate='one_to_one')
        delta = pair.Es_V_m_b-pair.Es_V_m_a
        controls.append(dict(comparison=label, case_a=first, case_b=second, points=len(pair),
                             max_absolute_difference_V_m=float(delta.abs().max()),
                             max_relative_difference_percent=float((100*delta/pair.analytic_Es_V_m_a).abs().max())))
    previous = pd.read_csv(STUDY/'fix-longitudinal/analysis/fields.csv', float_precision='round_trip')
    pair = d[(d.case=='opalx-pipe256')&d.acceptance].merge(previous[(previous.case=='fixed256')&previous.acceptance], on='point_id', suffixes=('_new', '_old'), validate='one_to_one')
    controls.append(dict(comparison='current vs previous OPALX pipe control', case_a='fixed256-old', case_b='opalx-pipe256', points=len(pair),
                         max_absolute_difference_V_m=float((pair.Es_V_m_new-pair.Es_V_m_old).abs().max()),
                         max_relative_difference_percent=float((100*(pair.Es_V_m_new-pair.Es_V_m_old)/pair.analytic_Es_V_m_new).abs().max())))
    wall_data, wall_check, wall_checks = wall()
    d.to_csv(OUT/'fields.csv', index=False)
    summary.to_csv(OUT/'summary.csv', index=False)
    pd.DataFrame(controls).to_csv(OUT/'controls.csv', index=False)
    native_extensions = sorted((STUDY/'pyorbit/native-package/orbit/core').glob('*.so'))
    native_extensions += [STUDY/'pyorbit/native-package/.pyorbit.mesonpy.libs/libcore.dylib']
    record = dict(passed=True, role='Separate straight local conducting-pipe control; not curved free-space validation',
                  fixed_acceptance_abs_s_m=[1., 4.], radial_acceptance_r_m=[0., .005],
                  nonzero_relative_tolerance_percent=1., wall_absolute_tolerance_V_m=1e-4,
                  binary=native_manifest['binary'], binary_sha256=native_manifest['binary_sha256'],
                  analytic=CASE.metadata(), native_snapshot_checks=checks+wall_checks,
                  pyorbit_checks=pychecks, wall=wall_check, summary=rows, comparisons=controls,
                  native_runtime_hashes={str(p):sha(p) for p in native_extensions},
                  scripts_sha256={str(p):sha(p) for p in [Path(__file__), HERE/'run_control.py',
                                  STUDY/'opalx/run_opalx.py', STUDY/'pyorbit/run_native.py', STUDY/'analytic-audit/analytic.py']})
    (OUT/'validation.json').write_text(json.dumps(record, indent=2)+'\n')
    plot(d, wall_data)
    print(summary.to_string(index=False))
    print(pd.DataFrame(controls).to_string(index=False))
    print(json.dumps(wall_check, indent=2))


if __name__ == '__main__':
    main()
