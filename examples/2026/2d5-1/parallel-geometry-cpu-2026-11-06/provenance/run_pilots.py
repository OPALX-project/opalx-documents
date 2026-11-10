from pathlib import Path
import subprocess,os,time,json,hashlib
r=Path('/Users/adelmann/git/opalx');s=r/'tmp/2026-11-06-parallel-geometry'
for n in [1,2,4]:
 for threads in [1,4]:
  for mode in ['before','after']:
   exe=r/'build-omp/src'/('opalx.pre-parallel-geometry-20261106' if mode=='before' else 'opalx')
   d=s/f'cpu-{n}-omp{threads}-{mode}';d.mkdir(exist_ok=False)
   (d/'case.in').write_text((r/'tmp/2026-11-06-longitudinal-batch/cpu-1-after/case.in').read_text())
   args=['/opt/homebrew/bin/mpirun','--oversubscribe','--map-by','slot','--bind-to','none','-n',str(n),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'tmp/2026-11-05-merlin6-a100/payload/assets/dba-initial-state.h5')]
   t=time.monotonic()
   with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT).returncode
   (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,omp_threads=threads,returncode=rc,wall_seconds=time.monotonic()-t,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_base_commit='a8ce134afa4e79c97e1611635e029579564ada35',mode=mode),indent=2));print(d.name,rc,flush=True);assert rc==0
