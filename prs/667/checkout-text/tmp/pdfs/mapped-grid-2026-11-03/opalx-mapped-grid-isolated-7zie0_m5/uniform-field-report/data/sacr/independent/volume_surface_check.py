"""Independent uniform-volume Coulomb check at the bend centre (no singularity).

The source-angle integral is analytic at this exterior observation point.
Compare it with a separately parameterized boundary integral. No prototype
field routine or Dubin coefficient is used by this check.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss

ROOT = Path(__file__).resolve().parent


def source_volume_integral(a,b,c,R,n):
    q, weights = leggauss(n)
    w = (q[:,None]+1)/2
    weights = weights[:,None]/2
    phi = 2*np.pi*(np.arange(4*n)[None,:]+.5)/(4*n)
    r = np.sqrt(1-w*w)
    u,y = a*r*np.cos(phi), c*r*np.sin(phi)
    rs = R+u
    value = -2*a*c*w*rs**2/(rs**2+y**2)**1.5*np.sin(b*w/R)
    return np.array([float(np.sum(value*weights)*2*np.pi/(4*n)),0.,0.])


def boundary_integral(a,b,c,R,n):
    mu, weights = leggauss(n)
    mu, weights = mu[:,None], weights[:,None]
    phi = 2*np.pi*(np.arange(4*n)[None,:]+.5)/(4*n)
    w = np.sqrt(1-mu*mu)
    u,y = a*w*np.cos(phi), c*w*np.sin(phi)
    theta = b*mu/R
    jac = 1+u/R
    radial_area = b*c*jac*w*np.cos(phi)
    vertical_area = a*b*jac*w*np.sin(phi)
    tangential_area = a*c*mu+np.zeros_like(phi)
    distance = np.sqrt((R+u)**2+y**2)
    nx = radial_area*np.cos(theta)-tangential_area*np.sin(theta)
    nz = radial_area*np.sin(theta)+tangential_area*np.cos(theta)
    return np.array([np.sum(component/distance*weights)*2*np.pi/(4*n)
                     for component in [nx,vertical_area,nz]])


def main():
    a,b,c = .005,2.5,.0005
    rows=[]
    for R in [2.,20.]:
        for n in [32,64,128]:
            volume=source_volume_integral(a,b,c,R,n)
            surface=boundary_integral(a,b,c,R,n)
            rows.append(dict(radius_m=R,gauss_nodes=n,angular_nodes=4*n,
                             volume_x_m=float(volume[0]),surface_x_m=float(surface[0]),
                             surface_y_m=float(surface[1]),surface_z_m=float(surface[2]),
                             vector_relative_difference=float(np.linalg.norm(surface-volume)/np.linalg.norm(volume))))
    data=pd.DataFrame(rows)
    data.to_csv(ROOT/'volume_surface_check.csv',index=False)
    maximum=float(data.vector_relative_difference.max())
    result=dict(passed=maximum<1e-9,max_vector_relative_difference=maximum,
                observation='bend centre (-R,0,0), outside source',
                normalization='E/(k*rho), in metres',
                scope='independent analytic-angle volume integral vs boundary integral; not a prototype target call',
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'volume_surface_check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(data.to_string(index=False))
    print(json.dumps(result,indent=2))
    if not result['passed']:
        raise SystemExit(2)


if __name__=='__main__':
    main()
