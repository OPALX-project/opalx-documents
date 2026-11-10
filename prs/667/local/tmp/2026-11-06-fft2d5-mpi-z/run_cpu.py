from pathlib import Path
import subprocess, os, time, json, hashlib
root=Path('/Users/adelmann/git/opalx'); study=root/'tmp/2026-11-06-fft2d5-mpi-z'; assets=root/'tmp/2026-11-05-merlin6-a100/payload/assets'
base=(root/'tmp/2026-11-05-merlin6-a100/payload/inputs/dba-pilot.in').read_text().replace('/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/assets',str(assets))
env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OMP_PROC_BIND='false')
for name,exe,n,parallel in [(f'final-cpu-ranks-{n}-repeat-{r}',study/'opalx.cpu-z-validated',n,True) for r in [1,2] for n in [1,2,4]]:
 d=study/name;d.mkdir(exist_ok=True);(d/'case.in').write_text(base.replace('PARFFTZ=FALSE',f'PARFFTZ={str(parallel).upper()}'))
 command=['/opt/homebrew/bin/mpirun','--oversubscribe','-n',str(n),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(assets/'dba-initial-state.h5')]
 start=time.monotonic()
 with (d/'case.out').open('w') as log: result=subprocess.run(command,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
 (d/'run.json').write_text(json.dumps(dict(binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),ranks=n,command=command,returncode=result.returncode,wall_seconds=time.monotonic()-start),indent=2))
 if result.returncode: break
