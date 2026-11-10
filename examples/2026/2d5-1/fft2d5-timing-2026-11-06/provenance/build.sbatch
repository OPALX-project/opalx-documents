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
#SBATCH --job-name=2d5-timers-build
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-timing-20261106/build-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
tar xzf validation-timing-20261106/source.tgz
touch src/SpaceCharge/FFT2D5/FFT2D5{Algorithm.cpp,Algorithm.h,Algorithm.hpp,FieldStorage.cpp,FieldStorage.h,Poisson.cpp,Poisson.h} unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp
cmake --build build/gwendolen-cuda -j 16 --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestFFT2D5Parallel > validation-timing-20261106/build.log 2>&1
sha256sum build/gwendolen-cuda/src/opalx > validation-timing-20261106/binary.sha256
