#!/usr/bin/env python3
"""Read the complete CSCS matrix for an exact OPALX commit; never start jobs."""
import argparse
import concurrent.futures
import datetime
import json
from pathlib import Path
import urllib.parse
import urllib.request

TARGETS = {
    'GH200': (82981356, 'cuda13-sm90', 'cuda13-sm90'),
    'OpenMP': (83034039, 'openmp', 'openmp'),
    'MI300': (83033814, 'rocm6_3', 'rocm6_3-mi300'),
}


def get_json(path):
    request = urllib.request.Request('https://gitlab.com/api/v4/' + path,
                                     headers={'User-Agent': 'OPALX-CI-diagnostics'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def inspect_target(item, sha):
    label, (project, stem, regression_stem) = item
    query = urllib.parse.urlencode({'sha': sha, 'ref': '__CSCSCI__pr637', 'per_page': 100})
    pipelines = get_json(f'projects/{project}/pipelines?{query}')
    real = [p for p in pipelines if p['status'] != 'skipped']
    if not real:
        return {'backend': label, 'state': 'awaiting-pipeline', 'sha': sha, 'jobs': []}
    selected = max(real, key=lambda p: p['id'])
    metadata = get_json(f"projects/{project}/pipelines/{selected['id']}")
    if metadata['sha'] != sha:
        raise RuntimeError(f'{label}: unexpected pipeline revision {metadata["sha"]}')
    jobs = get_json(f"projects/{project}/pipelines/{selected['id']}/jobs?per_page=100")
    expected = {
        f'opalx-build-{stem}-debug', f'opalx-build-{stem}-release',
        f'opalx-test-{stem}-debug-1-rank', f'opalx-test-{stem}-release-1-rank',
        f'opalx-test-{stem}-release-4-ranks',
        f'opalx-regression-{regression_stem}-release',
    }
    names = {j['name'] for j in jobs}
    summary = [{k: j.get(k) for k in ('id', 'name', 'stage', 'status', 'failure_reason', 'web_url')}
               for j in sorted(jobs, key=lambda j: j['name'])]
    complete = (names == expected and metadata['status'] == 'success'
                and all(j['status'] == 'success' for j in jobs))
    return {'backend': label, 'project_id': project, 'pipeline_id': selected['id'],
            'sha': metadata['sha'], 'pipeline_status': metadata['status'],
            'web_url': metadata['web_url'], 'missing_jobs': sorted(expected - names),
            'unexpected_jobs': sorted(names - expected), 'complete': complete, 'jobs': summary}


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('sha')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if len(args.sha) != 40 or any(c not in '0123456789abcdef' for c in args.sha):
    parser.error('provide the full lowercase commit SHA')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    rows = list(pool.map(lambda item: inspect_target(item, args.sha), TARGETS.items()))
report = {'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'sha': args.sha, 'complete': all(row.get('complete', False) for row in rows),
          'pipelines': rows}
args.output.write_text(json.dumps(report, indent=2) + '\n')
for row in rows:
    counts = {}
    for job in row['jobs']:
        counts[job['status']] = counts.get(job['status'], 0) + 1
    print(row['backend'], row.get('pipeline_id'), row.get('pipeline_status', row.get('state')), counts)
    for job in row['jobs']:
        if job['status'] in {'failed', 'canceled', 'skipped', 'manual'}:
            print(' ', job['name'], job['status'], job['web_url'])
    if row.get('missing_jobs') or row.get('unexpected_jobs'):
        print('  JOB INVENTORY MISMATCH:', row.get('missing_jobs'), row.get('unexpected_jobs'))
print('All CSCS gates verified:', report['complete'])
