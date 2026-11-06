# FFT2D5 status and timings, 5 November 2026

Work continues in ~/git/opalx on codex/fft2d5-explicit-original-model (PR667). The A100 build is /psi/home/adelmann/opalx-dev/dba/build/gwendolen-cuda. These pilot measurements use FFT2D5MODEL=ORIGINAL; no curvature-correction or 3D Coulomb solve is enabled. IPPL is unchanged.

## Changes and publication status

| Change | Purpose | Status |
|---|---|---|
| Frame handling, transverse cell fields, workspace reuse | Correct fields and reuse allocations | Pushed, 40856f1a2 |
| Precomputed path geometry and reused particle projections | Avoid repeated geometry/projection work within a solve | Pushed, 01bb3835a |
| Exact nearest-segment hierarchy | Accelerate projection while preserving segment selection | Pushed, a1ad007c8 |
| CPU slice batching | Group independent slices via existing heFFTe functionality | Pushed, a28af0417 |
| Release build with FFTW | Use optimized host FFT backend; FFTW threading experiment was removed | Build configuration |
| CUDA slice batching | Enable native device-buffer batching and GPU numerical checks | Pushed, daaf914b0 |
| CUDA occupancy launch fix | Replace a header-defined extended lambda with a named functor to avoid a null NVCC copy-helper call across translation units | Uncommitted; validated |

The Gaussian test correction (6301c2cab) and restart argument fix (07e6fbb54) are also pushed. The results archive is pushed in opalx-documents at d7ecdba. Unrelated local FFA/workflow changes remain untouched.

## DBA pilot performance

Same source/checkpoint: 100k matched KV particles, 5.602212333965894 nC, 64×64×512, 100 steps of 3 ps, one MPI rank. PIPEMODE=NONE is appropriate for the uniform coasting-beam longitudinal model. CPU uses four OpenMP threads on the laptop; GPU uses one A100. CPU serial has one timing; CPU batch8 and all GPU settings have two unprofiled repetitions. Counts are from separate Nsight traces and cover the whole invocation. The serial GPU trace uses the preserved pre-batching executable; new-executable serial tracking agrees with that reference.

| Implementation | Full wall time (s) | Time excluding OrbitThreader (s) | CUDA kernels | Device synchronizations |
|---|---:|---:|---:|---:|
| Laptop CPU, serial slices | 21.38 | 19.59 | — | — |
| Laptop CPU, batch8 | 11.02 | 9.16 | — | — |
| A100, serial slices | 59.44 | 17.17 | 1,447,837 | 736,041 |
| A100, batch1 | 56.00 | 12.28 | 884,839 | 378,141 |
| A100, batch8 | 50.96 | 9.04 | 705,639 | 154,141 |
| A100, batch32 | 50.56 | 8.70 | 686,439 | 130,141 |
| A100, batch64 | 50.55 | 8.62 | 683,239 | 126,141 |

Batch64 gives 1.99× GPU speedup excluding initialization, 52.8% fewer launches and 82.9% fewer device synchronizations. Batch32 is within 1%. GPU reference-orbit initialization remains about 39 s and dominates the short-run wall time. Time excluding OrbitThreader still includes other tracking bookkeeping and output; it is not a pure solver timer. CPU/GPU values are measurements on different machines. For this small mesh, optimized CPU and GPU tracking times are similar.

The later CUDA launch-fix smoke check retains 8.64 s for batch64 excluding initialization. It is a separate single repetition, not part of the timing averages above.

## Validation

Published ZeroSC/10pC bend repeats agree between GPU and current/published CPU rms/emittance curves; charged peak-normalized differences are below 1e-6 percent. Those bend cases include the longitudinal model, but GPU batching has not yet been repeated for that charged bend. The batch study and CUDA-fix pilots agree in all recorded rms sizes/emittances to roundoff (below 2e-12 percent of reference peaks). Endpoint coordinates, momenta, charge, IDs and final step/time are checked.

After the CUDA launch fix, all five checked GPU CTest targets pass, including 11/11 FFT2D5 algorithm tests with none skipped. FFT2D5 algorithm/numerical targets pass locally with one and four OpenMP threads. No tolerance was relaxed. No 16-turn run was started.

## Executable identities

| Executable SHA256 prefix | Source represented | Preservation |
|---|---|---|
| 5457c6bd | 6301c2cab, pre-GPU-batching production source | opalx.pre-gpu-batching-6301c2c |
| 103fa00f | 6301c2cab plus batching edits subsequently committed as daaf914b0 | opalx.pre-cuda-occupancy-daaf914b0 |
| 6bd5c3a4 | daaf914b0 plus uncommitted CUDA occupancy fix | Current remote src/opalx |

The two preserved files are next to the active executable in the remote build directory. Per-run manifests retain complete hashes. The CUDA fix and this overview remain uncommitted.

Next: commit the CUDA fix, validate batch64 on the published charged bend with longitudinal fields, then run a one-turn DBA check before proceeding to 16-turn tune calculations.
