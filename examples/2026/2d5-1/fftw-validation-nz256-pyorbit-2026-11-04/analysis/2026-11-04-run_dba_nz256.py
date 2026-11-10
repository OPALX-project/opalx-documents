"""Change only NZ from512to256 for the frozen100-stepB8/FFT1/OMP4pilot."""
from pathlib import Path
import json,hashlib,time,subprocess,os,shutil,argparse
p=argparse.ArgumentParser();p.add_argument('repeat',type=int);a=p.parse_args();R=Path(__file__).resolve().parent;d=R/'dba-nz256'/f'nz-256-{a.repeat}';d.mkdir(parents=True,exist_ok=False)
build=json.loads(Path('/Users/adelmann/git/opalx/tmp/2026-11-04-fftw-threading/build-final.json').read_text());B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');old=R/'dba-fftw-threads/fftw-1-1';m=json.loads((old/'manifest.json').read_text());initial=R/'dba-sc-feasibility/initial-state.h5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B)==build['binary_sha256'];text=(old/'case.in').read_text();assert text.count('NZ=512')==1;text=text.replace('NZ=512','NZ=256');(d/'case.in').write_text(text)
assert text.replace('NZ=256','NZ=512')==(old/'case.in').read_text();assert sha(initial)==m['initial_state_sha256'];args=[str(B),'case.in','--restart',str(initial),'--info','1','--2D5BatchSize','8','--2D5FFTThreads','1']
meta=dict(m,case=d.name,argv=args,input_sha256=sha(d/'case.in'),mesh=[64,64,256],repeat=a.repeat,scope='100step NZ-only mesh comparison; no turns or tunes');meta.pop('completed',None);t=time.monotonic()
with (d/'run.log').open('w') as f:p=subprocess.run(args,cwd=d,env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
meta.update(completed=p.returncode==0,returncode=p.returncode,elapsed_seconds=time.monotonic()-t);(d/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True);assert p.returncode==0
