from pathlib import Path
import sys,json
import h5py,numpy as np
root=Path(sys.argv[1]);backend=sys.argv[2];rows=[]
def read(path,steps):
 with h5py.File(path) as f:
  for g in f.values():
   assert np.array_equal(np.sort(g['id'][:]),np.arange(100000))
   assert abs(g['q'][:].sum()/5.602212333965894e-9-1)<1e-12
  g=max(f.values(),key=lambda x:float(np.asarray(x.attrs['TIME']).flat[0]))
  assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-steps*3e-12)<1e-21
  assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==steps-1
  a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(g['id'][:])]
  assert np.isfinite(a).all();return a
for n in ([1,2] if backend=='cpu' else [1,2,3]):
 for steps in ([100] if backend=='cpu' else [100,1000]):
  suffix='' if steps==100 else str(steps)
  b=read(root/f'{backend}-{n}-before{suffix}/case.h5',steps)
  a=read(root/f'{backend}-{n}-after{suffix}/case.h5',steps)
  row=dict(backend=backend,ranks=n,steps=steps,max_position_m=float(np.linalg.norm(a[:,:3]-b[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(a[:,3:6]-b[:,3:6],axis=1).max()),particles=len(a),charge_C=float(a[:,-1].sum()))
  assert row['max_position_m']<1e-8 and row['max_momentum']<1e-9,row
  rows.append(row)
(root/f'{backend}-particle-audit.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
