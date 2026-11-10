#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=96G
#SBATCH --time=01:00:00
#SBATCH --job-name=opalx-bend-batch64
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend/bend-batch64-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend/bend-batch64-%j.err
set -euo pipefail
OUT=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
module -t list > "$OUT/bend-batch64-modules.txt" 2>&1
nvidia-smi > "$OUT/bend-batch64-gpu.txt"
python3 "$OUT/run_case.py" bend-batch64
module unload Python/3.14.4
module load Python/3.11.11
export LD_LIBRARY_PATH="/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/python-runtime-libs:${LD_LIBRARY_PATH:-}"
unset PYTHONHOME PYTHONPATH
/psi/home/adelmann/opalx-dev/venv-h6-py311/bin/python "$OUT/analyze_bend.py"
