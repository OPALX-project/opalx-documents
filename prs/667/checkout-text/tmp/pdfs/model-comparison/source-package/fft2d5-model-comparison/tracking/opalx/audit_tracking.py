#!/usr/bin/env python3
"""Aggregate the four authorized native ten-step tracking controls."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import run_tracking as driver

ROOT = Path(__file__).resolve().parent
selected = []
for geometry in ['straight', 'bend']:
    paths = json.loads((ROOT/f'selected-{geometry}.json').read_text())
    assert len(paths) == 2
    selected.extend(paths)
rows = []
for path in selected:
    path = Path(path)
    m = json.loads(path.read_text())
    checks = json.loads((path.parent/'integrity.json').read_text())
    assert m['returncode'] == 0 and m['integrity_passed'] and checks['passed']
    assert m['steps'] == 10 and m['expected_particles'] == 1048576
    assert m['nonlocal_3D_operator'] is False and m['binary_sha256'] == driver.BINARY_SHA
    assert m['assigned_charge_C'] == 1e-11 and m['sc_field_update'] == 'MIDPOINT'
    assert checks['all_stat_counts_charge_time_finite_passed']
    assert checks['all_saved_ids_q_frames_finite_passed']
    assert m['nominal_design_path_advance_m'] == 1.
    assert abs(m['total_time_s']-driver.TOTAL_TIME) < 1e-18
    for key in ['distribution', 'npz']:
        assert driver.sha(m['source'][key]) == m['source'][key+'_sha256']
    moments = pd.read_csv(path.parent/'moments.csv')
    assert len(moments) == 11 and np.array_equal(moments.step, np.arange(11))
    assert np.allclose(moments.time_s, np.arange(11)*driver.DT, rtol=1e-12, atol=1e-18)
    fields = ['sigma_global_x_m', 'sigma_global_y_m', 'sigma_global_z_m']
    if m['geometry'] == 'bend':
        fields += [f'sigma_frenet_{d}_m' for d in ['u', 'y', 's']]
        fields += [f'cov_frenet_{a}{b}_m2' for a in ['u', 'y', 's'] for b in ['u', 'y', 's']]
    assert np.isfinite(moments[fields]).all().all()
    if m['zero_sc']:
        assert checks['zero_sc_kinematics_checked']
    final = moments.iloc[-1]
    row = dict(name=m['name'], geometry=m['geometry'], zero_sc=m['zero_sc'],
        native_elapsed_s=m['elapsed_s'], initial_plus_endpoint_rows=11,
        saved_particle_snapshots=len(checks['saved_particle_steps']),
        time_s=final.time_s, nominal_design_advance_m=1., all_integrity_passed=True,
        final_sigma_global_x_m=final.sigma_global_x_m,
        final_sigma_global_y_m=final.sigma_global_y_m,
        final_sigma_global_z_m=final.sigma_global_z_m)
    if m['geometry'] == 'bend':
        for direction in ['u', 'y', 's']:
            row['final_sigma_frenet_'+direction+'_m'] = final['sigma_frenet_'+direction+'_m']
    rows.append(row)
pd.DataFrame(rows).to_csv(ROOT/'native-tracking-summary.csv', index=False)
driver.dump(ROOT/'campaign-completion.json', dict(passed=True, native_runs=4,
    requested_steps_per_run=10, source_particles=1048576, source_charge_C=1e-11,
    geometries=['straight', 'bend'], reference_radius_m=2.,
    nominal_design_path_advance_m=1., dt_s=driver.DT, total_time_s=driver.TOTAL_TIME,
    mesh=[128, 128, 512], free_transverse_box_m=[.048, .048],
    solver='immutable e85 original independent 2D slices, OPEN local g=6.36',
    zero_control='same source and nominal charge; TYPE=NONE disables self-fields',
    binary_sha256=driver.BINARY_SHA, no_build=True, no_production_source_change=True,
    nonlocal_3D_operator_used=False, all_counts_q_ids_time_frames_finite_passed=True,
    straight_zero_analytic_translation_passed=True, bend_zero_discrete_Boris_identity_passed=True,
    bend_moments='exact-circle centred u,y,s plus Cartesian moments, initial+all10endpoints',
    native_mpi_ranks=1, native_omp_threads=4, selected=selected))
print('PASS: four native tracking runs, exactly ten steps each')
