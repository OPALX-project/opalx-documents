# FFA probe efficiency and PR #667

Status: design discussion, 7 November 2026. User explicitly accepts performance optimization after parity with old OPAL results. No production edits, builds, simulations, branch changes, commits or pushes made for this review.

## Verified PR state and scope

Inspected through GitHub CLI: https://github.com/OPALX-project/OPALX/pull/667
Title: Fix and accelerate the original FFT2D5 solver.
At inspection: OPEN, not merged, head bf5bf84337e8e9e8839ba1b0fa7fe9960309dd4e; API updated_at 2026-11-07T09:41:56Z. Metadata, changed-file patches and selected pinned source files are saved in pr667-evidence/.

Its 24 changed files accelerate/fix FFT2D5: common particle/reference solve frames; projection reuse; an exact nearest-segment hierarchy; native FFT row/slice batching; batched longitudinal-density reductions; parallel geometry preparation; and MPI z-slab distribution. It does not change ParallelTracker, CyclotronProbeRecorder or probe crossing kernels. ParticleContainer gains lazily registered Cartesian scratch positions for spatial migration.

The latest cleanup pilot reports about 3.902 ms per steady SC call on one A100, for a 100-step DBA case. The earlier updated 63.1 min/turn estimate is an extrapolation from short complete-tracking calibration and measured SC savings, not a newly completed turn or a school FFA/probe benchmark. PR performance numbers must not be presented as predicted school runtimes or probe speedups. No PR tests or benchmark claims were independently rerun in this read-only review.

## Cost model and current recorder source facts

Let S be accepted particle-tracking steps per turn, P the number of stations and N the local particle count. The current observer scans O(S*P*N) particle/station combinations. This observer does not initiate a new TRACK run for each station. It runs once at the accepted-step boundary for each active container, outside integrator trial stages. COF/preparation must remain unobserved.

CyclotronProbeRecorder.cpp:120 loops over stations. Each station resets a device count (:126), performs a particle parallel_reduce (:128), executes an MPI_Allreduce for invalid state (:149), transfers the hit count (:152) and transfers compact hits (:153). The collective is executed even with no hits. Thus 16 stations mean 16 error allreduces per accepted step per active container, as well as host/device synchronization. This is a code fact, not measured elapsed overhead.

Example for scale only: S=400,000 and P=16 gives 6.4 million error allreduces per container per turn before output-related collectives. This illustrative S is not a measured step count for the supplied school cases. Exact S depends on orbit/energy, integration timestep and adaptive/boundary stepping.

The present recorder recomputes laboratory coordinate conversion and segment geometry per particle/station. Bidirectional histories duplicate previous endpoints. From fields and conventional ABI layout, the state is approximately 160 bytes per particle/station, so 16 stations would be about 2.56 GB for one million particles before other buffers. This is an uncompiled layout estimate; confirm sizeof and actual allocations per backend before using as measured memory.

Every 100 global tracking steps, save() flushes phase-space hits, reduces cumulative histograms, rewrites summaries and reduces each accumulated turn separately. Therefore output and summary work can grow with station count and run length even when crossings are sparse. Preserve bounded buffering and failure diagnostics while measuring this later.

## Required compatibility with PR #667

FFT2D5Algorithm::solve() transforms tracker coordinates to a solve frame and restores them before returning. MPI z decomposition temporarily puts projected coordinates in R, migrates all registered attributes, and restores Cartesian positions. Histories already contain laboratory endpoints and must migrate unchanged with particle IDs; they must not be transformed into temporary solver coordinates. Probe observation remains after accepted physical transport and coordinate restoration, at ParallelTracker.cpp:931-949. Never use temporary FFT2D5 projections as probe samples or reuse a solve-only cache after its frame/lifetime has ended.

The school PROBE milestone should integrate on the relevant updated base once the solver PR is available, while preserving a clear source baseline. FFT2D5 availability is independent of the first bare-FFA probe parity cases. No early merge or cherry-pick is necessary just to discuss/design probes.

## Agreed priority and recommended sequence

1. Implement the shared passive FFA observer and agreed native-output/school-adapter contract. Establish raw-hit geometry, identity, turn, phase-space and timestep-convergence parity against matched old OPAL runs. Exact legacy file equality is not the target because event interpolation and coordinate conventions differ.
2. Retain existing compact-hit output, accepted-step-only sampling, registered migration history and bounded flushing. Keep the no-PROBE path free of probe allocation/work. Avoid new per-station host gathers or solver coupling.
3. Record short representative probe-off/4-station/16-station timings during validation, using the same executable, particle states, timestep, output settings and MPI/GPU configuration. Separate crossing detection, transforms, synchronization/communication, migration memory and file output. Do not require long full-turn runs merely to measure a per-step cost.
4. After parity, optimize according to measurements: fuse station loops and aggregate error reductions; convert each accepted endpoint to laboratory once per particle; precompute immutable detector geometry; share one previous lab endpoint per particle with station-specific arming/counters; batch compact extraction; aggregate turn-summary reductions and avoid unchanged summary rewrites. Preserve stable-ID and CUDA ownership contracts.

Do not reduce sampling to every k-th accepted step as a shortcut. It can miss crossings or hidden recrossings and alters the event-location approximation. Use conservative candidate rejection/batching only when completeness and crossing results can be verified. Do not loosen physics/event tolerances or rebaseline old results to obtain a speedup.
