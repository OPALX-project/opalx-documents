"""Immutable PR667 one-rank A100 repeats; no source patches or full-turn runs."""
from pathlib import Path
import subprocess,os,json,time,hashlib,shutil
import h5py,numpy as np
ROOT=Path('/psi/home/adelmann/opalx-dev/dba');OUT=ROOT/'validation-a100-20261105';B=ROOT/'build/gwendolen-cuda/src/opalx';HEAD='6301c2cab10bf164e6d1ea60de5d0d25cdd0ca8a'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()
assert subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()==HEAD
assert set(subprocess.check_output(['git','-C',str(ROOT),'diff','--name-only'],text=True).splitlines()) <= {'unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp'}
for item in json.loads((OUT/'staging-manifest.json').read_text()):assert sha(OUT/item['relative'])==item['sha256']
identity=dict(branch='codex/fft2d5-explicit-original-model',head=HEAD,binary=str(B),binary_sha256=sha(B),slurm_job_id=os.environ['SLURM_JOB_ID'],cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),mpi_ranks=1,omp_threads=1,backend='CUDA AMPERE80 / cuFFT',hostname=subprocess.check_output(['hostname'],text=True).strip())
identity['unit_test_patch_sha256']=sha(OUT/'unit-cuda.patch')
identity['production_source_clean']=True
identity['driver_sha256']=sha(Path(__file__))
identity['analysis_driver_sha256']=sha(OUT/'analyze_cases.py')
identity['dependencies']={}
for name,relative in [('ippl','_deps/ippl-src'),('kokkos','_deps/ippl-build/_deps/kokkos-src'),('heffte','_deps/ippl-build/_deps/heffte-src'),('h5hut','_deps/h5hut-src')]:
 path=ROOT/'build/gwendolen-cuda'/relative
 identity['dependencies'][name]=dict(sha=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip(),dirty=subprocess.check_output(['git','-C',str(path),'diff','--name-only'],text=True).strip())
assert identity['dependencies']['ippl']['sha']=='d6216553e39dcf4405849c027517cc3401fefee5'
assert identity['dependencies']['heffte']['sha']=='4d8d4597b479d1e4709a2b1b4cd7d8922600045f'
assert identity['dependencies']['kokkos']['sha']=='d9397f95a04a0334d327647e64ab7f1882ca0664'
assert all(not d['dirty'] for d in identity['dependencies'].values())
(OUT/'run-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
rows=[]
def run(name,input_name,repeat,kind,extra=None):
 d=OUT/'runs'/name
 if (d/'manifest.json').exists():
  old=json.loads((d/'manifest.json').read_text())
  assert old['binary_sha256']==identity['binary_sha256'] and old['input_sha256']==sha(OUT/'inputs'/input_name)
  rows.append(old);print('PRESERVED',name,old.get('completed'),old.get('unsupported'),flush=True);return
 d.mkdir(parents=True,exist_ok=False);shutil.copy2(OUT/'inputs'/input_name,d/'case.in');args=['srun','--ntasks=1',str(B),'case.in','--info','1']
 if extra:args+=extra
 record=dict(identity,case=name,input_sha256=sha(d/'case.in'),repeat=repeat,kind=kind,argv=args,steps=100)
 if kind.startswith('dba'):record.update(particles=100000,mesh=[64,64,512],charge_C=5.602212333965894e-9,dt_s=3e-12,checkpoint_sha256=sha(OUT/'assets/dba-initial-state.h5'))
 else:record.update(particles=1048576,mesh=[512,512,512] if '10pC' in name else [8,8,8],charge_C=1e-11,dt_s=3.3356409519815204e-7)
 (d/'running.json').write_text(json.dumps(record,indent=2)+'\n');print('START',name,flush=True);start=time.monotonic()
 with (d/'run.log').open('w') as f:p=subprocess.run(args,cwd=d,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 record.update(returncode=p.returncode,elapsed_seconds=time.monotonic()-start)
 if kind=='dba-batch-availability':
  record['unsupported']= 'Explicit slice batching is currently validated for host execution only.' in (d/'run.log').read_text();record['completed']=False
  assert record['unsupported'],'Expected explicit host-only guard; inspect any different failure'
 else:
  record['completed']=p.returncode==0
  assert record['completed'],f'Native process failed {name}'
  with h5py.File(d/'case.h5') as f:
   expected=1 if kind=='dba' else 100;assert len(f)==expected
   g=f[sorted(f,key=lambda k:int(k.split('#')[-1]))[-1]];assert len(g['id'])==record['particles'];assert np.isfinite(g['px'][:]).all();assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-100*record['dt_s'])<1e-16
 (d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');rows.append(record);(OUT/'run-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print('DONE',name,record['elapsed_seconds'],record.get('unsupported',False),flush=True);assert sha(B)==identity['binary_sha256']
def attempt(*args):
 try:run(*args)
 except Exception as error:
  d=OUT/'runs'/args[0];record=json.loads((d/'running.json').read_text()) if (d/'running.json').exists() else dict(identity,case=args[0]);record.update(completed=False,error=repr(error));(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');rows.append(record);(OUT/'run-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print('FAILED',args[0],repr(error),flush=True)
for mode in ['ZeroSC','10pC']:attempt('bend-'+mode,'bend-'+mode+'.in',1,'bend')
restart=['--restart',str(OUT/'assets/dba-initial-state.h5')]
for repeat in [1,2]:attempt('dba-serial-'+str(repeat),'dba-pilot.in',repeat,'dba',restart)
for batch in [1,8,32,64]:attempt('dba-batch-'+str(batch),'dba-pilot.in',1,'dba-batch-availability',restart+['--2D5BatchSize',str(batch)])
print('ALL CASES FINISHED',flush=True)
