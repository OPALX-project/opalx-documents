#!/usr/bin/env python3
"""Check and join the two independently implemented SACR extension results."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    volume = json.loads((ROOT/'volume_acceptance.json').read_text())
    radius = json.loads((ROOT/'radius-sweep/acceptance.json').read_text())
    assert volume['passed'] and radius['passed']
    for name, digest in volume['output_sha256'].items():
        assert sha(ROOT/name) == digest
    for name, digest in radius['output_sha256'].items():
        assert sha(ROOT/'radius-sweep'/name) == digest
    fields = pd.read_csv(ROOT/'radius-sweep/radius_fields.csv', float_precision='round_trip')
    assert len(fields) == 300
    coordinates = fields.groupby(['profile','point_id'])[['u_m','y_m','s_m']].nunique()
    assert (coordinates == 1).all().all()
    assert (fields.groupby(['profile','point_id']).size() == 10).all()
    checks = []
    for profile in ['uniform','triangle']:
        chosen = fields[fields.profile == profile]
        for d in ['u','y','s']:
            scale = radius['fixed_full51_straight_scales_V_m'][profile][d]
            rows = []
            for value, block in chosen.groupby('R_m'):
                maximum = float(max(abs(block['E_'+d]-block['straight_'+d])))
                rows.append((float(value), maximum, maximum/scale))
            rows.sort()
            finite = [r for r in rows if np.isfinite(r[0])]
            decreasing = bool(np.all(np.diff([r[1] for r in finite]) <= 1e-12))
            assert decreasing
            limit = next(r for r in rows if np.isinf(r[0]))
            assert limit[1] < 2e-10
            checks.append(dict(profile=profile,component=d,
                maximum_over_selected_targets_monotone_to_straight=decreasing,
                R2_max_abs_difference_V_m=finite[0][1],R2_max_difference_over_fixed_scale=finite[0][2],
                R1000_max_abs_difference_V_m=finite[-1][1],R1000_max_difference_over_fixed_scale=finite[-1][2],
                infinity_max_abs_difference_V_m=limit[1]))
    refinement = pd.read_csv(ROOT/'volume_refinement.csv',float_precision='round_trip')
    refinement_summary = refinement.groupby(['profile','nphi','nrad'],as_index=False).agg(
        max_absolute_difference_V_m=('difference_V_m',lambda x:abs(x).max()),
        max_fixed_scale_error=('scaled_abs_difference','max'))
    refinement_summary.to_csv(ROOT/'volume_error_summary.csv',index=False,float_format='%.17g')
    reference = ROOT.parent/'reference'
    original = json.loads((reference/'acceptance.json').read_text())
    assert all(sha(reference/name) == digest for name,digest in original['output_sha256'].items())
    result = dict(passed=True,date='2026-11-04',
        current_source=dict(full_length_m=5.,transverse_radius_m=.02,charge_C=1e-11,
                            physical_density_profiles=['uniform','triangle'],curved_test_radius_m=2.),
        direct_volume=dict(point_profile_cases=volume['point_cases'],components=volume['scalar_components'],
            mixed_all_components_nonzero_cases=volume['mixed_all_nonzero_point_cases'],
            maximum_absolute_difference_V_m=volume['maximum_absolute_difference_V_m'],
            maximum_nonzero_relative_error=volume['maximum_nonzero_component_relative_error'],
            maximum_fixed_scale_error=volume['maximum_fixed_scale_error'],
            maximum_final_refinement_delta_V_m=volume['maximum_last_refinement_delta_V_m']),
        radius_sweep=dict(material_targets=radius['targets'],radii_per_profile=10,profiles=2,
            field_rows=300,scalar_fields=900,maximum_quadrature_change_V_m=radius['worst_recorded_quadrature_change_V_m'],
            maximum_straight_limit_difference_V_m=max(c['infinity_max_abs_difference_V_m'] for c in checks),
            component_summary=checks),
        old_reference_outputs_unchanged=True,no_native_runs=True,no_production_edits=True,
        output_paths=dict(volume='volume_checks.csv',volume_refinement='volume_error_summary.csv',
            radii='radius-sweep/radius_fields.csv',radius_summary='radius-sweep/radius-error-summary.csv'),
        limits=['Sampled validation for the stated constant round tube and two profiles, not a uniform error bound over every target/source shape.',
                'Closest mixed off-axis control is5mm inside an end; a0.1mm end control is on axis.',
                'This validates frozen SACR fields; tracking, energy conservation and conducting boundaries remain separate.',
                'Finite-radius differences from straight fields are physical geometry changes, not quadrature error.'],
        provenance=dict(volume_acceptance_sha256=sha(ROOT/'volume_acceptance.json'),
            radius_acceptance_sha256=sha(ROOT/'radius-sweep/acceptance.json'),
            original_reference_acceptance_sha256=sha(reference/'acceptance.json'),
            integration_script_sha256=sha(Path(__file__))))
    (ROOT/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
