from pathlib import Path
import subprocess,os,json,time,hashlib,sys
r=Path('/psi/home/adelmann/opalx-dev/dba');s=r/'validation-longitudinal-batch-20261106';mode=sys.argv[1];assert mode in ['before','after'];exe=r/'build/gwendolen-cuda/src'/('opalx.pre-longitudinal-density-20261106' if mode=='before' else 'opalx')
for steps,n in [(100,1),(100,2),(100,3),(1000,1),(1000,2),(1000,3)]:
 d=s/f'gpu-{n}-{mode}{"" if steps==100 else str(steps)}';d.mkdir(exist_ok=False);(d/'case.in').write_text((r/'validation-r2c-rows-20261106/gpu-2-rows/case.in').read_text().replace('MAXSTEPS=100;',f'MAXSTEPS={steps};'))
 args=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(r/'validation-mpi-z-20261106/gpu_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'validation-a100-20261105/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_base_commit='57f3997293fb0994267804257a825ded2b909f73',mode=mode,steps=steps),indent=2));assert rc==0
