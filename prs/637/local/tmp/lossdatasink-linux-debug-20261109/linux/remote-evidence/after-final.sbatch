#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=00:30:00
#SBATCH --job-name=loss-sink-final
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490'
source_dir="$job_root/src"
build_dir="$job_root/build"
run_dir="$job_root/evidence-final"
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
import hashlib,json
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');source=root/'src';m=json.loads((source/'source-manifest.json').read_text())
for name,digest in m['files'].items():
 expected='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6' if name=='unit_tests/Structure/TestLossDataSink.cpp' else digest
 assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected,name
(root/'evidence-final/source-verification.json').write_text(json.dumps({'base_source_id':m['source_id'],'files_verified':len(m['files']),'changed_file':'unit_tests/Structure/TestLossDataSink.cpp','after_sha256':'c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6','other_verified_files':len(m['files'])-1},indent=2)+'\n')
lib=root/'build/src/libopalx.so'
current_lib=hashlib.sha256(lib.read_bytes()).hexdigest()
baseline_lib=(root/'evidence/binaries-corrected.sha256').read_text().splitlines()[0].split()[0]
assert current_lib==baseline_lib,'Production library changed unexpectedly'
(root/'evidence-final/library-before.sha256').write_text(current_lib+'\n')
# Updating metadata ensures GNU make rebuilds both policies from the fixed bytes.
(source/'unit_tests/Structure/TestLossDataSink.cpp').touch()
VERIFY
printf 'phase\trebuild-fixed-targets\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel 16 --target TestLossDataSink TestLossDataSinkMPI \
 2>&1 | tee "$run_dir/rebuild-fixed-targets.log"
printf 'phase\tverify-fixed-binaries\n' >> "$run_dir/status.tsv"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');source=root/'src/unit_tests/Structure/TestLossDataSink.cpp';rows={}
assert hashlib.sha256((root/'build/src/libopalx.so').read_bytes()).hexdigest()==(root/'evidence-final/library-before.sha256').read_text().strip()
for name in ['TestLossDataSink','TestLossDataSinkMPI']:
 obj=root/'build/unit_tests/Structure/CMakeFiles'/(name+'.dir')/'TestLossDataSink.cpp.o'
 binary=root/'build/unit_tests/Structure'/name;baseline=root/'evidence'/('baseline-'+name)
 data=binary.read_bytes();digest=hashlib.sha256(data).hexdigest();old=hashlib.sha256(baseline.read_bytes()).hexdigest()
 assert digest!=old,name
 assert obj.stat().st_mtime>=source.stat().st_mtime,name
 assert binary.stat().st_mtime>=obj.stat().st_mtime,name
 for leaf in [b'test_monitor_checkpoint_rewind.h5',b'test_monitor_checkpoint_keep_all.h5',b'test_monitor_checkpoint_missing_step.h5',b'test_monitor_checkpoint_compaction.h5']:assert leaf not in data,(name,leaf)
 assert b'checkpoint-rewind' in data,name
 rows[name]={'sha256':digest,'baseline_sha256':old,'source_mtime':source.stat().st_mtime,'object_mtime':obj.stat().st_mtime,'binary_mtime':binary.stat().st_mtime,'old_fixed_names_absent':True,'new_owned_directory_label_present':True}
(root/'evidence-final/binary-verification.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
VERIFY
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
r=json.loads((root/'evidence-final/parallel-summary.json').read_text());assert len(r['runs'])==100 and r['failed_runs']==0,r
print('Verified1072sourcefiles withonlyintendedtestfix;100concurrentpairiterationspass')
VERIFY
sha256sum "$build_dir/src/libopalx.so" "$build_dir/unit_tests/Structure/TestLossDataSink" "$build_dir/unit_tests/Structure/TestLossDataSinkMPI" > "$run_dir/binaries.sha256"
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
