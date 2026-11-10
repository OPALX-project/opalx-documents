#!/usr/bin/env python3
"""Refined independent Cartesian-volume checks against the current tube SACR."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from scipy.constants import epsilon_0
from direct_cartesian import original_volume_field

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT.parent/'reference'
A, B, R, Q = .02, 2.5, 2., 1e-11
K = 1/(4*np.pi*epsilon_0)
RULES = [(64, 24), (128, 48), (256, 96), (512, 160)]
SCALED_GOAL, NONZERO_RELATIVE_GOAL = 1e-8, 1e-5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evaluator_modules():
    names = [('uniform_reference', 'uniform_reference'), ('profile_reference', 'extension_profile_reference')]
    modules, hashes = [], {}
    for prefix, module_name in names:
        paths = list((REFERENCE/'provenance').glob(prefix+'-*.py'))
        assert len(paths) == 1
        path = paths[0]
        digest = sha(path)
        assert digest in path.name
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        modules.append(module)
        hashes[str(path)] = digest
    return modules, hashes


def selected_points():
    old = pd.read_csv(REFERENCE/'curved_R2_points.csv', float_precision='round_trip').set_index('point_id')
    selected = ['centre', 'bulk_+0.50_+0.25_+0.50', 'bulk_-0.50_+0.25_+0.90',
                'end_+0.50_+0.25_+0.996', 'end_-0.50_+0.25_+0.996',
                'axis_s_+0.998', 'extra_axis_+2.4999']
    points = old.loc[selected, ['label', 'u_m', 'y_m', 's_m']].reset_index()
    points['existing_target'] = True
    points = pd.concat([points, pd.DataFrame([dict(point_id='extension_mixed_end_5mm',
        label='mixed_end_5mm', u_m=.01, y_m=.005, s_m=B-.005, existing_target=False)])], ignore_index=True)
    points['end_distance_m'] = B-abs(points.s_m)
    points['all_components_nonzero_expected'] = (abs(points.u_m)>0)&(abs(points.y_m)>0)&(abs(points.s_m)>0)
    points.to_csv(ROOT/'volume_points.csv', index=False, float_format='%.17g')
    return points


def main():
    ROOT.mkdir(exist_ok=True)
    (uniform, triangular), producer_hashes = evaluator_modules()
    points = selected_points()
    final_rows, refinement_rows, boundary_rows, metadata = [], [], [], []
    for profile in ['uniform', 'triangle']:
        existing = pd.read_csv(REFERENCE/f'curved_R2_{profile}_fields.csv', float_precision='round_trip').set_index('point_id')
        scales = np.array([float(abs(existing[f'E_{d}_V_m']).max()) for d in ['r', 'y', 's']])
        density = Q/(np.pi*A*A*B*(2 if profile=='uniform' else 1))
        surface = uniform.field if profile=='uniform' else triangular.triangle_field
        for point in points.itertuples(index=False):
            target = np.array([point.u_m, point.y_m, point.s_m])
            coarse = K*density*surface(A, A, B, target, R, 512, 96)
            truth = K*density*surface(A, A, B, target, R, 1024, 192 if profile=='uniform' else 128)
            assert max(abs(truth-coarse)/scales) < 1e-8
            if point.existing_target:
                archived = existing.loc[point.point_id, ['E_r_V_m', 'E_y_V_m', 'E_s_V_m']].to_numpy(dtype=float)
                assert max(abs(truth-archived)/scales) < 1e-8
            if point.all_components_nonzero_expected:
                assert np.all(abs(truth) > 1e-7*scales)
            previous = None
            current = None
            last_delta = None
            rules = list(RULES)
            for number, (nphi, nrad) in enumerate(rules):
                current, info = original_volume_field(target, profile, nphi=nphi, nrad=nrad)
                delta = np.full(3, np.nan) if previous is None else current-previous
                for j, component in enumerate(['u', 'y', 's']):
                    refinement_rows.append(dict(profile=profile, point_id=point.point_id,
                        u_m=point.u_m, y_m=point.y_m, s_m=point.s_m, component=component,
                        nphi=nphi, nrad=nrad, direct_V_m=current[j], sacr_V_m=truth[j],
                        difference_V_m=current[j]-truth[j], refinement_delta_V_m=delta[j],
                        component_scale_V_m=scales[j], scaled_abs_difference=abs(current[j]-truth[j])/scales[j],
                        adaptive_error_estimate_V_m=info['adaptive_max_error_estimate_V_m']))
                metadata.append(dict(profile=profile, point_id=point.point_id, **info))
                previous, last_delta = current, delta
            nonzero = abs(truth) > max(scales)*1e-10
            scaled_difference = abs(current-truth)/scales
            relative = np.full(3, np.nan)
            relative[nonzero] = abs((current-truth)[nonzero]/truth[nonzero])
            # If a selected case needs more quadrature, refine it locally only.
            if max(scaled_difference) > SCALED_GOAL or max(abs(last_delta)/scales) > SCALED_GOAL or np.nanmax(relative)>NONZERO_RELATIVE_GOAL:
                previous = current
                current, info = original_volume_field(target, profile, nphi=768, nrad=256)
                last_delta = current-previous
                metadata.append(dict(profile=profile, point_id=point.point_id, **info))
                for j, component in enumerate(['u','y','s']):
                    refinement_rows.append(dict(profile=profile, point_id=point.point_id,
                        u_m=point.u_m,y_m=point.y_m,s_m=point.s_m,component=component,nphi=768,nrad=256,
                        direct_V_m=current[j],sacr_V_m=truth[j],difference_V_m=current[j]-truth[j],
                        refinement_delta_V_m=last_delta[j],component_scale_V_m=scales[j],
                        scaled_abs_difference=abs(current[j]-truth[j])/scales[j],
                        adaptive_error_estimate_V_m=info['adaptive_max_error_estimate_V_m']))
                scaled_difference = abs(current-truth)/scales
                relative[nonzero] = abs((current-truth)[nonzero]/truth[nonzero])
            assert max(scaled_difference) < SCALED_GOAL, (profile,point.point_id,scaled_difference)
            assert max(abs(last_delta)/scales) < SCALED_GOAL, (profile,point.point_id,last_delta/scales)
            assert np.nanmax(relative) < NONZERO_RELATIVE_GOAL, (profile,point.point_id,relative)
            for j, component in enumerate(['u', 'y', 's']):
                final_rows.append(dict(profile=profile, point_id=point.point_id, u_m=point.u_m,y_m=point.y_m,s_m=point.s_m,
                    end_distance_m=point.end_distance_m,component=component,sacr_V_m=truth[j],direct_V_m=current[j],
                    difference_V_m=current[j]-truth[j],refinement_delta_V_m=last_delta[j],
                    component_scale_V_m=scales[j],scaled_abs_error=scaled_difference[j],
                    nonzero_component_relative_error=relative[j],
                    all_components_nonzero_case=point.all_components_nonzero_expected))
                boundary_rows.append(dict(profile=profile,point_id=point.point_id,component=component,
                    nphi_coarse=512,nrad_coarse=96,nphi_fine=1024,nrad_fine=192 if profile=='uniform' else 128,
                    coarse_V_m=coarse[j],fine_V_m=truth[j],difference_V_m=truth[j]-coarse[j]))
            pd.DataFrame(final_rows).to_csv(ROOT/'volume_checks.csv',index=False,float_format='%.17g')
            print(json.dumps(dict(profile=profile,point_id=point.point_id,
                maximum_scaled_error=float(max(scaled_difference)),maximum_nonzero_relative_error=float(np.nanmax(relative)))),flush=True)
    final = pd.DataFrame(final_rows)
    pd.DataFrame(refinement_rows).to_csv(ROOT/'volume_refinement.csv',index=False,float_format='%.17g')
    pd.DataFrame(boundary_rows).to_csv(ROOT/'volume_boundary_refinement.csv',index=False,float_format='%.17g')
    result = dict(passed=True,date='2026-11-04',profiles=['uniform','triangle'],radius_m=R,
        transverse_radius_m=A,full_length_m=2*B,charge_C=Q,point_cases=len(final_rows)//3,
        mixed_all_nonzero_point_cases=int(final.groupby(['profile','point_id']).all_components_nonzero_case.first().sum()),
        scalar_components=len(final),maximum_absolute_difference_V_m=float(abs(final.difference_V_m).max()),
        maximum_fixed_scale_error=float(final.scaled_abs_error.max()),
        maximum_nonzero_component_relative_error=float(final.nonzero_component_relative_error.max()),
        maximum_last_refinement_delta_V_m=float(abs(final.refinement_delta_V_m).max()),
        fixed_scale_goal=SCALED_GOAL,nonzero_component_relative_goal=NONZERO_RELATIVE_GOAL,
        zero_handling='Near-zero components use fixed full51 R2SACR component scales; no division by zero or field fitting.',
        independent_method='Literal Cartesian original vector Coulomb volume; linear transverse-ray rule + adaptive full source-s integration.',
        no_surface_helper_in_independent_kernel=True,no_softening_or_exclusion=True,no_charge_renormalization=True,
        source_sha256={name:sha(ROOT/name) for name in ['direct_cartesian.py','run_volume_checks.py']},
        SACR_producer_sha256=producer_hashes,quadrature_metadata=metadata,
        output_sha256={name:sha(ROOT/name) for name in ['volume_points.csv','volume_checks.csv','volume_refinement.csv','volume_boundary_refinement.csv']})
    (ROOT/'volume_acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ['quadrature_metadata','SACR_producer_sha256']},indent=2))


if __name__=='__main__':main()
