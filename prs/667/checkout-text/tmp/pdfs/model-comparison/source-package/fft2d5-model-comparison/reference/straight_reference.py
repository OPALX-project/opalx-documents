"""Finite straight round-cylinder Coulomb reference in SI units.

The longitudinal Coulomb integrals are exact for piecewise-linear density.
Only the physical transverse disk is quadrature-integrated. Exact disk-axis
integration supplies an independent closed-form check, including end fields.
No SACR, tracking solver, mesh kernel, fitting, or softening is imported.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import epsilon_0


def segments(profile, half_length):
    if profile == 'uniform':
        return [(-half_length, half_length, 1., 0.)]
    if profile == 'triangle':
        return [(-half_length, 0., 1., 1/half_length),
                (0., half_length, 1., -1/half_length)]
    raise ValueError(profile)


def peak_density(radius, half_length, charge, profile):
    return charge/(np.pi*radius**2*half_length*(2 if profile == 'uniform' else 1))


def axis_field(radius, half_length, charge, s, profile='uniform'):
    """Exact axis Ez for every s, from analytic integration of charged disks."""
    a = float(radius)
    s = np.asarray(s, dtype=float)
    def primitive0(t):
        # |t|-sqrt(t²+a²), evaluated without catastrophic cancellation.
        return -a*a/(np.hypot(t, a)+np.abs(t))
    def primitive1(t):
        return .5*a*a*(np.arcsinh(t/a)-t/(np.hypot(t, a)+np.abs(t)))
    value = np.zeros_like(s)
    for lo, hi, intercept, slope in segments(profile, half_length):
        low, high = s-hi, s-lo
        value += ((intercept+slope*s)*(primitive0(high)-primitive0(low))
                  -slope*(primitive1(high)-primitive1(low)))
    return peak_density(radius, half_length, charge, profile)/(2*epsilon_0)*value


def axis_potential(radius, half_length, charge, s, profile='uniform'):
    """Exact axis potential with zero at infinity, independent of field primitive."""
    a = float(radius)
    s = np.asarray(s, dtype=float)
    def primitive0(t):
        return .5*a*a*(t/(np.hypot(t, a)+np.abs(t))+np.arcsinh(t/a))
    def primitive1(t):
        d = np.hypot(t, a)
        ab = np.abs(t)
        return a*a*(d*d+d*ab+ab*ab)/(3*(d+ab))
    value = np.zeros_like(s)
    for lo, hi, intercept, slope in segments(profile, half_length):
        low, high = s-hi, s-lo
        value += ((intercept+slope*s)*(primitive0(high)-primitive0(low))
                  -slope*(primitive1(high)-primitive1(low)))
    return peak_density(radius, half_length, charge, profile)/(2*epsilon_0)*value


def transverse_rule(radius, x, y, nphi, nrad):
    """Target-centred rays through the exact physical disk, with r=rmax*t^4."""
    if x*x+y*y >= radius*radius:
        raise ValueError('This quadrature requires a target strictly inside the transverse disk.')
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    cp, sp = np.cos(phi), np.sin(phi)
    b = x*cp+y*sp
    rmax = -b+np.sqrt(b*b+radius*radius-x*x-y*y)
    nodes, weights = leggauss(nrad)
    t, dt = (nodes[:, None]+1)/2, weights[:, None]/2
    rr = rmax*t**4
    dr_dphi = dt*(4*rmax*t**3)*(2*np.pi/nphi)
    return rr, dr_dphi, cp, sp


def field(radius, half_length, charge, target, profile='uniform', nphi=512, nrad=48,
          return_potential=False):
    """Original finite-volume Coulomb field; longitudinal integrals exact."""
    x, y, s = np.asarray(target, dtype=float)
    q, dr, cp, sp = transverse_rule(radius, x, y, nphi, nrad)
    transverse_q2 = np.zeros_like(q)
    longitudinal = np.zeros_like(q)
    potential = np.zeros_like(q)
    for lo, hi, intercept, slope in segments(profile, half_length):
        tlow, thigh = s-hi, s-lo
        dlow, dhigh = np.hypot(q, tlow), np.hypot(q, thigh)
        c0 = intercept+slope*s
        # q² * integral w(s')/[q²+(s-s')²]^(3/2) ds'.
        transverse_q2 += c0*(thigh/dhigh-tlow/dlow)+slope*q*q*(1/dhigh-1/dlow)
        # integral w(s')*(s-s')/[q²+(s-s')²]^(3/2) ds'.
        longitudinal += c0*(1/dlow-1/dhigh)-slope*(
            np.arcsinh(thigh/q)-thigh/dhigh-np.arcsinh(tlow/q)+tlow/dlow)
        potential += c0*(np.arcsinh(thigh/q)-np.arcsinh(tlow/q))-slope*(dhigh-dlow)
    coupling = peak_density(radius, half_length, charge, profile)/(4*np.pi*epsilon_0)
    result = coupling*np.array([-np.sum(cp*transverse_q2*dr),
                                -np.sum(sp*transverse_q2*dr),
                                np.sum(longitudinal*q*dr)])
    if return_potential:
        return result, float(coupling*np.sum(potential*q*dr))
    return result
