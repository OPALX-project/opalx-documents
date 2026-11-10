"""Audit completed bounded pilots and extrapolate measured fixed-step cost."""
from pathlib import Path
import re,json,hashlib
import numpy as np,pandas as pd,h5py
R=Path('/Users/adelmann/git/dba-lattice/comparison-20261104/unified-current');O=R/'dba-sc-feasibility';rows=[];endpoints={}
period=json.loads((R/'dba-timesteps/dt-3ps/manifest.json').read_text())['nominal_period_s']
for d in [O/'omp1-100steps',O/'omp4-100steps',O/'zerosc-omp4-100steps']:
 m=json.loads((d/'manifest.json').read_text());log=(d/'run.log').read_text();assert hashlib.sha256((d/'case.in').read_bytes()).hexdigest()==m['input_sha256'];assert 'Error>' not in log
 count=int(re.search(r'Timings> TIntegration2\.+ Count =\s*(\d+)',log).group(1));assert count==100
 with h5py.File(d/'case.h5') as f:
  keys=sorted(f,key=lambda k:int(k.split('#')[-1]));g=f[keys[-1]];i=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][i],np.arange(100000));assert abs(float(g.attrs['TIME'][0])-3e-10)<1e-22;assert int(g.attrs['GlobalTrackStep'][0])==99
  r=np.column_stack([g[k][:][i] for k in 'xyz']);p=np.column_stack([g[k][:][i] for k in ['px','py','pz']]);assert np.isfinite(r).all() and np.isfinite(p).all();q=float(g['q'][:].sum());assert abs(q/m['charge_C']-1)<1e-12
  refp=g.attrs['RefPartP'];ez=refp/np.linalg.norm(refp);ex=np.array([ez[2],0.,-ez[0]]);ey=np.array([0.,1.,0.]);labp=p[:,0,None]*ex+p[:,1,None]*ey+p[:,2,None]*ez;endpoints[d.name]=dict(r=r,p=labp)
 main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',log).group(1));orbit=float(re.search(r'Timings> OrbThreader\.+ Wall max =\s*([\d.eE+-]+)',log).group(1));steady=(main-orbit)/count
 points=[]
 for h,mi,se,step in re.findall(r'\* (\d\d):(\d\d):(\d\d) Step\s+(\d+) container',log):
  if int(step)>=10:points.append([int(step),int(h)*3600+int(mi)*60+int(se)])
 progress=float(np.polyfit(np.array(points)[:,0],np.array(points)[:,1],1)[0]) if len(points)>1 else None
 row=dict(case=d.name,space_charge=m['space_charge'],omp_threads=m['omp_threads'],particles=100000,steps=count,pilot_wall_s=m['elapsed_seconds'],native_main_s=main,orbit_threader_s=orbit,steady_s_per_step=steady,progress_fit_s_per_step=progress,turns_tracked=3e-10/period,charge_C=q,peak_rss_bytes=m.get('peak_rss_bytes'),estimated_16turn_steps_3ps=int(np.ceil(16*period/3e-12)),estimated_16turn_days_3ps=16*period/3e-12*steady/86400,estimated_16turn_days_4ps=16*period/4e-12*steady/86400,all_particle_ids_present=True,all_coordinates_and_momenta_finite=True)
 rows.append(row)
 if not m['completed']:
  assert 'time: sysctl kern.clockrate: Operation not permitted' in log;m.update(native_tracking_completed=True,completed=True,completion_basis='100 native integration steps, final H5 at300ps/step99, all IDs/count/charge/finite audit; resource wrapper alone failed its kernel clockrate probe',wrapper_returncode=m['returncode'],native_returncode=None);(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
summary=pd.DataFrame(rows);summary.to_csv(O/'timing-summary.csv',index=False)
a=endpoints['omp4-100steps']['p'];b=endpoints['zerosc-omp4-100steps']['p'];delta=np.linalg.norm(a-b,axis=1);assert delta.max()>1e-10
j=dict(binary_sha256=rows and json.loads((O/'omp4-100steps/manifest.json').read_text())['binary_sha256'],period_s=period,scope='Timing only, full-ring5.602212nC matchedKV,100k,64x64x512,ORIGINAL transverseSC, longitudinalNONE,100steps at3ps. No full turn or tune study.',momentum_change_due_to_space_charge_betagamma=dict(maximum=float(delta.max()),median=float(np.median(delta))),thread_endpoint_difference_betagamma=float(np.max(np.linalg.norm(endpoints['omp1-100steps']['p']-a,axis=1))),method='steady=(native mainTimer - OrbitThreader)/100; excludes main orbit-threading startup but includes residual startup/I/O. Log progress fit is an independent coarse timestamp check.',rows=rows)
(O/'summary.json').write_text(json.dumps(j,indent=2)+'\n');print(summary.to_string(index=False));print(json.dumps({k:v for k,v in j.items() if k!='rows'},indent=2))
