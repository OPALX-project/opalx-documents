"""Run the unmodified standard regression driver on an isolated review draft."""
from pathlib import Path
from io import BytesIO
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile

SOURCE = Path('/Users/adelmann/git/opalx-master')
REGRESSION = Path('/Users/adelmann/git/regression-tests-x')
RUNNER = Path('/tmp/pr637-nightlybuildx-20261025')
DRAFT = SOURCE / 'tmp/pr637-ci-iteration-20261025/reference-drafts-a9d38caa'
EVIDENCE = SOURCE / 'tmp/pr637-ci-iteration-20261025/full-local-regression-a9d38caa'
WORK = Path('/tmp/pr637-full-regression-a9d38caa-20261025')
REVISION = 'a9d38caa4f88433a5de1508b3d5c7d01bdfea95a'
REGREV = '737547e6ae38cf3001d6bc45cf38dd1a47d78402'
RUNREV = '5539fa31b56d4952d923e6641557d6683c68725a'
EXEHASH = '68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590'
PATCHHASH = '05b649a08c40f351a048f9b4b051e832a2288032ab19a48d40a35cea9865ea4e'


def git(directory, *args):
    return subprocess.check_output(['git', *args], cwd=directory, text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (EVIDENCE / name).write_text(json.dumps(value, indent=2) + '\n')


assert not WORK.exists(), 'fresh full-suite directory already exists; do not duplicate'
assert git(SOURCE, 'rev-parse', 'HEAD') == REVISION
assert git(RUNNER, 'rev-parse', 'HEAD') == RUNREV
assert git(REGRESSION, 'rev-parse', REGREV) == REGREV
assert digest(DRAFT / 'executable/opalx') == EXEHASH
assert digest(DRAFT / 'combined-reference.patch') == PATCHHASH
assert not git(REGRESSION, 'status', '--porcelain')
EVIDENCE.mkdir(parents=True, exist_ok=True)
WORK.mkdir()
tree = WORK / 'regression-tests-x'
tree.mkdir()
archive = subprocess.check_output(['git', 'archive', '--format=tar', REGREV], cwd=REGRESSION)
with tarfile.open(fileobj=BytesIO(archive)) as stream:
    stream.extractall(tree, filter='data')
originals = {str(p.relative_to(tree)): digest(p) for p in tree.rglob('*') if p.is_file()}
inputs = {name: sha for name, sha in originals.items() if 'reference' not in Path(name).parts}
save('all-source-sha256-before.json', originals)
save('preserved-input-sha256-before.json', inputs)
patch = DRAFT / 'combined-reference.patch'
subprocess.run(['git', 'apply', '--check', str(patch)], cwd=tree, check=True)
subprocess.run(['git', 'apply', str(patch)], cwd=tree, check=True)
changed = [name for name, sha in originals.items() if digest(tree / name) != sha]
assert len(changed) == 12
assert all('reference' in Path(name).parts for name in changed)
assert all(digest(tree / name) == sha for name, sha in inputs.items())
save('applied-reference-paths.json', changed)

exe_dir = WORK / 'executable'
exe_dir.mkdir()
shutil.copy2(DRAFT / 'executable/opalx', exe_dir / 'opalx')
driver = RUNNER / 'scripts/run-reg-tests.py'
sys.path.insert(0, str(driver.parent))
spec = importlib.util.spec_from_file_location('nightly_driver', driver)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
tests = module.scan_for_tests(str(tree / 'RegressionTests'))
expected_comparisons = 0
launchers = {}
for case in tests:
    directory = tree / 'RegressionTests' / case
    local = directory / f'{case}.local'
    text = local.read_text()
    ranks = re.findall(r'mpirun\s+-np\s+(\d+)', text)
    assert ranks and set(ranks) == {'1'}, (case, ranks)
    launchers[case] = {'ranks': 1, 'launcher_sha256': digest(local)}
    rt = directory / f'{case}.rt'
    if rt.exists():
        expected_comparisons += sum(bool(re.match(r'\s*stat\s+"', line.split('#', 1)[0]))
                                    for line in rt.read_text().splitlines()[1:])
    else:
        expected_comparisons += 1
assert expected_comparisons == 401, expected_comparisons
save('enabled-cases.json', launchers)
env = os.environ.copy()
env.update(OMP_NUM_THREADS='1', OMP_PROC_BIND='false', OMP_DYNAMIC='false',
           OPALX_EXE_PATH=str(exe_dir), OPALX_SRC_DIR=str(SOURCE),
           PYTHONUNBUFFERED='1', MPLBACKEND='Agg', MPLCONFIGDIR=str(WORK / 'matplotlib-cache'))
env.pop('REGTEST_WWW', None)
args = ['/Users/adelmann/.venv-h6/bin/python', str(driver),
        '--base-dir', str(tree / 'RegressionTests'), '--opalx-exe-path', str(exe_dir),
        '--timestamp', '2026-10-25-a9d38caa-local', '--no-gpl']
manifest = {'source_revision': REVISION, 'regression_base': REGREV, 'runner_revision': RUNREV,
            'executable_sha256': EXEHASH, 'patch_sha256': PATCHHASH,
            'enabled_simulations': len(tests), 'expected_comparisons': expected_comparisons,
            'MPI_ranks_per_simulation': 1, 'OMP_NUM_THREADS': 1,
            'fresh_work_directory': str(WORK), 'argv': args,
            'external_publication': False,
            'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
save('manifest.json', manifest)
(EVIDENCE / 'run-command.sh').write_text('#!/bin/sh\n' + shlex.join(args) + '\n')
shutil.copy2(__file__, EVIDENCE / 'run_full_local_regression.py')
print(f'Staged exact {REGREV}: {len(tests)} simulations, {expected_comparisons} comparisons; all one rank/OMP1', flush=True)
print('Running unmodified standard driver without publication flags', flush=True)
with (EVIDENCE / 'runner.log').open('w') as log:
    result = subprocess.run(args, cwd=tree, env=env, stdout=log, stderr=subprocess.STDOUT)
manifest['runner_exit'] = result.returncode
manifest['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
log = (EVIDENCE / 'runner.log').read_text()
summary = re.findall(r'Summary:\s*(\d+)\s*/\s*(\d+)\s*tests passed', log)
manifest['reported_passed'] = int(summary[-1][0]) if summary else None
manifest['reported_total'] = int(summary[-1][1]) if summary else None
completions = {}
for case in tests:
    output = tree / 'RegressionTests' / case / f'{case}-RT.o'
    text = output.read_text(errors='replace') if output.exists() else ''
    completions[case] = {'output_exists': output.exists(),
                         'exact_runtime_revision': f'git rev. {REVISION}' in text,
                         'end_of_input': f"End of input stream '{case}.in'" in text}
save('simulation-completions.json', completions)
after = {name: digest(tree / name) if (tree / name).exists() else None for name in inputs}
save('preserved-input-sha256-after.json', after)
manifest['preserved_inputs_unchanged'] = inputs == after
manifest['executable_unchanged'] = digest(exe_dir / 'opalx') == EXEHASH
manifest['maintained_regression_status_after'] = git(REGRESSION, 'status', '--porcelain')
manifest['all_simulations_completed_at_exact_revision'] = all(all(record.values()) for record in completions.values())
save('manifest.json', manifest)
print(json.dumps(manifest, indent=2), flush=True)
assert result.returncode == 0
assert manifest['reported_passed'] == manifest['reported_total'] == expected_comparisons
assert manifest['preserved_inputs_unchanged'] and manifest['executable_unchanged']
assert manifest['all_simulations_completed_at_exact_revision']
assert not manifest['maintained_regression_status_after']
