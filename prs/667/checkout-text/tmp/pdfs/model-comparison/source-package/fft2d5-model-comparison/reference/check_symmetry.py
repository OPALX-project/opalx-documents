#!/usr/bin/env python3
"""Read-only reflection/round-symmetry checks on the generated references."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from straight_reference import field

ROOT = Path(__file__).resolve().parent


def main():
    rows = []
    for geometry in ['straight', 'curved_R2']:
        for profile in ['uniform', 'triangle']:
            data = pd.read_csv(ROOT/(geometry+'_'+profile+'_fields.csv'), float_precision='round_trip')
            table = {tuple(np.round(row[['u_m', 'y_m', 's_m']].to_numpy(dtype=float), 10)):
                     row[['E_r_V_m', 'E_y_V_m', 'E_s_V_m']].to_numpy(dtype=float)
                     for _, row in data.iterrows()}
            maxima = {}
            # Radial reflection is deliberately NOT a symmetry of a curved tube.
            for axis in ([0, 1, 2] if geometry == 'straight' else [1, 2]):
                maximum = 0.
                pairs = 0
                for target, value in table.items():
                    reflected = list(target)
                    reflected[axis] *= -1
                    other = table.get(tuple(reflected))
                    if other is None:
                        continue
                    expected = value.copy()
                    expected[axis] *= -1
                    maximum = max(maximum, float(np.max(abs(other-expected))))
                    pairs += 1
                assert pairs == 51
                assert maximum < 2e-11
                maxima['uys'[axis]] = dict(targets=pairs, max_field_difference_V_m=maximum)
            rows.append(dict(geometry=geometry, profile=profile, reflections=maxima))
    rotations = []
    for profile in ['uniform', 'triangle']:
        target = np.array([.006, .004, 1.25])
        base = field(.02, 2.5, 1e-11, target, profile, 1024, 96)
        rotated = field(.02, 2.5, 1e-11, [-target[1], target[0], target[2]], profile, 1024, 96)
        difference = float(np.max(abs(rotated-np.array([-base[1], base[0], base[2]]))))
        assert difference < 2e-13
        rotations.append(dict(profile=profile, angle_degrees=90, max_field_difference_V_m=difference))
    result = dict(passed=True, reference_reflections=rows, straight_round_rotations=rotations,
                  curved_radial_reflection_not_assumed=True)
    (ROOT/'symmetry-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
