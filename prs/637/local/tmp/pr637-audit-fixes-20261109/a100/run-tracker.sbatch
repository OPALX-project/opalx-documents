#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --gpus=2
#SBATCH --mem=32G
#SBATCH --time=00:15:00
#SBATCH --job-name=pr637-tracker-gpu
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/pr637-audit-fixes-20261109/3320cf6fc490'
run_dir="$job_root/gpu-integration"
mkdir "$run_dir"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
module purge
module load gcc/14.3.0 cuda/13.2.1 openmpi/5.0.10_slurm cmake/4.4.0
module -t list
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv
export OMP_NUM_THREADS=1 IPPL_OPENMP_THREADS=1
cd "$job_root"
sha256sum --check evidence/binaries.sha256
python3 - <<'UNPACK'
from pathlib import Path
import hashlib,json,tarfile
root=Path.cwd();archive=root/'gpu-integration-fixture.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='559eb9abc34b6b3323be9ed1838759807e233b25937005b083b40678c7ef9943'
fixture=root/'gpu-integration/fixture';fixture.mkdir()
with tarfile.open(archive) as tar:
    for m in tar.getmembers():
        p=Path(m.name);assert not p.is_absolute() and '..' not in p.parts
        assert m.isfile() or m.isdir()
    tar.extractall(fixture)
m=json.loads((fixture/'fixture-manifest.json').read_text())
for name,sha in m['files'].items():assert hashlib.sha256((fixture/name).read_bytes()).hexdigest()==sha,name
assert m['source_id']=='3320cf6fc490a8be7dc2a33468b35cd99804cf179fd13d07f4d62d00e4bc2ae3'
(root/'gpu-integration/fixture-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('Verified unchanged13fixture/referencefiles',flush=True)
UNPACK
printf 'phase\trun\n' >> "$run_dir/status.tsv"
python3 "$job_root/run_tracker_gpu.py"
sha256sum --check evidence/binaries.sha256
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
