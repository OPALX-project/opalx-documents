#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=8
#SBATCH --gpus=2
#SBATCH --mem=96G
#SBATCH --time=00:20:00
#SBATCH --job-name=ffa-school-790abac
set -euo pipefail
job_root="/data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643"
run_dir="$job_root/gpu-school"
mkdir -p "$run_dir"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
module purge
module load gcc/14.3.0
module load cuda/13.2.1
module load openmpi/5.0.10_slurm
module load cmake/4.4.0
module -t list
nvidia-smi --query-gpu=name,uuid,driver_version --format=csv
export OMP_NUM_THREADS=1
export IPPL_OPENMP_THREADS=1
sha256sum -c "$job_root/evidence/binaries.sha256"
python3 - <<'VERIFY'
from pathlib import Path
import hashlib,json,tarfile
root=Path('/data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643')
archive=root/'ffa-school-gpu-fixture-790abac19643.tar.gz'
metadata=json.loads((root/'ffa-school-gpu-fixture-790abac19643.json').read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==metadata['archive_sha256']
fixture=root/'gpu-school/fixture';fixture.mkdir()
with tarfile.open(archive) as tar:
    for member in tar.getmembers():
        assert member.isfile() and member.name in ['school.in','particles.dat','cpu-reference-manifest.json']
    tar.extractall(fixture)
for name,sha in metadata['files'].items():
    assert hashlib.sha256((fixture/name).read_bytes()).hexdigest()==sha,name
print('Verified unchanged school fixture:',json.dumps(metadata))
VERIFY
for ranks in 1 2; do
    target="$run_dir/r$ranks"
    mkdir "$target"
    cp "$run_dir/fixture/school.in" "$run_dir/fixture/particles.dat" "$target/"
    printf 'phase\trun-%s-ranks\n' "$ranks" >> "$run_dir/status.tsv"
    cd "$target"
    mpiexec --bind-to none -n "$ranks" python3 "$job_root/rank_gpu.py" "$job_root/build/bin/opalx" school.in --info 2 \
        > run.log 2>&1
    sha256sum school.in particles.dat > inputs-after.sha256
    printf 'run-%s-ranks\t0\n' "$ranks" >> "$run_dir/status.tsv"
done
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
