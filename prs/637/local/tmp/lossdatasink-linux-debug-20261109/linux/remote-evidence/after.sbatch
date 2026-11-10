#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=01:00:00
#SBATCH --job-name=loss-sink-fixed
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490'
source_dir="$job_root/src"
build_dir="$job_root/build"
run_dir="$job_root/evidence-after"
mkdir -p "$run_dir"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
uname -a
module purge
module load gcc/14.3.0 openmpi/5.0.10_slurm cmake/4.4.0
module -t list
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false IPPL_OPENMP_THREADS=4
if command -v strace >/dev/null; then
 printf 'phase\tbefore-strace\n' >> "$run_dir/status.tsv"
 set +e
 strace -ff -s 256 -e trace=openat,unlink,unlinkat,rename,renameat -o "$job_root/evidence/before-strace" \
 ctest --test-dir "$build_dir" -V -j2 --output-on-failure -R '^TestLossDataSink(MPI)?$' \
 > "$job_root/evidence/before-strace-ctest.log" 2>&1
 result=$?
 set -e
 printf 'strace_ctest\t%s\n' "$result" >> "$run_dir/status.tsv"
fi
python3 - <<'PATCH'
from pathlib import Path
import hashlib,json,shutil
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');source=root/'src';m=json.loads((source/'source-manifest.json').read_text())
for name,digest in m['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
original=source/'unit_tests/Structure/TestLossDataSink.cpp'
checks=[root/'build/src/libopalx.so',root/'build/unit_tests/Structure/TestLossDataSink',root/'build/unit_tests/Structure/TestLossDataSinkMPI']
(root/'evidence/binaries-corrected.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p)+'\n' for p in checks))
shutil.copy2(original,root/'evidence/original-TestLossDataSink.cpp')
for name in ['TestLossDataSink','TestLossDataSinkMPI']:shutil.copy2(root/'build/unit_tests/Structure'/name,root/'evidence'/('baseline-'+name))
fixed=root/'fixed-TestLossDataSink.cpp'
assert hashlib.sha256(fixed.read_bytes()).hexdigest()=='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6'
shutil.copy2(fixed,original)
(root/'evidence-after/source-change.json').write_text(json.dumps({'base_source_id':m['source_id'],'changed_file':'unit_tests/Structure/TestLossDataSink.cpp','before_sha256':m['files']['unit_tests/Structure/TestLossDataSink.cpp'],'after_sha256':'c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6','other_verified_source_files':len(m['files'])-1},indent=2)+'\n')
PATCH
printf 'phase\tbuild-all\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel 32 2>&1 | tee "$run_dir/build-all.log"
printf 'phase\tfull-suite\n' >> "$run_dir/status.tsv"
ctest --test-dir "$build_dir" -j4 --output-on-failure --output-junit "$run_dir/full-suite.xml" \
    2>&1 | tee "$run_dir/full-suite.log"
printf 'phase\tparallel-stress\n' >> "$run_dir/status.tsv"
python3 "$job_root/parallel_stress_after.py" "$build_dir" "$run_dir"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');source=root/'src';m=json.loads((source/'source-manifest.json').read_text())
for name,digest in m['files'].items():
 expected='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6' if name=='unit_tests/Structure/TestLossDataSink.cpp' else digest
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected,name
r=json.loads((root/'evidence-after/parallel-summary.json').read_text());assert len(r['runs'])==100 and r['failed_runs']==0,r
print('Verified full source snapshot except intended one-file fix and100 concurrent-pair iterations pass')
VERIFY
sha256sum "$build_dir/src/libopalx.so" "$build_dir/unit_tests/Structure/TestLossDataSink" "$build_dir/unit_tests/Structure/TestLossDataSinkMPI" > "$run_dir/binaries.sha256"
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
