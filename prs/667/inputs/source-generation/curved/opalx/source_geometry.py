"""Pinned physical curved round-disk source: exact Jacobian and D4 phases."""
import numpy as np
R,A,C,L,BETA=2.,.02,.02,5.,.001

def cross_section(nrad, nphi):
    radius = A
    """Exact round disk equal-area radial rule and D4 reflection/rotation octets."""
    assert nrad > 0 and nphi > 0 and nphi % 8 == 0
    r = np.sqrt((np.arange(nrad)+.5)/nrad)
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    rr, pp = np.meshgrid(r, phi, indexing='ij')
    rr, base = rr.ravel(), pp.ravel()
    phi = base.copy()
    for _ in range(8):
        phi -= (phi+A*rr/R*np.sin(phi)-base)/(1+A*rr/R*np.cos(phi))
    xy = np.column_stack([A*rr*np.cos(phi), C*rr*np.sin(phi)])
    groups = np.empty(nphi, dtype=int)
    for j in range(nphi//8):
        groups[[j, nphi//4-1-j, nphi//4+j, nphi//2-1-j,
                nphi//2+j, 3*nphi//4-1-j, 3*nphi//4+j, nphi-1-j]] = j
    index = np.repeat(np.arange(nrad), nphi)*(nphi//8)+np.tile(groups, nrad)
    count = nrad*nphi//8
    order = np.argsort(np.mod(np.arange(count)*((np.sqrt(5)-1)/2), 1.))
    ranks = np.empty(count, dtype=int)
    ranks[order] = np.arange(count)
    phase = (ranks[index]+.5)/count
    assert np.allclose(xy.mean(axis=0), [A*A/(4*R), 0.], atol=A*1e-13, rtol=0)
    assert np.allclose(np.mean(xy**2, axis=0), [A*A/4, C*C/4], rtol=2e-13, atol=0)
    return xy, phase


def longitudinal_positions(profile,ns,phase,start,stop,stagger=True):
    q=(np.arange(start,stop)[:,None]+phase)/(ns//2)
    if profile=='uniform': return L/2*q
    return L/2*(-np.expm1(.5*np.log1p(-q)))


def global_values(local):
    u,y,s=np.asarray(local).T
    theta=s/R
    co,si=np.cos(theta),np.sin(theta)
    position=np.c_[u*co-2*R*np.sin(theta/2)**2,y,(R+u)*si]
    bg=BETA/np.sqrt(1-BETA**2)
    momentum=bg*np.c_[-si,np.zeros_like(si),co]
    return np.column_stack([position[:,0],momentum[:,0],position[:,1],momentum[:,1],position[:,2],momentum[:,2]])
