from pathlib import Path
import sys,json
import h5py,numpy as np
s=Path(__file__).resolve().parent
def read(p):
 with h5py.File(p) as f:
  g=max(f.values(),key=lambda x:float(np.asarray(x.attrs['TIME']).flat[0]));a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(g['id'][:])];assert np.isfinite(a).all();return a
rows=[]
for mode in ['before','after']:
 ref=read(s/f'gpu-1-{mode}/case.h5')
 for n in [2,3]:
  d=s/f'gpu-{n}-{mode}'
  if not (d/'run.json').exists():continue
  a=read(d/'case.h5');row=dict(mode=mode,ranks=n,reference_ranks=1,max_position_m=float(np.linalg.norm(a[:,:3]-ref[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(a[:,3:6]-ref[:,3:6],axis=1).max()))
  assert row['max_position_m']<1e-8 and row['max_momentum']<1e-9,row
  rows.append(row)
(s/'cross-rank-particle-audit.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
