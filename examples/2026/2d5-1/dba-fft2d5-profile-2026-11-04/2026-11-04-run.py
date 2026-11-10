"""Profile the unchanged 100-step SC pilot; no full-turn execution."""
from pathlib import Path
import os,sys,time,json,hashlib,subprocess,shutil
R=Path('/Users/adelmann/git/dba-lattice/comparison-20261104/unified-current');O=R/'dba-fft2d5-profile';O.mkdir(exist_ok=True);mode=sys.argv[1];assert mode in ['kernel','sample'];d=O/mode;d.mkdir(exist_ok=False)
B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');lib=Path('/Users/adelmann/git/opalx/build-omp/profiling/fft2d5/libkernel_timer.dylib');old=R/'dba-sc-feasibility/omp4-100steps';m=json.loads((old/'manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B)==m['binary_sha256'];assert sha(old/'case.in')==m['input_sha256'];shutil.copy2(old/'case.in',d/'case.in');initial=R/'dba-sc-feasibility/initial-state.h5';assert sha(initial)==m['initial_state_sha256']
env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');env.pop('KOKKOS_PROFILE_LIBRARY',None);env.pop('KOKKOS_TOOLS_LIBS',None)
if mode=='kernel':env.update(KOKKOS_TOOLS_LIBS=str(lib),OPALX_KERNEL_PROFILE=str(d/'kernel-timings.csv'))
record=dict(mode=mode,binary=str(B),binary_sha256=sha(B),input_sha256=sha(d/'case.in'),initial_state_sha256=sha(initial),pilot_manifest=m,profiler_library_sha256=sha(lib) if mode=='kernel' else None,scope='100steps only; identical4thread5.602nC100k64x64x5123pspilot; no16turnrun',start_unix_s=time.time());(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
t=time.monotonic()
with (d/'run.log').open('w') as log:
 p=subprocess.Popen([str(B),'case.in','--restart',str(initial),'--info','1'],cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT);(d/'native.pid').write_text(str(p.pid));print('PID',p.pid,flush=True);code=p.wait()
record.update(elapsed_seconds=time.monotonic()-t,completed=code==0,returncode=code);(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
