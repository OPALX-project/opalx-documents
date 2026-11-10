from pathlib import Path
import h5py,numpy as np,json,re
s=Path(__file__).resolve().parent
arrays={};rows=[]
for name in ['stat10','stat0','stat0-profile']:
 d=s/name;meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0
 log=(d/'case.out').read_text();count=lambda key:int(m[1]) if (m:=re.search(re.escape(key)+r'\.+ Count =\s*(\d+)',log)) else 0
 with h5py.File(d/'case.h5') as f:
  for g in f.values():
   assert np.array_equal(np.sort(g['id'][:]),np.arange(100000));assert abs(g['q'][:].sum()/5.602212333965894e-9-1)<1e-12
  g=max(f.values(),key=lambda a:float(np.asarray(a.attrs['TIME']).flat[0]));assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-21;assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99
  a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(g['id'][:])];assert np.isfinite(a).all();arrays[name]=a
 row=dict(run=name,moment_count=count('computeMoments'),stat_write_count=count('Write Stat'),particles=len(a),charge_C=float(a[:,-1].sum()))
 assert row['stat_write_count']==(10 if name=='stat10' else 0)
 if name!='stat10':
  b=arrays['stat10'];row.update(max_position_m=float(np.linalg.norm(a[:,:3]-b[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(a[:,3:6]-b[:,3:6],axis=1).max()),all_particles_exact=bool(np.array_equal(a,b)));assert row['max_position_m']<1e-8 and row['max_momentum']<1e-9,row
 rows.append(row)
(s/'particle-audit.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
