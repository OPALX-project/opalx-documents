from pathlib import Path
import json,numpy as np,pandas as pd
from pilot_local_coordinates import local,moments
R=Path(__file__).resolve().parent;O=R/'dba-nz256'
namespace={'__file__':str(R/'analyze_dba_fftw_threads.py')};exec((R/'analyze_dba_fftw_threads.py').read_text().split("baseline=O/")[0],namespace);endpoint=namespace['endpoint'];stat=namespace['stat']
a=R/'dba-fftw-threads/fftw-1-1';ar,ap,_=endpoint(a/'case.h5');astat=stat(a/'case.stat');_,zp,_=endpoint(R/'dba-sc-feasibility/zerosc-omp4-100steps/case.h5');kick=ap-zp;scale=np.linalg.norm(kick,axis=1).max();am=moments(local(ar,ap));rows=[]
for d in sorted(O.glob('nz-*')):
 m=json.loads((d/'manifest.json').read_text());assert m['completed'];r,p,q=endpoint(d/'case.h5');ss=stat(d/'case.stat');dr=np.linalg.norm(r-ar,axis=1);dp=np.linalg.norm(p-ap,axis=1);v=moments(local(r,p));row=dict(case=d.name,nz=256,wall_s=m['elapsed_seconds'],max_position_difference_m=float(dr.max()),rms_momentum_difference_betagamma=float(np.sqrt(np.mean(np.sum((p-ap)**2,axis=1)))),max_momentum_difference_percent_peak_sc_kick=float(100*dp.max()/scale),rms_momentum_difference_percent_rms_sc_kick=float(100*np.linalg.norm(p-ap)/np.linalg.norm(kick)))
 for key,val in v.items():row[key]=val;row[key+'_change_percent']=100*(val/am[key]-1)
 row['max_stat_rms_relative']=max(float(abs(ss[c]-astat[c]).max()/abs(astat[c]).max()) for c in ss if c.startswith('rms_'))
 rows.append(row)
pd.DataFrame(rows).to_csv(O/'comparison.csv',index=False);(O/'summary.json').write_text(json.dumps(dict(baseline_local_moments=am,baseline_mesh=[64,64,512],rows=rows,scope='100step sensitivity only; no long-term mesh-convergence/tune claim'),indent=2)+'\n');print(pd.DataFrame(rows).to_string(index=False))
