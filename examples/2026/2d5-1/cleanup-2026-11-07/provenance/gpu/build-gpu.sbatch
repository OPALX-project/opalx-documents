#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus=1
#SBATCH --mem=64000M
#SBATCH --time=01:00:00
#SBATCH --job-name=2d5-cleanup-build
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-cleanup-20261107/build-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-cleanup-20261107
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
module -t list
hostname
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
sha256sum build/gwendolen-cuda/src/opalx.pre-cleanup-20261107
cmake --build build/gwendolen-cuda -j16 --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestFFT2D5Parallel > "$OUT/build.log" 2>&1
cp -n -p build/gwendolen-cuda/src/opalx build/gwendolen-cuda/src/opalx.cleanup-20261107
sha256sum build/gwendolen-cuda/src/opalx.cleanup-20261107 > "$OUT/after-binary.sha256"
git rev-parse HEAD > "$OUT/source-base.txt"
cd "$OUT"
mpirun -np 1 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/validation-mpi-z-20261106/mpi_gpu_probe" 1 > probe-1.log
for test in TestFFT2D5Algorithm TestFFT2D5Numerics TestFFT2D5Parallel; do
mpirun -np 1 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/$test" > "unit-${test,,}-rank1.log" 2>&1
done
python3 run_gpu.py 1
