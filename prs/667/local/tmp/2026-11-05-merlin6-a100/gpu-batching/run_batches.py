"""Matched single-rank GPU batch measurements; raw traces remain on Merlin6."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time,shutil
import numpy as np,h5py
R=Path('/psi/home/adelmann/opalx-dev/dba');S=R/'validation-a100-20261105';O=S/'gpu-batching';B=R/'build/gwendolen-cuda/src/opalx';OLD=B.with_name('opalx.pre-gpu-batching-6301c2c')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(OLD)=='5457c6bd1197b5151a95e295936234e148d7263eb6d5dc99690408609334c17e'
identity=dict(head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(B),preserved_binary_sha256=sha(OLD),source_patch_sha256=sha(O/'source.patch'),job_id=os.environ['SLURM_JOB_ID'],mpi_ranks=1,omp_threads=1,hostname=subprocess.check_output(['hostname'],text=True).strip(),input_sha256=sha(S/'inputs/dba-pilot.in'),checkpoint_sha256=sha(S/'assets/dba-initial-state.h5'))
for dep in ['ippl','heffte','kokkos']:
 p=R/'build/gwendolen-cuda/_deps'/('ippl-src' if dep=='ippl' else f'ippl-build/_deps/{dep}-src')
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'],text=True).strip()
 identity[dep+'_sha']=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
(O/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
def endpoint(p):
 with h5py.File(p) as f:
  assert len(f)==1;g=f[next(iter(f))];idx=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][idx],np.arange(100000));assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99
  assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-22
  arrays={k:g[k][:][idx] for k in ['x','y','z','px','py','pz','q']}
  assert all(np.isfinite(a).all() for a in arrays.values());return arrays
reference=endpoint(S/'runs/dba-serial-1/case.h5')
rows=[]
def run(batch,repeat,profile=False):
 name=f'batch-{batch}-'+('profile' if profile else f'repeat-{repeat}');d=O/name
 if (d/'manifest.json').exists():
  m=json.loads((d/'manifest.json').read_text());assert m['binary_sha256']==identity['binary_sha256'];rows.append(m);return
 d.mkdir(exist_ok=True);shutil.copy2(S/'inputs/dba-pilot.in',d/'case.in')
 args=['srun','--ntasks=1']
 if profile:args+=['nsys','profile','--trace=cuda,nvtx','--sample=none','--cpuctxsw=none','--force-overwrite=true','--output='+str(d/'trace')]
 args +=[str(B),'case.in','--info','1','--restart',str(S/'assets/dba-initial-state.h5')]
 if batch:args+=['--2D5BatchSize',str(batch)]
 print('START',name,flush=True);start=time.monotonic()
 with (d/'run.log').open('w') as f:r=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode);elapsed=time.monotonic()-start;got=endpoint(d/'case.h5')
 errors={k:float(abs(got[k]-reference[k]).max()) for k in got};assert errors['q']==0
 assert max(errors[k] for k in ['x','y','z'])<1e-9,errors
 assert max(errors[k] for k in ['px','py','pz'])<1e-10,errors
 text=(d/'run.log').read_text();main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',text)[1]);orbit=float(re.search(r'Timings> OrbThreader\.+ Wall max =\s*([\d.eE+-]+)',text)[1])
 m=dict(identity,batch=batch,repeat=repeat,profile=profile,elapsed_s=elapsed,main_s=main,orbit_s=orbit,tracking_s=main-orbit,errors=errors,argv=args)
 if profile:
  with (d/'stats.log').open('w') as f:r=subprocess.run(['nsys','stats','--report','cuda_gpu_kern_sum,cuda_api_sum,cuda_gpu_mem_time_sum','--format','csv','--output',str(d/'stats'),str(d/'trace.nsys-rep')],stdout=f,stderr=subprocess.STDOUT)
  assert r.returncode==0
 assert sha(B)==identity['binary_sha256'];(d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');rows.append(m);(O/'measurements.json').write_text(json.dumps(rows,indent=2)+'\n');print('DONE',name,'wall',elapsed,'tracking',main-orbit,'errors',errors,flush=True)
# Interleave batch order between repetitions to avoid a monotonic warm-up bias.
for b in [0,1,8,32,64]:run(b,1)
for b in [64,32,8,1,0]:run(b,2)
for b in [1,8,32,64]:run(b,1,True)
