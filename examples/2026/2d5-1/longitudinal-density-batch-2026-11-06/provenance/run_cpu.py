from pathlib import Path
import subprocess,os,time,json,hashlib,sys
r=Path('/Users/adelmann/git/opalx');s=r/'tmp/2026-11-06-longitudinal-batch';mode=sys.argv[1];exe=r/'build-omp/src'/('opalx.pre-longitudinal-density-20261106' if mode=='before' else 'opalx')
for n in [1,2]:
 d=s/f'cpu-{n}-{mode}';d.mkdir(exist_ok=False);(d/'case.in').write_text((r/'tmp/2026-11-06-r2c-integration/cpu-1-before/case.in').read_text())
 args=['/opt/homebrew/bin/mpirun','--oversubscribe','--map-by','slot','--bind-to','none','-n',str(n),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'tmp/2026-11-05-merlin6-a100/payload/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,returncode=rc,wall_seconds=time.monotonic()-t,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_base_commit='57f3997293fb0994267804257a825ded2b909f73',mode=mode),indent=2));assert rc==0
