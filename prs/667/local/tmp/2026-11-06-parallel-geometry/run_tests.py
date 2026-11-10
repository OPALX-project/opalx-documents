from pathlib import Path
import subprocess,os
r=Path('/Users/adelmann/git/opalx');s=r/'tmp/2026-11-06-parallel-geometry';b=r/'build-omp/unit_tests/SpaceCharge'
for threads in [1,4]:
 for target in ['TestFFT2D5Algorithm','TestFFT2D5Numerics']:
  with (s/f'unit-{target.lower()}-omp{threads}.log').open('w') as f:rc=subprocess.run([str(b/target)],cwd=s,env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT).returncode
  print(threads,target,rc,flush=True);assert rc==0
 for n in [1,2,4]:
  with (s/f'unit-parallel-rank{n}-omp{threads}.log').open('w') as f:rc=subprocess.run(['/opt/homebrew/bin/mpirun','--oversubscribe','--bind-to','none','-n',str(n),str(b/'TestFFT2D5Parallel')],cwd=s,env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT).returncode
  print(threads,n,'Parallel',rc,flush=True);assert rc==0
