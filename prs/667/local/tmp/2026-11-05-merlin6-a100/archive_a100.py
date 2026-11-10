"""Store A100 evidence separately from the published CPU reference assets."""
from pathlib import Path
import shutil,json,hashlib
O=Path(__file__).resolve().parent;R=O/'results';REPO=Path('/Users/adelmann/git/opalx-documents');D=REPO/'examples/2026/2d5-1/merlin6-a100-pr667-2026-11-05';D.mkdir(exist_ok=False);files=[];mapping=[]
def copy(source,relative):
 source=Path(source);target=D/relative;target=target.with_name('2026-11-05-'+target.name.lower());target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);files.append(target);mapping.append(dict(source=str(source),destination=str(target.relative_to(D)),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
for name in ['summary.json','analysis-summary.json','run-identity.json','run-summary.json','gpu-series.csv','overlay-series.csv','bend-vs-published.csv','dba-vs-published.csv','dba-stat-comparison.csv','snapshot-audit.csv','rms-a100-vs-pr.png','rms-a100-vs-pr.pdf','emittance-a100-vs-pr.png','emittance-a100-vs-pr.pdf','dba-runtime-a100.png','dba-runtime-a100.pdf']:
 copy(R/name,name)
for p in sorted((R/'runs').rglob('*')):
 if p.is_file() and p.suffix in ['.json','.log','.in']:copy(p,Path('runs')/p.relative_to(R/'runs'))
for name in ['configure.log','build.log','finish-build.log','unit-cuda.patch','binary-before-helper.sha256','unit-individual.json','empty-gdb.log','build-modules.txt','gpus.txt','binary.sha256','ctest-inventory.json','unit-tests.xml','unit-tests.log','unit-tests.exit','scheduler-accounting.txt','build-354963.out','build-354963.err']:
 if (R/name).exists():copy(R/name,Path('provenance')/name)
for p in sorted(R.glob('finish-*.out')):copy(p,Path('provenance')/p.name)
for p in sorted(R.glob('finish-*.err')):copy(p,Path('provenance')/p.name)
for p in sorted(R.glob('diag-*.out')):copy(p,Path('provenance')/p.name)
for p in sorted(R.glob('diag-*.err')):copy(p,Path('provenance')/p.name)
for p in sorted((R/'unit-individual').glob('*.log')):copy(p,Path('unit-individual')/p.name)
for p in sorted(R.glob('repeat-*.out')):copy(p,Path('provenance')/p.name)
for p in sorted(R.glob('repeat-*.err')):copy(p,Path('provenance')/p.name)
for name in ['run_cases.py','analyze_cases.py','emittance_reference.py','diagnose_units.py','analytic_zero_sc.py','staging-manifest.json','pr667.json','published-series.csv','published-dba-timings.csv']:
 copy(O/'payload'/name,Path('analysis')/name)
for name in ['build-a100.sbatch','run-a100.sbatch','finish-a100.sbatch','diagnose-a100.sbatch','plot_a100.py','plot_runtime.py','collect_results.py','archive_a100.py','local-dependencies.json']:
 copy(O/name,Path('analysis')/name)
for p in sorted((O/'payload/inputs').glob('*')):copy(p,Path('inputs')/p.name)
copy(O/'readme.md','readme.md');p=D/'2026-11-05-source-map.json';p.write_text(json.dumps(mapping,indent=2)+'\n');files.append(p)
manifest=REPO/'manifest.yml';existing=manifest.read_text()
for p in files:
 relative=str(p.relative_to(REPO));assert relative not in existing;item=dict(title='PR667 A100 validation — '+str(p.relative_to(D)),date='2026-11-05',category='examples/2d5-1',source='/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105',destination=relative,description='Current committed PR667 branch built Release/CUDA AMPERE80 on Merlin6/Gwendolen; one-rank one-A100 unit and physical benchmark repeats against the published CPU/PyORBIT/analytic references. Host-only batching remains explicitly unavailable.',status='experimental',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 with manifest.open('a') as f:f.write('\n  - '+'\n    '.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in item.items())+'\n')
print('Archived',len(files),'assets at',D)
