#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=8
#SBATCH --gpus=3
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=00:40:00
#SBATCH --job-name=2d5-row-calibrate3
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-row-profile-20261106/calibrate3-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-row-profile-20261106
cd "$OUT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
mpirun -np 3 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/TestFFT2D5Parallel" > unit-parallel3.log 2>&1
python3 calibrate3.py
