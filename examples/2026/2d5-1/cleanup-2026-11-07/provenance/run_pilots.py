from pathlib import Path
import subprocess,os,time,json,hashlib
r=Path('/Users/adelmann/git/opalx');s=r/'tmp/2026-11-07-fft2d5-cleanup'
for n in [1,2]:
 for mode in ['before','after']:
  exe=r/'build-omp/src'/('opalx.pre-cleanup-20261107' if mode=='before' else 'opalx')
  d=s/f'cpu-{n}-{mode}';d.mkdir(exist_ok=False)
  (d/'case.in').write_text((r/'tmp/2026-11-06-parallel-geometry/cpu-1-omp1-before/case.in').read_text())
  args=['/opt/homebrew/bin/mpirun','--oversubscribe','--map-by','slot','--bind-to','none','-n',str(n),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'tmp/2026-11-05-merlin6-a100/payload/assets/dba-initial-state.h5')]
  t=time.monotonic()
  with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT).returncode
  (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,omp_threads=1,mode=mode,returncode=rc,wall_seconds=time.monotonic()-t,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_base='e5f190d3b3f61dc3f04cae5834e4b46883f92d31'),indent=2)+'\n');print(d.name,rc,flush=True);assert rc==0
