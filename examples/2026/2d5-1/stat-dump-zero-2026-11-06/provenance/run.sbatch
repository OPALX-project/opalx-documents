#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=16000M
#SBATCH --time=00:15:00
#SBATCH --job-name=2d5-stat0
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-stat0-20261106/run-%j.out
set -euo pipefail
cd /psi/home/adelmann/opalx-dev/dba/validation-stat0-20261106
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
python3 run.py
