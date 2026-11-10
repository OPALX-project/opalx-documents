# OpenMP build
Goal: build this OPALX checkout in build-omp for the 2D5 solver work.
No build skill found in installed skills or local agent directories. Using README CMake workflow and existing local LLVM 21/libomp toolchain.
Configuration: Release, OPENMP, unit tests enabled, fetched project dependencies.
Next: configure, compile, run relevant tests and record results. No physics/source edits intended.
Configure succeeded with fresh fetched dependencies: IPPL master, Kokkos 5.2.0, Heffte 2.4.0, HDF5 2.2.0, H5hut cmake, LAPACK 3.12.1. Exact refs to be recorded after build.
Build running: cmake --build build-omp --parallel 8 > build-omp/build.log 2>&1.
Existing unrelated untracked ANNOUNCEMENTS.md and output/ left untouched.

Completed: full Release OpenMP build succeeded (all targets, parallel 8).
Binary: /Users/adelmann/git/opalx/build-omp/src/opalx
Validation: executable --version exited 0; ctest -j4 with OMP_NUM_THREADS=2, OMP_PROC_BIND=false passed all 138/138 registered tests (56.27 s), including registered MPI tests. Dedicated single-rank FFT2D5 CTest run passed 2/2.
Sandbox MPI launch initially failed before running tests; tests passed outside sandbox.
Additional manual two-rank FFT2D5 runs failed: Algorithm fixture explicitly disables partitioning in every dimension, causing FieldLayout initialization to reject two ranks; Numerics also fails on two ranks. These tests are registered for one rank. Two-rank FFT2D5 operation is therefore not validated by this build check. Logs preserved as fft2d5-{algorithm,numerics}-mpi2.log. No source changes made to accommodate tests.
No numerical tolerances changed. No pushes. Source diff reviewed with git diff --stat; existing unrelated untracked files preserved.
Next: binary ready for requested 2D5 simulation work.
