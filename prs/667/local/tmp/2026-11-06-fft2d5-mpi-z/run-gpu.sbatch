#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-gpu=124800M
#SBATCH --gpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --job-name=2d5-z-pilot
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-mpi-z-20261106/pilot-%j.out
set -euo pipefail
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
cd /psi/home/adelmann/opalx-dev/dba/validation-mpi-z-20261106
python run_gpu.py
