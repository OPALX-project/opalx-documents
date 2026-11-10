#!/Users/adelmann/.venv-h6/bin/python
"""Independent source-volume quadrature: exact circular Coulomb vs thin expansion.

This does not call SACR or the production FFT. It isolates curvature truncation
from mesh/deposition/gradient errors. Source physical density is uniform in each
elliptical cross-section; the Frenet Jacobian is included in its charge measure.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
P = argparse.ArgumentParser()
P.add_argument('--order', type=int, default=40)
P.add_argument('--radius', type=float, default=2.)
ARGS = P.parse_args()
R = ARGS.radius
kappa = 1/R
a,b,L,Q = .005,.0005,5.,1.e-11
kc = 8.9875517923e9
n = ARGS.order
nodes,w = leggauss(n)
rr = (1+nodes)/2
wr = w/2 * rr
phi = 2*np.pi * (np.arange(4*n)+.5)/(4*n)
up = a*rr[:,None]*np.cos(phi[None,:])
vp = b*rr[:,None]*np.sin(phi[None,:])
wxy = np.broadcast_to(wr[:,None]*(2*np.pi/(4*n))*a*b, up.shape)
rho0 = Q/(np.pi*a*b*L)

def tau_nodes(target_s):
    lo,hi=target_s-L/2,target_s+L/2
    # Resolve the local thin radius and possible beam end without a singular
    # grid point. Quadrature has an independent radial and angular refinement.
    steps=np.geomspace(1.e-7,8.,100)
    breaks=np.unique(np.r_[lo,hi,0.,target_s,-steps,steps])
    breaks=breaks[(breaks>=lo)&(breaks<=hi)]
    q,wq=leggauss(max(12,n//2))
    mids=(breaks[1:]+breaks[:-1])/2
    half=(breaks[1:]-breaks[:-1])/2
    return (mids[:,None]+half[:,None]*q).ravel(),(half[:,None]*wq).ravel()

def solve(u,v,s,profile):
    taus,wt = tau_nodes(s)
    exact=np.zeros(3)
    expanded=np.zeros(3)
    x=u-up
    y=v-vp
    sumu=u+up
    for tau,weight in zip(taus,wt):
        xi=2*np.sin(kappa*tau/2)/kappa
        xip=np.cos(kappa*tau/2)
        d2=x*x+y*y+xi*xi
        full=d2+kappa*sumu*xi*xi+kappa*kappa*u*up*xi*xi
        factor = 1. if profile=='uniform' else 2*(1-2*abs(s-tau)/L)
        mass=wxy * (1+kappa*up)*rho0*weight*factor
        full3=full**-1.5
        field_exact=np.stack([
            (x + .5*kappa*xi*xi*(1+kappa*up))*full3,
            y*full3,
            (1+kappa*up)*xi*xip*full3])
        d3=d2**-1.5
        d5=d3/d2
        field_expanded=np.stack([
            x*d3+.5*kappa*xi*xi*(d3-3*x*sumu*d5),
            y*d3-1.5*kappa*xi*xi*y*sumu*d5,
            (xi*xip*d3+.5*kappa*sumu*xi*xip*(2*d3-3*xi*xi*d5))/(1+kappa*u)])
        exact += np.sum(field_exact*mass,axis=(1,2))*kc
        expanded += np.sum(field_expanded*mass,axis=(1,2))*kc
    return exact,expanded

records=[]
for profile in ['uniform','triangular']:
    for label,u,v,s in [('centre',0.,0.,0.),('radial',a/2,0.,0.),
                        ('vertical',0.,b/2,0.),('end',0.,0.,L/2-a),
                        ('off-axis-end',a/2,b/2,L/2-a)]:
        exact,expanded=solve(u,v,s,profile)
        for d in range(3):
            records.append(dict(profile=profile,probe=label,component=['u','y','s'][d],
                                exact=exact[d],expanded=expanded[d],
                                absolute_error=expanded[d]-exact[d],
                                relative_error=((expanded[d]-exact[d])/exact[d]
                                                if abs(exact[d])>1e-6 else np.nan)))
df=pd.DataFrame(records)
dest=HERE/f'curvature_expansion_R{R:g}_order{n}.csv'
df.to_csv(dest,index=False)
print(df.to_string(index=False,float_format=lambda v:f'{v:.12g}'))
metadata=dict(radius=R,radial_semiaxis=a,vertical_semiaxis=b,length=L,charge=Q,
              radial_order=n,angular_order=4*n,longitudinal_order=max(12,n//2),
              quadrature='independent volume Gauss integration, logarithmic longitudinal panels',
              maximum_relative_error=float(df.relative_error.abs().max()))
dest.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
