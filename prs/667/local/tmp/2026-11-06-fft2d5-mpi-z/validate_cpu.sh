#!/bin/zsh
set -eu
cd /Users/adelmann/git/opalx
export OMP_NUM_THREADS=1 OMP_PROC_BIND=false
for n in 1 2 4; do
 /opt/homebrew/bin/mpirun --oversubscribe -n "$n" build-omp/unit_tests/SpaceCharge/TestFFT2D5Parallel > "tmp/2026-11-06-fft2d5-mpi-z/unit-mpi-$n.log" 2>&1
done
ctest --test-dir build-omp -R '^(TestFFT2D5Algorithm|TestFFT2D5Numerics|TestSpaceChargeConfig|TestFFT2D5Parallel)$' --output-on-failure > tmp/2026-11-06-fft2d5-mpi-z/unit-final.log 2>&1
OMP_NUM_THREADS=4 ctest --test-dir build-omp -R '^(TestFFT2D5Algorithm|TestFFT2D5Numerics|TestSpaceChargeConfig|TestFFT2D5Parallel)$' --output-on-failure > tmp/2026-11-06-fft2d5-mpi-z/unit-final-omp4.log 2>&1
/Users/adelmann/.venv-h6/bin/python tmp/2026-11-06-fft2d5-mpi-z/run_cpu.py
