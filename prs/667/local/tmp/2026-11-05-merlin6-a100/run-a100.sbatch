#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#SBATCH --job-name=opalx-pr667-repeat
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/repeat-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/repeat-%j.err
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-a100-20261105
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
module -t list 2>&1
hostname
nvidia-smi --query-gpu=index,name,uuid,memory.total --format=csv
python3 "$OUT/run_cases.py"
python3 "$OUT/analyze_cases.py"
