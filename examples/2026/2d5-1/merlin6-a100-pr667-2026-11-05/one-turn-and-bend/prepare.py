from pathlib import Path
import hashlib,subprocess,json,shutil,tarfile
R=Path('/psi/home/adelmann/opalx-dev/dba');O=R/'validation-a100-20261105/one-turn-and-bend';O.mkdir(exist_ok=False)
with tarfile.open(R/'one-turn-and-bend.tar') as t:t.extractall(O,filter='data')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
B=R/'build/gwendolen-cuda/src/opalx';assert sha(B)==json.loads((O/'plan.json').read_text())['binary_sha256']
assert set(subprocess.check_output(['git','-C',str(R),'diff','--name-only'],text=True).splitlines())=={'src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp'}
shutil.copy2(B,O/'opalx');(O/'opalx').chmod(0o555)
patch=subprocess.check_output(['git','-C',str(R),'diff','--binary'],text=True);(O/'source.patch').write_text(patch)
identity=dict(head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(B),source_patch_sha256=sha(O/'source.patch'),uncommitted_fix='Named occupancy functor; validated CUDA launch fix',dependencies={})
for dep in ['ippl','heffte','kokkos']:
 p=R/'build/gwendolen-cuda/_deps'/('ippl-src' if dep=='ippl' else f'ippl-build/_deps/{dep}-src');assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'],text=True).strip();identity['dependencies'][dep]=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
(O/'source-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
jobs={}
for case in ['dba-one-turn','bend-batch64']:
 result=subprocess.check_output(['sbatch','--parsable',str(O/(case+'.sbatch'))],text=True).strip();jobs[case]=result;print(case,result,flush=True);(O/'jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
