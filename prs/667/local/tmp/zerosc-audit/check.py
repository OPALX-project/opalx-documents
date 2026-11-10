from pathlib import Path
import numpy as np
import pandas as pd
root=Path('/Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper/tracking')
src=np.load(root/'sources/bend-uniform-n1048576.npz');print('source',src.files)
a=src['material_m'][:,0];R=2.;p0=.001/np.sqrt(1-.001**2);phi=5.
def em(u,p):
 u=u-u.mean();p=p-p.mean();return np.sqrt(max(0,np.mean(u*u)*np.mean(p*p)-np.mean(u*p)**2))*1e6
r=np.sqrt(R*R+2*R*a*np.cos(phi)+a*a)
ut=(2*R*a*np.cos(phi)+a*a)/(r+R);pt=-p0*a*np.sin(phi)/r
rs=a*np.cos(phi)+np.sqrt(R*R-a*a*np.sin(phi)**2);us=rs-R;ps=-p0*a*np.sin(phi)/R
print('exact time',em(ut,pt),'exact station',em(us,ps))
f=np.load(root/'bend-10m-100steps/pyorbit/runs/bend-ZeroSC-10m-100steps/final-particles.npz');st=f['native_state'];print('native',em(st[:,0],st[:,1]*p0));print('station errors',np.max(abs(st[:,0]-us)),np.max(abs(st[:,1]*p0-ps)))
# Transform each station-crossing state to common elapsed time using its arrival-time displacement z=-beta*c*delta_t.
# Positive native z denotes early arrival, so propagate forward z/(beta*c), gyro-angle z/R.
z=st[:,4]-src['material_m'][:,2]
# local crossing radial coordinates and momenta embedded with arbitrary initial azimuth zero.
x=R+st[:,0];qr=st[:,1]*p0;qt=np.sqrt(p0*p0-qr*qr)
for sign in [-1,1]:
 d=sign*z/R
 # displacement in local radial/tangent basis under uniform rotation: dr=(qr*sin(d)+qt*(cos(d)-1))*R/p0
 xx=x+R/p0*(qr*np.sin(d)+qt*(np.cos(d)-1));zz=R/p0*(qr*(1-np.cos(d))+qt*np.sin(d))
 rr=np.hypot(xx,zz);u=rr-R
 pr=qr*np.cos(d)-qt*np.sin(d);pz=qr*np.sin(d)+qt*np.cos(d)
 radial=(pr*xx+pz*zz)/rr
 print('time transform sign',sign,'emit',em(u,radial),'errors',np.max(abs(u-ut)),np.max(abs(radial-pt)))
