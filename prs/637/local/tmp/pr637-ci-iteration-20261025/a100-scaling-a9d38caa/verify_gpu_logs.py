"""Read-only audit of an existing A100 batch-job log copy; never a native unit-test dependency."""
from pathlib import Path
import hashlib
import io
import json
import re
import subprocess
import tarfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent
expected = 'a9d38caa4f88433a5de1508b3d5c7d01bdfea95a'
remote = root / 'remote-logs'
status = (remote / 'status.tsv').read_text()
assert 'ctest\t0' in status and 'two-rank\t0' in status
assert 'phase\tcomplete' in status and 'job-exit\t0' in status
assert expected in (remote / 'source.txt').read_text()

junit = ET.parse(remote / 'junit.xml').getroot()
testcases = list(junit.iter('testcase'))
assert len(testcases) == 6
assert not any(list(test.iter('failure')) or list(test.iter('error')) or list(test.iter('skipped')) for test in testcases)
assert all(test.attrib.get('status', 'run') != 'notrun' for test in testcases)
logs = (remote / 'tests.log').read_text()
assert '[  FAILED  ]' not in logs and '[  SKIPPED ]' not in logs
passed = [int(value) for value in re.findall(r'\[  PASSED  \]\s+(\d+)\s+tests?\.', logs)]
assert len(passed) == 6 and sum(passed) == 64, passed
for name in ['TestMultipoleTStraight.AnalyticFringeFieldsAgreeForParticlesAndReferenceOutsideTheBody',
             'ScalingFFAMagnetTest.SuperposesParticleAndReferenceFieldsWithoutErasingOtherElements']:
    assert re.search(r'\[\s+RUN\s+\]\s+' + re.escape(name), logs), name
    assert re.search(r'\[\s+OK\s+\]\s+' + re.escape(name), logs), name
mpi = (remote / 'two-rank.log').read_text()
name = 'ScalingFFAMagnetTest.SuperposesParticleAndReferenceFieldsWithoutErasingOtherElements'
assert len(re.findall(r'\[\s+RUN\s+\]\s+' + re.escape(name), mpi)) == 2
assert len(re.findall(r'\[\s+OK\s+\]\s+' + re.escape(name), mpi)) == 2
assert '[  FAILED  ]' not in mpi and '[  SKIPPED ]' not in mpi

manifest = {}
for line in (remote / 'source.sha256').read_text().splitlines():
    digest, path = line.split(None, 1)
    manifest[path.strip()] = digest
archive = subprocess.check_output(['git', 'archive', expected, 'src', 'unit_tests', 'CMakeLists.txt', 'ci'], cwd='/Users/adelmann/git/opalx-master')
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    actual = {item.name: hashlib.sha256(tar.extractfile(item).read()).hexdigest()
              for item in tar.getmembers() if item.isfile()}
assert manifest == actual, 'remote tracked source hash manifest differs from exact committed source'
after = (remote / 'source-after-check.txt').read_text().splitlines()
assert len(after) == len(manifest) and all(line.endswith(': OK') for line in after)
report = dict(job=354773, source=expected, junit_targets=6, native_cases=sum(passed),
              target_case_counts=passed, skipped_cases=0, two_rank_new_case_executions=2,
              source_files_verified=len(manifest), expected_source_archive_verified=True,
              source_after_checks_passed=len(after),
              binary_hashes=(remote / 'binaries.sha256').read_text(),
              dependencies_before=(remote / 'dependencies.txt').read_text(),
              note='Slurm terminal state and GPU/backend/cache metadata require separate independent review.')
(root / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
