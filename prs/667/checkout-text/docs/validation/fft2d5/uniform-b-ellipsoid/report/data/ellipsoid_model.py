"""Cold uniform-volume ellipsoid in uniform Bz: electrostatic, nonrelativistic.
Affine continuum r=C+A*u for uniform u in unit ball. Independent of OPALX.
Finite vertical thickness; Carlson integrals provide exact internal E coefficients.
See MODEL.md for assumptions and initial co-rotation.
"""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-2d5-matplotlib')
import numpy as np,pandas as pd
from scipy.integrate import solve_ivp,quad
from scipy.special import elliprd,elliprf
from scipy.constants import c,e,epsilon_0,proton_mass
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
J=np.array([[0.,1.,0.],[-1.,0.,0.],[0.,0.,0.]])
L=.05;AXES=np.array([.005,.05,.0005]);R=1.;SPEED=.01*c
OMEGA=SPEED/R;BZ=proton_mass*OMEGA/e
TAU=np.linspace(0,np.pi,1001)
A0=np.diag(AXES/L);V0=J@A0

def geometry(A):
 vals,rotation=np.linalg.eigh(A@A.T)
 if vals.min()<=0 or np.linalg.det(A)<=0:raise ValueError('Affine map lost positive volume')
 axes=np.sqrt(vals);volume=np.prod(axes)
 factors=np.array([volume/3*elliprd(vals[(i+1)%3],vals[(i+2)%3],vals[i]) for i in range(3)])
 return (rotation*factors)@rotation.T,vals,factors

def integrate(Q,rtol=2e-11):
 strength=3*e*Q/(4*np.pi*epsilon_0*proton_mass*OMEGA**2*L**3)
 def rhs(t,y):
  A=y[:9].reshape(3,3);V=y[9:].reshape(3,3)
  D,_,_=geometry(A)
  accel=J@V+strength/np.linalg.det(A)*D@A
  return np.r_[V.ravel(),accel.ravel()]
 sol=solve_ivp(rhs,[0,TAU[-1]],np.r_[A0.ravel(),V0.ravel()],t_eval=TAU,method='DOP853',rtol=rtol,atol=rtol*.01)
 assert sol.success,sol.message
 A=sol.y[:9].T.reshape(-1,3,3);V=sol.y[9:].T.reshape(-1,3,3)
 covariance=A@A.transpose(0,2,1)*L*L/5
 rows=[];energies=[];canonical=[];maxDsum=0
 for i,tau in enumerate(TAU):
  D,vals,factors=geometry(A[i]);maxDsum=max(maxDsum,abs(factors.sum()-1))
  radial=np.array([np.cos(tau),-np.sin(tau),0])
  tangent=np.array([-np.sin(tau),-np.cos(tau),0])
  rmsr=np.sqrt(radial@covariance[i]@radial)
  rmss=np.sqrt(tangent@covariance[i]@tangent)
  energy=np.sum(V[i]*V[i])+strength*2*elliprf(*vals)
  canonicalL=np.sum(A[i,0]*V[i,1]-A[i,1]*V[i,0])+.5*np.sum(A[i,:2]**2)
  energies.append(energy);canonical.append(canonicalL)
  rows.append(dict(charge_C=Q,t_s=tau/OMEGA,phase_rad=tau,x_centroid_m=R*np.cos(tau),
   y_centroid_m=-R*np.sin(tau),sigma_radial_m=rmsr,sigma_tangential_m=rmss,
   sigma_vertical_m=np.sqrt(covariance[i,2,2]),internal_energy_normalized=energy,
   canonical_Lz_normalized=canonicalL,det_A_m3=np.linalg.det(A[i])*L**3))
 frame=pd.DataFrame(rows)
 energy_error=float(np.max(np.abs(np.array(energies)/energies[0]-1)))
 angular_error=float(np.max(np.abs(np.array(canonical)/canonical[0]-1)))
 # Bound every particle's speed by centroid speed plus the largest singular value
 # of the affine velocity map over the unit ball.
 speed_bound=max(SPEED+OMEGA*L*np.linalg.svd(v,compute_uv=False)[0] for v in V)/c
 checks={'energy_max_relative_drift':energy_error,'canonical_Lz_max_relative_drift':angular_error,
  'max_sum_D_error':maxDsum,'upper_bound_particle_beta':float(speed_bound),'min_det_A_m3':float(frame.det_A_m3.min())}
 return frame,checks,A,V

