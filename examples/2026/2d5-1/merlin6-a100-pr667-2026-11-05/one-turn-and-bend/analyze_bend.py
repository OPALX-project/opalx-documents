"""Audit batch64 charged-bend snapshots and compare preserved GPU/CPU series."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd,h5py
S=Path('/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105');O=S/'one-turn-and-bend';D=O/'bend-batch64';sys.path.insert(0,str(S));import emittance_reference as h
m=json.loads((D/'manifest.json').read_text());assert m['completed'];rows=[];audits=[];p0=.001/np.sqrt(1-.001**2)
def record(step,r,p):
 phase=step*.1/2;theta=np.arctan2(r[:,2],r[:,0]+2);u=np.hypot(r[:,0]+2,r[:,2])-2;s=2*np.arctan2(np.sin(theta-phase),np.cos(theta-phase));values=dict(sigma_u_m=np.std(u),sigma_y_m=np.std(r[:,1]),sigma_s_m=np.std(s),**h.particle_emittances(r,p,phase,p0,938272088.16));assert all(np.isfinite(v) for v in values.values());rows.append(dict(code='A100 batch64',mode='10pC',step=step,s_m=step*.1,**values))
with np.load(S/'assets/bend-source.npz') as src:record(0,src['cartesian_m'],src['momenta_betagamma'])
with h5py.File(D/'case.h5') as f:
 keys=sorted(f,key=lambda k:int(k.split('#')[-1]));assert len(keys)==100
 for step,key in enumerate(keys,1):
  g=f[key];assert np.array_equal(np.sort(g['id'][:]),np.arange(1048576));q=float(g['q'][:].sum());assert abs(q/1e-11-1)<1e-10;t=float(np.asarray(g.attrs['TIME']).flat[0]);assert abs(t-step*m['dt_s'])<1e-16;r,p=h.global_snapshot(g);assert np.isfinite(r).all() and np.isfinite(p).all();record(step,r,p);audits.append(dict(step=step,particles=len(r),charge_C=q,time_s=t))
a=pd.DataFrame(rows);a.to_csv(D/'series.csv',index=False,float_format='%.17g');pd.DataFrame(audits).to_csv(D/'snapshot-audit.csv',index=False)
fields=['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV'];metrics=[]
for filename,code,label in [('gpu-series.csv','A100 OPALX','Preserved A100 serial'),('published-series.csv','Local original','Published CPU ORIGINAL'),('current-cpu-series.csv','Current OPALX','Current CPU')]:
 b=pd.read_csv((O if filename=='current-cpu-series.csv' else S)/filename,float_precision='round_trip');b=b[(b.code==code)&(b['mode']=='10pC')].set_index('step');assert len(b)==101
 for field in fields:
  delta=float(abs(a.set_index('step')[field]-b[field]).max());scale=float(abs(b[field]).max());error=delta/scale if scale else 0.;metrics.append(dict(reference=label,field=field,max_absolute_difference=delta,max_difference_percent_reference_peak=100*error));assert error<1e-6,(label,field,error)
pd.DataFrame(metrics).to_csv(D/'comparison.csv',index=False);summary=dict(completed=True,audited_snapshots=100,all_particles_retained=True,charge_C=1e-11,longitudinal='OPEN',batch_size=64,max_difference_percent_reference_peak=max(t['max_difference_percent_reference_peak'] for t in metrics),comparisons=metrics);(D/'validation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
