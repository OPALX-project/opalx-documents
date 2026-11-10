#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=8
#SBATCH --gpus=3
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=01:00:00
#SBATCH --job-name=2d5-density-baseline
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-longitudinal-batch-20261106/baseline-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-longitudinal-batch-20261106
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
cp -p build/gwendolen-cuda/src/opalx build/gwendolen-cuda/src/opalx.pre-density-master-20261106
python3 - <<'PY'
from pathlib import Path
import subprocess,shutil,json
r=Path.cwd();out=r/'validation-longitudinal-batch-20261106';backup=out/'source-backup';backup.mkdir(exist_ok=True)
(out/'source-before.patch').write_bytes(subprocess.check_output(['git','diff','--binary','HEAD']))
(out/'git-before.txt').write_bytes(subprocess.check_output(['git','status','--short','--branch']))
subprocess.check_call(['git','fetch','origin','codex/fft2d5-explicit-original-model'])
assert subprocess.check_output(['git','rev-parse','origin/codex/fft2d5-explicit-original-model']).decode().strip()=='57f3997293fb0994267804257a825ded2b909f73'
subprocess.check_call(['git','stash','push','-m','Preserve pre-density source state before published-branch baseline'])
new=set(subprocess.check_output(['git','ls-tree','-r','--name-only','origin/codex/fft2d5-explicit-original-model']).decode().splitlines())
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0')
for p in untracked:
 if p in new:
  dst=backup/p;dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(r/p,dst)
subprocess.check_call(['git','merge','--ff-only','origin/codex/fft2d5-explicit-original-model'])
(out/'baseline-source.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
PY
cmake -S . -B build/gwendolen-cuda > "$OUT/configure-baseline.log" 2>&1
cmake --build build/gwendolen-cuda -j24 --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestFFT2D5Parallel > "$OUT/build-baseline.log" 2>&1
cp -p build/gwendolen-cuda/src/opalx build/gwendolen-cuda/src/opalx.pre-longitudinal-density-20261106
sha256sum build/gwendolen-cuda/src/opalx* > "$OUT/baseline-binaries.sha256"
cd "$OUT"
for test in TestFFT2D5Numerics TestFFT2D5Algorithm; do
mpirun -np 1 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/$test" > "baseline-$test.log" 2>&1
done
mpirun -np 3 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/TestFFT2D5Parallel" > baseline-mpi3.log 2>&1
python3 run_gpu.py before
