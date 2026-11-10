#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=96G
#SBATCH --time=24:00:00
#SBATCH --job-name=opalx-dba-one-turn
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend/dba-one-turn-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend/dba-one-turn-%j.err
set -euo pipefail
OUT=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
module -t list > "$OUT/dba-one-turn-modules.txt" 2>&1
nvidia-smi > "$OUT/dba-one-turn-gpu.txt"
python3 "$OUT/run_case.py" dba-one-turn
