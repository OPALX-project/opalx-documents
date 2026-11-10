"""One-turn coasting KV comparison in exact design coordinates, without new tracking.

Use the recorded free-space, transverse-only source and hard-edge KV envelope.
Physical slice rms values are compared with particle-weighted bin-averaged model
covariances. For time evolution, remove the known periodic Twiss variation:
  xi=x/a(s), pi=[a(s)*x'-a'(s)*x]/epsilon_edge.
Map these to the cell entrance via x0=a0*xi, x0'=a0'*xi+epsilon_edge*pi/a0.
This unit-determinant map prevents pooling different lattice Twiss phases from
creating an artificial projected emittance. The model predicts sigma0=a0/2,
epsilon_rms=epsilon_edge/4. Pooled residual slice-centroid variations are retained.
"""
from pathlib import Path
import sys,json,hashlib,os
import numpy as np,pandas as pd,h5py
ROOT=Path(__file__).resolve().parent;MODEL=ROOT/'model';sys.path.insert(0,str(MODEL))
H5_PATH=Path(os.environ.get('OPALX_DBA_H5',str(ROOT/'case.h5')))
assert H5_PATH.is_file()
from kv_model import matched,propagate,beam_parameters
from fullring_kv_source import envelopes_at
cfg=json.loads((MODEL/'config.json').read_text());machine=json.loads((MODEL/'machine.json').read_text());meta=json.loads((MODEL/'source.json').read_text());run=json.loads((ROOT/'manifest.json').read_text());assert run['completed'] and run['retained_particles']==meta['particle_count']==100000
assert hashlib.sha256((ROOT/'case.in').read_bytes()).hexdigest()==run['input_sha256']
ex=4*cfg['rms_emittance_x_m_rad'];ey=4*cfg['rms_emittance_y_m_rad'];C=meta['circumference_m'];beta,gamma,rigidity,IA=beam_parameters(cfg['kinetic_energy_MeV']);current=meta['charge_C']*beta*299792458./C;K=2*current/(IA*(beta*gamma)**3)
assert abs(K/meta['perveance']-1)<1e-10
initial,tunes,residual=matched(cfg['elements'],ex,ey,K,guess=meta['initial_envelope']);assert np.max(abs(initial-np.asarray(meta['initial_envelope']))/np.repeat(initial[[0,2]],2))<1e-7
_,grid,model=propagate(initial,cfg['elements'],ex,ey,K,samples=200)
pd.DataFrame(dict(s_cell_m=grid,a_m=model[:,0],ap=model[:,1],b_m=model[:,2],bp=model[:,3],sigma_x_m=model[:,0]/2,sigma_y_m=model[:,2]/2)).to_csv(ROOT/'analytic-envelope-cell.csv',index=False)
def local(r,p):
 best=np.full(len(r),np.inf);out=np.empty((len(r),6))
 for el in machine['elements']:
  X,Z,t0=el['entry_X_Z_theta'];L=el['length_m'];h=el['h_per_m'];dx=r[:,0]-X;dz=r[:,2]-Z
  if h:
   cx=X-np.cos(t0)/h;cz=Z+np.sin(t0)/h;theta=np.arctan2(-(r[:,2]-cz),r[:,0]-cx);delta=np.arctan2(np.sin(t0-theta),np.cos(t0-theta));u=np.clip(delta/h,0,L);t=t0-h*u;xx=cx+np.cos(t)/h;zz=cz-np.sin(t)/h
  else:u=np.clip(dx*np.sin(t0)+dz*np.cos(t0),0,L);t=np.full(len(r),t0);xx=X+u*np.sin(t0);zz=Z+u*np.cos(t0)
  dist=(r[:,0]-xx)**2+(r[:,2]-zz)**2;use=dist<best;best[use]=dist[use]
  values=np.c_[(r[:,0]-xx)*np.cos(t)-(r[:,2]-zz)*np.sin(t),p[:,0]*np.cos(t)-p[:,2]*np.sin(t),r[:,1],p[:,1],el['s_start_m']+u,p[:,0]*np.sin(t)+p[:,2]*np.cos(t)];out[use]=values[use]
 assert np.isfinite(out).all() and np.min(out[:,5])>0
 return out
source=np.load(MODEL/'source.npz');assert hashlib.sha256((MODEL/'source.npz').read_bytes()).hexdigest()==meta['source_sha256']
v0=local(source['positions_m'],source['momenta_betagamma']);projection_errors=dict(position_m=float(np.max(abs(v0[:,[0,2]]-source['transverse'][:,[0,2]]))),slope=float(np.max(abs(v0[:,[1,3]]/v0[:,5,None]-source['transverse'][:,[1,3]]))),path_s_m=float(np.max(abs(v0[:,4]-source['s_m']))));assert projection_errors['position_m']<1e-12 and projection_errors['slope']<1e-12
rows=[];profiles=[];audits=[]
def covariance_area(q,p):
 q=q-q.mean();p=p-p.mean();variance=np.mean(q*q);res=p-np.mean(q*p)/variance*q;return float(np.sqrt(variance*np.mean(res*res)))
