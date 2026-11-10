"""Archive scoped evidence without large particle dumps or published mutations."""
from pathlib import Path
import json,hashlib,shutil,subprocess
import pandas as pd
R=Path(__file__).resolve().parent;C=Path('/Users/adelmann/git/opalx');REPO=Path('/Users/adelmann/git/opalx-documents');D=REPO/'examples/2026/2d5-1/fftw-validation-nz256-pyorbit-2026-11-04';D.mkdir(exist_ok=True);assert str(D.relative_to(REPO)) not in (REPO/'manifest.yml').read_text();files=[];mapping=[]
def copy(src,relative):
 src=Path(src);target=D/relative;target.parent.mkdir(parents=True,exist_ok=True);target=target.with_name('2026-11-04-'+target.name.lower());shutil.copy2(src,target);files.append(target);mapping.append(dict(source=str(src),destination=str(target.relative_to(D)),sha256=hashlib.sha256(target.read_bytes()).hexdigest()));return target
for folder,names in {
 'dba-fftw-threads':['comparison.csv','comparison.json','stat-comparison.csv','runtime.png','runtime.pdf'],
 'pr-fftw-repeat':['overlay-series.csv','published-retention.csv','published-retention.json','analytic-retention.json','current-vs-published.csv','audit.json','rms-current-vs-pr.png','rms-current-vs-pr.pdf','emittance-current-vs-pr.png','emittance-current-vs-pr.pdf','phase1-complete.json'],
 'dba-fftw-pr-recheck':['comparison.csv','comparison.json','stat-comparison.csv','published-retention.csv'],
 'dba-nz256':['comparison.csv','summary.json'],
 'dba-pyorbit-pilot':['timing-comparison.csv','local-moment-comparison.csv','moment-differences.csv','summary.json','runtime-comparison.png','runtime-comparison.pdf','pilot-comparison.png','pilot-comparison.pdf']}.items():
 for name in names:copy(R/folder/name,str(Path(folder)/name))
for folder in ['dba-fftw-threads','dba-fftw-pr-recheck','dba-nz256']:
 for d in sorted((R/folder).iterdir()):
  if d.is_dir() and (d/'manifest.json').exists() and d.name!='sample':
   for name in ['manifest.json','case.in','run.log']:copy(d/name,f'{folder}/{d.name}/{name}')
for mode in ['ZeroSC','10pC']:
 for name in ['manifest.json','track.in']:copy(R/'pr-fftw-repeat'/mode/name,f'pr-fftw-repeat/{mode.lower()}/{name}')
for d in sorted((R/'dba-pyorbit-pilot').glob('nz-*')):
 for name in ['manifest.json','moments.csv']:copy(d/name,f'dba-pyorbit-pilot/{d.name}/{name}')
for p in sorted((R/'dba-pyorbit-pilot').glob('launch-*')):copy(p,'dba-pyorbit-pilot/'+p.name)
for name in ['cpu-sample.txt','manifest.json']:copy(R/'dba-fftw-threads/sample'/name,'worker-verification/'+name)
for name in ['worker-verification.json','worker-sample-summary.csv','stack-leaves.csv']:copy(R/'dba-fftw-threads'/name,'worker-verification/'+name)
T=C/'tmp/2026-11-04-fftw-threading'
for name in ['build-final.json','ctest-omp1.log','ctest-omp4.log','cli-checks.json','mpi2-rejection-final.log','doxygen-warnings.log','check-final.py','check-cli.py','configure-final.log','build-callback-final.log','pr667.json']:copy(T/name,'provenance/'+name)
patch=D/'provenance/2026-11-04-source.patch';patch.write_bytes(subprocess.check_output(['git','diff','--','src','unit_tests/SpaceCharge'],cwd=C));files.append(patch)
for name in ['run_dba_fftw_threads.py','analyze_dba_fftw_threads.py','plot_fftw_threads.py','run_fft2d5_fftw16_sample.py','analyze_fftw_worker_verification.py','run_pr_fftw_repeat.py','analyze_pr_fftw_repeat.py','plot_pr_fftw_overlay.py','check_pr_fftw_repeat.py','run_dba_pr_recheck.py','analyze_dba_pr_recheck.py','continue_after_pr_fftw.py','run_dba_nz256.py','analyze_dba_nz256.py','pilot_local_coordinates.py','run_pyorbit_dba_pilot.py','launch_pyorbit_dba_pilot.py','analyze_pyorbit_dba_pilot.py','plot_followup_pilot.py','archive_fftw_followup.py']:copy(R/name,'analysis/'+name)
copy(REPO/'examples/2026/2d5-1/analytic_zero_sc.py','analysis/analytic-zero-sc.py')
for name in ['source.json','reference-path.dat']:copy(R/'dba-sc-feasibility'/name,'inputs/'+name)
for name in ['machine.json']:copy(Path('/Users/adelmann/git/dba-lattice/model')/name,'inputs/'+name)
copy(Path('/Users/adelmann/git/dba-lattice/tune-shift-ring/config.json'),'inputs/lattice-config.json')
copy(T/'followup-readme.md','readme.md');copy(T/'final-checks.json','provenance/final-checks.json')
p=D/'2026-11-04-source-map.json';p.write_text(json.dumps(mapping,indent=2)+'\n');files.append(p)
manifest=REPO/'manifest.yml';existing=manifest.read_text()
for p in files:
 relative=str(p.relative_to(REPO));assert relative not in existing
 with manifest.open('a') as f:
  entry=dict(title='FFT2D5 threading and follow-up — '+str(p.relative_to(D)),date='2026-11-04',category='examples/2d5-1',source=str(R),destination=relative,description='Frozen local Release FFTW build; thread study, published PR retention, NZ256 sensitivity and native PyORBIT timing. 100-step scope; no full-turn run.',status='experimental',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  f.write('\n  - '+ '\n    '.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in entry.items())+'\n')
print('ARCHIVED',len(files),'assets at',D)
