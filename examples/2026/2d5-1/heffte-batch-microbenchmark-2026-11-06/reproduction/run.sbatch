#!/bin/bash
#SBATCH --job-name=2d5-heffte
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --mem=124800M
#SBATCH --time=01:00:00
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-heffte-batch-20261106/job-%j.out
set -euo pipefail
cd /psi/home/adelmann/opalx-dev/dba
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
tar -xzf validation-heffte-batch-20261106/opalx-heffte-benchmark-20261106.tar.gz
touch unit_tests/SpaceCharge/BenchmarkFFT2D5Batch.cpp
sha256sum build/gwendolen-cuda/src/opalx
cmake -S . -B build/gwendolen-cuda > validation-heffte-batch-20261106/configure.log 2>&1
cmake --build build/gwendolen-cuda --target BenchmarkFFT2D5Batch -j16 > validation-heffte-batch-20261106/build.log 2>&1
sha256sum build/gwendolen-cuda/src/opalx
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
mkdir -p validation-heffte-batch-20261106/gpu
cd validation-heffte-batch-20261106/gpu
nvidia-smi > gpu-info.txt
mpirun -np 1 --map-by slot --bind-to none /psi/home/adelmann/opalx-dev/dba/build/gwendolen-cuda/unit_tests/SpaceCharge/BenchmarkFFT2D5Batch > run.log 2>&1