def analyse(step,time,sref,v):
 env=envelopes_at(v[:,4],initial,cfg['elements'],ex,ey,K);row=dict(step=step,time_s=time,reference_s_m=sref,reference_turns=sref/C)
 bin_id=np.minimum((np.remainder(v[:,4],C)/C*96).astype(int),95)
 for j,axis,epsilon in [(0,'x',ex),(2,'y',ey)]:
  a,ap=env[:,j],env[:,j+1];xi=v[:,j]/a;pi=(a*v[:,j+1]/v[:,5]-ap*v[:,j])/epsilon
  xeq=initial[j]*xi;peq=initial[j+1]*xi+epsilon/initial[j]*pi
  sigma=float(np.std(xeq));emit=covariance_area(xeq,peq);target_sigma=initial[j]/2;target_emit=epsilon/4
  row.update({f'sigma_equivalent_{axis}_m':sigma,f'emit_equivalent_{axis}_m_rad':emit,f'sigma_{axis}_error_percent':100*(sigma/target_sigma-1),f'emit_{axis}_error_percent':100*(emit/target_emit-1),f'normalized_centroid_{axis}':float(xi.mean()),f'normalized_momentum_centroid_{axis}':float(pi.mean())})
  # Always retain the physical profile and finite-bin model comparison.
  for b in range(96):
   keep=bin_id==b;n=int(keep.sum());assert n>=500
   std=float(np.std(v[keep,j]));expected=float(np.sqrt(np.mean(a[keep]**2)/4));equivalent_emit=epsilon*covariance_area(xi[keep],pi[keep])
   profiles.append(dict(step=step,reference_s_m=sref,reference_turns=sref/C,axis=axis,bin=b,s_m=(b+.5)*C/96,particles=n,sigma_m=std,model_sigma_bin_m=expected,sigma_error_percent=100*(std/expected-1),emit_geometric_m_rad=equivalent_emit,model_emit_m_rad=epsilon/4,emit_error_percent=100*(equivalent_emit/(epsilon/4)-1)))
 rows.append(row)
analyse(0,0.,0.,v0)
with h5py.File(H5_PATH) as f:
 keys=sorted(f,key=lambda k:int(k.split('#')[-1]));assert len(keys)==run['retained_snapshots']==40
 for key in keys:
  g=f[key];ids=g['id'][:];order=np.argsort(ids);assert np.array_equal(ids[order],np.arange(100000));q=float(g['q'][:].sum());assert abs(q/meta['charge_C']-1)<1e-12
  ez=np.asarray(g.attrs['RefPartP'],float);ez/=np.linalg.norm(ez);assert abs(ez[1])<1e-12;rotation=np.array([[ez[2],0.,-ez[0]],[0.,1.,0.],ez]);r=np.column_stack([g[k][:][order] for k in 'xyz'])@rotation+g.attrs['RefPartR'];p=np.column_stack([g[k][:][order] for k in ['px','py','pz']])@rotation;assert np.isfinite(r).all() and np.isfinite(p).all()
  t=float(np.asarray(g.attrs['TIME']).flat[0]);sref=float(np.asarray(g.attrs['SPOS']).flat[0]);step=int(np.asarray(g.attrs['GlobalTrackStep']).flat[0]);assert abs(t/3e-12-round(t/3e-12))<1e-5
  v=local(r,p);analyse(step,t,sref,v);audits.append(dict(step=step,time_s=t,reference_s_m=sref,particles=len(r),charge_C=q,max_local_x_m=float(abs(v[:,0]).max()),max_local_y_m=float(abs(v[:,2]).max()),min_longitudinal_momentum_betagamma=float(v[:,5].min())));print(step,rows[-1]['sigma_x_error_percent'],rows[-1]['emit_x_error_percent'],flush=True)
a=pd.DataFrame(rows);b=pd.DataFrame(profiles);a.to_csv(ROOT/'evolution.csv',index=False,float_format='%.17g');b.to_csv(ROOT/'profiles.csv',index=False,float_format='%.17g');pd.DataFrame(audits).to_csv(ROOT/'snapshot-audit.csv',index=False,float_format='%.17g')
summary=dict(run=run,model=dict(charge_C=meta['charge_C'],current_A=current,perveance=K,initial_envelope=initial.tolist(),edge_emittances_m_rad=[ex,ey],geometric_rms_emittances_m_rad=[ex/4,ey/4],normalized_rms_emittances_m_rad=[beta*gamma*ex/4,beta*gamma*ey/4],periodicity_residual=residual,analytic_tunes=(6*tunes).tolist()),source_projection_errors=projection_errors,initial=a.iloc[0].to_dict(),final=a.iloc[-1].to_dict(),max_abs_evolution_difference_percent={k:float(abs(a[k]).max()) for k in a if k.endswith('error_percent')},all_snapshots_audited=len(audits),finite_bin_profile_max_difference_percent={axis:float(abs(b[(b.axis==axis)&(b.step==a.step.iloc[-1])].sigma_error_percent).max()) for axis in ['x','y']},limits='Section-equivalent moments pool all ring phases after the analytic unit-determinant Twiss map. Residual slice-centroid differences remain included. Profiles use 96 finite spatial bins; model rms is particle-weighted over the same bin. Analytic KV is paraxial linear focusing, uniform coasting density and free-space linear transverse self-fields, with no dispersion or longitudinal force. This one-turn check is not mesh/timestep convergence or a tune measurement.')
(ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['initial','final','max_abs_evolution_difference_percent','finite_bin_profile_max_difference_percent']},indent=2))
