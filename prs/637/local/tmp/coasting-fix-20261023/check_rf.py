from pathlib import Path
import shutil,os,subprocess
repo=Path('/Users/adelmann/git/opalx-master');src=repo/'tmp/ring-probes-20261023/acceleration-590MeV';dst=repo/'tmp/coasting-fix-20261023/after-rf';dst.mkdir()
for p in src.iterdir():
 if p.name in ['acceleration.in','bfield.dat','proton72.dat','proton.dat','rffield1.dat','rffield2.dat']:shutil.copy2(p,dst/p.name)
with (dst/'run.log').open('w') as f:subprocess.run(['mpirun','-np','1',str(repo/'build_openmp/src/opalx'),'acceleration.in','--info','2'],cwd=dst,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1200)
import h5py,numpy as np
with h5py.File(src/'acceleration.h5') as a,h5py.File(dst/'acceleration.h5') as b:
 assert set(a)==set(b)
 for key in a:
  for n in ['id','x','y','z','px','py','pz']:np.testing.assert_array_equal(a[key][n][:],b[key][n][:])
  for n in ['TIME','SPOS','GlobalTrackStep','RefPartR','RefPartP']:np.testing.assert_array_equal(a[key].attrs[n],b[key].attrs[n])
 print('RF all',len(a),'saved states EXACT')
