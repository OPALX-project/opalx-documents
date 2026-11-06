#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=00:30:00
#SBATCH --job-name=r2c-rows-2gpu
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-r2c-rows-20261106/pilot-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
cd "$ROOT/validation-r2c-rows-20261106"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
mpirun -np 2 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/validation-mpi-z-20261106/mpi_gpu_probe" 2
mpirun -np 2 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/TestFFT2D5Parallel" > unit-mpi-2.log 2>&1
python3 run_gpu.py
