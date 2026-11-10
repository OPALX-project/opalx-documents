"""Repeat the straight triangular-pipe side control with the current OPALX binary.

This is a local conducting-pipe model control, independent of the curved
free-space acceptance study. Existing results and source artifacts are retained.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import re


HERE = Path(__file__).resolve().parent
STUDY = Path('/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe')
BINARY = HERE.parent / 'binaries/opalx-final-70383ff72345d869'
PYTHON = '/Users/adelmann/.venv-h6/bin/python'
sys.path.insert(0, str(STUDY / 'opalx'))
from run_opalx import run


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            result.update(block)
    return result.hexdigest()


def native():
    run('pipe256-final703', (256, 256, 256), STUDY / 'common/triangle-ns16384-nr16-np32.json',
        .020, 'CIRCULAR_UNIFORM', .020, HERE / 'opalx/runs', BINARY)


def wall():
    fixture = Path('/Users/adelmann/git/regression-tests-x/RegressionTests/FFT2D5-TriangularPipe')
    cfg = json.loads((fixture / 'physics_config.json').read_text())
    original = (fixture / 'FFT2D5-TriangularPipe.in').read_text()
    for companion in (False, True):
        directory = HERE / 'wall-final703' / ('probes' if companion else 'full')
        directory.mkdir(parents=True, exist_ok=True)
        if (directory / 'manifest.json').exists():
            raise FileExistsError(directory)
        dist = fixture / 'triangle.dist'
        count = cfg['expected_particles']
        if companion:
            dist = directory / 'probes.dist'
            count = cfg['probe_particles']
            source = (fixture / 'triangle.dist').read_text().splitlines()
            dist.write_text(str(count) + '\n' + '\n'.join(source[1:2] + source[-count:]) + '\n')
        charge = count * cfg['macrocharge_C']
        text = original.replace('FNAME="triangle.dist"', f'FNAME="{dist}"')
        text = text.replace('REFPATHFNAME="reference_path.dat"',
                            f'REFPATHFNAME="{fixture / "reference_path.dat"}"')
        text = re.sub(r'NPARTDIST=\d+', f'NPARTDIST={count}', text)
        text = re.sub(r'NALLOC=\d+', f'NALLOC={count}', text)
        text = re.sub(r'BCHARGE=[0-9.e+-]+', f'BCHARGE={charge:.17g}', text)
        (directory / 'triangle.in').write_text(text)
        start = time.monotonic()
        argv = [str(BINARY), 'triangle.in', '--info', '4']
        with (directory / 'triangle.out').open('w') as stream:
            result = subprocess.run(argv, cwd=directory,
                env={**os.environ, 'OMP_NUM_THREADS': '2', 'OMP_PROC_BIND': 'false'},
                stdout=stream, stderr=subprocess.STDOUT)
        record = dict(argv=argv, companion=companion, returncode=result.returncode,
                      elapsed_s=time.monotonic()-start, expected_particles=count,
                      charge_C=charge, config=cfg, binary=str(BINARY), binary_sha256=digest(BINARY),
                      input_sha256=digest(directory/'triangle.in'), distribution=str(dist),
                      distribution_sha256=digest(dist), h5=str(directory/'triangle.h5'),
                      probe_input=str(fixture/'probes.csv'), probe_sha256=digest(fixture/'probes.csv'),
                      reference_path=str(fixture/'reference_path.dat'),
                      reference_path_sha256=digest(fixture/'reference_path.dat'))
        (directory / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
        print(directory.name, result.returncode, record['elapsed_s'], flush=True)
        if result.returncode:
            raise RuntimeError(str(directory/'triangle.out'))


def pyorbit():
    package = STUDY / 'pyorbit/native-package'
    env = {**os.environ, 'PYTHONPATH': str(package), 'OMP_NUM_THREADS': '1', 'OMP_PROC_BIND': 'false'}
    for model, nx, nz, source in [
        ('slice', 512, 128, 'triangle-ns8192-nr32-np64.npz'),
        ('rb', 128, 256, 'triangle-ns65536-nr16-np32.npz'),
    ]:
        for ranks in (1, 2):
            name = f'{model}-r{ranks}'
            directory = HERE / 'pyorbit/runs' / name
            if (directory / 'launch.json').exists():
                old = json.loads((directory / 'launch.json').read_text())
                if old['returncode'] != 0:
                    raise RuntimeError('Failed case exists: ' + name)
                continue
            directory.mkdir(parents=True, exist_ok=True)
            argv = [PYTHON, str(STUDY / 'pyorbit/run_native.py'),
                    '--source', str(STUDY / 'common' / source),
                    '--probes', str(STUDY / 'common/probes.csv'), '--out', str(directory),
                    '--nx', str(nx), '--nz', str(nz), '--model', model]
            if ranks > 1:
                argv = ['mpirun', '--oversubscribe', '--map-by', 'slot', '--bind-to', 'none',
                        '-n', str(ranks)] + argv
            start = time.monotonic()
            with (directory / 'run.log').open('w') as log:
                result = subprocess.run(argv, cwd=HERE, env=env, stdout=log, stderr=subprocess.STDOUT)
            record = dict(argv=argv, returncode=result.returncode, elapsed_s=time.monotonic()-start,
                          env={key: env[key] for key in ['PYTHONPATH', 'OMP_NUM_THREADS', 'OMP_PROC_BIND']},
                          harness_sha256=digest(STUDY / 'pyorbit/run_native.py'),
                          launcher_sha256=digest(__file__),
                          source_sha256=digest(STUDY / 'common' / source))
            (directory / 'launch.json').write_text(json.dumps(record, indent=2) + '\n')
            print(name, result.returncode, record['elapsed_s'], flush=True)
            if result.returncode:
                raise RuntimeError(str(directory / 'run.log'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['native', 'pyorbit', 'wall'])
    args = parser.parse_args()
    globals()[args.stage]()


if __name__ == '__main__':
    main()
