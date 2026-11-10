"""Compare the unchanged100-step charged pilot before/after caching."""
from pathlib import Path
import json,re,io
import numpy as np,pandas as pd,h5py
R=Path('/Users/adelmann/git/dba-lattice/comparison-20261104/unified-current');O=R/'dba-projection-cache'
def endpoint(path):
 with h5py.File(path) as f:
  assert len(f)==1;g=f[next(iter(f))];i=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][i],np.arange(100000));assert abs(float(g.attrs['TIME'][0])-3e-10)<1e-22;assert int(g.attrs['GlobalTrackStep'][0])==99;r=np.column_stack([g[c][:][i] for c in 'xyz']);p=np.column_stack([g[c][:][i] for c in ['px','py','pz']]);assert np.isfinite(r).all() and np.isfinite(p).all();q=float(g['q'][:].sum());assert abs(q/5.602212333965894e-9-1)<1e-12
  ez=g.attrs['RefPartP']/np.linalg.norm(g.attrs['RefPartP']);ex=np.array([ez[2],0.,-ez[0]]);ey=np.array([0.,1.,0.]);rot=np.array([ex,ey,ez]);return r@rot+g.attrs['RefPartR'],p@rot,q
def stat(path):
 text=path.read_text();blocks=re.findall(r'&column\b(.*?)&end',text,re.S);names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in blocks];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];values=np.loadtxt(io.StringIO('\n'.join(lines)));assert values.shape[1]==len(names);return pd.DataFrame(values,columns=names)
base=endpoint(O/'baseline/case.h5');basestat=stat(O/'baseline/case.stat');assert len(basestat)==10;zero=endpoint(R/'dba-sc-feasibility/zerosc-omp4-100steps/case.h5');kick_scale=float(np.linalg.norm(base[1]-zero[1],axis=1).max());baseline=json.loads((O/'baseline/manifest.json').read_text());rows=[];metrics=[]
for name in ['baseline','optimized-1','optimized-2','optimized-profile']:
 d=O/name
 if not (d/'manifest.json').exists():continue
 m=json.loads((d/'manifest.json').read_text())
 if not m.get('completed'):continue
 assert m['returncode']==0 and m['input_sha256']==baseline['input_sha256'] and m['initial_state_sha256']==baseline['initial_state_sha256'];r,p,q=endpoint(d/'case.h5');s=stat(d/'case.stat');assert s.shape==basestat.shape;assert np.allclose(s.t,basestat.t,rtol=0,atol=1e-14)
 log=(d/'run.log').read_text();main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',log)[1]);orbit=float(re.search(r'Timings> OrbThreader\.+ Wall max =\s*([\d.eE+-]+)',log)[1]);steady=(main-orbit)/100
 delta_p=float(np.linalg.norm(p-base[1],axis=1).max());delta_r=float(np.linalg.norm(r-base[0],axis=1).max());assert delta_r<1e-9 and delta_p<1e-10;assert delta_p/kick_scale<.001
 row=dict(case=name,wall_seconds=m['elapsed_seconds'],steady_seconds_per_step=steady,speedup=baseline['elapsed_seconds']/m['elapsed_seconds'],time_reduction_percent=100*(1-m['elapsed_seconds']/baseline['elapsed_seconds']),max_lab_position_difference_m=delta_r,max_lab_momentum_difference_betagamma=delta_p,max_momentum_difference_percent_of_reference_sc_kick=100*delta_p/kick_scale,charge_C=q,particles=100000,binary_sha256=m['binary_sha256']);rows.append(row)
 for c in [c for c in s if c.startswith(('rms_','emit_'))]:
  diff=float(np.max(abs(s[c]-basestat[c])));scale=float(np.max(abs(basestat[c])));metrics.append(dict(case=name,column=c,max_absolute_difference=diff,max_reference_magnitude=scale,max_relative_difference=diff/scale if scale else 0.))
summary=pd.DataFrame(rows);summary.to_csv(O/'comparison.csv',index=False);pd.DataFrame(metrics).to_csv(O/'stat-comparison.csv',index=False);j=dict(baseline_binary_sha256=baseline['binary_sha256'],reference_sc_kick_scale_betagamma=kick_scale,rows=rows,comparison='100000IDmatched laboratory endpointvectors and all10stat RMS/emittance samples;same exactinput/checkpoint,4OMP,1MPI,100steps. Numerical-QA bounds1e-9m,1e-10beta-gamma and0.1% ofreferenceSCkick; no physics tolerance changed.');(O/'comparison.json').write_text(json.dumps(j,indent=2)+'\n');print(summary.to_string(index=False));print(pd.DataFrame(metrics).groupby('case').max_relative_difference.max().to_string())
