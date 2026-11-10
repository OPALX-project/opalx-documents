from pathlib import Path
import json,hashlib,subprocess,os,time
ROOT=Path(__file__).resolve().parent;TRACK=Path('/Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper/tracking');REPO=Path('/Users/adelmann/git/opalx');build=json.loads((REPO/'tmp/2026-11-04-unified-validation/validated-build.json').read_text());binary=Path(build['binary'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for mode in ['ZeroSC','10pC']:
 old=TRACK/'bend-10m-100steps-local-original/opalx/runs'/f'bend-{mode}-10m-100steps-local-original';d=ROOT/'pr-bend'/mode;d.mkdir(parents=True,exist_ok=False);m=json.loads((old/'manifest.json').read_text());text=(old/'track.in').read_text();(d/'track.in').write_text(text)
 assert sha(binary)==build['binary_sha256'];assert sha(m['source']['npz'])==m['source']['npz_sha256']
 meta=dict(build=build,binary=str(binary),binary_sha256=sha(binary),mode=mode,source=m['source'],mesh=m['mesh'] if mode=='10pC' else [8,8,8],steps=100,dt_s=m['dt_s'],charge_C=1e-11,mpi_ranks=1,omp_threads=4,input_sha256=sha(d/'track.in'),reference_manifest=str(old/'manifest.json'),field_solver='FFT2D5MODEL=ORIGINAL' if mode=='10pC' else 'NONE')
 (d/'running.json').write_text(json.dumps(meta,indent=2)+'\n');print('Starting PR bend',mode,flush=True);started=time.monotonic()
 with (d/'track.out').open('w') as f:p=subprocess.run([str(binary),'track.in','--info','4'],cwd=d,env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 meta.update(completed=p.returncode==0,returncode=p.returncode,elapsed_seconds=time.monotonic()-started);(d/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({k:meta[k] for k in ['mode','completed','elapsed_seconds','binary_sha256']}),flush=True);assert p.returncode==0
