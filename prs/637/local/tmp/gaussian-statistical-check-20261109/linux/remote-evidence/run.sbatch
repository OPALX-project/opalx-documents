#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --job-name=gaussian-statistical
set -euo pipefail
run_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490/gaussian-statistical-20261109'
mkdir -p "$run_root/after"
exec > >(tee -a "$run_root/after/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_root/after/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_root/after/status.tsv"
module purge
module load gcc/14.3.0 openmpi/5.0.10_slurm cmake/4.4.0
module -t list
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false IPPL_OPENMP_THREADS=4 KOKKOS_NUM_THREADS=4
hostname
uname -a
python3 "$run_root/run.py"
