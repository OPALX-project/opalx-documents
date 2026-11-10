#!/usr/bin/env python3
"""Matched physical targets for the round straight/curved beam paper."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parents[1]/'sacr/free-r2-profiles/reference/points_extended.csv'


def main():
    original = pd.read_csv(OLD, float_precision='round_trip')
    points = original.copy()
    points['u_m'] *= .020/.005
    points['y_m'] *= .020/.0005
    for radius, name in [(np.inf, 'straight_points.csv'), (2., 'curved_R2_points.csv')]:
        out = points.copy()
        u, y, s = out[['u_m', 'y_m', 's_m']].to_numpy().T
        if np.isinf(radius):
            out['x_m'], out['global_y_m'], out['z_m'] = u, y, s
        else:
            out['x_m'] = u*np.cos(s/radius)-2*radius*np.sin(s/(2*radius))**2
            out['global_y_m'] = y
            out['z_m'] = (radius+u)*np.sin(s/radius)
        out.to_csv(ROOT/name, index=False, float_format='%.17g')
    result = dict(full_length_m=5., charge_C=1e-11, radial_semiaxis_m=.02,
                  vertical_semiaxis_m=.02, rms_x_m=.01, rms_y_m=.01,
                  profiles=['uniform', 'triangle'], curved_radius_m=2.,
                  targets=len(points), original_targets=int(points.original_target.sum()),
                  prior_target_file=str(OLD), prior_target_sha256=hashlib.sha256(OLD.read_bytes()).hexdigest(),
                  unchanged_longitudinal_coordinates=True,
                  axis_end_distances_m=sorted(set(points.loc[abs(points.u_m)+abs(points.y_m)==0, 'end_distance_m'])))
    (ROOT/'parameters.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
