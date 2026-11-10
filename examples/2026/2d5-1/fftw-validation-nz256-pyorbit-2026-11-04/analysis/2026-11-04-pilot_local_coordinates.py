"""Independent exact hard-edge design geometry, for output diagnostics only."""
from pathlib import Path
import json,numpy as np
M=json.loads(Path('/Users/adelmann/git/dba-lattice/model/machine.json').read_text())
def local(r,p):
 n=len(r);best=np.full(n,np.inf);out=np.empty((n,6))
 for el in M['elements']:
  X,Z,t0=el['entry_X_Z_theta'];L=el['length_m'];h=el['h_per_m'];dx=r[:,0]-X;dz=r[:,2]-Z
  if h:
   cx=X-np.cos(t0)/h;cz=Z+np.sin(t0)/h;theta=np.arctan2(-(r[:,2]-cz),r[:,0]-cx);delta=np.arctan2(np.sin(t0-theta),np.cos(t0-theta));u=np.clip(delta/h,0,L);t=t0-h*u;xx=cx+np.cos(t)/h;zz=cz-np.sin(t)/h
  else:u=np.clip(dx*np.sin(t0)+dz*np.cos(t0),0,L);t=np.full(n,t0);xx=X+u*np.sin(t0);zz=Z+u*np.cos(t0)
  dist=(r[:,0]-xx)**2+(r[:,2]-zz)**2;use=dist<best;best[use]=dist[use]
  values=np.c_[(r[:,0]-xx)*np.cos(t)-(r[:,2]-zz)*np.sin(t),p[:,0]*np.cos(t)-p[:,2]*np.sin(t),r[:,1],p[:,1],el['s_start_m']+u,p[:,0]*np.sin(t)+p[:,2]*np.cos(t)]
  out[use]=values[use]
 return out

def moments(v):
 result={}
 for j,axis in [(0,'x'),(2,'y')]:
  x=v[:,j]-v[:,j].mean();p=v[:,j+1]-v[:,j+1].mean();variance=np.mean(x*x);res=p-np.mean(x*p)/variance*x
  result['sigma_'+axis+'_m']=float(np.sqrt(variance));result['emit_n_'+axis+'_m']=float(np.sqrt(variance*np.mean(res*res)))
 return result
