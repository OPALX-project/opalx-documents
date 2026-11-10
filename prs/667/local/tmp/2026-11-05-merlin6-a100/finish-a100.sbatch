#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus=1
#SBATCH --mem=96G
#SBATCH --time=01:00:00
#SBATCH --job-name=opalx-pr667-finish
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/finish-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/finish-%j.err
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
test -z "$(git diff --name-only -- src cmake CMakeLists.txt)"
printf 'CUDA_VISIBLE_DEVICES=%s\n' "${CUDA_VISIBLE_DEVICES-}"
nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv | tee "$OUT/gpus.txt"
command -v cmake gcc g++ gfortran mpicxx nvcc
nvcc --version
sha256sum "$BUILD/src/opalx" > "$OUT/binary-before-helper.sha256"
git diff -- unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp > "$OUT/unit-cuda.patch"
cmake --build "$BUILD" --parallel "$SLURM_CPUS_PER_TASK" \
 --target TestSpaceChargeConfig TestFFT2D5Algorithm TestFFT2D5Numerics TestPoissonSolver TestGaussian \
 2>&1 | tee "$OUT/finish-build.log"
sha256sum "$BUILD/src/opalx" | tee "$OUT/binary.sha256"
git diff --exit-code -- src cmake CMakeLists.txt
cmp "$OUT/binary-before-helper.sha256" "$OUT/binary.sha256"
ctest --test-dir "$BUILD" --show-only=json-v1 > "$OUT/ctest-inventory.json"
export OMP_NUM_THREADS=1
set +e
ctest --test-dir "$BUILD" -R '^(TestSpaceChargeConfig|TestFFT2D5Algorithm|TestFFT2D5Numerics|TestPoissonSolver|TestGaussian)$' --parallel 1 --output-on-failure --output-junit "$OUT/unit-tests.xml" > "$OUT/unit-tests.log" 2>&1
status=$?
set -e
printf '%s\n' "$status" > "$OUT/unit-tests.exit"
printf 'build completed\n' > "$OUT/build-complete.txt"
date --iso-8601=seconds
