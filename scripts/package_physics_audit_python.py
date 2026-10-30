#!/usr/bin/env python3
"""Archive recovered Python source without importing or executing it."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def build(source, destination):
    patterns = [
        'sandbox/cyclotron/report_acceleration590.py',
        'sandbox/cyclotron/compare_cof_energies.py',
        'sandbox/map-2/*.py',
        'sandbox/map-2/dba/*.py',
        'sandbox/map-3/dba/*.py',
        'sandbox/map-3/ring/*.py',
        'sandbox/Regression-Tests/dba-ring-cof/*.py',
        'sandbox/Regression-Tests/dba-ring-cof/reference_models/*.py',
    ]
    paths = sorted({p for pattern in patterns for p in source.glob(pattern) if p.is_file()})
    if not paths:
        raise ValueError('No Python sources found')
    payloads = {p.relative_to(source).as_posix(): p.read_bytes() for p in paths}
    manifest = {
        'packaged_on': '2026-10-30',
        'source_checkout': 'old-opal/opalx',
        'scope': 'Physics Manual chapters 28–35 sandbox Python source',
        'validation': 'File copying and SHA-256 comparison only; recovered scripts were not executed.',
        'files': [{'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
                  for name, data in payloads.items()],
    }
    payloads['SOURCE-MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    payloads['README.txt'] = (
        'Physics Manual chapters 28–35: recovered sandbox Python sources\n'
        'Packaged 2026-10-30 from old-opal/opalx. Original relative paths retained.\n\n'
        'Includes the five explicitly named Python scripts and maintained map-2,\n'
        'map-3 and DBA-ring Python helpers/tests in the referenced study directories.\n'
        'Generated ElementPositions.py files and duplicate archived source snapshots\n'
        'are excluded. Inputs, maps, result data, logs, figures and executables are\n'
        'not included. This is a Python-source archive, not a complete reproducer.\n\n'
        'Files are unchanged. No recovered script was imported, executed or tested.\n'
        'Some scripts depend on local installations, original inputs, source trees\n'
        'and archived results. No portability or current-version compatibility is claimed.\n'
        'SOURCE-MANIFEST.json records each Python file and its SHA-256 digest.\n'
        'COPYING contains the source checkout license; retain individual file notices.\n'
    ).encode()
    license_path = source / 'LICENSE'
    if not license_path.is_file():
        raise FileNotFoundError(license_path)
    payloads['COPYING'] = license_path.read_bytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as archive:
                for name, data in sorted(payloads.items()):
                    info = tarfile.TarInfo('physics-audit-python/' + name)
                    info.size = len(data)
                    info.mode = 0o644
                    archive.addfile(info, io.BytesIO(data))
    # Verify archived bytes against the source; do not execute recovered Python.
    with tarfile.open(destination) as archive:
        for record in manifest['files']:
            data = archive.extractfile('physics-audit-python/' + record['path']).read()
            if hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError('Archive hash mismatch: ' + record['path'])
    print(f'{len(paths)} Python files; archive SHA-256 {hashlib.sha256(destination.read_bytes()).hexdigest()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    build(args.source.resolve(), args.destination.resolve())
