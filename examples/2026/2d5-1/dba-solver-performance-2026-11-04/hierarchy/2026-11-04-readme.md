# Exact FFT2D5 nearest-segment search

2026-11-04. Local changes on codex/fft2d5-explicit-original-model, base commit 01bb3835ab7442c00f71cac5fb49bf77cba85661. No commit or push in this task. Built only /Users/adelmann/git/opalx/build-omp, Release (-O3 -DNDEBUG), OpenMP, FFTW3.3.11 enabled. No field-model, mesh, timestep, SC cadence or boundary-condition changes. No16turnruns.

## Implementation

A balanced implicit hierarchy stores axis-aligned endpoint boxes for contiguous path segments. Leaves follow the original segment order; power-of-two padding uses empty boxes. Rebuild the hierarchy in the existing geometry preparation kernel each solve, in the aligned solve frame. The previous cached segment supplies only an initial distance upper bound. All nodes capable of containing a winner remain eligible; particle movement, reordering and path-frame changes cannot restrict search to neighbouring indices.

Leaf calculations retain the exhaustive implementation's direction, clamped fraction, closest point, squared distance, tangent and cached arc-length arithmetic. Exact computed distance ties choose the lowest segment index, matching the original increasing scan. Conservative pruning includes256*epsilon*L^2+256*min_normal squared-distance slack, where L bounds absolute particle and path coordinates. This accounts for rounded interpolation/box-distance operations and subnormal distances; it changes only whether a box is explored, never the segment scoring or a physics tolerance. Borderline or overflow comparisons descend. A fixed64-entry local traversal stack has an exhaustive fallback. Worst case remains exhaustive O(N*M), e.g. strongly overlapping boxes or conservative margins after very large translations. GPU execution/performance has not been checked; ordinary IEEE arithmetic without fast-math is assumed.

No new solver classes or source files. Changes: FFT2D5Algorithm.cpp/.h; existing TestFFT2D5Algorithm.cpp and its README. The existing internal verification interface now exposes preparation and cache views to tests. Doxygen describes the hierarchy, rounding guard, seed/tie handling, lifetime, memory and fallback.

For2606segments:4096heap leaves,8192nodes,393216extra bytes (~0.375MiB). Geometry plus100kparticle caches and bounds total3718304bytes (~3.55MiB), shared across OpenMP workers. The64-entry per-particle traversal stack is transient kernel storage, not a persistent N-by-M allocation.

## Exact search and unit validation

The new numerical test compares selected segment indices and all three cached coordinates to an independent exhaustive scan, using exact equality (no tolerance). It checks43540entries over seven geometries and three source preparations: straight and self-intersecting paths, non-power-of-two segment counts, repeated vertices/segments, endpoint and adjacent-float probes, first-index ties, invalid particles, reused stale seeds after movement/reordering, cache growth, translations of1e8, scales1e-140/1e140 and subnormal squared lengths at1e-160. Twenty-one entries are invalid sentinels. Existing tests separately compare full charge density and electric/magnetic fields with uncached stages, including frame changes, inactive containers and exceptions.

Four CTest targets pass with both OMP1 andOMP4: TestSpaceChargeConfig, TestFFT2D5Algorithm, TestFFT2D5Numerics, TestPoissonSolver. The existing two-rank rejection test passes on both ranks; distributed FFT2D5 remains unsupported. Doxygen generated with zero warnings. Diff whitespace and scope reviewed; unrelated working changes hash-verified unchanged. No numerical tolerance relaxed. Initial test compile required materializing a vector expression before euclidean_norm; corrected before the final build/tests. Analysis was initially invoked while the profile manifest was incomplete; it now skips unfinished runs and final analysis passed.

## Identical 100-step tracking pilot

100k matched KV particles,5.602212333965894nC,64x64x512,3ps,4OMP/1MPI,ORIGINAL transverse model, longitudinal NONE,PARFFTflagsFALSE. Same input SHA f6692da8991aadf01282f7811183427c78e649ac5266c3b11bb5ecf813185f38 and checkpoint SHA4d6adf38da35d9168f9cdb10847786eb1ea64d27e13e521211173901037e19f5. Raw manifests record binary/source identities for each run.

| Run | Elapsed wall time |
|---|---:|
| Preserved exhaustive FFTW baseline |32.71144s|
| Hierarchy, repeat1 |21.81368s|
| Hierarchy, repeat2 |21.26740s|
| Hierarchy, kernel-profiled |21.43313s|

Unprofiled mean 21.54054s: 34.15% less time, 1.519x speedup. The previous baseline and new repeats were sequential pilot measurements on the same laptop; small timing variations remain.

Projection kernel over100solves: 10.855881s exhaustive versus0.395936s hierarchy (27.42x faster). Geometry+hierarchy preparation0.002280s. FFT buffer copies now dominate individual kernel costs at6.408612s. Profiler callbacks report zero errors/pending callbacks. A subsequent fresh CPU-stack sample is recorded below.

All new runs retain100,000particle IDs, correct charge, finite arrays,100steps to300ps/globalstep99. Relative to exhaustive FFTW baseline: maximum lab endpoint displacement3.8209e-13m; momentum difference1.4423e-12beta-gamma. All10statRMS/emittance samples have maximum relative difference1.2186e-14. Search outputs match exactly in the direct oracle tests; complete tracking outputs agree at floating-point reduction roundoff, rather than bit-for-bit. Numerical QA bounds1e-9m,1e-10beta-gamma and1e-8relativeRMS/emittance remain unchanged.

Current executable SHA256 d2c0add433c40f47557d354323093f1d3949835defff5945bcb7337e7223f4d1. Previous executable preserved byte-for-byte at /Users/adelmann/git/opalx/build-omp/previous/opalx-9b4a00eae1cd-exhaustive, SHA256 9b4a00eae1cd121dbcb00dfed6cdd46c1f34f7131f597e72973a56686f77a2c2. No archived executable was used for new runs; all new runs use build-omp/src/opalx. Scoped source diff SHA256 f075e8a68b60a92540b1d5e63a4129eaeb9b0db950313b6caebdee7bb73fc3bb.

Raw HDF5outputs, exact input and logs: /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-exact-search. Reproducible runner/analysis/plot scripts, scoped patch, build/test records, comparisons and PNG/PDF accompany this report. Next candidate is reducing redundant real/complex FFT buffer transfers in IPPL; no such change was made here.

## Fresh hierarchy CPU sample

A separate unchanged100step hierarchy-build pilot was sampled for15seconds at2ms intervals during tracking. Its elapsed wall time was22.59037s. Main-thread exclusive stack samples: slice-solver/FFT interface50.25%, runtime/waiting24.48%, FFTW/heFFTe arithmetic/reshaping22.02%, projection2.17%, deposition/gathering0.83%, otherhost0.25%. Three OpenMP workers spend94.93% of samples in runtime/waiting. These sampled fractions are separate from the left-panel blocking wall measurements and must not be added to them. The figure now uses this fresh sample on the right. The main measured optimization target remains FFT-buffer transfers and slice-interface overhead.

All100,000IDs, correct charge, finitearrays and final300ps/globalstep99 verified against the hierarchy unprofiled run. Max labposition difference4.156e-13m, momentum7.812e-13beta-gamma; RMS/emittance relative differences<=1.163e-14. Binary and source hashes match the validated hierarchy build. No rebuild/sourcechanges or16turnruns.
