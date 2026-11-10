#!/bin/bash -l
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=8
#SBATCH --gpus=3
#SBATCH --mem-per-gpu=124800M
#SBATCH --time=01:00:00
#SBATCH --job-name=2d5-density-batched
#SBATCH --output=/psi/home/adelmann/opalx-dev/dba/validation-longitudinal-batch-20261106/after-%j.out
set -euo pipefail
ROOT=/psi/home/adelmann/opalx-dev/dba
OUT=$ROOT/validation-longitudinal-batch-20261106
cd "$ROOT"
module load gcc/14.3.0 openmpi/5.0.10_slurm cuda/12.9.1 cmake/4.4.0
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPENBLAS_NUM_THREADS=1
sha256sum build/gwendolen-cuda/src/opalx.pre-longitudinal-density-20261106 > "$OUT/before-optimized-build.sha256"
tar xzf "$OUT/density-source.tgz"
touch src/SpaceCharge/FFT2D5/FFT2D5Algorithm.{h,hpp,cpp} src/SpaceCharge/SpaceChargeFactory.cpp unit_tests/SpaceCharge/TestFFT2D5{Algorithm,Numerics,Parallel}.cpp
cmake --build build/gwendolen-cuda -j24 --target opalx_exe TestFFT2D5Algorithm TestFFT2D5Numerics TestFFT2D5Parallel > "$OUT/build-after.log" 2>&1
sha256sum build/gwendolen-cuda/src/opalx > "$OUT/after-binary.sha256"
cd "$OUT"
for test in TestFFT2D5Algorithm TestFFT2D5Numerics; do
mpirun -np 1 --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/$test" > "after-$test.log" 2>&1
done
for ranks in 1 2 3; do
mpirun -np "$ranks" --map-by slot --bind-to none "$ROOT/validation-mpi-z-20261106/gpu_rank.sh" "$ROOT/build/gwendolen-cuda/unit_tests/SpaceCharge/TestFFT2D5Parallel" > "after-mpi$ranks.log" 2>&1
done
python3 run_gpu.py after
python3 profile_after.py
