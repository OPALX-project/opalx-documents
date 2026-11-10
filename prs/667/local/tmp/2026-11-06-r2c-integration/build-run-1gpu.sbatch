#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus=1
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=01:00:00
#SBATCH --job-name=r2c-rows-build
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-r2c-rows-20261106/build-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-r2c-rows-20261106
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
tar xzf "$OUT/source.tgz"
touch src/SpaceCharge/FFT2D5/FFT2D5Poisson.{h,cpp}
cmake --build build/gwendolen-cuda -j16 --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestFFT2D5Parallel > "$OUT/build.log" 2>&1
sha256sum build/gwendolen-cuda/src/opalx* > "$OUT/binaries.sha256"
cd "$OUT"
for test in TestFFT2D5Algorithm TestFFT2D5Numerics; do
mpirun -np1 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/$test" > "$test.log" 2>&1
done
python3 run_gpu.py
