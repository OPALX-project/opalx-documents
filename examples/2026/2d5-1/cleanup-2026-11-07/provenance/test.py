from pathlib import Path
import os,subprocess
r=Path('/Users/adelmann/git/opalx');s=r/'tmp/2026-11-07-fft2d5-cleanup'
regex='^(TestSpaceChargeConfig|TestFFT2D5Algorithm|TestFFT2D5Numerics|TestFFT2D5Parallel|TestPoissonSolver|TestSpaceChargeSolver)$'
for threads in [1,4]:
 env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_PROC_BIND='false')
 with (s/f'ctest-omp{threads}.log').open('w') as f:rc=subprocess.run(['ctest','--test-dir',str(r/'build-omp'),'-R',regex,'--output-on-failure','-j1'],env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 print('ctest',threads,rc,flush=True);assert rc==0
 with (s/f'unit-mpi2-omp{threads}.log').open('w') as f:rc=subprocess.run(['/opt/homebrew/bin/mpirun','--oversubscribe','--bind-to','none','-n','2',str(r/'build-omp/unit_tests/SpaceCharge/TestFFT2D5Parallel')],cwd=s,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 print('mpi2',threads,rc,flush=True);assert rc==0
