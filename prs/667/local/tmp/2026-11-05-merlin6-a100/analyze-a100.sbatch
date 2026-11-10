#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:20:00
#SBATCH --job-name=opalx-pr667-analysis
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/analysis-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/analysis-%j.err
set -euo pipefail
OUT=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105
PYTHON=/psi/home/adelmann/opalx-dev/venv-h6-py311/bin/python
module unload Python/3.14.4
module load Python/3.11.11
export LD_LIBRARY_PATH="$OUT/python-runtime-libs:${LD_LIBRARY_PATH:-}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
unset PYTHONHOME PYTHONPATH
hostname
"$PYTHON" -c 'import sys,numpy,pandas,h5py; print(sys.version); print(numpy.__version__,pandas.__version__,h5py.__version__)'
"$PYTHON" "$OUT/analyze_cases.py"
