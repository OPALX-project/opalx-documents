#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=00:20:00
#SBATCH --job-name=loss-sink-stress
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490'
source_dir="$job_root/src"
build_dir="$job_root/build"
run_dir="$job_root/evidence-stress"
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
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json,os
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');source=root/'src';m=json.loads((source/'source-manifest.json').read_text())
for name,digest in m['files'].items():
 expected='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6' if name=='unit_tests/Structure/TestLossDataSink.cpp' else digest
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected,name
proof=json.loads((root/'evidence-final/binary-verification.json').read_text())
for name,row in proof.items():assert hashlib.sha256((root/'build/unit_tests/Structure'/name).read_bytes()).hexdigest()==row['sha256'],name
libhash=hashlib.sha256((root/'build/src/libopalx.so').read_bytes()).hexdigest();assert libhash==(root/'evidence-final/library-before.sha256').read_text().strip()
gaussian=root/'build/unit_tests/Distribution/TestGaussian'
report={'source_files_verified':len(m['files']),'changed_file_sha256':'c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6','library_sha256':libhash,'loss_binary_sha256':proof['TestLossDataSink']['sha256'],'gaussian_binary_sha256':hashlib.sha256(gaussian.read_bytes()).hexdigest(),'gaussian_default_Options_seed':123456789,'environment':{k:v for k,v in os.environ.items() if k in ['OMP_NUM_THREADS','OMP_PROC_BIND','IPPL_OPENMP_THREADS'] or k.startswith('KOKKOS_')}}
(root/'evidence-stress/input-metadata.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
VERIFY
printf 'phase\tisolated-gaussian-once\n' >> "$run_dir/status.tsv"
set +e
ctest --test-dir "$build_dir" -V -j1 --output-on-failure --output-junit "$run_dir/gaussian-isolated.xml" \
 -R '^TestGaussian$' 2>&1 | tee "$run_dir/gaussian-isolated.log"
gaussian_status=${PIPESTATUS[0]}
set -e
printf 'gaussian_isolated_exit\t%s\n' "$gaussian_status" >> "$run_dir/status.tsv"
printf 'phase\trelated-targets\n' >> "$run_dir/status.tsv"
ctest --test-dir "$build_dir" -V -j2 --output-on-failure --output-junit "$run_dir/related.xml" \
 -R '^Test(LossDataSink(MPI)?|CheckpointFile|CyclotronProbe(MPI)?)$' \
 2>&1 | tee "$run_dir/related.log"
printf 'phase\tparallel-stress\n' >> "$run_dir/status.tsv"
python3 "$job_root/parallel_stress_after.py" "$build_dir" "$run_dir"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');source=root/'src';m=json.loads((source/'source-manifest.json').read_text())
for name,digest in m['files'].items():
 expected='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6' if name=='unit_tests/Structure/TestLossDataSink.cpp' else digest
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected,name
r=json.loads((root/'evidence-stress/parallel-summary.json').read_text());assert len(r['runs'])==100 and r['failed_runs']==0,r
metadata=json.loads((root/'evidence-stress/input-metadata.json').read_text())
assert hashlib.sha256((root/'build/src/libopalx.so').read_bytes()).hexdigest()==metadata['library_sha256']
assert hashlib.sha256((root/'build/unit_tests/Distribution/TestGaussian').read_bytes()).hexdigest()==metadata['gaussian_binary_sha256']
(root/'evidence-stress/terminal-verification.json').write_text(json.dumps({'source_files_verified':len(m['files']),'library_unchanged':True,'gaussian_binary_unchanged':True,'pair_iterations':100,'pair_failures':0},indent=2)+'\n')
print('Verified sources, library and Gaussian binary unchanged;100 concurrent pair iterations pass')
VERIFY
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
