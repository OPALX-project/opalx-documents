"""Run the unchanged FFA regression with a named master executable and compare."""
from pathlib import Path
from io import StringIO
import hashlib
import json
import os
import re
import shutil
import subprocess

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
EVIDENCE = Path('/Users/adelmann/git/opalx-master/tmp/pr637-ci-iteration-20261025/master-baseline')
EXE = EVIDENCE / 'opalx-master-8c1a862'
CASE = 'ScalingFFABasicPlacements'
BASELINE = '8c1a862369fb05034bb27aa1111d63a7b1e16c02'
CANDIDATE = '23f04f6c8e57f497e6f1a722038f9e1cef010803'


def stat(path):
    text = path.read_text()
    columns = re.findall(r'&column\s+name=(\w+),', text)
    rows = re.split(r'&data\b.*?&end\s*\n', text, flags=re.S)[1].splitlines()
    return pd.read_csv(StringIO('\n'.join(rows[3:])), sep=r'\s+', names=columns)


assert EXE.is_file()
manifest = json.loads((EVIDENCE / 'manifest.json').read_text())
assert manifest['source_revision'] == BASELINE
assert manifest['build_exit'] == 0
assert hashlib.sha256(EXE.read_bytes()).hexdigest() == manifest['executable_sha256']
run = ROOT / 'master-thousand-steps'
shutil.copytree(ROOT / 'pristine' / 'RegressionTests' / CASE, run,
                ignore=shutil.ignore_patterns('reference'))
env = os.environ.copy()
env.update(OMP_NUM_THREADS='1', OMP_PROC_BIND='false')
with (run / 'run.log').open('w') as log:
    result = subprocess.run(['/opt/homebrew/bin/mpirun', '-np', '1', str(EXE),
                             f'{CASE}.in', '--info', '2'], cwd=run, env=env,
                            stdout=log, stderr=subprocess.STDOUT)
result.check_returncode()
log = (run / 'run.log').read_text()
assert f'git rev. {BASELINE}' in log
assert f"End of input stream '{CASE}.in'" in log
master = stat(run / f'{CASE}.stat')
candidate_file = ROOT / 'current-thousand-steps/reference' / f'{CASE}.stat'
candidate = stat(candidate_file)
assert master.columns.equals(candidate.columns)
assert len(master) == len(candidate) == 10
comparison = []
for column in candidate.columns:
    a, b = master[column].to_numpy(), candidate[column].to_numpy()
    finite = np.isfinite(a) & np.isfinite(b)
    special_equal = bool(np.all((a[~finite] == b[~finite]) |
                                (np.isnan(a[~finite]) & np.isnan(b[~finite]))))
    difference = abs(a[finite] - b[finite])
    comparison.append({'column': column,
                       'finite_rows': int(finite.sum()),
                       'nonfinite_values_match': special_equal,
                       'max_absolute_difference': float(difference.max()) if len(difference) else None,
                       'mean_absolute_difference': float(difference.mean()) if len(difference) else None})
frame = pd.DataFrame(comparison).set_index('column')
frame.to_csv(EVIDENCE / 'scaling-master-candidate-differences.csv')
checked = ['mean_x', 'mean_y', 'mean_s']
passes = {column: bool(frame.loc[column, 'max_absolute_difference'] < 1e-4)
          for column in checked}
report = {'baseline_revision': BASELINE, 'baseline_executable_sha256': manifest['executable_sha256'],
          'candidate_revision': CANDIDATE,
          'candidate_executable_sha256': hashlib.sha256((ROOT / 'current-executable/opalx').read_bytes()).hexdigest(),
          'rows': len(master), 'numeric_columns': len(master.columns),
          'numeric_dataframes_identical': master.equals(candidate),
          'existing_avg_1e_minus_4_m_checks_pass_under_stricter_max_absolute_check': passes,
          'master_final_mean_x_m': float(master.mean_x.iloc[-1]),
          'candidate_final_mean_x_m': float(candidate.mean_x.iloc[-1]),
          'master_final_mean_s_m': float(master.mean_s.iloc[-1]),
          'candidate_final_mean_s_m': float(candidate.mean_s.iloc[-1]),
          'limitation': 'Baseline agreement detects pre-existing behavior; it does not establish the physical correctness of the particle/reference separation.'}
(EVIDENCE / 'scaling-comparison.json').write_text(json.dumps(report, indent=2) + '\n')
shutil.copy2(run / 'run.log', EVIDENCE / 'scaling-run.log')
shutil.copy2(run / f'{CASE}.stat', EVIDENCE / 'scaling-baseline.stat')
print(json.dumps(report, indent=2))
assert all(passes.values())
