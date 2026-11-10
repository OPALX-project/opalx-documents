#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --gpus=2
#SBATCH --mem=192G
#SBATCH --time=01:00:00
#SBATCH --job-name=pr637-audit-663f
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/pr637-audit-fixes-20261109/663f93a30bef'
source_dir="$job_root/src"
build_dir="$job_root/build"
run_dir="$job_root/evidence"
mkdir -p "$run_dir/gpu-mapping"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
module purge
module load gcc/14.3.0 cuda/13.2.1 openmpi/5.0.10_slurm cmake/4.4.0
module -t list
nvcc --version
mpicxx --showme
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv
export OMP_NUM_THREADS=1 IPPL_OPENMP_THREADS=1
export AUDIT_GPU_MAP_DIR="$run_dir/gpu-mapping"
cd "$source_dir"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json
root=Path.cwd();m=json.loads((root/'source-manifest.json').read_text())
for name,digest in m['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
print('Verified source before build:',m['source_id'],len(m['files']))
VERIFY
printf 'phase\tconfigure\n' >> "$run_dir/status.tsv"
cmake --fresh --preset=release-testing -S . -B "$build_dir" \
    '-DPLATFORMS=CUDA;SERIAL' -DARCH=AMPERE80 \
    -DIPPL_GIT_TAG=3.4.0 -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_Fortran_COMPILER="$(command -v gfortran)" \
    -DOPALX_ENABLE_TESTS=OFF -DOPALX_ENABLE_UNIT_TESTS=ON -DBUILD_TESTING=ON \
    -DFETCHCONTENT_SOURCE_DIR_IPPL="$job_root/deps/ippl-src" \
    -DFETCHCONTENT_SOURCE_DIR_KOKKOS="$job_root/deps/kokkos-src" \
    -DFETCHCONTENT_SOURCE_DIR_HEFFTE="$job_root/deps/heffte-src" \
    -DFETCHCONTENT_SOURCE_DIR_GTEST="$job_root/deps/gtest-src" \
    -DFETCHCONTENT_SOURCE_DIR_H5HUT="$job_root/deps/h5hut-src" \
    -DFETCHCONTENT_SOURCE_DIR_HDF5="$job_root/deps/hdf5-src" \
    -DFETCHCONTENT_SOURCE_DIR_OPALX_LAPACK="$job_root/deps/opalx_lapack-src" \
    -DKokkos_ENABLE_DEBUG_BOUNDS_CHECK=OFF \
    -DMPIEXEC_EXECUTABLE="$(command -v mpiexec)" \
    "-DMPIEXEC_PREFLAGS=--bind-to;none;$(command -v python3);$job_root/rank_gpu.py" \
    2>&1 | tee "$run_dir/configure.log"
printf 'phase\tbuild\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel "${SLURM_CPUS_PER_TASK:?}" \
    --target opalx_exe TestRFEventStep TestRFEventStepMPI TestCyclotronSector TestCyclotronSectorMPI TestCyclotronProbe TestCyclotronProbeMPI \
    2>&1 | tee "$run_dir/build.log"
printf 'phase\ttest\n' >> "$run_dir/status.tsv"
ctest --test-dir "$build_dir" -N -V -R '^Test(RFEventStep|CyclotronSector|CyclotronProbe)(MPI)?$' > "$run_dir/test-commands.log" 2>&1
ctest --test-dir "$build_dir" -V -j 1 --timeout 180 --output-on-failure --output-junit "$run_dir/junit.xml" \
    -R '^Test(RFEventStep|CyclotronSector|CyclotronProbe)(MPI)?$' 2>&1 | tee "$run_dir/tests.log"
printf 'ctest\t0\n' >> "$run_dir/status.tsv"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json
root=Path.cwd();m=json.loads((root/'source-manifest.json').read_text())
for name,digest in m['files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
(root.parent/'evidence/source-verification.json').write_text(json.dumps({'source_id':m['source_id'],'base_head':m['base_head'],'files_verified':len(m['files'])},indent=2)+'\n')
print('Verified source after tests:',m['source_id'],len(m['files']))
VERIFY
sha256sum "$build_dir/bin/opalx" "$build_dir/lib/libopalx.so" \
    "$build_dir/bin/TestRFEventStep" "$build_dir/bin/TestRFEventStepMPI" \
    "$build_dir/bin/TestCyclotronSector" "$build_dir/bin/TestCyclotronSectorMPI" \
    "$build_dir/bin/TestCyclotronProbe" "$build_dir/bin/TestCyclotronProbeMPI" > "$run_dir/binaries.sha256"
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
