"""Independent original Cartesian Coulomb-volume integral for a curved tube.

No SACR, surface-identity, longitudinal-primitive, mesh or particle helper is
imported. The only reduction uses transverse polar rays for the exact source
disk; the original Cartesian three-component kernel is integrated adaptively
over the full source arclength. No path/visibility restriction, fit or softening.
"""
import time
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad_vec
from scipy.constants import epsilon_0


def position(material, radius):
    u, y, s = np.asarray(material, dtype=float)
    if np.isinf(radius):
        return np.array([u, y, s])
    angle = s/radius
    return np.array([u*np.cos(angle)-2*radius*np.sin(angle/2)**2,
                     y, (radius+u)*np.sin(angle)])


def original_volume_field(target, profile, *, radius=2., transverse_radius=.02,
                          half_length=2.5, charge=1e-11, nphi=128, nrad=48,
                          epsabs=1e-12, epsrel=5e-11):
    started = time.monotonic()
    a, b, R = transverse_radius, half_length, radius
    ut, yt, st = np.asarray(target, dtype=float)
    if ut*ut+yt*yt >= a*a or abs(st) >= b:
        raise ValueError('Use a target strictly inside the finite tube.')
    if profile not in ['uniform', 'triangle']:
        raise ValueError(profile)
    if not np.isinf(R) and (R <= a or b/R >= np.pi):
        raise ValueError('Use a regular finite nonwrapping circular tube.')
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    cp, sp = np.cos(phi), np.sin(phi)
    projection = ut*cp+yt*sp
    rmax = -projection+np.sqrt(projection*projection+a*a-ut*ut-yt*yt)
    nodes, weights = leggauss(nrad)
    t = (nodes[:, None]+1)/2
    ray_radius = rmax*t
    # A LINEAR ray map deliberately differs from the SACR logarithmic rule.
    area = (weights[:, None]/2)*rmax*ray_radius*(2*np.pi/nphi)
    source_u, source_y = ut+ray_radius*cp, yt+ray_radius*sp
    jacobian = np.ones_like(source_u) if np.isinf(R) else 1+source_u/R
    rho_peak = charge/(np.pi*a*a*b*(2 if profile == 'uniform' else 1))
    coupling = rho_peak/(4*np.pi*epsilon_0)
    integrated_charge = rho_peak*np.sum(area*jacobian)*b*(2 if profile == 'uniform' else 1)
    assert abs(integrated_charge/charge-1) < 1e-11
    target_xyz = position([ut, yt, st], R)

    def kernel(source_s):
        if np.isinf(R):
            source_x = source_u
            source_z = source_s+np.zeros_like(source_u)
        else:
            angle = source_s/R
            source_x = source_u*np.cos(angle)-2*R*np.sin(angle/2)**2
            source_z = (R+source_u)*np.sin(angle)
        dx, dy, dz = target_xyz[0]-source_x, target_xyz[1]-source_y, target_xyz[2]-source_z
        distance_squared = dx*dx+dy*dy+dz*dz
        # This is the original Coulomb vector, with the actual Cartesian chord.
        volume_weight = area*jacobian/(distance_squared*np.sqrt(distance_squared))
        shape = 1. if profile == 'uniform' else 1-abs(source_s)/b
        return shape*np.array([np.sum(dx*volume_weight), np.sum(dy*volume_weight),
                               np.sum(dz*volume_weight)])

    # Break around the target on scales resolved by this source rule; these
    # partitions cover the COMPLETE domain and introduce no excluded region.
    narrow = float(ray_radius.min())
    widths = np.unique(np.r_[narrow*np.array([.25, 1., 4., 16., 64., 256.]),
                             a*np.array([.01, .1, 1., 4.])])
    splits = sorted(set([0., float(st)]+[float(st+sign*w) for sign in [-1., 1.]
                                       for w in widths if -b < st+sign*w < b]))
    value, error, info = quad_vec(kernel, -b, b, points=splits, epsabs=epsabs,
                                  epsrel=epsrel, norm='max', limit=1500, full_output=True)
    if not info.success:
        raise RuntimeError(info.message)
    cartesian = coupling*value
    angle = 0. if np.isinf(R) else st/R
    local = np.array([cartesian[0]*np.cos(angle)+cartesian[2]*np.sin(angle),
                      cartesian[1], -cartesian[0]*np.sin(angle)+cartesian[2]*np.cos(angle)])
    return local, dict(nphi=nphi, nrad=nrad, source_s_integrand_evaluations=int(info.neval),
                       source_s_partitions=len(splits)+1, adaptive_max_error_estimate_V_m=float(coupling*error),
                       independent_charge_quadrature_C=float(integrated_charge),
                       charge_relative_error=float(integrated_charge/charge-1),
                       elapsed_seconds=time.monotonic()-started,
                       Cartesian_Ex_Ey_Ez_V_m=cartesian.tolist())
