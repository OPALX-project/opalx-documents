from pathlib import Path
import importlib.util,json,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
import numpy as np
import pandas as pd
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;TRACKING=ROOT.parent
helper=TRACKING/'bend-10m-100steps-658-committed/provenance/emittance_reference-f2687a55cea723923a642af5bbc0a444f0d3d61b2758e1f4db5ac4e6d3f3dba5.py'
spec=importlib.util.spec_from_file_location('emit_helper',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
manifest=json.loads((ROOT/'run/manifest.json').read_text());assert manifest['completed']
with np.load(manifest['source']['npz']) as source:r0=source['cartesian_m'];p0=source['momenta_betagamma']
bg=manifest['source']['momentum_betagamma'];mass=938272088.16
rows=[];checks=[]
def record(step,r,p,time):
 phase=step*.1/2;theta=np.arctan2(r[:,2],r[:,0]+2);u=np.hypot(r[:,0]+2,r[:,2])-2;s=2*np.arctan2(np.sin(theta-phase),np.cos(theta-phase))
 row=dict(step=step,s_m=step*.1,time_s=time,sigma_u_m=np.std(u),sigma_y_m=np.std(r[:,1]),sigma_s_m=np.std(s),**h.particle_emittances(r,p,phase,bg,mass));rows.append(row)
record(0,r0,p0,0)
with h5py.File(ROOT/'run/track.h5') as f:
 keys=sorted(f,key=lambda k:int(k.split('#')[-1]));assert len(keys)==100
 for i,k in enumerate(keys,1):
  g=f[k];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(100000));time=float(np.asarray(g.attrs['TIME']).flat[0]);assert abs(time-i*manifest['dt_s'])<1e-16
  r,p=h.global_snapshot(g);assert np.isfinite(r).all() and np.isfinite(p).all();record(i,r,p,time)
  q=g['q'][:];charge=float(q.sum());assert np.isclose(charge,1e-11,rtol=1e-10,atol=0)
  checks.append(dict(step=i,particles=len(ids),charge_C=charge))
d=pd.DataFrame(rows);d.to_csv(ROOT/'series.csv',index=False,float_format='%.17g')
ref=pd.read_csv(TRACKING/'bend-10m-100steps-local-original/analysis/series.csv');ref=ref[(ref.code=='Local original')&(ref['mode']=='10pC')&(ref.steps==100)].sort_values('step')
fields=['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV']
comparison=[]
for field in fields:
 a=d[field].iloc[-1];b=ref[field].iloc[-1];comparison.append(dict(field=field,reduced_grid=a,previous_fine_grid=b,endpoint_change_percent=100*(a/b-1)))
pd.DataFrame(comparison).to_csv(ROOT/'endpoint-comparison.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axes=plt.subplots(2,3,figsize=(10,6),layout='constrained')
for ax,field,factor,label in zip(axes.flat,fields,[1e3,1e3,1,1e6,1e6,1e3],['RMS radial (mm)','RMS vertical (mm)','RMS longitudinal (m)','Normalized radial emittance (mm mrad)','Normalized vertical emittance (mm mrad)','Longitudinal emittance (mm eV)']):
 ax.plot(ref.s_m,ref[field]*factor,label=r'$512^3$, 1,048,576 particles (archived local build)',color='#0072B2');ax.plot(d.s_m,d[field]*factor,label=r'$64\times64\times512$, 100,000 particles (same archived executable)',color='#D55E00')
 ax.set(xlabel='$s$ (m)',ylabel=label,xlim=(0,10),ylim=(0,None));ax.grid(alpha=.2)
fig.suptitle('10 pC, R=2 m, 5 m uniform beam: 10 m tracking, 100 steps, ORIGINAL')
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',fontsize=9)
for ext in ['png','pdf']:fig.savefig(ROOT/f'comparison.{ext}',dpi=300)
summary=dict(completed=True,elapsed_seconds=manifest['elapsed_seconds'],previous_elapsed_seconds=1301.8812748,runtime_ratio=1301.8812748/manifest['elapsed_seconds'],checks_passed=True,particle_charge_time_checks=checks,endpoints=comparison,comparison_limit='Exact same executable and4OMPthreads as fine reference; mesh andparticle count both differ, so not isolated mesh convergence.',initial_rms_m=[float(np.std(np.hypot(r0[:,0]+2,r0[:,2])-2)),float(np.std(r0[:,1])),float(np.std(2*np.arctan2(r0[:,2],r0[:,0]+2)))])
(ROOT/'results.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='particle_charge_time_checks'},indent=2))
