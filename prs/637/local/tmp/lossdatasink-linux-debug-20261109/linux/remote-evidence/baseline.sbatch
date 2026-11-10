#!/bin/bash
#SBATCH --clusters=gmerlin6
#SBATCH --partition=gwendolen
#SBATCH --account=gwendolen
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=01:00:00
#SBATCH --job-name=loss-sink-debug
set -euo pipefail
job_root='/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490'
source_dir="$job_root/src"
build_dir="$job_root/build"
run_dir="$job_root/evidence"
exec > >(tee -a "$run_dir/job.log") 2>&1
trap 'status=$?; printf "exit\t%s\n" "$status" >> "$run_dir/status.tsv"' EXIT
printf 'job\t%s\n' "${SLURM_JOB_ID:?}" > "$run_dir/status.tsv"
date -u
hostname
uname -a
module purge
module load gcc/14.3.0 openmpi/5.0.10_slurm cmake/4.4.0
module -t list
mpicxx --showme
export OMP_NUM_THREADS=4 OMP_PROC_BIND=false IPPL_OPENMP_THREADS=4
cd "$source_dir"
printf 'phase\tconfigure\n' >> "$run_dir/status.tsv"
cmake --fresh -S . -B "$build_dir" \
    -DPLATFORMS=OPENMP -DIPPL_GIT_TAG=3.4.0 -DCMAKE_BUILD_TYPE=Debug -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_Fortran_COMPILER="$(command -v gfortran)" \
    -DOPALX_ENABLE_TESTS=OFF -DOPALX_ENABLE_UNIT_TESTS=ON -DBUILD_TESTING=ON \
    -DFETCHCONTENT_SOURCE_DIR_IPPL="$job_root/deps/ippl-src" \
    -DFETCHCONTENT_SOURCE_DIR_KOKKOS="$job_root/deps/kokkos-src" \
    -DFETCHCONTENT_SOURCE_DIR_HEFFTE="$job_root/deps/heffte-src" \
    -DFETCHCONTENT_SOURCE_DIR_GTEST="$job_root/deps/gtest-src" \
    -DFETCHCONTENT_SOURCE_DIR_H5HUT="$job_root/deps/h5hut-src" \
    -DFETCHCONTENT_SOURCE_DIR_HDF5="$job_root/deps/hdf5-src" \
    -DFETCHCONTENT_SOURCE_DIR_OPALX_LAPACK="$job_root/deps/opalx_lapack-src" \
    -DMPIEXEC_EXECUTABLE="$(command -v mpiexec)" '-DMPIEXEC_PREFLAGS=--bind-to;none' \
    2>&1 | tee "$run_dir/configure.log"
printf 'phase\tbuild\n' >> "$run_dir/status.tsv"
cmake --build "$build_dir" --parallel 32 --target TestLossDataSink TestLossDataSinkMPI \
    2>&1 | tee "$run_dir/build.log"
printf 'phase\tisolated-controls\n' >> "$run_dir/status.tsv"
ctest --test-dir "$build_dir" -V -j1 --output-on-failure \
    --output-junit "$run_dir/isolated.xml" -R '^TestLossDataSink(MPI)?$' \
    2>&1 | tee "$run_dir/isolated.log"
printf 'phase\tparallel-stress\n' >> "$run_dir/status.tsv"
python3 "$job_root/parallel_stress.py" "$build_dir" "$run_dir"
sha256sum "$build_dir/lib/libopalx.so" "$build_dir/bin/TestLossDataSink" "$build_dir/bin/TestLossDataSinkMPI" > "$run_dir/binaries.sha256"
printf 'phase\tcomplete\n' >> "$run_dir/status.tsv"
date -u
