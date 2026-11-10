#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gpus=1
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --job-name=2d5-mpi-z-build
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-mpi-z-20261106/build-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
cd "$ROOT"
tar xzf validation-mpi-z-20261106/source-portability.tgz
touch src/SpaceCharge/FFT2D5/FFT2D5Algorithm.{cpp,hpp}
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
cmake -S . -B build/gwendolen-cuda > validation-mpi-z-20261106/configure-final.log 2>&1
cmake --build build/gwendolen-cuda -j 16 --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestSpaceChargeConfig TestFFT2D5Parallel > validation-mpi-z-20261106/build-portability.log 2>&1
sha256sum build/gwendolen-cuda/src/opalx > validation-mpi-z-20261106/binary.sha256
