from pathlib import Path
import subprocess,os,json,re,hashlib
import h5py,numpy as np
record=Path(__file__).resolve().parent
source=Path('/Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper/tracking')
variant=__import__('sys').argv[1]
d=record/('smoke-'+variant);d.mkdir(exist_ok=True)
lines=(source/'sources/bend-uniform-n1048576.dist').read_text().splitlines()
(d/'single.dist').write_text('1\n'+lines[1]+'\n'+lines[2]+'\n')
text=(source/'bend-10m-100steps-local-original/opalx/runs/bend-ZeroSC-10m-100steps-local-original/track.in').read_text()
text=text.replace('NPARTDIST=1048576','NPARTDIST=1').replace('NALLOC=1048576','NALLOC=1').replace(str(source/'sources/bend-uniform-n1048576.dist'),str(d/'single.dist')).replace('MAXSTEPS=100,ZSTOP={10},DT={3.3356409519815204e-07}','MAXSTEPS=2,ZSTOP={.001},DT={1e-9}')
(d/'smoke.in').write_text(text)
exe=Path('/Users/adelmann/git/opalx')/variant/'src/opalx'
with (d/'smoke.out').open('w') as log:p=subprocess.run([str(exe),'smoke.in','--info','4'],cwd=d,env=dict(os.environ,OMP_NUM_THREADS='4' if variant=='build-omp' else '1',OMP_PROC_BIND='false'),stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(variant,p.returncode)
log=(d/'smoke.out').read_text();assert 'd47703aff69879de8e3a87f862a171926b288f69' in log
with h5py.File(d/'smoke.h5') as f:
 assert len(f)==2
 for g in f.values():
  assert len(g['id'])==1
  for name in ['x','y','z','px','py','pz']:assert np.isfinite(g[name][:]).all()
r={'passed':True,'executable':str(exe),'sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'steps':2,'particles':1,'space_charge':False,'expected_backend':'OpenMP' if variant=='build-omp' else 'Serial','log':str(d/'smoke.out')}
(d/'result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
