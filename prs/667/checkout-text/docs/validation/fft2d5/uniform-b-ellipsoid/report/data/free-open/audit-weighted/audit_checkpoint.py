"""Independent audit of variable-q/m frozen-source restart runs.

The input/source and native output are joined by every particle ID. Header
CHARGE is recorded but never used as the authoritative variable-weight Q.
No study analyzer or source-generator functions are imported.
"""
from pathlib import Path
import argparse
import hashlib
import json

import h5py
import numpy as np
import pandas as pd
from scipy.constants import c, e, proton_mass
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    with h5py.File(path) as f:
        assert list(f) == ['Step#0']
        g = f['Step#0']
        ids = g['id'][:].astype(np.int64)
        order = np.argsort(ids)
        assert np.array_equal(ids[order], np.arange(len(ids)))
        data = {key: g[key][:][order] for key in g if key in ['q', 'm', 'x', 'y', 'z', 'px', 'py', 'pz', 'Ex', 'Ey', 'Ez']}
        attrs = {key: np.asarray(value).tolist() for key, value in g.attrs.items() if key in ['CHARGE', 'TIME', 'RefPartR', 'RefPartP', 'ToLabOrigin', 'ToLabQuaternion', 'QMStorageMode', 'MacroCharge', 'MacroMass']}
        for key in ['TIME', 'DT']:
            if key in f.attrs:
                attrs['file_'+key] = np.asarray(f.attrs[key]).tolist()
        for values in data.values():
            assert np.isfinite(values).all()
    return data, attrs


def local_coordinates(xyz, radius):
    s = radius * np.arctan2(xyz[:, 2], radius + xyz[:, 0])
    u = np.hypot(radius + xyz[:, 0], xyz[:, 2]) - radius
    return np.column_stack((u, xyz[:, 1], s))


def independent_cell_charges(coords, m):
    """Adaptive ellipse-clipped J integration, independent of Gauss16 generator."""
    src = m['source']; nx, ny, nz = src['source_mesh']; wx, wy = src['source_box_m']
    du, dy, ds = wx/nx, wy/ny, 8./nz
    a, b, radius, half = m['radial_semiaxis_m'], m['vertical_semiaxis_m'], m['radius_m'], m['full_length_m']/2
    ix = np.rint((coords[:, 0]+wx/2)/du-.5).astype(int)
    iy = np.rint((coords[:, 1]+wy/2)/dy-.5).astype(int)
    iz = np.rint((coords[:, 2]+4.)/ds-.5).astype(int)
    assert np.max(np.abs(coords[:, 0]-(-wx/2+(ix+.5)*du))) < 2e-14
    assert np.max(np.abs(coords[:, 1]-(-wy/2+(iy+.5)*dy))) < 2e-14
    assert np.max(np.abs(coords[:, 2]-(-4+(iz+.5)*ds))) < 2e-14
    areas = np.zeros(nx*ny)
    for code in np.unique(ix*ny+iy):
        i, j = divmod(code, ny)
        xlo, xhi = -wx/2+i*du, -wx/2+(i+1)*du
        ylo, yhi = max(-b, -wy/2+j*dy), min(b, -wy/2+(j+1)*dy)
        cuts = [ylo, yhi]
        for edge in [xlo, xhi]:
            if abs(edge) < a:
                yp = b*np.sqrt(1-(edge/a)**2)
                cuts.extend(x for x in [-yp, yp] if ylo<x<yhi)
        cuts = np.unique(cuts)
        def line(y):
            extent = a*np.sqrt(max(0., 1-(y/b)**2))
            lo, hi = max(xlo, -extent), min(xhi, extent)
            return 0. if hi<=lo else hi-lo+(hi*hi-lo*lo)/(2*radius)
        areas[code] = sum(quad(line, lo, hi, epsabs=1e-22, epsrel=1e-10)[0] for lo, hi in zip(cuts[:-1], cuts[1:]))
    slo, shi = np.maximum(-half, -4+iz*ds), np.minimum(half, -4+(iz+1)*ds)
    if m['profile']=='uniform':
        longitudinal = shi-slo; integral = 2*half
    else:
        primitive = lambda s: s-s*np.abs(s)/(2*half)
        longitudinal = primitive(shi)-primitive(slo); integral = half
    expected = src['nominal_charge_C']/(np.pi*a*b*integral)*areas[ix*ny+iy]*longitudinal
    return expected, float(areas.sum()/(np.pi*a*b)-1)


