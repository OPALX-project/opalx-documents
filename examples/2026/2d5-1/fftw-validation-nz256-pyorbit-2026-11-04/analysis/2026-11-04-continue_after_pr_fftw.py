"""Sequential gate after fine PR repeat; no long-turn campaign."""
from pathlib import Path
import subprocess,json,time
R=Path(__file__).resolve().parent;P='/Users/adelmann/.venv-h6/bin/python'
def run(name,*args):subprocess.run([P,str(R/name),*map(str,args)],check=True)
while not (R/'pr-fftw-repeat/10pC/manifest.json').exists():time.sleep(10)
assert json.loads((R/'pr-fftw-repeat/10pC/manifest.json').read_text())['completed']
if not (R/'pr-fftw-repeat/published-retention.json').exists():
 run('analyze_pr_fftw_repeat.py');run('plot_pr_fftw_overlay.py');run('check_pr_fftw_repeat.py')
for n in [0,1,8,32,64]:
 if not (R/f'dba-fftw-pr-recheck/batch-{n}-1/manifest.json').exists():run('run_dba_pr_recheck.py',n,1)
 run('analyze_dba_pr_recheck.py')
# Published batch output consistency in addition to within-current equivalence.
namespace={'__file__':str(R/'analyze_dba_fftw_threads.py')};exec((R/'analyze_dba_fftw_threads.py').read_text().split('baseline=O/')[0],namespace)
import numpy as np,pandas as pd
rows=[]
for n in [0,1,8,32,64]:
 new=R/f'dba-fftw-pr-recheck/batch-{n}-1';old=R/f'dba-fftw-batching/batch-{n}-1';ar,ap,_=namespace['endpoint'](old/'case.h5');br,bp,_=namespace['endpoint'](new/'case.h5');aa=namespace['stat'](old/'case.stat');bb=namespace['stat'](new/'case.stat');rel=max(float(abs(aa[c]-bb[c]).max()/abs(aa[c]).max()) for c in aa if c.startswith(('rms_','emit_')));assert rel<1e-8;assert np.max(np.linalg.norm(br-ar,axis=1))<1e-9;assert np.max(np.linalg.norm(bp-ap,axis=1))<1e-10
 rows.append(dict(batch=n,max_stat_relative=rel,max_position_difference_m=float(np.max(np.linalg.norm(br-ar,axis=1))),max_momentum_difference_betagamma=float(np.max(np.linalg.norm(bp-ap,axis=1)))))
pd.DataFrame(rows).to_csv(R/'dba-fftw-pr-recheck/published-retention.csv',index=False)
(R/'pr-fftw-repeat/phase1-complete.json').write_text(json.dumps(dict(passed=True,physical_benchmark=True,batch_matrix=True,unit_tests_omp1_omp4=True,notes='Published references preserved. No16turns.'),indent=2)+'\n');print('PHASE1 COMPLETE',flush=True)
for repeat in [1,2]:run('run_dba_nz256.py',repeat);run('analyze_dba_nz256.py')
print('PHASE2 COMPLETE; PyORBIT ready for separate launch',flush=True)
