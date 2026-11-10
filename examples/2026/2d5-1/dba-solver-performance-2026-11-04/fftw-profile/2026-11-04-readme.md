# FFTW FFT2D5 profile

2026-11-04. Unchanged Release/OpenMP executable ~/git/opalx/build-omp/src/opalx, SHA256 9b4a00eae1cd121dbcb00dfed6cdd46c1f34f7131f597e72973a56686f77a2c2; commit01bb3835a. FFTW3.3.11. No rebuild, source changes, push or16turnruns.

Same DBA pilot:100steps,3ps,100kmatchedKV particles,5.602212nC,64x64x512,4OMP/1MPI,ORIGINAL transverse SC, longitudinal NONE,PARFFTflagsFALSE. Input/checkpoint hashes match the prior pilot; all512slices occupied. Separate sequential runs used the existing Kokkos blocking kernel timer and a20second CPU sample at2ms intervals. No added profiler fences. Zero callback errors/pending callbacks.

Runtime: unprofiled baseline32.7114s; kernel-profiled32.1331s; CPU-sampled33.1849s. These small differences are timing variability, not a negative profiler cost. Internal native mainTimer32.0811s excludes~0.052s process wrapper overhead. Earlier stockFFT kernel-profile native mainTimer52.2679s.

Measured nonoverlapping blocking wall groups (kernel run):
- Particle projection10.8559s (33.84%). Geometry preparation0.00130s.
- FFT pack/unpack6.50236s (20.27%);204,806calls each of FFT_toTemp and FFT_fromTemp.
- Scatter0.11108s andgather0.07111s (~0.57% together).
- Other Kokkos kernels8.04060s (~25.06%). This includes tracking frame transforms (~2.39s), slice copies, coupling, Green multiplication, finite differences and zeroing.
- Work outside callbacks6.49877s (~20.26%), including FFTW arithmetic, other host work and initialization. This is a residual, not a direct FFT timer.

Independent main-thread stack samples during tracking: projection37.04%, slice-solver/FFT interface32.43%, FFTW/heFFTe arithmetic/reshapes13.88%, runtime/waiting15.98%, other0.67%. Sampling fractions differ from whole-run wall fractions and must not be added to them. Three OpenMP workers spend61.50% in runtime/waiting,36.69% inprojection,1.48% inFFTinterface and0.33% indeposit/gather. FFTW OpenMP libraries are linked, but the production heFFTe path contains no fftw_init_threads/fftw_plan_with_nthreads calls (these exist only in its benchmark code). Linking omp libraries alone does not make these transforms multithreaded.

Next improvements, in priority order:
1. Exact nearest-segment acceleration. Current cache projects eachparticle once persolve but still scans all2606segments (~260.6million candidates perstep). Use conservative spatial bounds to reject distant segments while preserving exact global closest-segment, first-tie and seam semantics; use the previous segment as an initial distance bound, with a full correctness-guaranteed search/fallback. Compare against the exhaustive implementation for curved paths, corners/seams and particle movement. Largest measured individual target is10.86s; no speedup claim until implemented and measured.
2. Reduce FFT buffer copies using the existing IPPL interface. FFT/Transform/RC.h copies both real andcomplex fields to temporaries andback for each direction; forward has one logical input/output andbackward reverses them. Audit backend input destruction and the public mutation contract before omitting copies. Direction-aware input/output transfers could remove redundant work; half of measured6.50s is~3.25s (~10% of total), an illustrative upper opportunity for removing half the copy work, not a measured speedup. Add transform roundtrip/input-preservation tests andrerun thispilot. This change belongs inIPPL.
3. Consider batching independent2Dslice transforms or reducing small OpenMP launches/fences after1/2. Current51,200slice solves use a shared workspace sequentially. A plain parallel loop would race. Batched2DFFTs or bounded independent workspaces need explicit design andtests; do not replace this with a3Dphysics solve. Threading each small128x128padded transform may cost more in overhead andmust be benchmarked. Existing plans/Greenfunctions are already reused.

Numerical validation against unprofiled FFTW run: both profiles retain100,000IDs, correct charge, finitearrays,100steps to300ps/globalstep99. Max labendpoint differences3.43e-13m and1.445e-12beta-gamma. All10statRMS/emittance samples maxrelative difference1.069e-14. Existing QA bounds1e-9m,1e-10beta-gamma and1e-8relativeRMS/emittance pass; no physics tolerance changed. No tests or source changes needed for read-only profiling.

Raw HDF5outputs and full CPUstack sample remain in /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-fftw-profile. Reproducible runner/analysis/plot scripts accompany this report. Figure separates walltimers from CPU-stack evidence. Profiling is limited to this100step pilot; no fullturn/tune claim.
