from pathlib import Path
import subprocess,os,time,json,hashlib
root=Path('/psi/home/adelmann/opalx-dev/dba');study=root/'validation-row-profile-20261106';exe=root/'build/gwendolen-cuda/src/opalx';assert hashlib.sha256(exe.read_bytes()).hexdigest()=='a21ab5e66c046f089d907ff14eb7b5c932a234336d49efc6b082431a8f1dd32a'
for n in [1,2]:
 d=study/f'gpu-{n}-nsys';d.mkdir(exist_ok=False);(d/'case.in').write_text((root/'validation-r2c-rows-20261106/gpu-1-rows/case.in').read_text())
 args=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(root/'validation-mpi-z-20261106/gpu_rank.sh'),str(study/'profile_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'validation-a100-20261105/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()),indent=2));assert rc==0
 for rep in d.glob('*.nsys-rep'):
  with rep.with_suffix('.export.log').open('w') as f:
   rc=subprocess.run(['nsys','export','--type','sqlite','--force-overwrite=true','--output',str(rep.with_suffix('.sqlite')),str(rep)],stdout=f,stderr=subprocess.STDOUT).returncode
  assert rc==0
