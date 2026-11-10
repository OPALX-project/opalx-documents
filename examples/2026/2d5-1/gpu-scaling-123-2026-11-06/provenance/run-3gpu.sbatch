#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=8
#SBATCH --gpus=3
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=00:20:00
#SBATCH --job-name=2d5-row-3gpu
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-row-profile-20261106/gpu3-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-row-profile-20261106/gpu-3-rows
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
cd "$OUT"
mpirun -np 3 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/validation-mpi-z-20261106/mpi_gpu_probe" 3 > gpu-probe.log 2>&1
python3 - <<'PY'
from pathlib import Path
import subprocess,time,os,json,hashlib
root=Path('/psi/home/adelmann/opalx-dev/dba');exe=root/'build/gwendolen-cuda/src/opalx'
sha=hashlib.sha256(exe.read_bytes()).hexdigest();assert sha=='a21ab5e66c046f089d907ff14eb7b5c932a234336d49efc6b082431a8f1dd32a'
args=['mpirun','-np','3','--map-by','slot','--bind-to','none',str(root/'validation-mpi-z-20261106/gpu_rank.sh'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'validation-a100-20261105/assets/dba-initial-state.h5')]
t=time.monotonic()
with Path('case.out').open('w') as f:rc=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT).returncode
Path('run.json').write_text(json.dumps(dict(command=args,ranks=3,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=sha,input_sha256=hashlib.sha256(Path('case.in').read_bytes()).hexdigest()),indent=2))
assert rc==0
assert 'MPI ranks: 3' in Path('case.out').read_text()
PY
