from pathlib import Path
import sys,json
import h5py,numpy as np
root=Path(sys.argv[1]);n=int(sys.argv[2]);rows=[]
def read(path):
 with h5py.File(path) as f:
  for g in f.values():
   assert np.array_equal(np.sort(g['id'][:]),np.arange(100000))
   assert abs(g['q'][:].sum()/5.602212333965894e-9-1)<1e-12
  g=max(f.values(),key=lambda x:float(np.asarray(x.attrs['TIME']).flat[0]))
  assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-100*3e-12)<1e-21
  assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99
  a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(g['id'][:])]
  assert np.isfinite(a).all();return a
for profile in [False,True]:
 suffix='-profile' if profile else ''
 b=read(root/f'gpu-{n}-before{suffix}/case.h5');a=read(root/f'gpu-{n}-after{suffix}/case.h5')
 row=dict(ranks=n,profiled=profile,all_particles_exact=bool(np.array_equal(a,b)),max_position_m=float(np.linalg.norm(a[:,:3]-b[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(a[:,3:6]-b[:,3:6],axis=1).max()),particles=len(a),charge_C=float(a[:,-1].sum()))
 assert row['max_position_m']<1e-8 and row['max_momentum']<1e-9,row
 rows.append(row)
(root/f'particle-audit-{n}.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
