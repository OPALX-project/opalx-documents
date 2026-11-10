from pathlib import Path
import os,subprocess,time,json,hashlib
root=Path('/psi/home/adelmann/opalx-dev/dba');old=root/'validation-mpi-z-20261106';exe=root/'build/gwendolen-cuda/src/opalx'
n=int(os.environ['SLURM_NTASKS'])
args=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(old/'gpu_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'validation-a100-20261105/assets/dba-initial-state.h5')]
record=dict(command=args,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),input_sha256=hashlib.sha256(Path('case.in').read_bytes()).hexdigest(),job=os.environ['SLURM_JOB_ID'],ranks=n)
t=time.monotonic()
with Path('case.out').open('w') as f:rc=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT).returncode
record.update(returncode=rc,wall_seconds=time.monotonic()-t);Path('run.json').write_text(json.dumps(record,indent=2));assert rc==0
assert f'MPI ranks: {n}' in Path('case.out').read_text();assert Path('timing.dat').exists()
