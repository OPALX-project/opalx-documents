#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=00:40:00
#SBATCH --job-name=2d5-row-profile
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-row-profile-20261106/job-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-row-profile-20261106
cd "$OUT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
chmod +x profile_rank.sh
nsys --version > profiler-versions.txt
ncu --version >> profiler-versions.txt
nvidia-smi -q > gpu-identity.txt
nvidia-smi --query-gpu=timestamp,index,uuid,utilization.gpu,utilization.memory,memory.used,power.draw,clocks.sm,clocks.mem --format=csv -lms 100 > telemetry.csv &
monitor_pid=$!
trap 'kill "$monitor_pid" 2>/dev/null || true' EXIT
nsys profile --gpu-metrics-devices=help > metrics-probe.txt 2>&1 || true
python3 profile.py
