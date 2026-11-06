from pathlib import Path
import os,subprocess,time,json,hashlib
root=Path('/psi/home/adelmann/opalx-dev/dba');study=root/'validation-r2c-rows-20261106';n=int(os.environ['SLURM_NTASKS'])
source=(root/'validation-timing-20261106/gpu-2/case.in').read_text().replace('PIPEMODE="NONE"','PIPEMODE="OPEN"')
for label,name in [('before','opalx.pre-r2c-rows-20261106'),('rows','opalx')]:
 exe=root/'build/gwendolen-cuda/src'/name
 out=study/f'gpu-{n}-{label}';out.mkdir(exist_ok=False);(out/'case.in').write_text(source)
 args=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(root/'validation-mpi-z-20261106/gpu_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'validation-a100-20261105/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (out/'case.out').open('w') as f:rc=subprocess.run(args,cwd=out,stdout=f,stderr=subprocess.STDOUT).returncode
 record=dict(command=args,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),input_sha256=hashlib.sha256((out/'case.in').read_bytes()).hexdigest(),job=os.environ['SLURM_JOB_ID'],ranks=n,returncode=rc,wall_seconds=time.monotonic()-t)
 (out/'run.json').write_text(json.dumps(record,indent=2));assert rc==0
 assert f'MPI ranks: {n}' in (out/'case.out').read_text();assert (out/'timing.dat').exists()
