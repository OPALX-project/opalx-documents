#!/usr/bin/env python3
"""Archive build/native/source evidence without copying third-party binaries."""
from pathlib import Path
import hashlib
import importlib.metadata as md
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
SOURCE=Path('/Users/adelmann/git/PyORBIT3')

def run(args,cwd=None):
    r=subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
    return r.stdout.strip()

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def main():
    revision=run(['git','rev-parse','HEAD'],SOURCE)
    assert revision=='28df66018aebe4e2b780b9747f4a2d7b8430a5c0'
    assert run(['git','status','--porcelain'],SOURCE)==''
    files=[SOURCE/p for p in ['src/spacecharge/SpaceChargeCalcSliceBySlice2D.cc',
       'src/spacecharge/SpaceChargeCalcSliceBySlice2D.hh',
       'src/spacecharge/SpaceChargeCalc2p5Drb.cc','src/spacecharge/Grid3D.cc',
       'src/spacecharge/Grid2D.cc','src/spacecharge/Grid1D.cc',
       'src/spacecharge/PoissonSolverFFT2D.cc','src/spacecharge/ShapedBoundary2D.cc',
       'src/spacecharge/BaseBoundary2D.cc','src/orbit/Bunch.cc','src/meson.build',
       'meson.build','meson_options.txt','pyproject.toml','LICENSE.txt',
       'examples/SpaceCharge/scSliceBySlice2D/sc_Slice2D_driftLatt_longitudinal_test.py']]
    native=[*sorted((HERE/'native-package/orbit/core').glob('*.so')),
            HERE/'native-package/.pyorbit.mesonpy.libs/libcore.dylib']
    record=dict(source_revision=revision,source_tree_clean=True,
        source_url='https://github.com/PyORBIT-Collaboration/PyORBIT3',
        source_sha256={str(p.relative_to(SOURCE)):digest(p) for p in files},
        native_files=[dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size) for p in native],
        libcore_link_dependencies=run(['otool','-L',str(native[-1])]),
        compiler=run(['clang++','--version']),
        mpi=run(['/opt/homebrew/Cellar/open-mpi/5.0.8/bin/mpirun','--version']),
        fftw_pkgconfig_version=run(['pkg-config','--modversion','fftw3']),
        python=sys.executable,python_version=sys.version,
        build_dependencies={d.metadata['Name']:d.version for d in md.distributions(path=[str(HERE/'build-python')])},
        native_distribution_version=next(md.distributions(path=[str(HERE/'native-package')])).version,
        build_log_sha256=digest(HERE/'build.log'),
        build_argv=['python','-m','pip','install','--no-build-isolation','--no-deps',
            '--target',str(HERE/'native-package'),'--config-settings=setup-args=-DUSE_MPI=ompi',
            '--config-settings=compile-args=-j4','.'],
        build_env=dict(PYTHONPATH=str(HERE/'build-python'),
            PATH='build-python/bin plus venv, Homebrew OpenMPI and system compiler paths'),
        compiled_source_modifications='None; pinned upstream unmodified',
        external_binary_redistribution='No native binaries copied into report evidence; paths/hashes only',
        harness_revisions=[dict(path=str(p),sha256=digest(p)) for p in sorted((HERE/'harness-snapshots').glob('*.py'))])
    (HERE/'build-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
    print(HERE/'build-provenance.json')

if __name__=='__main__': main()
