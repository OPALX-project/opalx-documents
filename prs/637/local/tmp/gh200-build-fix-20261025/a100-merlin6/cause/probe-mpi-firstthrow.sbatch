#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --gpus=2
#SBATCH --mem=32G
#SBATCH --time=00:08:00
#SBATCH --job-name=probe-mpi-throw

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
run_dir="$PWD/tmp/probe-cause-20261025-61c90499"
build_dir="$PWD/build/gwendolen-cuda132-shared-release"
exec > >(tee "$run_dir/mpi-firstthrow-job.log") 2>&1
date -Is
hostname
module purge
module load gcc/14.3.0
module load cuda/13.2.1
module load openmpi/5.0.10_slurm
module load cmake/4.4.0
module -t list
git diff --exit-code
test "$(git rev-parse HEAD)" = 61c90499b3f5638f2e26612561e149839774666d
export OMP_NUM_THREADS=1
export LD_LIBRARY_PATH="$run_dir/overlay:$build_dir/lib:${LD_LIBRARY_PATH:-}"
set +e
timeout 100 mpiexec --bind-to none -n 2 --output-filename "$run_dir/mpi-firstthrow" \
  gdb -batch -x "$run_dir/mpi-firstthrow.py" \
  --args "$build_dir/bin/TestCyclotronProbeMPI" \
  --gtest_filter=CyclotronProbeTest.AsciiEmptyRanksMigrationFramesAndTurnGroups
status=$?
set -e
printf 'mpi-firstthrow-launcher-exit\t%s\n' "$status"
git diff --exit-code
sha256sum "$build_dir/bin/TestCyclotronProbeMPI" "$build_dir/lib/libopalx.so"
date -Is
