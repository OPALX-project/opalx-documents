"""Check error of the independent C++ test's Gauss-law potential quadrature."""
from pathlib import Path
import json
import numpy as np

EPS=8.8541878128e-12
A=.25

def simpson(lo,hi,f):
    if lo==hi:return 0.
    n=1024;x=np.linspace(lo,hi,n+1);w=np.full(n+1,2.);w[1:-1:2]=4;w[[0,-1]]=1
    return (hi-lo)/n/3*np.dot(w,f(x))

def potential(r,b):
    inside=lambda x:x/(2*np.pi*EPS*A*A)
    outside=lambda x:1/(2*np.pi*EPS*x)
    return ((simpson(r,A,inside)+simpson(A,b,outside)) if r<A else simpson(r,b,outside))

def main():
    rows=[]
    for b in (1.,1.5):
        for r in (0.,A/2,A,(A+b)/2,b):
            physical=(1+2*np.log(b/A)-(r/A)**2)/(4*np.pi*EPS) if r<=A else np.log(b/r)/(2*np.pi*EPS)
            numerical=potential(r,b)
            err=0. if physical==0 else (numerical/physical-1)
            for z in (1.35,4.65):
                for ps in (0.,.4,1.,-.4):
                    lam=lambda zz:1e-9*(1-abs(zz-3)/3)
                    finite=-(lam(z+.01)*numerical-lam(z-.01)*numerical)/(.02*(1+ps*ps))
                    exact=(1 if z>3 else -1)*1e-9/3*physical/(1+ps*ps)
                    rows.append(dict(b=b,r=r,z=z,ps=ps,potential_relative_error=err,
                                     field_relative_error=0 if exact==0 else finite/exact-1))
    result=dict(panels_per_interval=1024,tests=len(rows),
                max_relative_potential_error=max(abs(x['potential_relative_error']) for x in rows),
                max_relative_field_error=max(abs(x['field_relative_error']) for x in rows),
                unit_relative_tolerance=2e-8,
                tolerance_reason='Independent radial quadrature plus finite-s differentiation; tolerance safely exceeds the measured quadrature error and floating-point cancellation.')
    assert result['max_relative_field_error']<1e-9
    (Path(__file__).parent/'unit-reference-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
