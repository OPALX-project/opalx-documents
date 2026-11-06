from pathlib import Path
import json,sys,numpy as np,pandas as pd
from pilot_local_coordinates import local,moments
R=Path(__file__).resolve().parent;O=R/'dba-pyorbit-pilot';ns={'__file__':str(R/'analyze_dba_fftw_threads.py')};exec((R/'analyze_dba_fftw_threads.py').read_text().split('baseline=O/')[0],ns)
rows=[];local_rows=[]
for nz in [512,256]:
 candidates=list((R/('dba-fftw-threads' if nz==512 else 'dba-nz256')).glob('fftw-1-*' if nz==512 else 'nz-256-*'))
 for d in candidates:
  m=json.loads((d/'manifest.json').read_text());r,p,_=ns['endpoint'](d/'case.h5');v=moments(local(r,p));rows.append(dict(code='OPALX',nz=nz,repeat=m['repeat'],launch_wall_s=m['elapsed_seconds'],tracking_s=None,native_sc_s=None,python_grouping_copy_s=0.));local_rows.append(dict(code='OPALX',nz=nz,repeat=m['repeat'],**v))
for d in sorted(O.glob('nz-*')):
 m=json.loads((d/'manifest.json').read_text());assert m['completed'] and m['particles']==100000 and m['steps']==100 and abs(m['dt_s']-3e-12)<1e-25
 nz=m['mesh'][2];repeat=int(d.name.split('-')[-1]);launch=json.loads((O/f'launch-{nz}-{repeat}.json').read_text());assert launch['returncode']==0
 p=np.load(d/'endpoint.npz');assert np.array_equal(p['id'],np.arange(100000));state=p['state'];assert np.isfinite(state).all();bg=json.loads((R/'dba-sc-feasibility/source.json').read_text())['momentum_betagamma'];v=state[:,:4].copy();v[:,[1,3]]*=bg
 local_rows.append(dict(code='PyORBIT',nz=nz,repeat=repeat,**moments(v)));rows.append(dict(code='PyORBIT',nz=nz,repeat=repeat,launch_wall_s=launch['launch_wall_s'],tracking_s=m['tracking_s'],native_sc_s=m['native_sc_s'],native_body_maps_s=m['native_body_maps_s'],python_grouping_copy_s=m['python_grouping_copy_s']))
d=pd.DataFrame(rows);v=pd.DataFrame(local_rows);d.to_csv(O/'timing-comparison.csv',index=False);v.to_csv(O/'local-moment-comparison.csv',index=False)
comparison=[]
for nz in [512,256]:
 a=v[(v.code=='OPALX')&(v.nz==nz)].iloc[0];b=v[(v.code=='PyORBIT')&(v.nz==nz)].iloc[0]
 for key in ['sigma_x_m','sigma_y_m','emit_n_x_m','emit_n_y_m']:comparison.append(dict(nz=nz,field=key,opalx=a[key],pyorbit=b[key],pyorbit_minus_opalx_percent=100*(b[key]/a[key]-1)))
pd.DataFrame(comparison).to_csv(O/'moment-differences.csv',index=False)
summary=d.groupby(['code','nz']).launch_wall_s.agg(['mean','min','max']);print(summary);print(pd.DataFrame(comparison).to_string(index=False))
(O/'summary.json').write_text(json.dumps(dict(completed=True,timing_rows=rows,moment_rows=comparison,limitations='Timing pilot only. Same source, reference flight and boundaries. PyORBIT native NGP slice/TSC transverse deposition, OPALX CIC; common-s versus common-time transport. Python phase grouping cost reported separately; total times include this driver overhead and must not be read as an intrinsic code speed ratio.'),indent=2)+'\n')
