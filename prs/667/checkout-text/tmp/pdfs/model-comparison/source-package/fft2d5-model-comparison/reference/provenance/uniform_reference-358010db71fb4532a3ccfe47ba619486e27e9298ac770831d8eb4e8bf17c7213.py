"""SACR field of a uniform physical-density finite curved elliptical tube.

All field values are E/(k*rho), k=1/(4*pi*epsilon0), in metres. Coordinates
and returned components are (outward radial u, vertical y, arclength s).
No particle, mesh, OPALX field, fitted coefficient or softening enters.
"""
from functools import lru_cache
import math

import numpy as np
from scipy.integrate import quad_vec
from numpy.polynomial.legendre import leggauss


def position(s, u, y, radius):
    if math.isinf(radius):
        return np.array([u, y, s])
    theta = s/radius
    return np.array([u*np.cos(theta)-2*radius*np.sin(theta/2)**2,
                     y, (radius+u)*np.sin(theta)])


def basis(s, radius):
    theta = 0. if math.isinf(radius) else s/radius
    co, si = np.cos(theta), np.sin(theta)
    return np.array([[co,0.,-si],[0.,1.,0.],[si,0.,co]])


def transverse_scale(a, c):
    """Infinite straight ellipse's radial/vertical boundary field / (k*rho)."""
    return 4*np.pi*a*c/(a+c)


@lru_cache(maxsize=32)
def disk_rule(nphi, nrad):
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    gx, gw = leggauss(nrad)
    rr, wr = (gx+1)/2, gw/2
    return rr[:,None]*np.cos(phi), rr[:,None]*np.sin(phi), \
        wr[:,None]*rr[:,None]*(2*np.pi/nphi)


def validate(a, c, b, target, radius):
    if min(a,c,b)<=0:
        raise ValueError("All semiaxes and half length must be positive")
    ut,yt,st = target
    if (ut/a)**2+(yt/c)**2>=1 or abs(st)>=b:
        raise ValueError("Target must be strictly inside the untapered tube")
    if not math.isinf(radius) and (radius<=a or b/radius>=np.pi):
        raise ValueError("Curved source must not meet the bend axis or wrap")


def _distance(a,c,target,radius,u,y,s):
    ut,yt,st = target
    if math.isinf(radius):
        delta = 0.
        distance = np.sqrt((ut-u)**2+(yt-y)**2+(s-st)**2)
    else:
        delta = (s-st)/radius
        distance = np.sqrt((ut-u)**2+(yt-y)**2+
                           4*(radius+ut)*(radius+u)*np.sin(delta/2)**2)
    return distance,delta


def field(a,c,b,target,radius=math.inf,nphi=256,nrad=32,
          quadrature_tol=2e-11,return_info=False):
    """Exact Coulomb boundary identity integrated over side and both caps.

    X(s,u,y)=((R+u)cos(s/R)-R,y,(R+u)sin(s/R)). The volume Jacobian
    is J=1+u/R. On the side, vector area is
        J*(c*cos(phi)*e_r + a*sin(phi)*e_y) ds dphi.
    The planar elliptical end caps carry vector area +/-e_s du dy.
    Physical density is uniform, with Q=rho*pi*a*c*(2*b): the odd
    Jacobian term integrates to zero over every centred section.
    """
    target = np.asarray(target,dtype=float)
    validate(a,c,b,target,radius)
    ut,yt,st = target
    phi=2*np.pi*(np.arange(nphi)+.5)/nphi
    co,si=np.cos(phi),np.sin(phi)
    u,y=a*co,c*si
    jac=1. if math.isinf(radius) else 1+u/radius
    ar,ay=c*co*jac,a*si*jac
    scale=transverse_scale(a,c)
    def side_integrand(s):
        dist,delta=_distance(a,c,target,radius,u,y,s)
        return (np.array([ar*np.cos(delta),ay,ar*np.sin(delta)])/dist/scale).ravel()
    # The side kernel is narrowly peaked near st for this very long beam.
    # Adaptive subdivision resolves it without longitudinal mesh assumptions.
    result,error,info=quad_vec(side_integrand,-b,b,points=[st],
                               epsabs=quadrature_tol,epsrel=quadrature_tol,
                               limit=1000,full_output=True)
    if not info.success:
        raise RuntimeError(f"SACR side quadrature failed: {info.message}")
    side=result.reshape(3,nphi).sum(axis=1)*(2*np.pi/nphi)*scale
    uu,yy,weights=disk_rule(nphi,nrad)
    uu,yy=a*uu,c*yy
    caps=np.zeros(3)
    for sign in (-1,1):
        dist,delta=_distance(a,c,target,radius,uu,yy,sign*b)
        integ=np.sum(a*c*weights/dist)
        caps += sign*np.array([-np.sin(delta),0.,np.cos(delta)])*integ
    total=side+caps
    if return_info:
        return total,dict(side=side,caps=caps,side_neval=int(info.neval),
                          side_quad_error_normalized=float(2*np.pi*error/np.sqrt(nphi)))
    return total


def tangent_endpoint(a,c,b,target,radius=math.inf,nphi=256,nrad=32):
    """Independent exact integration along every longitudinal charge filament.

    F_s = int_A (R+u_source)/(R+u_target) * (1/d_plus-1/d_minus) du dy.
    The distances refer to source points on the two common end planes.
    """
    target=np.asarray(target,dtype=float)
    validate(a,c,b,target,radius)
    uu,yy,weights=disk_rule(nphi,nrad)
    uu,yy=a*uu,c*yy
    dp,_=_distance(a,c,target,radius,uu,yy,b)
    dm,_=_distance(a,c,target,radius,uu,yy,-b)
    ratio=1. if math.isinf(radius) else (radius+uu)/(radius+target[0])
    return float(np.sum(a*c*weights*ratio*(1/dp-1/dm)))