def part(case):
    manifest_path = ROOT/'runs'/case/'manifest.json'
    m = json.loads(manifest_path.read_text())
    src = m['source']; ns = src['source_particles']; probe_only = m['probe_only']
    for path, expected in [(m['distribution'], m['distribution_sha256']),
                           (m['binary_snapshot'], m['binary_sha256']),
                           (m['reference_path'], m['reference_path_sha256']),
                           (ROOT/'reference/points_extended.csv', m['points_sha256']),
                           (ROOT/f'reference/{m["profile"]}_fields_reference.csv', m['reference_fields_sha256'])]:
        assert sha(path) == expected, path
    assert sha(manifest_path.parent/'tube.in') == m['input_sha256']
    assert m['returncode'] == 0 and '--restart' in m['command']
    text = (manifest_path.parent/'tube.in').read_text()
    assert 'QM_MODE="ATTRIBUTES"' in text and 'PIPEMODE=OPEN' in text
    assert 'SACR' not in text and 'CHECKPOINTFREQ=1' in text
    inp, ia = read(m['distribution'])
    out, oa = read(m['h5'])
    checkpoint_path = manifest_path.parent/'tube_checkpoint.h5'
    chk, ca = read(checkpoint_path)
    assert len(inp['q']) == len(out['q']) == len(chk['q']) == m['expected_particles']
    assert ia['file_TIME'] == [0.]
    assert np.isclose(ia['file_DT'][0], m['dt_s'], rtol=1e-14, atol=0)
    assert np.isclose(oa['TIME'][0], m['dt_s'], rtol=1e-14, atol=0)
    assert np.isclose(ca['file_TIME'][0], m['dt_s'], rtol=1e-14, atol=0)
    assert ia['QMStorageMode'] == [1] and ca['QMStorageMode'] == [1]
    assert ia['ToLabQuaternion'] == [1., 0., 0., 0.]
    assert ia['ToLabOrigin'] == [0., 0., 0.] and ia['RefPartR'] == [0., 0., 0.]
    assert np.allclose(ia['RefPartP'], [0., 0., m['beta']/np.sqrt(1-m['beta']**2)], rtol=1e-14, atol=0)
    count = 0 if probe_only else ns
    check = dict(case=case, binary_sha256=m['binary_sha256'], input_sha256=m['distribution_sha256'],
                 native_h5_sha256=sha(m['h5']), native_checkpoint_sha256=sha(checkpoint_path),
                 particles=len(inp['q']), source_particles=count, exact_ids=True,
                 input_total_q_C=float(inp['q'].sum()), output_total_q_C=float(out['q'].sum()),
                 input_source_q_C=float(inp['q'][:count].sum()), output_source_q_C=float(out['q'][:count].sum()),
                 input_marker_q_C=float(inp['q'][count:].sum()), output_marker_q_C=float(out['q'][count:].sum()),
                 header_charge_C=oa.get('CHARGE'),
                 input_q_min_C=float(inp['q'].min()), input_q_max_C=float(inp['q'].max()),
                 output_q_min_C=float(out['q'].min()), output_q_max_C=float(out['q'].max()))
    for key in ['q', 'm']:
        expected = inp[key]
        actual = out[key] if key in out else chk[key]
        check[key+'_preserved_by_id'] = bool(np.array_equal(expected, actual) and np.array_equal(expected, chk[key]))
        check[key+'_max_relative_change'] = float(np.max(np.abs(chk[key]/expected-1)))
        check[key+'_input_sha256'] = hashlib.sha256(np.asarray(expected, dtype=np.float64).tobytes()).hexdigest()
        check[key+'_output_checkpoint_sha256'] = hashlib.sha256(np.asarray(chk[key], dtype=np.float64).tobytes()).hexdigest()
        expected_hash = m['expected_'+key+'_dataset_sha256']
        assert hashlib.sha256(np.asarray(expected, dtype=np.float64).tobytes()).hexdigest() == expected_hash
    mass_per_charge = proton_mass*c*c/e/1e9/e
    check['input_q_over_m_proton_pass'] = bool(np.allclose(inp['m']/inp['q'], mass_per_charge, rtol=2e-14))
    check['output_q_over_m_proton_pass'] = bool(np.allclose(chk['m']/chk['q'], mass_per_charge, rtol=2e-14))
    xyz = np.column_stack([inp[k] for k in ['x', 'y', 'z']])
    local = local_coordinates(xyz, m['radius_m'])
    qprobe = src['nominal_charge_C']/ns
    if count:
        if src.get('layout')=='physical-cell-charge':
            expected_q, area_error = independent_cell_charges(local[:count], m)
            l1_error = float(np.abs(inp['q'][:count]-expected_q).sum()/src['nominal_charge_C'])
            check['independent_cell_charge_L1_relative_error'] = l1_error
            check['independent_cross_J_relative_error'] = area_error
            # A fixed 1e-7 charge-integration budget is far below the 1% field
            # goal; tiny boundary-cell charges are judged by total-charge norm.
            check['input_analytic_profile_q_pass'] = bool(l1_error < 1e-7)
            check['J_weighted_transverse_mean_pass'] = bool(abs(area_error)<1e-10 and l1_error<1e-7)
        else:
            weights = np.ones(count) if m['profile']=='uniform' else 2*(1-np.abs(local[:count, 2])/(m['full_length_m']/2))
            expected_q = qprobe * weights
            check['input_analytic_profile_q_pass'] = bool(np.allclose(inp['q'][:count], expected_q, rtol=1e-9, atol=1e-32))
            cross = local[:src['ncross']]
            check['J_weighted_transverse_mean_pass'] = bool(abs(cross[:, 0].mean()-m['radial_semiaxis_m']**2/(4*m['radius_m']))<1e-12 and abs(cross[:, 1].mean())<1e-15)
        q = inp['q'][:count]; coords = local[:count]
        moments = np.sum(q[:, None]*coords, axis=0)/q.sum()
        second = np.sum(q[:, None]*coords**2, axis=0)/q.sum()
        check['input_weighted_mean_uy_s_m'] = moments.tolist()
        check['input_weighted_second_uy_s_m2'] = second.tolist()
        check['expected_mean_u_m'] = m['radial_semiaxis_m']**2/(4*m['radius_m'])
        check['expected_second_s_m2'] = m['full_length_m']**2/(12 if m['profile']=='uniform' else 24)
        check['source_Q_normalization_pass'] = bool(np.isclose(q.sum(), src['nominal_charge_C'], rtol=1e-13, atol=0))
        check['longitudinal_second_moment_pass'] = bool(np.isclose(second[2], check['expected_second_s_m2'], rtol=1e-4))
    else:
        check.update(input_analytic_profile_q_pass=True, source_Q_normalization_pass=True,
                     J_weighted_transverse_mean_pass=True, longitudinal_second_moment_pass=True)
    check['marker_q_pass'] = bool(np.allclose(inp['q'][count:], qprobe, rtol=1e-14, atol=0))
    # This fixed reference is kept along +z. The native checkpoint records the
    # moving frame exactly; a nonidentity frame must be audited explicitly.
    assert np.allclose(ca['ToLabQuaternion'], [1., 0., 0., 0.], rtol=0, atol=1e-14)
    actual_xyz = np.column_stack([chk[k] for k in ['x', 'y', 'z']])-np.asarray(ca['ToLabOrigin'])
    bg = m['beta']/np.sqrt(1-m['beta']**2)
    velocity = c*np.column_stack([inp[k] for k in ['px', 'py', 'pz']])/np.sqrt(1+bg*bg)
    expected_xyz = xyz + velocity*m['dt_s']
    residual = np.linalg.norm(actual_xyz-expected_xyz, axis=1)
    check['max_frozen_motion_residual_m'] = float(residual.max())
    check['frame_motion_pass'] = bool(residual.max()<1e-10)
    fields = np.column_stack([out[k] for k in ['Ex', 'Ey', 'Ez']])[count:]
    points = pd.read_csv(ROOT/'reference/points_extended.csv', float_precision='round_trip')
    theta = points.s_m.to_numpy()/m['radius_m']
    frenet_fields = np.column_stack((fields[:, 0]*np.cos(theta)+fields[:, 2]*np.sin(theta),
                                     fields[:, 1], -fields[:, 0]*np.sin(theta)+fields[:, 2]*np.cos(theta)))
    required = ['q_preserved_by_id', 'm_preserved_by_id', 'input_q_over_m_proton_pass',
                'output_q_over_m_proton_pass', 'input_analytic_profile_q_pass', 'source_Q_normalization_pass',
                'J_weighted_transverse_mean_pass', 'longitudinal_second_moment_pass', 'marker_q_pass', 'frame_motion_pass']
    check['initialization_valid'] = all(check[k] for k in required)
    return check, frenet_fields, m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case')
    args = parser.parse_args()
    full, efull, m = part(args.case)
    probes, eprobe, companion = part(args.case+'-probes')
    assert m['source']==companion['source'] and m['binary_sha256']==companion['binary_sha256']
    refpath = ROOT/f'reference/{m["profile"]}_fields_reference.csv'
    ref = pd.read_csv(refpath, float_precision='round_trip')
    points = pd.read_csv(ROOT/'reference/points_extended.csv', float_precision='round_trip')
    assert np.array_equal(ref.point_id, points.point_id)
    assert np.allclose(ref.rho_normalization_C_m3, 1e-11/(np.pi*.005*.0005*5)*(2 if m['profile']=='triangle' else 1), rtol=1e-13)
    fields = efull-eprobe
    rows = points[['point_id', 'u_m', 'y_m', 's_m']].copy()
    for j, component in enumerate(['r', 'y', 's']):
        expected = ref[f'E_{component}_V_m'].to_numpy()
        rows[f'native_E_{component}_V_m'] = fields[:, j]
        rows[f'SACR_E_{component}_V_m'] = expected
        rows[f'error_{component}_V_m'] = fields[:, j]-expected
    valid = full['initialization_valid'] and probes['initialization_valid']
    rows['initialization_valid'] = valid
    rows.to_csv(HERE/(args.case+'-fields.csv'), index=False)
    metric_rows = []
    for group, selection in [('original43', points.original_target.to_numpy()),
                             ('closer_end_diagnostics8', ~points.original_target.to_numpy()),
                             ('all51', np.ones(len(points), dtype=bool))]:
        for component in ['r', 'y', 's']:
            expected = rows[f'SACR_E_{component}_V_m'].to_numpy()
            delta = rows[f'error_{component}_V_m'].to_numpy()
            nonzero = selection & (np.abs(expected)>1e-8)
            zero = selection & ~nonzero
            ratios = np.where(nonzero, 100*np.abs(delta)/np.maximum(np.abs(expected), 1e-300), -1.)
            worst = int(np.argmax(ratios))
            metric_rows.append(dict(target_set=group, component=component,
                nonzero_points=int(nonzero.sum()),
                max_relative_error_percent=float(ratios[worst]) if nonzero.any() else None,
                worst_nonzero_point=rows.point_id.iloc[worst] if nonzero.any() else None,
                max_symmetry_zero_absolute_error_V_m=float(np.abs(delta[zero]).max()) if zero.any() else None))
    pd.DataFrame(metric_rows).to_csv(HERE/(args.case+'-metrics.csv'), index=False)
    result = dict(case=args.case, initialization_valid=valid, full=full, companion=probes,
                  reference_path=str(refpath), reference_sha256=sha(refpath),
                  reference_charge_C=1e-11, comparison_interpretable=valid,
                  field_metrics=metric_rows,
                  failure=None if valid else 'Native q and/or m initialization was not preserved; field comparison is invalid and must not support acceptance.',
                  script_sha256=sha(__file__))
    (HERE/(args.case+'.json')).write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return 0 if valid else 1


if __name__=='__main__':
    raise SystemExit(main())
