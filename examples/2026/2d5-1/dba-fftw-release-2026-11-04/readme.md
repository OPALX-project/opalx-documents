# FFTW Release build and pilot

2026-11-04. OPALX branch codex/fft2d5-explicit-original-model, commit 01bb3835ab7442c00f71cac5fb49bf77cba85661. No source edits or remote push.

Installed FFTW3.3.11 from https://www.fftw.org/download.html under /Users/adelmann/git/fftw. Source tarball SHA256 5630c24cdeb33b131612f7eb4b1a9934234754f9f388ff8617458d0be6f239a1. Double and float, shared/static, ARM NEON, OpenMP, clang21 with -O3 -mcpu=native. Both FFTW make check suites passed. OpenMP uses existing /opt/homebrew/opt/libomp; no additional runtime installed.

OPALX build directory /Users/adelmann/git/opalx/build-omp. CMAKE_BUILD_TYPE=Release; -O3 -DNDEBUG -fopenmp=libomp; Heffte_ENABLE_FFTW=ON; FFTW_ROOT=/Users/adelmann/git/fftw. Existing configuration was already Release. IPPL automatically selects FFTW host backend. Executable linkage verified to the installed double/float FFTW libraries; unresolved FFTW plan/execute symbols verified. No physics/model change. FFTW OpenMP libraries are available; this does not establish multithreaded FFT execution in heFFTe.

Current executable /Users/adelmann/git/opalx/build-omp/src/opalx SHA256 9b4a00eae1cd121dbcb00dfed6cdd46c1f34f7131f597e72973a56686f77a2c2.
Previous stock executable preserved /Users/adelmann/git/opalx/build-omp/previous/opalx-a38391aa99db-stock SHA256 a38391aa99db0cf5e6813ca96bd03dac68246e6ad1b4c204857df314edc261a3.

Reconfigure: cmake -S /Users/adelmann/git/opalx -B /Users/adelmann/git/opalx/build-omp -DCMAKE_BUILD_TYPE=Release -DHeffte_ENABLE_FFTW=ON -DFFTW_ROOT=/Users/adelmann/git/fftw
Build executable target: cmake --build /Users/adelmann/git/opalx/build-omp --target opalx_exe -j4
The lowercase opalx target builds the library only; opalx_exe links the executable. Configuration/cache and full build/test logs archived in /Users/adelmann/git/opalx/tmp/2026-11-04-fftw-release.

Four CTest targets TestSpaceChargeConfig, TestFFT2D5Algorithm, TestFFT2D5Numerics, TestPoissonSolver pass with OMP1 andOMP4. Two-rank unsupported-FFT2D5 rejection test passes both ranks. GPU not tested.

Identical100step DBA pilot: 100k matchedKV particles,5.602212nC,64x64x512,3ps,4OMP/1MPI,ORIGINAL transverse model, longitudinal NONE,PARFFT flagsFALSE. Same input/checkpoint/source hashes verified. Current FFTW elapsed 32.71144s, fresh stock repeat 51.09580s: 1.562x speedup, 35.98% less time. One FFTW timing repeat; no long campaign.

All100,000IDs retained,correct charge,finite arrays,100steps to300ps. Lab endpoint maxdifference position 3.6543e-13m, momentum 7.8133e-13beta-gamma; all10statRMS/emittance samples maxrelative difference1.294e-14. QA bounds unchanged at1e-9m,1e-10beta-gamma,1e-8relativeRMS/emittance. No physics tolerance changed.

Raw outputs and reproducible scripts: /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-fftw-release; runners run_dba_fftw_pilot.py and analyze_dba_fftw_pilot.py in parent directory. Unrelated working edits hash-verified unchanged. No16turnruns.
