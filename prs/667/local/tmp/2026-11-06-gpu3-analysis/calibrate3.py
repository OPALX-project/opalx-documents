from pathlib import Path
import os,subprocess,json,time,hashlib,re
r=Path('/psi/home/adelmann/opalx-dev/dba');s=r/'validation-row-profile-20261106';exe=r/'build/gwendolen-cuda/src/opalx';assert hashlib.sha256(exe.read_bytes()).hexdigest()=='a21ab5e66c046f089d907ff14eb7b5c932a234336d49efc6b082431a8f1dd32a'
for steps in [100,1000]:
 d=s/f'calibrate3-{steps}';d.mkdir(exist_ok=False);text=(r/'validation-r2c-rows-20261106/gpu-2-rows/case.in').read_text().replace('MAXSTEPS=100;','MAXSTEPS='+str(steps)+';');assert 'MAXSTEPS='+str(steps)+';' in text;(d/'case.in').write_text(text)
 args=['mpirun','-np','3','--map-by','slot','--bind-to','none',str(r/'validation-mpi-z-20261106/gpu_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'validation-a100-20261105/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,steps=steps,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()),indent=2));assert rc==0
