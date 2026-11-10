"""Run one pinned-executable A100 case, recording provenance and completion checks."""
from pathlib import Path
import sys,subprocess,os,json,hashlib,time,shutil
import numpy as np,h5py
R=Path('/psi/home/adelmann/opalx-dev/dba');S=R/'validation-a100-20261105';O=S/'one-turn-and-bend';plan=json.loads((O/'plan.json').read_text());case=sys.argv[1];assert case in ['dba-one-turn','bend-batch64'];d=O/case;d.mkdir(exist_ok=False);B=O/'opalx'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()
assert sha(B)==plan['binary_sha256'];shutil.copy2(O/(case+'.in'),d/'case.in')
meta=dict(case=case,status='running',binary=str(B),binary_sha256=sha(B),source_identity=json.loads((O/'source-identity.json').read_text()),input_sha256=sha(d/'case.in'),job_id=os.environ['SLURM_JOB_ID'],hostname=subprocess.check_output(['hostname'],text=True).strip(),mpi_ranks=1,batch_size=64,omp_threads=1)
args=['srun','--ntasks=1',str(B),'case.in','--info','1','--2D5BatchSize','64']
if case=='dba-one-turn':args+=['--restart',str(S/'assets/dba-initial-state.h5')];meta.update(plan,particles=100000,mesh=[64,64,512],charge_C=5.602212333965894e-9,longitudinal='NONE: uniform coasting beam',checkpoint_sha256=sha(S/'assets/dba-initial-state.h5'))
else:meta.update(particles=1048576,mesh=[512,512,512],charge_C=1e-11,steps=100,dt_s=3.3356409519815204e-7,longitudinal='OPEN; SCATTERLONGITUDINALLY=TRUE',source_distribution_sha256=sha(S/'assets/bend-source.dist'))
meta['argv']=args;(d/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print('START',case,flush=True);start=time.monotonic()
with (d/'run.log').open('w') as f:r=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT)
meta.update(native_returncode=r.returncode,elapsed_s=time.monotonic()-start,status='native-complete' if r.returncode==0 else 'failed',completed=False)
(d/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');assert r.returncode==0,(case,r.returncode)
try:
 with h5py.File(d/'case.h5') as f:
  keys=sorted(f,key=lambda k:int(k.split('#')[-1]));g=f[keys[-1]];assert len(g['id'])==meta['particles'];assert np.array_equal(np.sort(g['id'][:]),np.arange(meta['particles']));charge=float(g['q'][:].sum());assert abs(charge/meta['charge_C']-1)<1e-10
  assert all(np.isfinite(g[k][:]).all() for k in ['x','y','z','px','py','pz']);t=float(np.asarray(g.attrs['TIME']).flat[0]);s=float(np.asarray(g.attrs['SPOS']).flat[0]);step=int(np.asarray(g.attrs['GlobalTrackStep']).flat[0]);meta.update(final_time_s=t,final_s_m=s,final_global_step=step,retained_snapshots=len(keys),retained_particles=len(g['id']),retained_charge_C=charge)
  if case=='dba-one-turn':assert abs(s-plan['circumference_m'])<1e-4,(s,plan['circumference_m']);assert abs(t/plan['nominal_period_s']-1)<1e-4
  else:assert len(keys)==100;assert abs(t-100*meta['dt_s'])<1e-16
 assert sha(B)==plan['binary_sha256'];meta.update(completed=True,status='complete')
except Exception as e:meta.update(status='validation-failed',validation_error=repr(e));raise
finally:(d/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
print('DONE',json.dumps(meta),flush=True)
