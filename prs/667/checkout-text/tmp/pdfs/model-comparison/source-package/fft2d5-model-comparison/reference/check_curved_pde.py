#!/usr/bin/env python3
"""Metric divergence/curl checks for the new round R=2 m SACR fields."""
from pathlib import Path
import json
import numpy as np
from scipy.constants import epsilon_0
from build_reference import curved_modules, peak_density, K, A, H, Q, R

ROOT = Path(__file__).resolve().parent


def main():
    uniform, triangle = curved_modules()
    target = np.array([.3*A, .2*A, .5*H])
    step = A*1e-3
    curvature = 1/R
    metric = 1+curvature*target[0]
    rows = []
    for profile in ['uniform', 'triangle']:
        evaluate = uniform.field if profile == 'uniform' else triangle.triangle_field
        rho_peak = peak_density(A, H, Q, profile)
        def field(point):
            return K*rho_peak*evaluate(A, A, H, point, R, 1024, 96)
        center = field(target)
        jac = np.empty((3, 3))
        for j in range(3):
            offset = np.eye(3)[j]*step
            jac[:, j] = (field(target+offset)-field(target-offset))/(2*step)
        divergence = jac[0, 0]+jac[1, 1]+jac[2, 2]/metric+curvature*center[0]/metric
        curl = np.array([jac[2, 1]-jac[1, 2]/metric,
                         jac[0, 2]/metric-jac[2, 0]-curvature*center[2]/metric,
                         jac[1, 0]-jac[0, 1]])
        rho = rho_peak*(1 if profile == 'uniform' else 1-abs(target[2])/H)
        scale = rho/epsilon_0
        assert abs(divergence/scale-1) < 2e-6
        assert max(abs(curl))/scale < 2e-6
        rows.append(dict(profile=profile, target_m=target.tolist(), difference_step_m=step,
                         metric=metric, divergence_V_m2=divergence, rho_over_epsilon_V_m2=scale,
                         relative_divergence_error=divergence/scale-1,
                         curl_V_m2=curl.tolist(), max_curl_over_rho_epsilon=float(max(abs(curl))/scale)))
    result = dict(passed=True, geometry='exact circular metric J=1+u/R', radius_m=R, checks=rows)
    (ROOT/'curved-pde-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
