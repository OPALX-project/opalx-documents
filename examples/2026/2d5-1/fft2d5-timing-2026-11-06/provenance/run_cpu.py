from pathlib import Path
import os,subprocess,time,json,hashlib
root=Path('/Users/adelmann/git/opalx');study=root/'tmp/2026-11-06-fft2d5-timing'
for n in [1,2,4,8]:
 out=study/f'cpu-ranks-{n}';out.mkdir(exist_ok=False)
 (out/'case.in').write_text((root/'tmp/2026-11-06-fft2d5-mpi-z/final-cpu-ranks-2-repeat-1/case.in').read_text())
 args=['/opt/homebrew/bin/mpirun','--oversubscribe','-n',str(n),str(study/'opalx.cpu'),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'tmp/2026-11-05-merlin6-a100/payload/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (out/'case.out').open('w') as f:rc=subprocess.run(args,cwd=out,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT).returncode
 (out/'run.json').write_text(json.dumps(dict(ranks=n,returncode=rc,command=args,wall_seconds=time.monotonic()-t,binary_sha256=hashlib.sha256((study/'opalx.cpu').read_bytes()).hexdigest()),indent=2));assert rc==0
