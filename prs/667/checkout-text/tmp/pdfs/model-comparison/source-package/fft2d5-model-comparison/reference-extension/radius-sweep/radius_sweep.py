#!/usr/bin/env python3
"""Fixed-source SACR radius sweep with separate angular/radial error checks."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import shutil
import sys
import time

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from scipy.constants import epsilon_0

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT.parents[1]/'reference'
A, H, Q = .020, 2.5, 1e-11
K = 1/(4*np.pi*epsilon_0)
RADII = [2., 5., 10., 20., 50., 100., 200., 500., 1000., math.inf]
POINT_IDS = [
    'centre', 'axis_r_-0.5', 'axis_r_+0.5', 'axis_r_+0.9',
    'axis_y_-0.5', 'axis_y_+0.5', 'axis_s_-0.500', 'axis_s_+0.500',
    'axis_s_+0.998', 'bulk_-0.50_+0.25_+0.50', 'bulk_+0.50_-0.25_+0.90',
    'end_-0.50_-0.25_-0.996', 'end_+0.50_+0.25_+0.996',
    'extra_axis_-2.4999', 'extra_axis_+2.4999']
TOLERANCE_V_M = 2e-8


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name, source):
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def producers():
    provenance = ROOT/'provenance'
    provenance.mkdir(exist_ok=True)
    names = ['uniform_reference', 'profile_reference']
    paths = {}
    for name in names:
        matches = list((REFERENCE/'provenance').glob(name+'-*.py'))
        assert len(matches) == 1
        source = matches[0]
        target = provenance/source.name
        if not target.exists():
            shutil.copy2(source, target)
        assert sha(source) == sha(target)
        paths[name] = target
    straight = REFERENCE/'straight_reference.py'
    target = provenance/('straight_reference-'+sha(straight)+'.py')
    if not target.exists():
        shutil.copy2(straight, target)
    assert sha(target) == sha(straight)
    paths['straight_reference'] = target
    uniform = load('uniform_reference', paths['uniform_reference'])
    triangle = load('radius_sweep_triangle', paths['profile_reference'])
    straight = load('radius_sweep_straight', paths['straight_reference'])
    return uniform, triangle, straight, paths


def main():
    start = time.monotonic()
    uniform, triangle, straight, paths = producers()
    points = pd.read_csv(REFERENCE/'straight_points.csv', float_precision='round_trip').set_index('point_id').loc[POINT_IDS].reset_index()
    points.to_csv(ROOT/'selected-points.csv', index=False, float_format='%.17g')
    values, convergence, wide, final_long, scales_out, checks = [], [], [], [], {}, []
    for profile in ['uniform', 'triangle']:
        complete_straight = pd.read_csv(REFERENCE/f'straight_{profile}_fields.csv', float_precision='round_trip').set_index('point_id')
        exact = complete_straight.loc[POINT_IDS, ['E_r_V_m', 'E_y_V_m', 'E_s_V_m']].to_numpy()
        # Fixed full-51 scales, including the explicitly declared extra targets.
        scales = complete_straight[['E_r_V_m', 'E_y_V_m', 'E_s_V_m']].abs().max().to_numpy()
        scales_out[profile] = dict(zip(['u', 'y', 's'], scales.tolist()))
        rho = straight.peak_density(A, H, Q, profile)
        evaluator = uniform.field if profile == 'uniform' else triangle.triangle_field
        coarse_nr, fine_nr = (160, 192) if profile == 'uniform' else (64, 96)
        for radius in RADII:
            label = 'inf' if math.isinf(radius) else f'{radius:g}'
            rules = [(512, coarse_nr), (1024, coarse_nr), (1024, fine_nr)]
            arrays = []
            angular = radial = None
            for rule_index, (nphi, nrad) in enumerate(rules):
                current = np.array([K*rho*evaluator(A, A, H, target, radius, nphi, nrad)
                                    for target in points[['u_m', 'y_m', 's_m']].to_numpy()])
                arrays.append(current)
                if rule_index:
                    difference = current-arrays[rule_index-1]
                    if rule_index == 1:
                        angular = difference
                    else:
                        radial = difference
                    convergence.append(dict(profile=profile, R_m=radius, radius_label=label,
                        check='angular' if rule_index == 1 else 'radial', nphi=nphi, nrad=nrad,
                        max_abs_change_u_V_m=float(np.max(np.abs(difference[:, 0]))),
                        max_abs_change_y_V_m=float(np.max(np.abs(difference[:, 1]))),
                        max_abs_change_s_V_m=float(np.max(np.abs(difference[:, 2]))),
                        max_change_over_fixed_scale=float(np.max(np.abs(difference)/scales))))
                for index, point in points.iterrows():
                    for j, direction in enumerate(['u', 'y', 's']):
                        values.append(dict(profile=profile, point_id=point.point_id, R_m=radius,
                            radius_label=label, u_m=point.u_m, y_m=point.y_m, s_m=point.s_m,
                            quadrature_index=rule_index, nphi=nphi, nrad=nrad,
                            component=direction, E_V_m=current[index, j]))
            final = arrays[-1]
            maximum_angular = float(np.max(np.abs(angular)))
            maximum_radial = float(np.max(np.abs(radial)))
            # Extra refinement only if the predeclared independent changes fail.
            if max(maximum_angular, maximum_radial) > TOLERANCE_V_M:
                nphi, nrad = 2048, (256 if profile == 'uniform' else 128)
                extra = np.array([K*rho*evaluator(A, A, H, target, radius, nphi, nrad)
                                  for target in points[['u_m', 'y_m', 's_m']].to_numpy()])
                delta = extra-final
                convergence.append(dict(profile=profile, R_m=radius, radius_label=label,
                    check='additional_joint', nphi=nphi, nrad=nrad,
                    max_abs_change_u_V_m=float(np.max(np.abs(delta[:, 0]))),
                    max_abs_change_y_V_m=float(np.max(np.abs(delta[:, 1]))),
                    max_abs_change_s_V_m=float(np.max(np.abs(delta[:, 2]))),
                    max_change_over_fixed_scale=float(np.max(np.abs(delta)/scales))))
                assert np.max(np.abs(delta)) < TOLERANCE_V_M, (profile, radius, np.max(np.abs(delta)))
                final = extra
                uncertainty = np.abs(delta)
            else:
                nphi, nrad = rules[-1]
                uncertainty = np.maximum(np.abs(angular), np.abs(radial))
            if math.isinf(radius):
                difference = float(np.max(np.abs(final-exact)))
                assert difference < TOLERANCE_V_M, (profile, difference)
                # Independent direct straight producer is explicitly re-evaluated.
                direct = np.array([straight.field(A, H, Q, target, profile, 1024, 96)
                                   for target in points[['u_m', 'y_m', 's_m']].to_numpy()])
                independent_difference = float(np.max(np.abs(final-direct)))
                assert independent_difference < TOLERANCE_V_M
                checks.append(dict(profile=profile, curved_producer_inf_vs_archived_straight_max_V_m=difference,
                                   curved_producer_inf_vs_independent_straight_max_V_m=independent_difference))
            if radius == 2.:
                old = pd.read_csv(REFERENCE/f'curved_R2_{profile}_fields.csv', float_precision='round_trip').set_index('point_id')
                difference = float(np.max(np.abs(final-old.loc[POINT_IDS, ['E_r_V_m', 'E_y_V_m', 'E_s_V_m']].to_numpy())))
                assert difference < TOLERANCE_V_M
                checks.append(dict(profile=profile, R2_vs_existing_full51_reference_max_V_m=difference))
            for index, point in points.iterrows():
                row = dict(profile=profile, point_id=point.point_id, R_m=radius, radius_label=label,
                           curvature_m_inv=0. if math.isinf(radius) else 1/radius,
                           u_m=point.u_m, y_m=point.y_m, s_m=point.s_m,
                           end_distance_m=point.end_distance_m, nphi=nphi, nrad=nrad,
                           E_u=final[index, 0], E_y=final[index, 1], E_s=final[index, 2],
                           straight_u=exact[index, 0], straight_y=exact[index, 1], straight_s=exact[index, 2])
                wide.append(row)
                for j, direction in enumerate(['u', 'y', 's']):
                    final_long.append(dict(profile=profile, point_id=point.point_id, R_m=radius,
                        radius_label=label, curvature_m_inv=row['curvature_m_inv'],
                        u_m=point.u_m, y_m=point.y_m, s_m=point.s_m, end_distance_m=point.end_distance_m,
                        component=direction, E_V_m=final[index, j], straight_V_m=exact[index, j],
                        finite_radius_difference_V_m=final[index, j]-exact[index, j],
                        fixed_full51_straight_component_scale_V_m=scales[j],
                        difference_over_fixed_scale=(final[index, j]-exact[index, j])/scales[j],
                        quadrature_change_V_m=uncertainty[index, j],
                        quadrature_change_over_fixed_scale=uncertainty[index, j]/scales[j]))
            pd.DataFrame(wide).to_csv(ROOT/'radius_fields.csv', index=False, float_format='%.17g')
            pd.DataFrame(final_long).to_csv(ROOT/'radius-errors.csv', index=False, float_format='%.17g')
            pd.DataFrame(convergence).to_csv(ROOT/'quadrature-convergence.csv', index=False, float_format='%.17g')
            print(json.dumps(dict(profile=profile, R_m=None if math.isinf(radius) else radius,
                                  targets=len(points), max_angular_change_V_m=maximum_angular,
                                  max_radial_change_V_m=maximum_radial)), flush=True)
    pd.DataFrame(values).to_csv(ROOT/'quadrature-fields.csv', index=False, float_format='%.17g')
    errors = pd.DataFrame(final_long)
    summary = errors.groupby(['profile', 'R_m', 'component'], dropna=False).agg(
        max_absolute_finite_radius_difference_V_m=('finite_radius_difference_V_m', lambda x: float(np.max(np.abs(x)))),
        max_abs_difference_over_fixed_scale=('difference_over_fixed_scale', lambda x: float(np.max(np.abs(x)))),
        max_quadrature_change_V_m=('quadrature_change_V_m', 'max'),
        max_quadrature_change_over_fixed_scale=('quadrature_change_over_fixed_scale', 'max')).reset_index()
    summary.to_csv(ROOT/'radius-error-summary.csv', index=False, float_format='%.17g')
    acceptance = dict(passed=True, physical_parameters=dict(a_m=A, c_m=A, full_length_m=2*H, charge_C=Q),
        radius_values_m=[None if math.isinf(r) else r for r in RADII], infinity_represented_by_null=True,
        fixed_material_target_ids=POINT_IDS, targets=len(points), profiles=['uniform', 'triangle'],
        field_units='SI electrostatic V/m, local outward-u/y/s basis',
        physical_source='same rho(s), Q, physical ellipse and material coordinates at every radius; J=1+u/R',
        normalization='fixed component maxima from each full51 straight reference, never a per-point near-zero denominator',
        fixed_full51_straight_scales_V_m=scales_out, quadrature_tolerance_V_m=TOLERANCE_V_M,
        independent_angular_and_radial_checks=True, endpoint_checks=checks,
        worst_recorded_quadrature_change_V_m=float(errors.quadrature_change_V_m.max()),
        source_sha256={p.name: sha(p) for p in paths.values()},
        input_reference_sha256={name: sha(REFERENCE/name) for name in
            ['straight_points.csv', 'straight_uniform_fields.csv', 'straight_triangle_fields.csv',
             'curved_R2_uniform_fields.csv', 'curved_R2_triangle_fields.csv']},
        script_sha256=sha(__file__), output_sha256={name: sha(ROOT/name) for name in
            ['selected-points.csv', 'radius_fields.csv', 'radius-errors.csv', 'quadrature-convergence.csv',
             'quadrature-fields.csv', 'radius-error-summary.csv']},
        elapsed_seconds=time.monotonic()-start, no_fit_no_softening=True, no_native_solver_runs=True)
    (ROOT/'acceptance.json').write_text(json.dumps(acceptance, indent=2)+'\n')
    print(json.dumps(acceptance, indent=2))


if __name__ == '__main__':
    main()
