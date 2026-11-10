#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --gpus=2
#SBATCH --mem=192G
#SBATCH --time=01:30:00
#SBATCH --job-name=pr637-scaling-a100

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
run_dir="$PWD/tmp/pr637-scaling-a100-20261025-r2"
build_dir="$PWD/build/gwendolen-cuda132-shared-release"
expected=a9d38caa4f88433a5de1508b3d5c7d01bdfea95a
mkdir -p "$run_dir"
exec > >(tee "$run_dir/job.log") 2>&1
trap 'status=$?; printf "job-exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -Is
hostname
module purge
module load gcc/14.3.0
module load cuda/13.2.1
module load openmpi/5.0.10_slurm
module load cmake/4.4.0
module -t list
nvcc --version
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv
test "$(git rev-parse HEAD)" = "$expected"
git diff --exit-code
git diff --cached --exit-code
git show --no-patch --format=fuller HEAD > "$run_dir/source.txt"
git status --short --branch > "$run_dir/working-tree.txt"
git ls-files -z src unit_tests CMakeLists.txt ci | xargs -0 sha256sum > "$run_dir/source.sha256"
for dep in ippl-src ippl-build/_deps/kokkos-src ippl-build/_deps/heffte-src gtest-src; do
  printf 'dependency\t%s\t' "$dep"
  git -C "$build_dir/_deps/$dep" rev-parse HEAD
done > "$run_dir/dependencies.txt"
export OMP_NUM_THREADS=1
printf 'phase\tconfigure\n' >> "$run_dir/status.tsv"
cmake -S . -B "$build_dir" \
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  2>&1 | tee "$run_dir/configure.log"
printf 'phase\tbuild\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel "${SLURM_CPUS_PER_TASK:?}" \
  --target TestMultipoleT TestMultipoleTBase TestMultipoleTStraight \
    TestScalingFFAMagnet TestDeviceExternalField TestTrackReferenceStep opalx_exe \
  2>&1 | tee "$run_dir/build.log"
printf 'phase\ttest\n' >> "$run_dir/status.tsv"
pattern='^Test(MultipoleT|MultipoleTBase|MultipoleTStraight|ScalingFFAMagnet|DeviceExternalField|TrackReferenceStep)$'
ctest --test-dir "$build_dir" -N -V -R "$pattern" > "$run_dir/test-commands.log" 2>&1
set +e
ctest --test-dir "$build_dir" -V -j 1 --output-on-failure \
  --output-junit "$run_dir/junit.xml" -R "$pattern" \
  2>&1 | tee "$run_dir/tests.log"
test_status=${PIPESTATUS[0]}
printf 'ctest\t%s\n' "$test_status" >> "$run_dir/status.tsv"
printf '%s\n' "mpiexec -n 2 --bind-to none $build_dir/bin/TestScalingFFAMagnet --gtest_filter=ScalingFFAMagnetTest.SuperposesParticleAndReferenceFieldsWithoutErasingOtherElements" > "$run_dir/two-rank-command.txt"
mpiexec -n 2 --bind-to none "$build_dir/bin/TestScalingFFAMagnet" \
  --gtest_filter=ScalingFFAMagnetTest.SuperposesParticleAndReferenceFieldsWithoutErasingOtherElements \
  2>&1 | tee "$run_dir/two-rank.log"
mpi_status=${PIPESTATUS[0]}
printf 'two-rank\t%s\n' "$mpi_status" >> "$run_dir/status.tsv"
set -e
test "$(git rev-parse HEAD)" = "$expected"
git diff --exit-code
git diff --cached --exit-code
sha256sum -c "$run_dir/source.sha256" > "$run_dir/source-after-check.txt"
sha256sum "$build_dir/bin/opalx" "$build_dir/bin/TestMultipoleTStraight" \
  "$build_dir/bin/TestScalingFFAMagnet" "$build_dir/lib/libopalx.so" > "$run_dir/binaries.sha256"
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -Is
if ((test_status != 0)); then exit "$test_status"; fi
exit "$mpi_status"
