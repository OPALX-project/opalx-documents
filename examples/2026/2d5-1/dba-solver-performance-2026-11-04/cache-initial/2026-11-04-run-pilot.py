"""Run only the unchanged100-step pilot; archive each executable/source identity."""
from pathlib import Path
import sys,os,json,hashlib,time,subprocess,shutil
R=Path('/Users/adelmann/git/dba-lattice/comparison-20261104/unified-current');O=R/'dba-projection-cache';O.mkdir(exist_ok=True);name=sys.argv[1];assert name in ['baseline','optimized-1','optimized-2','optimized-profile'];d=O/name;d.mkdir(exist_ok=False);B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');old=R/'dba-sc-feasibility/omp4-100steps';m=json.loads((old/'manifest.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if name=='baseline':assert sha(B)==m['binary_sha256']
else:assert sha(B)!=m['binary_sha256']
shutil.copy2(old/'case.in',d/'case.in');initial=R/'dba-sc-feasibility/initial-state.h5';assert sha(d/'case.in')==m['input_sha256'];assert sha(initial)==m['initial_state_sha256'];env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');env.pop('KOKKOS_TOOLS_LIBS',None);env.pop('KOKKOS_PROFILE_LIBRARY',None)
if name=='optimized-profile':env.update(KOKKOS_TOOLS_LIBS='/Users/adelmann/git/opalx/build-omp/profiling/fft2d5/libkernel_timer.dylib',OPALX_KERNEL_PROFILE=str(d/'kernel-timings.csv'))
rec=dict(case=name,binary=str(B),binary_sha256=sha(B),source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd='/Users/adelmann/git/opalx',text=True).strip(),source_diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','src'],cwd='/Users/adelmann/git/opalx')).hexdigest(),input_sha256=sha(d/'case.in'),initial_state_sha256=sha(initial),mpi_ranks=1,omp_threads=4,steps=100,dt_s=3e-12,charge_C=m['charge_C'],particles=100000,mesh=[64,64,512],baseline_manifest=m,scope='100stepcomparisononly;no16turnrun');(d/'manifest.json').write_text(json.dumps(rec,indent=2)+'\n');t=time.monotonic()
with (d/'run.log').open('w') as log:p=subprocess.run([str(B),'case.in','--restart',str(initial),'--info','1'],cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
rec.update(returncode=p.returncode,completed=p.returncode==0,elapsed_seconds=time.monotonic()-t);(d/'manifest.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
