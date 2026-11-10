"""Independent SACR for a triangular physical longitudinal density.

Returns E/(k rho_peak), in metres. Uses the exact weighted-boundary identity,
not a particle or longitudinal/transverse mesh solver. The density is uniform
over physical elliptical cross sections, w(s)=1-|s|/h.
"""
from functools import lru_cache
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad_vec
from scipy.special import ellipkinc, ellipeinc
from uniform_reference import validate, transverse_scale, _distance


@lru_cache(maxsize=32)
def angular_rule(nphi):
    phi=2*np.pi*(np.arange(nphi)+.5)/nphi
    return np.cos(phi),np.sin(phi)


def cross_rule(a,c,target,nphi=256,nrad=32,power=4):
    """Exact elliptical domain, rays originating at the target (u,y).

    r=rmax*t**power resolves the logarithm at r=0 without a cutoff.
    Weights integrate physical du dy, with no curved-volume Jacobian.
    """
    ut,yt,_=target
    cp,sp=angular_rule(nphi)
    aa=(cp/a)**2+(sp/c)**2
    bb=ut*cp/a**2+yt*sp/c**2
    cc=(ut/a)**2+(yt/c)**2-1
    root=np.sqrt(bb*bb-aa*cc)
    rmax=np.where(bb>0,-cc/(bb+root),(-bb+root)/aa)
    q,w=leggauss(nrad)
    t=(q[:,None]+1)/2
    r=rmax[None,:]*t**power
    weights=(w[:,None]/2)*(power*rmax[None,:]**2*t**(2*power-1))*(2*np.pi/nphi)
    return ut+r*cp,yt+r*sp,weights,r


def primitives(s,st,r,source_u,target_u,radius):
    """Primitives of 1/D and cos((s-st)/R)/D with respect to s."""
    if math.isinf(radius):
        pp=np.arcsinh((s-st)/r)
        return pp,pp
    aa=(radius+target_u)*(radius+source_u)
    mm=-4*aa/r**2
    tt=(s-st)/(2*radius)
    ff=ellipkinc(tt,mm)
    ee=ellipeinc(tt,mm)
    factor=2*radius/r
    return factor*ff,factor*((1-2/mm)*ff+(2/mm)*ee)


def triangle_field(a,c,h,target,radius=math.inf,nphi=512,nrad=32,
                   quadrature_tol=2e-11,return_info=False):
    target=np.asarray(target,dtype=float)
    validate(a,c,h,target,radius)
    ut,yt,st=target
    cp,sp=angular_rule(nphi)
    uu,yy=a*cp,c*sp
    jac=1. if math.isinf(radius) else 1+uu/radius
    ar,ay=c*cp*jac,a*sp*jac
    scale=transverse_scale(a,c)
    def side_integrand(s):
        dist,delta=_distance(a,c,target,radius,uu,yy,s)
        weight=1-abs(s)/h
        return (weight*np.array([ar*np.cos(delta),ay,ar*np.sin(delta)])/dist/scale).ravel()
    side_value,error,info=quad_vec(side_integrand,-h,h,points=sorted(set([0.,st])),
                                 epsabs=quadrature_tol,epsrel=quadrature_tol,
                                 limit=1000,full_output=True)
    if not info.success:
        raise RuntimeError(f"Triangle side quadrature failed: {info.message}")
    side=side_value.reshape(3,nphi).sum(axis=1)*(2*np.pi/nphi)*scale
    uu,yy,weights,rr=cross_rule(a,c,target,nphi,nrad)
    pm,cm=primitives(-h,st,rr,uu,ut,radius)
    p0,c0=primitives(0.,st,rr,uu,ut,radius)
    pp,cc=primitives(h,st,rr,uu,ut,radius)
    if math.isinf(radius):
        radial=np.zeros_like(rr)
        ratio=1.
    else:
        aa=(radius+ut)*(radius+uu)
        dm,_=_distance(a,c,target,radius,uu,yy,-h)
        d0,_=_distance(a,c,target,radius,uu,yy,0.)
        dp,_=_distance(a,c,target,radius,uu,yy,h)
        radial=radius/(h*aa)*(2*d0-dm-dp)
        ratio=(radius+uu)/(radius+ut)
    gradient=np.array([np.sum(weights*radial),0.,-np.sum(weights*(2*c0-cm-cc)/h)])
    filament_s=-np.sum(weights*ratio*(2*p0-pm-pp)/h)
    total=side+gradient
    if return_info:
        return total,dict(side=side,gradient=gradient,filament_s=float(filament_s),
                          side_neval=int(info.neval),
                          side_quad_error_normalized=float(2*np.pi*error/np.sqrt(nphi)))
    return total


def direct_volume_field(a,c,h,target,radius=math.inf,nphi=256,nrad=48,
                        quadrature_tol=1e-8):
    """Independent original 3-D Coulomb integral (no boundary identity).

    Target-centred rays, linear radial map, and adaptive source-s integration
    resolve the integrable singularity. Intended for selected validation points.
    """
    target=np.asarray(target,dtype=float)
    validate(a,c,h,target,radius)
    ut,yt,st=target
    uu,yy,weights,rr=cross_rule(a,c,target,nphi,nrad,power=1)
    scale=transverse_scale(a,c)
    jac=1. if math.isinf(radius) else 1+uu/radius
    def integrand(s):
        dist,delta=_distance(a,c,target,radius,uu,yy,s)
        if math.isinf(radius):
            dr=ut-uu
            ds=st-s+np.zeros_like(uu)
        else:
            dr=ut-uu+2*(radius+uu)*np.sin(delta/2)**2
            ds=-(radius+uu)*np.sin(delta)
        dy=yt-yy
        return (np.array([dr,dy,ds])*(weights*jac*(1-abs(s)/h)/dist**3)/scale).ravel()
    value,error,info=quad_vec(integrand,-h,h,points=sorted(set([0.,st])),
                             epsabs=quadrature_tol,epsrel=quadrature_tol,
                             limit=1200,full_output=True)
    if not info.success:
        raise RuntimeError(f"Direct volume quadrature failed: {info.message}")
    return value.reshape(3,*uu.shape).sum(axis=(1,2))*scale,dict(neval=int(info.neval),
                                            error_scaled=float(error))
