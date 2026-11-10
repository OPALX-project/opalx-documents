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
#SBATCH --job-name=opalx-cuda-occupancy
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/cuda-occupancy-fix/build-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/cuda-occupancy-fix/build-%j.err
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-a100-20261105/cuda-occupancy-fix
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$ROOT"
B=build/gwendolen-cuda
OLD=$B/src/opalx.pre-cuda-occupancy-daaf914b0
if [ ! -e "$OLD" ]; then cp -p "$B/src/opalx" "$OLD"; fi
sha256sum "$OLD" > "$OUT/preserved-binary.sha256"
git diff -- src > "$OUT/source.patch"
module -t list > "$OUT/modules.txt" 2>&1
cmake --build "$B" --parallel "$SLURM_CPUS_PER_TASK" --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestSpaceChargeConfig TestPoissonSolver TestGaussian > "$OUT/build.log" 2>&1
sha256sum "$B/src/opalx" > "$OUT/new-binary.sha256"
ctest --test-dir "$B" -R '^(TestFFT2D5Algorithm|TestFFT2D5Numerics|TestSpaceChargeConfig|TestPoissonSolver|TestGaussian)$' --output-on-failure --output-junit "$OUT/unit-tests.xml" > "$OUT/unit-tests.log" 2>&1
