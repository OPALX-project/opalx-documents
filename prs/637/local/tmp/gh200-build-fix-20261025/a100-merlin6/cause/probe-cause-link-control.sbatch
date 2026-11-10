#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --job-name=probe-cause-link

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?}"
run_dir="$PWD/tmp/probe-cause-20261025-61c90499"
build_dir="$PWD/build/gwendolen-cuda132-shared-release"
export run_dir build_dir
mkdir -p "$run_dir/overlay"
exec > >(tee "$run_dir/job.log") 2>&1
trap 'status=$?; printf "job-exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
module purge
module load gcc/14.3.0
module load cuda/13.2.1
module load openmpi/5.0.10_slurm
module load cmake/4.4.0
module -t list
nvcc --version
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv
git status --short --branch
test "$(git rev-parse HEAD)" = 61c90499b3f5638f2e26612561e149839774666d
git diff --exit-code
sha256sum "$build_dir/bin/TestCyclotronProbe" "$build_dir/bin/TestCyclotronProbeMPI" "$build_dir/lib/libopalx.so" > "$run_dir/baseline-before.sha256"
export OMP_NUM_THREADS=1
printf 'phase\trelink-overlay-only\n' >> "$run_dir/status.tsv"
python3 - <<'PY'
import os,pathlib,shlex,subprocess,json
build=pathlib.Path(os.environ['build_dir'])
run=pathlib.Path(os.environ['run_dir'])
args=shlex.split((build/'src/CMakeFiles/opalx.dir/link.txt').read_text())
assert not any('Bsymbolic' in arg for arg in args)
args[args.index('-o')+1]=str(run/'overlay/libopalx.so')
args.append('-Wl,-Bsymbolic-functions')
(run/'link-control-command.json').write_text(json.dumps({'cwd':str(build/'src'),'args':args},indent=2))
with (run/'relink.log').open('w') as log:
    subprocess.run(args,cwd=build/'src',stdout=log,stderr=subprocess.STDOUT,check=True)
PY
base_path="$build_dir/lib:${LD_LIBRARY_PATH:-}"
fixed_path="$run_dir/overlay:$base_path"
for variant in baseline local-functions; do
  current_path="$base_path"
  if test "$variant" = local-functions; then current_path="$fixed_path"; fi
  env LD_LIBRARY_PATH="$current_path" ldd "$build_dir/bin/TestCyclotronProbeMPI" > "$run_dir/$variant-libraries.log"
  printf 'phase\t%s-tests\n' "$variant" >> "$run_dir/status.tsv"
  set +e
  env LD_LIBRARY_PATH="$current_path" ctest --test-dir "$build_dir" -V -j 1 --timeout 60 \
    --output-junit "$run_dir/$variant-junit.xml" -R '^TestCyclotronProbe(MPI)?$' \
    > "$run_dir/$variant-tests.log" 2>&1
  test_status=$?
  set -e
  printf '%s-ctest\t%s\n' "$variant" "$test_status" >> "$run_dir/status.tsv"
  printf 'phase\t%s-registration-trace\n' "$variant" >> "$run_dir/status.tsv"
  set +e
  env LD_LIBRARY_PATH="$current_path" PROBE_TRACE_JSON="$run_dir/$variant-registration.json" \
    timeout 100 mpiexec --bind-to none -n 1 gdb -batch -x "$run_dir/trace.py" \
    --args "$build_dir/bin/TestCyclotronProbeMPI" \
    --gtest_filter=CyclotronProbeTest.AsciiEmptyRanksMigrationFramesAndTurnGroups \
    > "$run_dir/$variant-registration.log" 2>&1
  trace_status=$?
  set -e
  printf '%s-gdb\t%s\n' "$variant" "$trace_status" >> "$run_dir/status.tsv"
done
sha256sum "$build_dir/bin/TestCyclotronProbe" "$build_dir/bin/TestCyclotronProbeMPI" "$build_dir/lib/libopalx.so" > "$run_dir/baseline-after.sha256"
cmp "$run_dir/baseline-before.sha256" "$run_dir/baseline-after.sha256"
git diff --exit-code
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
