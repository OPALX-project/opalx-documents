#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus=1
#SBATCH --mem=96G
#SBATCH --time=03:00:00
#SBATCH --job-name=opalx-pr667-build
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/build-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/build-%j.err
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-a100-20261105
BUILD=$ROOT/build/gwendolen-cuda
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
module -t list 2>&1 | tee "$OUT/build-modules.txt"
hostname
date --iso-8601=seconds
git rev-parse HEAD
test "$(git rev-parse HEAD)" = 6301c2cab10bf164e6d1ea60de5d0d25cdd0ca8a
test -z "$(git diff --name-only)"
printf 'CUDA_VISIBLE_DEVICES=%s\n' "${CUDA_VISIBLE_DEVICES-}"
nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv | tee "$OUT/gpus.txt"
command -v cmake gcc g++ gfortran mpicxx nvcc
nvcc --version
cmake -S "$ROOT" -B "$BUILD" \
 -DCMAKE_BUILD_TYPE=Release -DPLATFORMS=CUDA -DARCH=AMPERE80 \
 -DOPALX_ENABLE_UNIT_TESTS=ON -DBUILD_TESTING=ON \
 -DIPPL_GIT_TAG=d6216553e39dcf4405849c027517cc3401fefee5 \
 -DKokkos_VERSION=5.2.0 -DHeffte_VERSION=git.4d8d4597b479d1e4709a2b1b4cd7d8922600045f \
 -DCMAKE_Fortran_COMPILER="$(command -v gfortran)" \
 2>&1 | tee "$OUT/configure.log"
cmake --build "$BUILD" --parallel "$SLURM_CPUS_PER_TASK" \
 --target opalx_exe TestSpaceChargeConfig TestFFT2D5Algorithm TestFFT2D5Numerics TestPoissonSolver TestGaussian \
 2>&1 | tee "$OUT/build.log"
sha256sum "$BUILD/src/opalx" | tee "$OUT/binary.sha256"
git diff --exit-code
ctest --test-dir "$BUILD" --show-only=json-v1 > "$OUT/ctest-inventory.json"
export OMP_NUM_THREADS=1
set +e
ctest --test-dir "$BUILD" -R '^(TestSpaceChargeConfig|TestFFT2D5Algorithm|TestFFT2D5Numerics|TestPoissonSolver|TestGaussian)$' --parallel 1 --output-on-failure --output-junit "$OUT/unit-tests.xml" > "$OUT/unit-tests.log" 2>&1
status=$?
set -e
printf '%s\n' "$status" > "$OUT/unit-tests.exit"
printf 'build completed\n' > "$OUT/build-complete.txt"
date --iso-8601=seconds
