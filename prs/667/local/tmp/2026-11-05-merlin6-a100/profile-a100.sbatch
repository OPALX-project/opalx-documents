#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus=1
#SBATCH --mem=64G
#SBATCH --time=00:20:00
#SBATCH --job-name=opalx-gpu-proof
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/profile-%j.out
#SBATCH --error=/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/profile-%j.err
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-a100-20261105
P=$OUT/gpu-execution-proof-$SLURM_JOB_ID
mkdir "$P"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$P"
cp "$OUT/inputs/dba-pilot.in" case.in
sha256sum "$ROOT/build/gwendolen-cuda/src/opalx" case.in > identity.sha256
module -t list > modules.txt 2>&1
nvidia-smi > gpu.txt
nsys --version > nsys-version.txt
srun --ntasks=1 nsys profile --trace=cuda,nvtx --sample=none --cpuctxsw=none --force-overwrite=true --output="$P/dba" "$ROOT/build/gwendolen-cuda/src/opalx" case.in --info 1 --restart "$OUT/assets/dba-initial-state.h5" > run.log 2>&1
nsys stats --report cuda_gpu_kern_sum,cuda_api_sum,cuda_gpu_mem_time_sum,cuda_gpu_mem_size_sum,nvtx_sum --format csv --output "$P/stats" "$P/dba.nsys-rep" > stats.log 2>&1
sha256sum "$ROOT/build/gwendolen-cuda/src/opalx" > binary-after.sha256
printf '%s\n' "$P" > "$OUT/latest-gpu-proof.txt"
