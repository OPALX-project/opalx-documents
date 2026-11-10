#!/bin/bash
set -euo pipefail
cd /psi/home/adelmann/opalx-dev/dba
OUT=$PWD/validation-a100-20261105/cuda-occupancy-fix
mkdir -p "$OUT"
git diff --binary > "$OUT/pre-update.patch"
git fetch origin codex/fft2d5-explicit-original-model
python3 - <<'CHECK'
import subprocess
files=set(subprocess.check_output(['git','diff','--name-only'],text=True).splitlines())
assert files <= {'src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp','src/SpaceCharge/FFT2D5/FFT2D5Poisson.h','unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp','unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp'},files
CHECK
git diff --quiet origin/codex/fft2d5-explicit-original-model -- src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp src/SpaceCharge/FFT2D5/FFT2D5Poisson.h unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp
git restore --source=HEAD -- src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp src/SpaceCharge/FFT2D5/FFT2D5Poisson.h unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp
git merge --ff-only origin/codex/fft2d5-explicit-original-model
cp cuda-fix-header.hpp src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp
cp cuda-fix-build.sbatch "$OUT/build.sbatch"
sbatch "$OUT/build.sbatch"
