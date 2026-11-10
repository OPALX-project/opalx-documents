#!/usr/bin/env python3
"""Explicitly snapshot small free-space study evidence; never run by build.sh.

Large particle distributions, H5 files, binaries and build trees remain at the
native study. Existing historical data directories are never modified.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'data/free-open'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study', type=Path, required=True)
    parser.add_argument('--selection', type=Path, required=True)
    args = parser.parse_args()
    source = args.study.resolve()
    selection = json.loads(args.selection.read_text())
    patterns = [
        '*.md', '*.py', '*.json', '*.log', '*.patch',
        'analysis/*.csv', 'analysis/*.json',
        'analysis/source_quadratures/*.json', 'analysis/source_quadratures/*.csv',
        'analysis/source_quadratures/*.npz',
        'reference/*.md', 'reference/*.py', 'reference/*.csv', 'reference/*.json',
        'design/*.md', 'design/*.py', 'design/*.cpp', 'design/*.csv', 'design/*.json',
        'sources/*.json', 'sources/path*.dat',
        'sources/generators/*.py',
        'runs/*/manifest.json', 'runs/*/tube.in', 'runs/*/tube.out', 'runs/*/tube.stat',
        'runs/*/probes.dist',
        'checks/**/*.json', 'checks/**/*.log', 'checks/**/*.xml',
        'code/**/*.h', 'code/**/*.hpp', 'code/**/*.cpp', 'code/**/CMakeLists.txt',
        'provenance/*.json', 'provenance/*.patch',
        'provenance/source/**/*.h', 'provenance/source/**/*.hpp',
        'provenance/source/**/*.cpp', 'provenance/source/**/CMakeLists.txt',
        'provenance/source/**/*.md', 'provenance/*.md',
        'pipe-control/**/*.json', 'pipe-control/**/*.csv', 'pipe-control/**/*.py',
        'pipe-control/**/*.md', 'pipe-control/**/*.log', 'pipe-control/**/*.out',
        'pipe-control/**/*.in', 'pipe-control/**/*.stat', 'pipe-control/**/LICENSE',
        'pipe-control/provenance/**/*',
        'pipe-control/analysis/*.pdf', 'pipe-control/analysis/*.png',
        'audit-weighted/*.json', 'audit-weighted/*.csv',
        'audit-weighted/*.py', 'audit-weighted/*.md', 'audit-weighted/*.log',
    ]
    paths = sorted({p for pattern in patterns for p in source.glob(pattern)
                    if p.is_file() and p.stat().st_size < 20_000_000})
    for name in selection['cases']:
        manifest = json.loads((source/'runs'/name/'manifest.json').read_text())
        companion = json.loads((source/'runs'/(name+'-probes')/'manifest.json').read_text())
        if manifest.get('returncode') != 0 or companion.get('returncode') != 0:
            raise ValueError(f'Incomplete selected native pair: {name}')
    entries = []
    for original in paths:
        target = DEST / original.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        entries.append(dict(original=str(original),snapshot=str(target.relative_to(ROOT)),sha256=sha(target)))
    target = DEST/'selection.json'
    target.write_text(json.dumps(selection,indent=2)+'\n')
    entries.append(dict(original=str(args.selection.resolve()),snapshot=str(target.relative_to(ROOT)),sha256=sha(target)))
    manifest_path = DEST/'snapshot-provenance.json'
    manifest_path.write_text(json.dumps(dict(
        study=str(source),date='2026-11-02',
        scope='Frozen free-space uniform and triangular curved-tube fields; no tracking accuracy claim',
        exclusions=['large distributions','HDF5 particle data','binaries','compiled packages','build trees'],
        sources=entries),indent=2)+'\n')
    global_path=ROOT/'data/provenance.json'
    provenance=json.loads(global_path.read_text())
    provenance['sources']=[e for e in provenance['sources']
                           if not e['snapshot'].startswith('data/free-open/')]
    provenance['sources'].extend(entries)
    provenance['sources'].append(dict(original='Free-space immutable snapshot manifest',
                                      snapshot=str(manifest_path.relative_to(ROOT)),sha256=sha(manifest_path)))
    global_path.write_text(json.dumps(provenance,indent=2)+'\n')
    print(f'Archived {len(entries)} small free-space evidence files; historical snapshots unchanged.')


if __name__ == '__main__':
    main()
