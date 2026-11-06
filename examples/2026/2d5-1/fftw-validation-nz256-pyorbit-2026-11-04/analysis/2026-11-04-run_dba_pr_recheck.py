"""Identical 100-step DBA pilot; explicit OPALX batch size, no full turns."""
from pathlib import Path
import sys,os,json,hashlib,time,subprocess,shutil,argparse
p=argparse.ArgumentParser();p.add_argument('batch',type=int,choices=[0,1,8,32,64]);p.add_argument('repeat',type=int);p.add_argument('--profile',action='store_true');a=p.parse_args()
R=Path(__file__).resolve().parent;O=R/'dba-fftw-pr-recheck';O.mkdir(exist_ok=True);name=f'batch-{a.batch}-{a.repeat}'+('-profile' if a.profile else '');d=O/name;d.mkdir(exist_ok=False)
B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');build=json.loads(Path('/Users/adelmann/git/opalx/tmp/2026-11-04-fftw-threading/build-final.json').read_text());old=R/'dba-sc-feasibility/omp4-100steps';m=json.loads((old/'manifest.json').read_text());initial=R/'dba-sc-feasibility/initial-state.h5'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sha(B)==build['binary_sha256'];assert sha(old/'case.in')==m['input_sha256'];assert sha(initial)==m['initial_state_sha256'];shutil.copy2(old/'case.in',d/'case.in')
env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');env.pop('KOKKOS_TOOLS_LIBS',None);env.pop('KOKKOS_PROFILE_LIBRARY',None)
if a.profile:env.update(KOKKOS_TOOLS_LIBS='/Users/adelmann/git/opalx/build-omp/profiling/fft2d5/libkernel_timer.dylib',OPALX_KERNEL_PROFILE=str(d/'kernel-timings.csv'))
args=[str(B),'case.in','--restart',str(initial),'--info','1']
if a.batch:args+=['--2D5BatchSize',str(a.batch)]
record=dict(case=name,argv=args,batch_size=a.batch,repeat=a.repeat,profile=a.profile,binary_sha256=sha(B),source_head=build['head'],source_diff_sha256=build['source_diff_sha256'],input_sha256=sha(d/'case.in'),initial_state_sha256=sha(initial),mpi_ranks=1,omp_threads=4,steps=100,dt_s=3e-12,charge_C=m['charge_C'],particles=100000,mesh=[64,64,512],scope='100step timing/numerical comparison only; no16turnrun')
(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');t=time.monotonic()
with (d/'run.log').open('w') as log:proc=subprocess.run(args,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
record.update(returncode=proc.returncode,completed=proc.returncode==0,elapsed_seconds=time.monotonic()-t)
assert sha(B)==record['binary_sha256'];(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['case','completed','returncode','elapsed_seconds','binary_sha256']}),flush=True)
if proc.returncode:raise SystemExit(proc.returncode)
if a.batch:assert f'--2D5BatchSize {a.batch}' in (d/'run.log').read_text()
