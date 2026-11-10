from pathlib import Path
import subprocess,os,json,time,hashlib,sys
r=Path('/psi/home/adelmann/opalx-dev/dba');s=r/'validation-cleanup-20261107';n=int(sys.argv[1]);assert n in [1,2]
for mode in ['before','after']:
 exe=r/'build/gwendolen-cuda/src'/('opalx.pre-cleanup-20261107' if mode=='before' else 'opalx.cleanup-20261107')
 d=s/f'gpu-{n}-{mode}';d.mkdir(exist_ok=False)
 (d/'case.in').write_text((r/'validation-parallel-geometry-20261106/gpu-1-after/case.in').read_text())
 args=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(r/'validation-mpi-z-20261106/gpu_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'validation-a100-20261105/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,profiled=False,mode=mode,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()),indent=2));assert rc==0
