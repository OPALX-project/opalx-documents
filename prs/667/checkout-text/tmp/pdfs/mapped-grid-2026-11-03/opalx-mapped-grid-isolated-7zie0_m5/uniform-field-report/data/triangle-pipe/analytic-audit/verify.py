#!/usr/bin/env python3
"""Independent quadrature checks for the triangular-pipe analytic reference."""

import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from analytic import Benchmark, EPSILON_0


def main():
    case = Benchmark()
    q_integral = quad(case.line_density, -case.length_m/2, case.length_m/2, points=[0])[0]
    mean_g_quad = quad(lambda r: 2*r/case.beam_radius_m**2 * case.geometry_factor(r), 0, case.beam_radius_m)[0]

    def potential_from_density(r, s):
        density = case.line_density(s) / (np.pi*case.beam_radius_m**2)

        def er_from_gauss(radius):
            if radius == 0:
                return 0.0
            enclosed_per_length = quad(lambda rp: density*2*np.pi*rp, 0, min(radius, case.beam_radius_m))[0]
            return enclosed_per_length / (2*np.pi*EPSILON_0*radius)

        return quad(er_from_gauss, r, case.pipe_radius_m, points=[case.beam_radius_m] if r<case.beam_radius_m else None)[0]

    ds = 0.001
    points = [(s,r) for s in [-4,-2,2,4] for r in [0,.0025,.005,.01]]
    errors = []
    for s,r in points:
        finite_gradient = -(potential_from_density(r,s+ds)-potential_from_density(r,s-ds))/(2*ds*case.gamma**2)
        ref = case.longitudinal_field(s,r)
        errors.append(abs(finite_gradient/ref-1))
    result = {
        "charge_integral_relative_error": abs(q_integral/case.charge_C-1),
        "disk_mean_geometry_factor_relative_error": abs(mean_g_quad/case.g_mean-1),
        "independent_gauss_potential_longitudinal_gradient_max_relative_error": max(errors),
        "gradient_points": len(points),
        "finite_difference_half_spacing_m": ds,
        "all_pass": bool(abs(q_integral/case.charge_C-1)<1e-12 and abs(mean_g_quad/case.g_mean-1)<1e-12 and max(errors)<1e-9),
    }
    if not result["all_pass"]:
        raise RuntimeError(result)
    print(json.dumps(result,indent=2))
    (Path(__file__).parent/"analytic-checks.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__ == "__main__":
    main()
