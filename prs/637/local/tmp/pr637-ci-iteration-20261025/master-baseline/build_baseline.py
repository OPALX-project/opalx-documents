from pathlib import Path
import datetime
import hashlib
import json
import shlex
import shutil
import subprocess
import sys

source = Path('/Users/adelmann/.codex/worktrees/pr637-master-baseline/opalx')
build = source / 'build_openmp'
main_deps = Path('/Users/adelmann/git/opalx-master/build_openmp/_deps')
evidence = Path('/Users/adelmann/git/opalx-master/tmp/pr637-ci-iteration-20261025/master-baseline')
expected = '8c1a862369fb05034bb27aa1111d63a7b1e16c02'
evidence.mkdir(parents=True, exist_ok=True)

def command(args, cwd):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()

def tree_hash(path):
    digest = hashlib.sha256()
    for file in sorted(path.rglob('*')):
        if file.is_file() and '.git' not in file.relative_to(path).parts:
            digest.update(str(file.relative_to(path)).encode() + b'\0')
            digest.update(hashlib.sha256(file.read_bytes()).digest())
    return digest.hexdigest()

assert command(['git', 'rev-parse', 'HEAD'], source) == expected
assert not command(['git', 'status', '--porcelain', '--untracked-files=no'], source)
paths = {
    'IPPL': main_deps / 'ippl-src',
    'H5HUT': main_deps / 'h5hut-src',
    'HDF5': main_deps / 'hdf5-src',
    'OPALX_LAPACK': main_deps / 'opalx_lapack-src',
    'KOKKOS': main_deps / 'ippl-build/_deps/kokkos-src',
    'HEFFTE': main_deps / 'ippl-build/_deps/heffte-src',
}
manifest = {'source_revision': expected, 'dependencies': {}, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
for name, path in paths.items():
    record = {'source': str(path)}
    if (path / '.git').exists():
        record['revision'] = command(['git', 'rev-parse', 'HEAD'], path)
        record['status_before'] = command(['git', 'status', '--porcelain'], path)
        assert not record['status_before'], (name, record['status_before'])
    else:
        record['tree_sha256_before'] = tree_hash(path)
    manifest['dependencies'][name] = record
(evidence / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

args = [shutil.which('cmake'), '-S', str(source), '-B', str(build), '-G', 'Unix Makefiles',
        '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_C_COMPILER=/opt/homebrew/opt/llvm@21/bin/clang',
        '-DCMAKE_CXX_COMPILER=/opt/homebrew/opt/llvm@21/bin/clang++',
        '-DCMAKE_Fortran_COMPILER=/opt/homebrew/bin/gfortran',
        '-DPLATFORMS=OPENMP', '-DBUILD_SHARED_LIBS=OFF', '-DBUILD_TESTING=OFF',
        '-DOPALX_ENABLE_UNIT_TESTS=OFF', '-DOPALX_ENABLE_TESTS=OFF', '-DOPALX_ENABLE_EXAMPLES=OFF',
        '-DOPALX_USE_STANDARD_FOLDERS=OFF', '-DOPALX_EMBED_BUILD_METADATA=OFF', '-DIPPL_EMBED_BUILD_METADATA=OFF',
        '-DIPPL_ENABLE_TESTS=OFF', '-DIPPL_ENABLE_UNIT_TESTS=OFF', '-DIPPL_ENABLE_ALPINE=OFF',
        '-DIPPL_OPENMP_THREADS=2', '-DKokkos_ENABLE_SERIAL=OFF', '-DKokkos_ENABLE_DEBUG_BOUNDS_CHECK=OFF',
        '-DKokkos_VERSION=git.' + manifest['dependencies']['KOKKOS']['revision'],
        '-DHeffte_VERSION=git.' + manifest['dependencies']['HEFFTE']['revision'],
        '-DIPPL_GIT_TAG=' + manifest['dependencies']['IPPL']['revision'],
        '-DOpenMP_ROOT=/opt/homebrew/opt/libomp', '-DOpenMP_C_FLAGS=-fopenmp=libomp',
        '-DOpenMP_CXX_FLAGS=-fopenmp=libomp', '-DOpenMP_C_LIB_NAMES=libomp', '-DOpenMP_CXX_LIB_NAMES=libomp',
        '-DOpenMP_C_INCLUDE_DIR=/opt/homebrew/opt/libomp/include',
        '-DOpenMP_CXX_INCLUDE_DIR=/opt/homebrew/opt/libomp/include',
        '-DOpenMP_libomp_LIBRARY=/opt/homebrew/opt/libomp/lib/libomp.dylib',
        '-DFETCHCONTENT_FULLY_DISCONNECTED=ON', '-DFETCHCONTENT_UPDATES_DISCONNECTED=ON']
args += [f'-DFETCHCONTENT_SOURCE_DIR_{name}={path}' for name, path in paths.items()]
(evidence / 'configure-command.sh').write_text('#!/bin/sh\n' + shlex.join(args) + '\n')
print('Configuring exact clean master baseline ' + expected, flush=True)
with (evidence / 'configure.log').open('w') as log:
    result = subprocess.run(args, cwd=source, stdout=log, stderr=subprocess.STDOUT)
manifest['configure_exit'] = result.returncode
(evidence / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Configure exit ' + str(result.returncode), flush=True)
result.check_returncode()
shutil.copy2(build / 'CMakeCache.txt', evidence / 'CMakeCache.txt')
build_args = [shutil.which('cmake'), '--build', str(build), '--target', 'opalx_exe', '--parallel', '6']
(evidence / 'build-command.sh').write_text('#!/bin/sh\n' + shlex.join(build_args) + '\n')
print('Building executable only with six workers', flush=True)
with (evidence / 'build.log').open('w') as log:
    result = subprocess.run(build_args, cwd=source, stdout=log, stderr=subprocess.STDOUT)
manifest['build_exit'] = result.returncode
(evidence / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Build exit ' + str(result.returncode), flush=True)
result.check_returncode()
exe = build / 'src/opalx'
assert exe.is_file()
shutil.copy2(exe, evidence / 'opalx-master-8c1a862')
manifest['executable_sha256'] = hashlib.sha256(exe.read_bytes()).hexdigest()
manifest['source_status_after'] = command(['git', 'status', '--porcelain', '--untracked-files=no'], source)
assert not manifest['source_status_after']
for name, path in paths.items():
    record = manifest['dependencies'][name]
    if 'revision' in record:
        record['status_after'] = command(['git', 'status', '--porcelain'], path)
        assert record['revision'] == command(['git', 'rev-parse', 'HEAD'], path)
        assert not record['status_after'], (name, record['status_after'])
    else:
        record['tree_sha256_after'] = tree_hash(path)
        assert record['tree_sha256_before'] == record['tree_sha256_after'], name
manifest['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
(evidence / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Executable copied; source and dependency source trees unchanged', flush=True)
print(manifest['executable_sha256'], flush=True)
