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
#SBATCH --job-name=pr637-followup-final

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
run_dir="$PWD/tmp/pr637-followup-final-20261025"
build_dir="$PWD/build/gwendolen-cuda132-shared-release"
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
test "$(git rev-parse HEAD)" = a27c1b392a178a67e4f0df8c10c7fe48acb111f3
git status --short --branch
git diff --binary > "$run_dir/source.patch"
sha256sum "$run_dir/source.patch"
export OMP_NUM_THREADS=1
printf 'phase\tconfigure\n' >> "$run_dir/status.tsv"
cmake -S . -B "$build_dir" \
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
  2>&1 | tee "$run_dir/configure.log"
printf 'phase\tbuild\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel "${SLURM_CPUS_PER_TASK:?}" \
  --target TestLossDataSink TestLossDataSinkMPI TestRFEventStep TestRFEventStepMPI TestTrackReferenceStep TestDeviceExternalField TestCyclotronProbe TestCyclotronProbeMPI TestParticleContainer TestCoordinateSystemTrafo opalx_exe \
  2>&1 | tee "$run_dir/build.log"
printf 'phase\ttest\n' >> "$run_dir/status.tsv"
pattern='^Test(CyclotronProbe(MPI)?|LossDataSink(MPI)?|RFEventStep(MPI)?|TrackReferenceStep|DeviceExternalField|ParticleContainer|CoordinateSystemTrafo)$'
ctest --test-dir "$build_dir" -N -V -R "$pattern" > "$run_dir/test-commands.log" 2>&1
set +e
ctest --test-dir "$build_dir" -V -j 1 --output-on-failure \
  --output-junit "$run_dir/junit.xml" -R "$pattern" \
  2>&1 | tee "$run_dir/tests.log"
test_status=${PIPESTATUS[0]}
set -e
printf 'ctest\t%s\n' "$test_status" >> "$run_dir/status.tsv"
git diff --check
git diff --binary > "$run_dir/source-after.patch"
cmp "$run_dir/source.patch" "$run_dir/source-after.patch"
sha256sum "$build_dir/bin/opalx" "$build_dir/bin/TestRFEventStepMPI" "$build_dir/bin/TestCyclotronProbeMPI" "$build_dir/lib/libopalx.so" > "$run_dir/binaries.sha256"
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -Is
exit "$test_status"
