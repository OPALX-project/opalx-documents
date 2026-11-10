"""Repeat PR667 physical benchmark with frozen local FFTW build; preserve prior runs."""
from pathlib import Path
import json,hashlib,subprocess,os,time,shutil
R=Path(__file__).resolve().parent;O=R/'pr-fftw-repeat';O.mkdir(exist_ok=True)
build=json.loads(Path('/Users/adelmann/git/opalx/tmp/2026-11-04-fftw-threading/build-final.json').read_text());binary=Path('/Users/adelmann/git/opalx/build-omp/src/opalx')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for mode in ['ZeroSC','10pC']:
 old=R/'pr-bend'/mode;m=json.loads((old/'manifest.json').read_text());d=O/mode;d.mkdir(exist_ok=False);shutil.copy2(old/'track.in',d/'track.in')
 assert sha(binary)==build['binary_sha256'];assert sha(m['source']['npz'])==m['source']['npz_sha256']
 meta=dict(m,build=build,binary=str(binary),binary_sha256=sha(binary),batch_size=8,fftw_threads=1,reference_manifest=str(old/'manifest.json'))
 meta.pop('completed',None);meta.pop('elapsed_seconds',None);(d/'running.json').write_text(json.dumps(meta,indent=2)+'\n')
 args=[str(binary),'track.in','--info','4','--2D5BatchSize','8','--2D5FFTThreads','1'];meta['argv']=args
 print('START PR repeat',mode,flush=True);t=time.monotonic()
 with (d/'track.out').open('w') as f:p=subprocess.run(args,cwd=d,env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 meta.update(completed=p.returncode==0,returncode=p.returncode,elapsed_seconds=time.monotonic()-t);(d/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print('DONE',mode,meta['elapsed_seconds'],flush=True);assert p.returncode==0
