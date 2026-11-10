#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=00:10:00
#SBATCH --job-name=unit-output-before
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490'
run_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490/ownership-20261109'
run_dir="$run_root/before"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
module purge
module load gcc/14.3.0 openmpi/5.0.10_slurm cmake/4.4.0
module -t list
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false IPPL_OPENMP_THREADS=4
hostname
uname -a
ctest --test-dir "$job_root/build" -V -j1 --output-on-failure --output-junit "$run_dir/isolated.xml" -R '^TestFM2D(Dynamic|MagnetoStatic)$' 2>&1 | tee "$run_dir/isolated.log"
python3 "$run_root/before_parallel.py" "$job_root/build" "$run_dir"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json
r=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');p=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490/ownership-20261109')
text=(p/'before/inventory.json').read_text()
if text.endswith('\\n'):text=text[:-2]
m=json.loads(text)
for name,h in m['source_sha256'].items():assert hashlib.sha256((r/'src'/name).read_bytes()).hexdigest()==h,name
for name,h in m['binary_sha256'].items():assert hashlib.sha256((r/'build'/name).read_bytes()).hexdigest()==h,name
(p/'before/terminal-verification.json').write_text(json.dumps({'all_source_files_unchanged':True,'all_binary_hashes_unchanged':True,'original_helper_absent':not(r/'src/unit_tests/TemporaryDirectory.h').exists()},indent=2))
print('Verified original source and binaries unchanged')
VERIFY
