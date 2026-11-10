"""Isolate cross-section sampling error using CIC and a 2D free-space convolution.

This is an independent Python reconstruction for a source-resolution control,
not an additional OPALX run or a curved-field oracle. The native OPALX mesh
scan remains the solver comparison. The Green function is the cell-averaged
logarithmic kernel used by FFT2D5, then centred differences and CIC gather.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.constants import epsilon_0
from numpy.polynomial.legendre import leggauss

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
A=.005;C=.0005;R=2.;BOX=(.016,.004);NX=512;NY=256
SCALE=4*np.pi*A*C/(A+C)

def cross_grid(n):
    u=-BOX[0]/2+(np.arange(n)+.5)*BOX[0]/n
    y=-BOX[1]/2+(np.arange(n)+.5)*BOX[1]/n
    u,y=np.meshgrid(u,y,indexing='ij');mask=(u/A)**2+(y/C)**2<1
    u=u[mask];y=y[mask];w2=A*A*(1-(y/C)**2)
    u=(2*R*u+w2)/(np.sqrt(R*R+2*R*u+w2)+R)
    return np.c_[u,y]

def kernel():
    dx,dy=BOX[0]/NX,BOX[1]/NY
    i=np.minimum(np.arange(2*NX),2*NX-np.arange(2*NX))
    j=np.minimum(np.arange(2*NY),2*NY-np.arange(2*NY))
    x,y=np.meshgrid(i*dx,j*dy,indexing='ij')
    scale=max(dx,dy);u=x/scale;v=y/scale;a=dx/(2*scale);b=dy/(2*scale)
    def primitive(x,y):
        aa=abs(x);bb=abs(y);nonzero=(aa>0)&(bb>0)
        result=np.zeros_like(x)
        av=aa[nonzero];bv=bb[nonzero]
        value=.5*av*bv*np.log(av*av+bv*bv)-1.5*av*bv+.5*av*av*np.arctan2(bv,av)+.5*bv*bv*np.arctan2(av,bv)
        result[nonzero]=np.sign(x[nonzero]*y[nonzero])*value
        return result
    average=(primitive(u+a,v+b)-primitive(u-a,v+b)-primitive(u+a,v-b)+primitive(u-a,v-b))/(4*a*b)
    far=np.maximum(u,v)>4
    nodes,weights=leggauss(4);values=np.zeros(np.count_nonzero(far))
    for ni,wi in zip(nodes,weights):
        for nj,wj in zip(nodes,weights):
            values+=wi*wj*np.log((u[far]+a*ni)**2+(v[far]+b*nj)**2)/8
    average[far]=values
    return -(np.log(scale)+average)/(2*np.pi)

def cic(points):
    spacing=np.array(BOX)/[NX,NY]
    cell=(points+np.array(BOX)/2)/spacing-.5
    left=np.floor(cell).astype(int);fraction=cell-left
    return left,fraction

def solve(cross,green):
    dx,dy=BOX[0]/NX,BOX[1]/NY
    rho=np.zeros((2*NX,2*NY));left,frac=cic(cross)
    weight=np.pi*A*C/len(cross)/(dx*dy)
    for i in range(2):
        for j in range(2):
            np.add.at(rho,(left[:,0]+i,left[:,1]+j),weight*(frac[:,0] if i else 1-frac[:,0])*(frac[:,1] if j else 1-frac[:,1]))
    phi=np.fft.ifft2(np.fft.fft2(rho)*green).real*dx*dy
    return np.stack([-(np.roll(phi,-1,axis=axis)-np.roll(phi,1,axis=axis))/(2*d) for axis,d in enumerate((dx,dy))],axis=-1)*4*np.pi

def gather(field,points):
    left,frac=cic(points);result=np.zeros((len(points),2))
    for i in range(2):
        for j in range(2):
            result+=field[left[:,0]+i,left[:,1]+j]*(frac[:,0] if i else 1-frac[:,0])[:,None]*(frac[:,1] if j else 1-frac[:,1])[:,None]
    return result

def main():
    green=np.fft.fft2(kernel());targets=pd.read_csv(STUDY/'reference/points.csv',float_precision='round_trip')
    unique=targets[['u_m','y_m']].drop_duplicates().reset_index(drop=True)
    rows=[];summary=[];previous=None
    for n in (512,1024,2048):
        cross=cross_grid(n);values=gather(solve(cross,green),unique.to_numpy())
        for i,p in unique.iterrows():
            for d,key in enumerate(('radial','vertical')):
                rows.append(dict(cross_grid=n,ncross=len(cross),point=i,u_m=p.u_m,y_m=p.y_m,direction=key,F=values[i,d],normalized_F=values[i,d]/SCALE))
        if previous is not None:
            change=np.max(abs(values-previous),axis=0)/SCALE
            summary.append(dict(cross_grid=n,ncross=len(cross),radial_max_change=float(change[0]),vertical_max_change=float(change[1])))
        previous=values
    frame=pd.DataFrame(rows);frame.to_csv(ROOT/'fields.csv',index=False,float_format='%.17g')
    pd.DataFrame(summary).to_csv(ROOT/'quadrature_changes.csv',index=False,float_format='%.17g')
    rho=1e-11/(np.pi*A*C*5)
    centre=frame[(frame.cross_grid==2048)&(frame.u_m==0)&(frame.y_m==0)&(frame.direction=='radial')].iloc[0]
    result=dict(scope=__doc__,mesh=[NX,NY],source_grid_levels=[512,1024,2048],
                component_scale_F_m=SCALE,changes=summary,
                reconstructed_flat_slice_center_Er_10pC_Vpm=float(centre.F*rho/(4*np.pi*epsilon_0)),
                analytic_flat_slice_center_Er_10pC_Vpm=float(-rho*A*A*C/(2*epsilon_0*R*(A+C))),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
