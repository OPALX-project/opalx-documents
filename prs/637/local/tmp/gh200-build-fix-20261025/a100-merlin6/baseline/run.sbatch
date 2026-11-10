#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2
#SBATCH --mem=96G
#SBATCH --time=02:00:00
#SBATCH --job-name=opalx-probe-615

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
run_dir="$PWD/tmp/a100-probe-20261025-61c90499"
build_dir="$PWD/build/gwendolen-cuda-shared-release"
mkdir -p "$run_dir"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
test "$(hostname -s)" != merlin-l-001
module purge
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
module -t list
command -v cmake gcc g++ gfortran mpicc mpicxx nvcc
cmake --version
mpicxx --showme
nvcc --version
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv
git status --short --branch
git rev-parse HEAD | tee "$run_dir/source-sha.txt"
test "$(git rev-parse HEAD)" = 61c90499b3f5638f2e26612561e149839774666d
export OMP_NUM_THREADS=1
printf 'phase\tconfigure\n' >> "$run_dir/status.tsv"
cmake --preset=release-testing -S . -B "$build_dir" \
  '-DPLATFORMS=CUDA;SERIAL' -DARCH=AMPERE80 \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON \
  -DCMAKE_Fortran_COMPILER="$(command -v gfortran)" \
  -DOPALX_ENABLE_UNIT_TESTS=ON -DBUILD_TESTING=ON \
  -DKokkos_ENABLE_DEBUG_BOUNDS_CHECK=OFF \
  -DMPIEXEC_EXECUTABLE="$(command -v mpiexec)" \
  '-DMPIEXEC_PREFLAGS=--bind-to;none' \
  2>&1 | tee "$run_dir/configure.log"
for dependency in ippl kokkos heffte googletest; do
  if test -d "$build_dir/_deps/$dependency-src/.git"; then
    printf '%s\t%s\n' "$dependency" "$(git -C "$build_dir/_deps/$dependency-src" rev-parse HEAD)"
  fi
done | tee "$run_dir/dependency-revisions.tsv"
printf 'phase\tbuild\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel "${SLURM_CPUS_PER_TASK:?}" \
  --target TestCyclotronProbe TestCyclotronProbeMPI \
  2>&1 | tee "$run_dir/build.log"
printf 'phase\ttest\n' >> "$run_dir/status.tsv"
ctest --test-dir "$build_dir" -N -V -R '^TestCyclotronProbe(MPI)?$' \
  2>&1 | tee "$run_dir/test-commands.log"
set +e
ctest --test-dir "$build_dir" -V -j 1 --output-on-failure \
  --output-junit "$run_dir/junit.xml" -R '^TestCyclotronProbe(MPI)?$' \
  2>&1 | tee "$run_dir/tests.log"
test_status=${PIPESTATUS[0]}
set -e
printf 'ctest\t%s\n' "$test_status" >> "$run_dir/status.tsv"
if test "$test_status" -ne 0; then
  printf 'phase\tisolated-failure-diagnostics\n' >> "$run_dir/status.tsv"
  executable="$build_dir/bin/TestCyclotronProbeMPI"
  filter='--gtest_filter=CyclotronProbeTest.AsciiEmptyRanksMigrationFramesAndTurnGroups'
  for ranks in 1 2; do
    set +e
    mpiexec --bind-to none -n "$ranks" "$executable" "$filter" \
      > "$run_dir/isolated-${ranks}-rank.log" 2>&1
    isolated_status=$?
    set -e
    printf 'isolated-%s-rank\t%s\n' "$ranks" "$isolated_status" >> "$run_dir/status.tsv"
  done
  if command -v gdb >/dev/null 2>&1; then
    set +e
    timeout 90 mpiexec --bind-to none -n 1 gdb -batch \
      -ex 'set pagination off' -ex 'catch throw' -ex run -ex 'bt 30' \
      --args "$executable" "$filter" > "$run_dir/first-throw-backtrace.log" 2>&1
    gdb_status=$?
    set -e
    printf 'gdb\t%s\n' "$gdb_status" >> "$run_dir/status.tsv"
  fi
fi
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
exit "$test_status"

