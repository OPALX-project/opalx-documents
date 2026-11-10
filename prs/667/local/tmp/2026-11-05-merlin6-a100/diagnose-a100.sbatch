#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gpus=1
#SBATCH --mem=16G
#SBATCH --time=00:15:00
#SBATCH --job-name=opalx-pr667-unitdiag
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/diag-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/diag-%j.err
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-a100-20261105
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge"
python3 "$OUT/diagnose_units.py"
if command -v gdb >/dev/null; then
 srun --ntasks=1 gdb -q -batch -ex 'set pagination off' -ex 'set print thread-events off' -ex run -ex 'thread apply all bt' --args ./TestFFT2D5Algorithm --gtest_filter=FFT2D5AlgorithmTest.LazyInitializationSkipsEmptySlices > "$OUT/empty-gdb.log" 2>&1 || true
fi
