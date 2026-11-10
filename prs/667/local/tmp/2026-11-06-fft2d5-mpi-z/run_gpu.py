from pathlib import Path
import subprocess,os,time,json,hashlib
root=Path('/psi/home/adelmann/opalx-dev/dba');study=root/'validation-mpi-z-20261106';old=root/'validation-a100-20261105';n=int(os.environ['SLURM_NTASKS']);exe=root/'build/gwendolen-cuda/src/opalx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=(old/'inputs/dba-pilot.in').read_text()
env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1')
launch=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(study/'gpu_rank.sh')]
subprocess.run(launch+[str(study/'mpi_gpu_probe'),str(n)],env=env,check=True)
with (study/f'unit-{n}.log').open('w') as log:
 rc=subprocess.run(launch+[str(root/'build/gwendolen-cuda/unit_tests/SpaceCharge/TestFFT2D5Parallel')],cwd=study,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
assert rc==0, f'distributed unit failed on {n} GPUs'
if n==1:
 with (study/'unit-serial.log').open('w') as log:
  for test in ['TestFFT2D5Algorithm','TestFFT2D5Numerics','TestSpaceChargeConfig']:
   subprocess.run(launch+[str(root/'build/gwendolen-cuda/unit_tests/SpaceCharge'/test)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
cases=([('gpu-preserved',root/'build/gwendolen-cuda/src/opalx.pre-mpi-z-20261106',False)] if n==1 else [])+[(f'gpu-ranks-{n}-repeat-{r}',exe,True) for r in [1,2]]
for name,binary,parallel in cases:
 d=study/name;d.mkdir(exist_ok=False);(d/'case.in').write_text(base.replace('PARFFTZ=FALSE',f'PARFFTZ={str(parallel).upper()}'))
 args=launch+[str(binary),'case.in','--info','1','--2D5BatchSize','64','--restart',str(old/'assets/dba-initial-state.h5')]
 record=dict(command=args,ranks=n,gpus=n,omp_threads=1,binary=str(binary),binary_sha256=sha(binary),input_sha256=sha(d/'case.in'),checkpoint_sha256=sha(old/'assets/dba-initial-state.h5'),job_id=os.environ['SLURM_JOB_ID'])
 start=time.monotonic()
 with (d/'case.out').open('w') as log:result=subprocess.run(args,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
 record.update(returncode=result.returncode,wall_seconds=time.monotonic()-start,launcher='OpenMPI mpirun; per-rank CUDA visibility; independently verified MPI size/GPU UUIDs')
 if n>1 and result.returncode==0:assert 'Timings{0}>' in (d/'case.out').read_text(),'OPALX did not enter multi-rank MPI'
 (d/'run.json').write_text(json.dumps(record,indent=2));assert result.returncode==0,name
print('ALL COMPLETE',n,flush=True)
