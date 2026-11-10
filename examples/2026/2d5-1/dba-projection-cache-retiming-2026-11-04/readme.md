# FFT2D5 retiming after projection caching

2026-11-04. Local commit 01bb3835ab7442c00f71cac5fb49bf77cba85661; no remote push. Unchanged build-omp executable SHA256 a38391aa99db0cf5e6813ca96bd03dac68246e6ad1b4c204857df314edc261a3. No source changes, rebuild or16turnrun.

Same100step DBA pilot:100k matched KV particles,5.602212nC,64x64x512,3ps,4OMP/1MPI,ORIGINAL transverse model, longitudinal NONE. Exact input/checkpoint hashes recorded in each manifest.

Unprofiled51.0958s; kernel-timer52.3190s (+2.39%); independent CPU-sampled54.5327s. Previous pre-cache baseline73.6520s: fresh unprofiled run30.63% faster. Sampling ran30s at2ms intervals during tracking; samples describe the main thread, not summed worker CPU time.

Measured blocking kernel wall times: particle projection11.2141s (21.45% of native wall), FFT pack/unpack6.5033s (12.44%), scatter0.11427s, gather0.07255s, geometry preparation0.00122s. Host FFT arithmetic lies outside these callbacks. All512slices occupied:51,200slice solves over100steps. Zero profiler callback errors/pending callbacks.

Independent main-thread stack samples: stock heFFTe FFT arithmetic/reshapes48.63%, other slice-solver/FFT interface18.79%, projection22.77%, runtime/waiting9.32%, other0.49%. These sample fractions must not be added to the kernel wall times. Three OpenMP worker threads spend76.19% of sampled stacks in runtime/waiting and22.48% in projection. Serial FFT arithmetic on the main thread is the leading target.

Priority candidates (not implemented or benchmarked):
1. Test an optimized CPU FFT backend through existing IPPL/heFFTe functionality. Current build has Heffte_ENABLE_FFTW=OFF and uses stock FFT. Preserve this executable before any rebuild. Compare identical pilot and endpoint fields/particles. Do not assume a speedup until measured.
2. Accelerate exact closest-segment search. Current projection still scans2606segments for each of100kparticles each solve (~260.6million segment candidates per step). Use conservative spatial bounds or a seeded search with a correctness-guaranteed fallback; retain global nearest-segment/tie/seam semantics. A local-neighbour-only search is not sufficient for general paths. Even complete elimination of measured projection saves only~21% of wall time.
3. Reduce per-slice FFT interface overhead or batch independent2D transforms. Current loop is sequential with a shared workspace; simply parallelizing it would race. Batching or separate bounded workspaces requires a separate design/test. FFT_toTemp/fromTemp alone account for6.50s. Existing plans and Green functions are already reused between slices. Do not introduce a3Dfield model or change mesh/SCcadence as a timing optimization.

Particle audits: kernel/sample runs retain all100,000IDs, correct total charge, finite state,100steps to300ps. Maximum laboratory endpoint differences versus pre-cache baseline: position3.91e-13m, momentum7.82e-13beta-gamma (bounds1e-9m and1e-10 respectively). No tolerance relaxed. Detailed CSV/JSON and reproducible runner/analysis scripts accompany this note; raw HDF5 outputs remain in the DBA comparison directory.
