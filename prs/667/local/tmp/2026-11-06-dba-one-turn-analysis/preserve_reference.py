from pathlib import Path
import json,hashlib,tarfile,subprocess,shutil
R=Path('/psi/home/adelmann/opalx-dev/dba');O=R/'validation-a100-20261105/one-turn-and-bend';D=O/'dba-one-turn'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
m=json.loads((D/'manifest.json').read_text());assert m['completed'] and sha(O/'opalx')==m['binary_sha256']
assert sha(D/'case.in~')==m['input_sha256']
with tarfile.open(R/'reference-analysis.tar.gz') as t:
 for member in t.getmembers():
  dest=D/member.name
  if dest.exists() and dest.is_file():
   data=t.extractfile(member).read();assert hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(data).digest(),str(dest)
  else:t.extract(member,D,filter='data')
assert sha(D/'reference-input.in')==m['input_sha256']
subprocess.run(['git','-C',str(R),'fetch','origin','codex/fft2d5-explicit-original-model'],check=True)
assert set(subprocess.check_output(['git','-C',str(R),'diff','--name-only'],text=True).splitlines()) <= {'src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp'}
subprocess.run(['git','-C',str(R),'diff','--quiet','origin/codex/fft2d5-explicit-original-model','--','src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp'],check=True)
subprocess.run(['git','-C',str(R),'restore','--source=HEAD','--','src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp'],check=True)
subprocess.run(['git','-C',str(R),'merge','--ff-only','origin/codex/fft2d5-explicit-original-model'],check=True)
assert sha(O/'opalx')==m['binary_sha256']
files=[D/name for name in ['reference-input.in','case.in','case.in~','case.h5','case.stat','case_checkpoint.h5','manifest.json','run.log','timing.dat']]+[O/'opalx',R/'validation-a100-20261105/assets/dba-initial-state.h5',R/'validation-a100-20261105/assets/dba-reference.dat',R/'validation-a100-20261105/assets/dba-particles.txt']
reference=dict(status='Retained one-turn DBA reference; keep this directory and its native outputs in place',source_fix_commit=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),executed_source=m['source_identity'],input_note='case.in was reformatted after completion. reference-input.in and case.in~ reproduce the executed input hash; current case.in is preserved unchanged.',completion=m,analysis='analysis/summary.json; analysis/readme.md',files=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size) for f in files])
(D/'REFERENCE.json').write_text(json.dumps(reference,indent=2)+'\n')
(D/'REFERENCE.md').write_text("""# Retained one-turn DBA reference

Keep this run at its present location. Do not rerun into this directory or overwrite its native outputs. Future comparisons belong in a new directory.

The run completed with job 354991 on one A100, one rank, batch64: 100k particles, 5.602 nC, 64×64×512, 3 ps, 393240 steps over one reference circumference. All IDs and charge are retained. The pinned executable is ../opalx; its full identity and source-fix commit are in REFERENCE.json. No executable was rebuilt or replaced when recording this reference.

Use reference-input.in for the exact executed input. case.in was reformatted after completion; it and its backup are preserved. Native case.h5, case.stat, checkpoint, log and manifest remain untouched. REFERENCE.json provides SHA256 hashes of the native files, executable and supporting inputs.

The matched-KV analysis, plots, frozen model and scripts are in analysis/. Reproduce using OPALX_DBA_H5=../case.h5 and python analysis/analyze.py, followed by analysis/plot.py in a suitable NumPy/SciPy/pandas/h5py/matplotlib environment. Geometry/optics conventions and the limits of the comparison are documented in analysis/readme.md.
""")
with tarfile.open(O/'completed-reference-evidence.tar.gz','w:gz') as t:
 for base in [D,O/'bend-batch64']:
  for f in sorted(base.rglob('*')):
   if f.is_file() and f.suffix in ['.in','.stat','.log','.json','.csv','.md','.py','.npz','.png','.pdf'] and '__pycache__' not in f.parts:t.add(f,arcname=str(f.relative_to(O)))
 for f in [O/'jobs.json',O/'plan.json',O/'source-identity.json',O/'source.patch',O/'run_case.py',O/'analyze_bend.py']:
  t.add(f,arcname=f.name)
print('PRESERVED',D,flush=True);print('SOURCE',reference['source_fix_commit'],flush=True);print('BINARY',sha(O/'opalx'),flush=True)
