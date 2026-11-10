"""SACR prototype: uniform curved ellipsoid fields and the Dubin straight limit.

Uses the exact Coulomb surface identity E/(k*rho)=int_boundary n'/distance dS.
No OPALX field values, grid, fitted g, softening or particle dynamics enter.
This is a field-operator check, not a complete SACR implementation.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

import numpy as np
import pandas as pd
from scipy.integrate import quad, quad_vec
from scipy.special import elliprd

ROOT = Path(__file__).resolve().parent


def position(s, u, y, radius):
    """OPALX x-z orbit; the flat limit has coordinates (u,y,s)."""
    if math.isinf(radius):
        return np.array([u, y, s])
    theta = s / radius
    return np.array([u*np.cos(theta)-2*radius*np.sin(theta/2)**2,
                     y, (radius+u)*np.sin(theta)])


def basis(s, radius):
    theta = 0. if math.isinf(radius) else s/radius
    return np.array([[np.cos(theta), 0., -np.sin(theta)],
                     [0., 1., 0.], [np.sin(theta), 0., np.cos(theta)]])


def dubin_field(a, b, c, local_target):
    """E/(k*rho) in radial,vertical,tangential order; k=1/(4*pi*epsilon0)."""
    vals = np.square([a, c, b])
    factors = np.array([a*b*c/3*elliprd(vals[(i+1)%3], vals[(i+2)%3], vals[i])
                        for i in range(3)])
    if abs(factors.sum()-1) > 1e-13:
        raise ValueError("Depolarization factors do not sum to one")
    return 4*np.pi*factors*np.asarray(local_target)


def sacr_field(a, b, c, local_target, radius=math.inf, nphi=128):
    """Uniform physical density; section tapers as sqrt(1-s^2/b^2).

    Boundary parameter mu=s/b, phi in [0,2pi]. Vector area is
    bc*J*w*cos(phi)*e_r + ab*J*w*sin(phi)*e_y + ac*mu*e_s,
    w=sqrt(1-mu^2), J=1+u/R. Integrate its Coulomb potential kernel.
    """
    ut, yt, st = local_target
    if (ut/a)**2+(yt/c)**2+(st/b)**2 >= 1:
        raise ValueError("Use targets strictly inside the test ellipsoid")
    if not math.isinf(radius) and radius <= a:
        raise ValueError("Tube must not intersect the bend axis")
    if not math.isinf(radius) and b/radius >= np.pi:
        raise ValueError("Tapered finite arc must not wrap onto itself")
    target = position(st, ut, yt, radius)
    total = np.zeros(3)
    for phi in 2*np.pi*(np.arange(nphi)+.5)/nphi:
        cp, sp = np.cos(phi), np.sin(phi)
        def integrand(mu):
            w = np.sqrt(max(0., 1-mu*mu))
            s, u, y = b*mu, a*w*cp, c*w*sp
            jac = 1. if math.isinf(radius) else 1+u/radius
            vector_area = basis(s, radius) @ np.array([b*c*jac*w*cp,
                                                       a*b*jac*w*sp, a*c*mu])
            return vector_area/np.linalg.norm(target-position(s, u, y, radius))
        result, _, info = quad_vec(integrand, -1, 1, points=[st/b],
                                  epsabs=1e-13, epsrel=2e-10, limit=500,
                                  full_output=True)
        if not info.success:
            raise RuntimeError(f"Surface quadrature failed: {info.message}")
        total += result
    return basis(st, radius).T @ (total*(2*np.pi/nphi))


def tangent_endpoint(a, b, c, local_target, radius=math.inf, nphi=128):
    """Independent exact tangential reduction with transverse-dependent ends.

    At each (u,y), s_plus/minus=+/-b*sqrt(1-u^2/a^2-y^2/c^2).
    The common end planes of a constant-section tube cannot be used here.
    """
    ut, yt, st = local_target
    total = 0.
    for phi in 2*np.pi*(np.arange(nphi)+.5)/nphi:
        cp, sp = np.cos(phi), np.sin(phi)
        def integrand(w):
            rr = np.sqrt(max(0., 1-w*w))
            u, y = a*rr*cp, c*rr*sp
            if math.isinf(radius):
                dp = np.sqrt((ut-u)**2+(yt-y)**2+(st-b*w)**2)
                dm = np.sqrt((ut-u)**2+(yt-y)**2+(st+b*w)**2)
                ratio = 1.
            else:
                rt, rs = radius+ut, radius+u
                dp = np.sqrt((ut-u)**2+(yt-y)**2+4*rt*rs*np.sin((b*w-st)/(2*radius))**2)
                dm = np.sqrt((ut-u)**2+(yt-y)**2+4*rt*rs*np.sin((-b*w-st)/(2*radius))**2)
                ratio = rs/rt
            return w*ratio*(1/dp-1/dm)
        value, _ = quad(integrand, 0, 1, points=[abs(st)/b],
                        epsabs=1e-11/b, epsrel=2e-10, limit=500)
        total += value
    return a*c*(2*np.pi/nphi)*total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT/"results")
    args = parser.parse_args()
    out = args.outdir
    out.mkdir(parents=True, exist_ok=True)
    cases = {"sphere": (.005, .005, .005),
             "previous_100mm_ellipsoid": (.005, .05, .0005),
             "five_metre_ellipsoid": (.005, 2.5, .0005)}
    rows = []
    for name, (a,b,c) in cases.items():
        target = np.array([.2*a, .1*c, .3*b])
        exact = dubin_field(a,b,c,target)
        for nphi in (64,128,256):
            value = sacr_field(a,b,c,target,nphi=nphi)
            for i,direction in enumerate(("radial","vertical","tangential")):
                rows.append(dict(case=name,a_m=a,b_m=b,c_m=c,
                                 target_u_over_a=.2,target_y_over_c=.1,target_s_over_b=.3,
                                 angular_nodes=nphi,direction=direction,
                                 sacr_field_div_k_rho_m=float(value[i]),
                                 dubin_field_div_k_rho_m=float(exact[i]),
                                 relative_error=float(value[i]/exact[i]-1)))
    flat = pd.DataFrame(rows)
    flat.to_csv(out/"dubin_straight_limit.csv", index=False)
    final = flat[flat.angular_nodes==256]
    assert final.relative_error.abs().max() < 1e-6

    a,b,c = cases["five_metre_ellipsoid"]
    target = np.array([.2*a,.1*c,.3*b])
    exact = dubin_field(a,b,c,target)
    rows = []
    for radius in (2.,20.,200.,2000.,math.inf):
        value = sacr_field(a,b,c,target,radius=radius,nphi=256)
        endpoint = tangent_endpoint(a,b,c,target,radius=radius,nphi=256)
        assert abs(value[2]/endpoint-1) < 1e-6
        for i,direction in enumerate(("radial","vertical","tangential")):
            rows.append(dict(radius_m=radius,direction=direction,
                             sacr_field_div_k_rho_m=float(value[i]),
                             dubin_field_div_k_rho_m=float(exact[i]),
                             relative_difference_from_flat=float(value[i]/exact[i]-1),
                             tangent_endpoint_relative_difference=float(value[2]/endpoint-1)))
    scan = pd.DataFrame(rows)
    scan.to_csv(out/"radius_limit.csv", index=False)
    summary = {"model":"semi-analytic curved-tube reference (SACR)",
               "scope":"prototype static field operator, uniform-density tapered source; one off-axis target per shape",
               "normalization":"field/(k*rho), k=1/(4*pi*epsilon0); result has units metre",
               "largest_flat_limit_component_relative_error_256_nodes":float(final.relative_error.abs().max()),
               "largest_tangent_surface_vs_endpoint_relative_difference":float(scan.tangent_endpoint_relative_difference.abs().max()),
               "passed":True,
               "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/"acceptance.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(final.groupby("case").relative_error.apply(lambda x: x.abs().max()).to_string())
    print(scan.to_string(index=False))
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
