#!/usr/bin/env python3
"""Independent read-only audit of shared sources and straight ten-step controls."""
from pathlib import Path
import hashlib
import json
import math
import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
C = 299792458.


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    results = dict(date='2026-11-04', source_checks=[], straight_cases=[],
                   no_native_runs=True, no_production_edits=True)
    initial_straight = initial_momentum = None
    for geometry in ['straight', 'bend']:
        path = ROOT/'tracking/sources'/f'{geometry}-uniform-n1048576.json'
        meta = json.loads(path.read_text())
        for key in ['npz', 'distribution']:
            assert sha(meta[key]) == meta[key+'_sha256']
        with np.load(meta['npz']) as data:
            local = data['material_m']
            position = data['cartesian_m']
            momentum = data['momenta_betagamma']
            ids = data['source_particle_id']
            q = float(data['macrocharge_C'])
        n = len(local)
        assert n == 1048576 and np.array_equal(ids, np.arange(n))
        assert np.isfinite(local).all() and np.isfinite(position).all() and np.isfinite(momentum).all()
        assert q*n == 1e-11
        mean = np.array([math.fsum(local[:, j])/n for j in range(3)])
        raw2 = np.array([math.fsum(local[:, j]**2)/n for j in range(3)])
        expected_mean = np.array([0. if geometry == 'straight' else .02**2/(4*2), 0., 0.])
        assert np.max(abs(mean-expected_mean)) < 1e-15
        assert np.max(abs(raw2[:2]-.02**2/4)) < 1e-18
        assert abs(raw2[2]-25/12) < 2e-8
        assert np.max(np.hypot(local[:, 0], local[:, 1])) < .02
        assert np.max(abs(local[:, 2])) < 2.5
        theta = local[:, 2]/2 if geometry == 'bend' else np.zeros(n)
        expected_position = np.c_[local[:, 0]*np.cos(theta)-4*np.sin(theta/2)**2,
                                  local[:, 1], (2+local[:, 0])*np.sin(theta)] if geometry == 'bend' else local
        bg = .001/math.sqrt(1-.001**2)
        expected_p = bg*np.c_[-np.sin(theta), np.zeros(n), np.cos(theta)]
        assert np.max(abs(position-expected_position)) < 2e-15
        assert np.max(abs(momentum-expected_p)) < 1e-18
        # Verify the actual FROMFILE numerical data, not only its declared hash.
        text_source = np.loadtxt(meta['distribution'], skiprows=2)
        wanted = np.c_[position[:, 0], momentum[:, 0], position[:, 1], momentum[:, 1],
                       position[:, 2], momentum[:, 2]]
        assert np.array_equal(text_source, wanted)
        results['source_checks'].append(dict(geometry=geometry, particles=n,
            physical_charge_C=q*n, material_mean_m=mean.tolist(),
            material_std_m=np.sqrt(raw2-mean**2).tolist(),
            source_json_sha256=sha(path), source_npz_sha256=sha(meta['npz']),
            FROMFILE_all_values_identical=True, physical_J_moments_passed=True,
            literal_geometry_and_tangent_momenta_passed=True))
        if geometry == 'straight':
            initial_straight, initial_momentum = position.copy(), momentum.copy()
    expected_dt = .1/(.001*C)
    for code in ['opalx', 'pyorbit']:
        suffix = '-e85' if code == 'opalx' else ''
        for charge in ['ZeroSC', '10pC']:
            case = ROOT/'tracking'/code/'runs'/f'straight-{charge}-10steps{suffix}'
            m = json.loads((case/'manifest.json').read_text())
            assert m['source']['npz_sha256'] == results['source_checks'][0]['source_npz_sha256']
            assert m['steps'] == 10 and m['mesh'] == [128, 128, 512]
            assert abs(m['dt_s']-expected_dt) < 1e-21
            assert m['longitudinal_period_m'] == 12.
            frame = pd.read_csv(case/'moments.csv', float_precision='round_trip')
            assert np.array_equal(frame.step, np.arange(11))
            assert np.max(abs(frame.time_s-np.arange(11)*expected_dt)) < 1e-18
            with np.load(case/'final-particles.npz') as f:
                positions, momentum = f['positions_m'], f['momenta_betagamma']
                ids = f['particle_id'] if code == 'opalx' else f['source_particle_id']
            assert np.array_equal(ids, np.arange(len(initial_straight)))
            assert np.isfinite(positions).all() and np.isfinite(momentum).all()
            check = dict(code=code, charge_case=charge,
                         initial_plus_ten_endpoints=True, same_initial_source_hash=True,
                         time_step_s=expected_dt, final_position_hash=sha(case/'final-particles.npz'))
            if charge == 'ZeroSC':
                residual = float(np.max(abs(positions-initial_straight-np.array([0.,0.,1.]))))
                pres = float(np.max(abs(momentum-initial_momentum)))
                assert residual < 1e-9 and pres < 1e-12
                check.update(zeroSC_position_residual_m=residual,
                             zeroSC_momentum_residual_betagamma=pres)
            if code == 'pyorbit':
                assert m['fixed_lab_mesh'] and not m['transverse_work_patch']
                assert m['physical_g'] == 6.36
                effective_g = m['longitudinal_period_m']*m['native_encoded_step_g']/.1
                assert abs(effective_g-6.36) < 1e-14
                assert m['guard_check']['maximum_native_gradient'] == 0.
                check['longitudinal_step_encoding_recovers_g'] = effective_g
            else:
                assert m['original_solver'] and not m['nonlocal_3D_operator']
                assert m['g'] == 6.36 and m['sc_field_update'] == 'MIDPOINT'
                # Recover final coordinates directly from native storage.
                with h5py.File(case/'track.h5') as h:
                    group = h[next(iter(h))]
                    rref = np.asarray(group.attrs['RefPartR'])
                    pref = np.asarray(group.attrs['RefPartP'])
                    t = math.atan2(-pref[0], pref[2])
                    b = np.array([[math.cos(t),0.,-math.sin(t)], [0.,1.,0.],
                                  [math.sin(t),0.,math.cos(t)]])
                    raw_position = np.c_[group['x'][:],group['y'][:],group['z'][:]]@b.T+rref
                    order = np.argsort(group['id'][:])
                    assert np.max(abs(raw_position[order]-positions)) < 1e-15
                    native_q = group['q'][:]
                    assert np.max(abs(native_q-q)) < q*5e-12
                    check['direct_H5_frame_and_all_native_q_passed'] = True
            results['straight_cases'].append(check)
    results['passed'] = True
    results['limits'] = [
        'Only the initial uniform sources and completed straight ten-step controls are audited here.',
        'Native PyORBIT transverse kicks retain their documented missing transverse-work update; this is a method difference.',
        'A ten-step code-to-code screen is not convergence, full finite-source field validation, or a curved transport certificate.',
        'The curved source tangent momenta have common rigidity: off-axis particles do not initially follow concentric circles of radius R+u.'
    ]
    (OUT/'tracking-contract-audit.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__ == '__main__':
    main()
