"""Compare the unchanged100-step charged pilot before/after caching."""
from pathlib import Path
import json,re,io
import numpy as np,pandas as pd,h5py
R=Path(__file__).resolve().parent;O=R/'dba-fftw-release'
def endpoint(path):
 with h5py.File(path) as f:
  assert len(f)==1;g=f[next(iter(f))];i=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][i],np.arange(100000));assert abs(float(g.attrs['TIME'][0])-3e-10)<1e-22;assert int(g.attrs['GlobalTrackStep'][0])==99;r=np.column_stack([g[c][:][i] for c in 'xyz']);p=np.column_stack([g[c][:][i] for c in ['px','py','pz']]);assert np.isfinite(r).all() and np.isfinite(p).all();q=float(g['q'][:].sum());assert abs(q/5.602212333965894e-9-1)<1e-12
  ez=g.attrs['RefPartP']/np.linalg.norm(g.attrs['RefPartP']);ex=np.array([ez[2],0.,-ez[0]]);ey=np.array([0.,1.,0.]);rot=np.array([ex,ey,ez]);return r@rot+g.attrs['RefPartR'],p@rot,q
def stat(path):
 text=path.read_text();blocks=re.findall(r'&column\b(.*?)&end',text,re.S);names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in blocks];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];values=np.loadtxt(io.StringIO('\n'.join(lines)));assert values.shape[1]==len(names);return pd.DataFrame(values,columns=names)

import hashlib
stock=R/'dba-projection-cache-retiming/optimized-1'
base=endpoint(stock/'case.h5');bs=stat(stock/'case.stat')
bm=json.loads((stock/'manifest.json').read_text());rows=[];metrics=[]
for name in ['optimized-1','optimized-2','optimized-profile']:
 d=O/name
 if not (d/'manifest.json').exists():continue
 m=json.loads((d/'manifest.json').read_text());assert m['completed'] and m['returncode']==0
 assert m['input_sha256']==bm['input_sha256'] and m['initial_state_sha256']==bm['initial_state_sha256']
 assert m['source_head']==bm['source_head'] and m['source_diff_sha256']==bm['source_diff_sha256']
 r,p,q=endpoint(d/'case.h5');ss=stat(d/'case.stat');assert ss.shape==bs.shape
 dr=float(np.linalg.norm(r-base[0],axis=1).max());dp=float(np.linalg.norm(p-base[1],axis=1).max())
 assert dr<1e-9 and dp<1e-10
 assert np.allclose(ss.t,bs.t,rtol=0,atol=1e-14)
 for c in [c for c in ss if c.startswith(('rms_','emit_'))]:
  absolute=float(np.max(abs(ss[c]-bs[c])));scale=float(np.max(abs(bs[c])));relative=absolute/scale if scale else 0.
  assert relative<1e-8
  metrics.append(dict(case=name,column=c,max_absolute_difference=absolute,max_relative_difference=relative))
 rows.append(dict(case=name,wall_s=m['elapsed_seconds'],stock_wall_s=bm['elapsed_seconds'],speedup=bm['elapsed_seconds']/m['elapsed_seconds'],max_lab_position_difference_m=dr,max_lab_momentum_difference_betagamma=dp,particles=100000,charge_C=q,binary_sha256=m['binary_sha256']))
summary=dict(stock_manifest=bm,rows=rows,numerical_bounds='1e-9m,1e-10beta-gamma,1e-8relativeRMS/emittance; same100kIDs/input/source/charge/100steps300ps; no physics tolerance changed')
(O/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
pd.DataFrame(rows).to_csv(O/'comparison.csv',index=False);pd.DataFrame(metrics).to_csv(O/'stat-comparison.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False));print(pd.DataFrame(metrics).groupby('case').max_relative_difference.max())