def main():
 D,_,_=geometry(np.eye(3));assert np.max(abs(D-np.eye(3)/3))<1e-14
 # Independent oblate-spheroid closed form and direct integral checks.
 disk=np.diag([1.,1.,.01]);_,_,factors=geometry(disk)
 ecc=np.sqrt(1/.01**2-1);Dz=(1+ecc**2)/ecc**3*(ecc-np.arctan(ecc))
 # eigh orders the thin axis first.
 assert abs(factors[0]-Dz)<1e-13
 for i in range(3):
  vals=np.array([.1,1.,.01])**2;abc=np.sqrt(np.prod(vals))
  integral=abc/2*quad(lambda u:1/((vals[i]+u)*np.sqrt(np.prod(vals+u))),0,np.inf,epsabs=1e-9,epsrel=1e-10,limit=250)[0]
  expected=abc/3*elliprd(vals[(i+1)%3],vals[(i+2)%3],vals[i])
  assert abs(integral-expected)<1e-10
 allframes=[];checks={};zero=None
 for Q in [0.,1e-13,1e-12]:
  frame,check,A,V=integrate(Q);allframes.append(frame);checks[str(Q)]=check
  if Q==0:
   rotation=np.array([[[np.cos(t),np.sin(t),0],[-np.sin(t),np.cos(t),0],[0,0,1]] for t in TAU])
   exact=rotation@A0
   check['zero_charge_rigid_rotation_max_absolute_error_m']=float(np.max(abs(A-exact))*L)
   assert check['zero_charge_rigid_rotation_max_absolute_error_m']<1e-10
  assert check['energy_max_relative_drift']<1e-8
  assert check['canonical_Lz_max_relative_drift']<1e-8
  assert check['max_sum_D_error']<1e-12
 # Independent integration of centroid Lorentz ODE against closed circle.
 center=solve_ivp(lambda t,y:np.r_[y[2:],J[:2,:2]@y[2:]],[0,np.pi],[R,0,0,-R],t_eval=TAU,method='DOP853',rtol=2e-12,atol=1e-13)
 exact=np.array([R*np.cos(TAU),-R*np.sin(TAU)])
 centroid_error=float(np.max(abs(center.y[:2]-exact)))
 assert centroid_error<1e-10
 # Tighter integration checks final charged envelope without a fitted parameter.
 fine,_,_,_=integrate(1e-12,rtol=2e-12)
 cols=['sigma_radial_m','sigma_tangential_m','sigma_vertical_m']
 fine_error=float(np.max(abs(fine[cols].to_numpy()/allframes[-1][cols].to_numpy()-1)))
 assert fine_error<1e-8
 data=pd.concat(allframes,ignore_index=True);data.to_csv(ROOT/'ellipsoid_model.csv',index=False)
 parameters={'model':'nonrelativistic electrostatic affine cold uniform-volume ellipsoid',
  'particle':'proton','initial_semiaxes_m':AXES.tolist(),'orbit_radius_m':R,'centroid_beta':.01,
  'Bz_T':BZ,'omega_rad_per_s':OMEGA,'initial_velocity':'rigid co-rotation: Adot=Omega*J*A',
  'duration_s':float(np.pi/OMEGA),'checks':checks,'centroid_max_error_m':centroid_error,
  'tighter_integrator_max_relative_envelope_change':fine_error}
 (ROOT/'parameters_and_checks.json').write_text(json.dumps(parameters,indent=2)+'\n')
 plt.rcParams.update({'font.family':'serif','mathtext.fontset':'stix','font.size':11,'pdf.fonttype':42})
 fig,axs=plt.subplots(1,3,figsize=(11.5,3.9),layout='constrained')
 for frame,Q,col,ls in zip(allframes,[0.,.1,1.],['black','#0072B2','#E69F00'],['--','-','-']):
  for ax,key in zip(axs,cols):ax.plot(frame.phase_rad*180/np.pi,frame[key]*1000,color=col,ls=ls,lw=1.8,label=rf'$Q={Q:g}$ pC')
 for ax,title in zip(axs,['Radial RMS size','Tangential RMS size','Vertical RMS size']):
  key=cols[list(axs).index(ax)]
  ymax=max(frame[key].max()*1000 for frame in allframes)
  ax.set(title=title,xlabel='Orbit angle [degrees]',ylabel='RMS size [mm]',xlim=(0,180),ylim=(0,1.12*ymax))
  ax.grid(alpha=.18);ax.minorticks_on();ax.tick_params(which='both',direction='in',top=True,right=True)
 axs[0].legend(fontsize=9)
 fig.savefig(ROOT/'ellipsoid_uniform_bz.png',dpi=350);fig.savefig(ROOT/'ellipsoid_uniform_bz.pdf')
 print(json.dumps(parameters,indent=2))
 print(data.groupby('charge_C')[cols].last().to_string())
if __name__=='__main__':main()
