"""Reduced grid/source, exact fine-reference executable and thread count."""
from pathlib import Path
import json,hashlib,subprocess,os,time,sys,shutil
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent/'bend-10m-100steps-32x32x512-n100000';RUN=ROOT/'run'
RUN.mkdir(exist_ok=True);assert not (RUN/'manifest.json').exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
fine_path=ROOT.parent/'bend-10m-100steps-local-original/opalx/runs/bend-10pC-10m-100steps-local-original/manifest.json'
fine=json.loads(fine_path.read_text());prior=json.loads((BASE/'run/manifest.json').read_text())
binary=Path(fine['binary']);assert sha(binary)==fine['binary_sha256']=='a2c87276106782554324753c889db203629f1b7f645d35e2f1bd30b00e32fa9e'
shutil.copy2(BASE/'run/track.in',RUN/'track.in')
# Keep reduced input byte-identical; opening comment describes its origin, not this executable.
assert sha(RUN/'track.in')==prior['input_sha256']
for key in ['npz','distribution']:assert sha(prior['source'][key])==prior['source'][key+'_sha256']
meta={**prior,'binary':str(binary),'binary_sha256':sha(binary),'omp_threads':fine['omp_threads'],'driver_sha256':sha(__file__),'reference_manifest':str(fine_path),'reference_manifest_sha256':sha(fine_path),'note':'Exact same executable and OMP count as fine-grid reference. Input and100k source byte-identical to prior reduced-grid run; input opening comment is inherited.'}
for k in ['returncode','elapsed_seconds','completed']:meta.pop(k,None)
(RUN/'running.json').write_text(json.dumps(meta,indent=2)+'\n')
env=dict(os.environ,OMP_NUM_THREADS=str(fine['omp_threads']),OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');t=time.monotonic()
with (RUN/'track.out').open('w') as f:result=subprocess.run([str(binary),'track.in','--info','4'],cwd=RUN,env=env,stdout=f,stderr=subprocess.STDOUT)
meta.update(returncode=result.returncode,elapsed_seconds=time.monotonic()-t,completed=result.returncode==0);(RUN/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2));sys.exit(result.returncode)
