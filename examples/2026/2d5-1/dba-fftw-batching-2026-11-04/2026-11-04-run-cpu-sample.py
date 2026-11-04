"""Profile the unchanged 100-step SC pilot; no full-turn execution."""
from pathlib import Path
import os,sys,time,json,hashlib,subprocess,shutil
R=Path(__file__).resolve().parent;O=R/'dba-fftw-batching';O.mkdir(exist_ok=True);mode=sys.argv[1];assert mode == 'sample';d=O/mode;d.mkdir(exist_ok=False)
B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');lib=Path('/Users/adelmann/git/opalx/build-omp/profiling/fft2d5/libkernel_timer.dylib');old=R/'dba-sc-feasibility/omp4-100steps';m=json.loads((old/'manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B)=='4d627521ac4f33e2ba54d7e5b605a5fc536a41673b69c58fc28e3b04cb17e1ec';assert sha(old/'case.in')==m['input_sha256'];shutil.copy2(old/'case.in',d/'case.in');initial=R/'dba-sc-feasibility/initial-state.h5';assert sha(initial)==m['initial_state_sha256']
env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');env.pop('KOKKOS_PROFILE_LIBRARY',None);env.pop('KOKKOS_TOOLS_LIBS',None)
if mode=='kernel':env.update(KOKKOS_TOOLS_LIBS=str(lib),OPALX_KERNEL_PROFILE=str(d/'kernel-timings.csv'))
record=dict(mode=mode,batch_size=8,sample_duration_s=7,sample_interval_ms=2,binary=str(B),binary_sha256=sha(B),input_sha256=sha(d/'case.in'),initial_state_sha256=sha(initial),pilot_manifest=m,profiler_library_sha256=sha(lib) if mode=='kernel' else None,scope='100steps only; identical4thread5.602nC100k64x64x5123pspilot; no16turnrun',start_unix_s=time.time());(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
t=time.monotonic()
with (d/'run.log').open('w') as log:
 p=subprocess.Popen([str(B),'case.in','--restart',str(initial),'--info','1','--2D5BatchSize','8'],cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT);(d/'native.pid').write_text(str(p.pid));print('PID',p.pid,flush=True)
 # Trigger sampling after tracking starts, rather than sampling initialization.
 while p.poll() is None and time.monotonic()-t<6:
  if 'Step      0 container' in (d/'run.log').read_text():break
  time.sleep(.05)
 with (d/'sampler.log').open('w') as sampleLog:
  sampler=subprocess.Popen(['/usr/bin/sample',str(p.pid),'7','2','-file',str(d/'cpu-sample.txt')],stdout=sampleLog,stderr=subprocess.STDOUT)
  code=p.wait();native_elapsed=time.monotonic()-t
  sample_code=sampler.wait()
 record.update(sample_returncode=sample_code)
record.update(elapsed_seconds=native_elapsed,completed=code==0,returncode=code);(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
