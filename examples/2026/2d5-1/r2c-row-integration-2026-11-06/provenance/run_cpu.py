from pathlib import Path
import os,subprocess,time,json,hashlib
root=Path('/Users/adelmann/git/opalx');outroot=root/'tmp/2026-11-06-r2c-integration'
source=(root/'tmp/2026-11-06-fft2d5-timing/cpu-ranks-1/case.in').read_text().replace('PIPEMODE="NONE"','PIPEMODE="OPEN"')
for label,exe in [('before',root/'build-omp/src/opalx.pre-r2c-rows-20261106'),('rows',root/'build-omp/src/opalx')]:
 for n in [1,2]:
  out=outroot/f'cpu-{n}-{label}';out.mkdir(exist_ok=False);(out/'case.in').write_text(source)
  args=['/opt/homebrew/bin/mpirun','--oversubscribe','--map-by','slot','--bind-to','none','-n',str(n),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'tmp/2026-11-05-merlin6-a100/payload/assets/dba-initial-state.h5')]
  t=time.monotonic()
  with (out/'case.out').open('w') as f:rc=subprocess.run(args,cwd=out,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT).returncode
  (out/'run.json').write_text(json.dumps(dict(ranks=n,returncode=rc,command=args,wall_seconds=time.monotonic()-t,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()),indent=2));assert rc==0
