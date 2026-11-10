# GPU execution verification

Nsight Systems traced the unchanged Release CUDA executable at commit 6301c2cab10bf164e6d1ea60de5d0d25cdd0ca8a on one A100, one MPI rank. Slurm job 354971. The original 100-step DBA pilot used 100,000 particles and a 64×64×512 mesh, with the original restart checkpoint and serial slices. No build or production-source change was made. Binary SHA256 before and after: 5457c6bd1197b5151a95e295936234e148d7263eb6d5dc99690408609334c17e.

The runtime trace contains CUDA kernels for path geometry/projections, deposition, convolution, field differentiation and gathering, plus cuFFT vector_fft/r2c/c2r kernels and heFFTe CUDA transpose kernels. This verifies device execution directly. The pilot disables longitudinal fields (PIPEMODE NONE), so this trace does not measure that model.

Across the entire native invocation, 1,447,837 CUDA kernels consumed 9.656121377 seconds of summed kernel duration: heFFTe rearrangement/scaling 63.253%, IPPL FFT device copies 10.216%, cuFFT 9.855%, FFT2D5 Kokkos kernels 12.482%, other kernels 4.194%. The categories are disjoint kernel-name classifications; full names and individual totals are retained. This sum is not GPU utilization, and percentages are of summed kernel time, not elapsed time.

CUDA API records include 736,041 cudaDeviceSynchronize calls (8.225 s), and cudaLaunchKernel plus cuLaunchKernel calls (6.796 s). API durations can include device work/waiting and must not be added to kernel times to infer CPU arithmetic. Device-to-device transfers dominate transfer time. Host-device transfers consume about 0.150 s in total.

The CPU still performs reference-orbit tracing: OrbitThreader 39.5725 s in this traced run. It also orchestrates slice loops, MPI and output. Profiled mainTimer is 60.3606 s; use the separate unprofiled runs for performance comparisons. Small per-slice operations, rearrangements and frequent synchronization limit the benefit of CUDA. No IPPL changes were made.

The raw dba.nsys-rep and SQLite database remain on Merlin6 at /psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/gpu-execution-proof-354971. CSV summaries, analysis script, launch script and executable checksums are stored here.
