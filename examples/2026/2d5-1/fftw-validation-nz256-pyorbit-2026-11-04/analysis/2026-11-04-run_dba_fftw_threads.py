"""100-step FFT2D5 FFTW-thread study: batch8, Kokkos/OpenMP4, one frozen binary."""
from pathlib import Path
import os,json,hashlib,time,subprocess,shutil,argparse
p=argparse.ArgumentParser();p.add_argument('threads',type=int,choices=[1,4,16]);p.add_argument('repeat',type=int);a=p.parse_args()
R=Path(__file__).resolve().parent;O=R/'dba-fftw-threads';O.mkdir(exist_ok=True);name=f'fftw-{a.threads}-{a.repeat}';d=O/name;d.mkdir(exist_ok=False)
B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');build=json.loads(Path('/Users/adelmann/git/opalx/tmp/2026-11-04-fftw-threading/build-final.json').read_text());old=R/'dba-sc-feasibility/omp4-100steps';m=json.loads((old/'manifest.json').read_text());initial=R/'dba-sc-feasibility/initial-state.h5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(B)==build['binary_sha256'];assert sha(old/'case.in')==m['input_sha256'];assert sha(initial)==m['initial_state_sha256'];shutil.copy2(old/'case.in',d/'case.in')
env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');env.pop('KOKKOS_TOOLS_LIBS',None);env.pop('KOKKOS_PROFILE_LIBRARY',None)
args=[str(B),'case.in','--restart',str(initial),'--info','1','--2D5BatchSize','8','--2D5FFTThreads',str(a.threads)]
record=dict(case=name,profile=False,argv=args,fftw_threads=a.threads,omp_threads=4,batch_size=8,repeat=a.repeat,binary_sha256=sha(B),source_head=build['head'],source_diff_sha256=build['source_diff_sha256'],input_sha256=sha(d/'case.in'),initial_state_sha256=sha(initial),mpi_ranks=1,steps=100,dt_s=3e-12,particles=100000,mesh=[64,64,512],charge_C=m['charge_C'],scope='100step FFTW planner-limit study only; Kokkos4 fixed; no16turnrun')
(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');t=time.monotonic()
with (d/'run.log').open('w') as log:proc=subprocess.run(args,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
record.update(completed=proc.returncode==0,returncode=proc.returncode,elapsed_seconds=time.monotonic()-t);(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['case','completed','returncode','elapsed_seconds']}),flush=True)
assert proc.returncode==0;assert sha(B)==record['binary_sha256'];log=(d/'run.log').read_text();assert f'FFTW planner maximum threads {a.threads}' in log;assert 'OpenMP max threads: 4; dynamic teams: 0' in log and 'Kokkos host concurrency: 4' in log
