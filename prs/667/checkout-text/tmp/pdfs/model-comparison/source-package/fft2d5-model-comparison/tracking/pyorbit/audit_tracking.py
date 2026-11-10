#!/usr/bin/env python3
"""Read-only structural audit of four native ten-step tracking payloads."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TRACKING = HERE.parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    cases, comparisons = [], []
    for geometry in ['straight', 'bend']:
        for mode in ['ZeroSC', '10pC']:
            folder = HERE/'runs'/f'{geometry}-{mode}-10steps'
            meta = json.loads((folder/'manifest.json').read_text())
            data = pd.read_csv(folder/'moments.csv', float_precision='round_trip')
            assert meta['passed'] and meta['steps'] == 10
            assert len(data) == 11 and data.step.to_list() == list(range(11))
            assert meta['guard_check']['passed'] and meta['guard_check']['maximum_native_gradient'] == 0.
            assert meta['source_json_sha256'] == sha(meta['source_json'])
            assert meta['source']['npz_sha256'] == sha(meta['source']['npz'])
            assert meta['native_driver_sha256'] == sha(meta['argv'][0])
            assert bool(meta['space_charge_enabled']) == (mode == '10pC')
            assert abs(data.time_s.iloc[-1]-10*meta['dt_s']) < 1e-18
            assert data.particles.nunique() == 1 and int(data.particles.iloc[0]) == 1048576
            assert np.isfinite(data.select_dtypes(include='number')).all().all()
            assert abs(meta['native_encoded_step_g']*meta['longitudinal_period_m']-meta['physical_g']*meta['ds_m']) < 1e-14
            with np.load(folder/'final-particles.npz') as final:
                assert np.array_equal(final['source_particle_id'], np.arange(1048576))
                assert np.isfinite(final['positions_m']).all() and np.isfinite(final['momenta_betagamma']).all()
                if geometry == 'bend':
                    assert np.max(np.abs(final['positions_frenet_m'][:, 2]-(final['native_state'][:, 4]+1.))) < 1e-14
            for item in meta['native_libraries'].values():
                assert sha(item['path']) == item['sha256']
            other = pd.read_csv(TRACKING/'opalx/runs'/f'{geometry}-{mode}-10steps-e85/moments.csv', float_precision='round_trip')
            keys = (['sigma_global_x_m', 'sigma_global_y_m', 'sigma_global_z_m'] if geometry == 'straight'
                    else ['sigma_frenet_u_m', 'sigma_frenet_y_m', 'sigma_frenet_s_m'])
            error = 100*(data[keys].to_numpy()-other[keys].to_numpy())/other[keys].to_numpy()
            cases.append(dict(case=folder.name, passed=True, rows=len(data), steps=10,
                              final_rms_m=data[keys].iloc[-1].to_dict(), source_hash=meta['source']['npz_sha256']))
            comparisons.append(dict(case=folder.name,
                max_abs_rms_difference_percent=dict(zip(keys, np.max(np.abs(error), axis=0).tolist()))))
    result = dict(passed=True, native_cases=cases, comparisons=comparisons,
                  no_native_solver_edits=True, exactly_ten_steps=True, no_extra_refinement_runs=True,
                  guards_verified_zero=True, audit_script_sha256=sha(__file__),
                  limits=['Native transverse SC work is not added to native dE; no patch applied.',
                          'Bend uses native TEAPOT paraxial body maps and circular embedding of native local coordinates.',
                          'Common bend SC period/mesh is pinned; native Frenet versus OPALX 5 mm polyline coordinates are documented.',
                          'Use mean_absolute_s_m for the absolute PyORBIT bend centroid; mean_frenet_s_m/native_mean_4 are relative.',
                          'RMS agreement tests matched reduced-model tracking, not full 3D curved-source accuracy.'])
    (HERE/'completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, cases=len(cases), comparisons=comparisons), indent=2))


if __name__ == '__main__':
    main()
