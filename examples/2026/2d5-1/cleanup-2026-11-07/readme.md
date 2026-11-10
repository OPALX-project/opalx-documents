# FFT2D5 cleanup: stage boundaries and CPU/GPU verification

The cleanup removes the compile-time IPPL comparison backend and its parameter wiring. The native cell-integrated free-space model remains the sole FFT2D5 transverse backend. The unused scalar line-density operator and stale numerical/diagnostic comments are removed. MPI Green initialization now allocates the workspace for its one transform; the single-rank row path allocates none of that unused scratch. No IPPL library, moment calculation, physics model or numerical tolerance is changed.

## Smaller methods

| Orchestrator | Before → after [source lines] | Subfunctionality |
|---|---:|---|
| `solveBatched` | 218 → 20 | Validate grid/indices; prepare buffers and Green; cache row plans; pack, transform, multiply and extract |
| `preparePathGeometryAndProjections` | 191 → 19 | Resize caches; build segments; build ordered-prefix hierarchy; project active containers |
| `migrateToSlabs` | 68 → 7 | Check domain; save logical coordinates; migrate ownership; restore Cartesian attributes/BC |

The new helpers stay in existing classes/files. CUDA-launching helpers remain public because of NVCC extended-lambda accessibility; their Doxygen marks them internal. Segment scoring, prefix addition order, box merges, tie breaking and stack fallback are retained. Deposition, line-density assembly, diagnostic serial/MPI slice paths and gathering are also separated into smaller responsibilities. The standalone benchmark separates validation and timing sweeps from each candidate's numerical stages.

Doxygen's XML source inventory finds no FFT2D5 production method above 56 lines. The remaining 56-line method is the existing exhaustive Cartesian-to-path conversion; the largest new helper is at most 51 lines. Benchmark helpers are also below one page. The definition counts include signature/internal comments and blank lines, excluding preceding Doxygen. See `function-sizes.csv` for actual source spans. Doxygen generation reports no warnings with internal documentation enabled, and all 86 new-function candidates have entries. Public configuration accessors, halo operations and mathematical helpers now have contracts rather than implicit or stale comments.

## Build and unit checks

Build directory: `/Users/adelmann/git/opalx/build-omp`, Release/OpenMP. The old executable is preserved at `src/opalx.pre-cleanup-20261107`, SHA256 `e77830e07e695f84baa45db5dc5c67a1fcafdb92dc84e4cec9254a38c0853e1c`. The cleanup binary is `src/opalx`, SHA256 `a26d0c24843d468e5315aa2c41e8c22740b41814b6a10fa0f5371c6f2488979f`. The CPU cleanup snapshot is committed as `25f742689` on base `e5f190d3b`. Both CPU binaries are retained. Follow-up commit `bf5bf8433` uses Kokkos device-safe epsilon/minimum-normal constants in the extracted geometry helper; these have the same values and produce the identical CPU executable hash. The focused CPU tests and two-rank MPI tests pass again after that change.

The six focused CTest targets pass with one and four OpenMP threads: `TestSpaceChargeConfig`, `TestFFT2D5Algorithm`, `TestFFT2D5Numerics`, `TestSpaceChargeSolver`, `TestPoissonSolver`, and `TestFFT2D5Parallel`. Both parallel tests also pass on two MPI ranks at each thread count. The exact serial-build/exhaustive geometry and projection checks remain unchanged. The standalone benchmark's 78 validation rows pass; maximum relative field error is 9.21×10⁻¹⁵ and potential error 4.21×10⁻¹⁶. No references or tolerances were relaxed.

## Same 100-step pilot

The paired CPU pilots use one OpenMP thread per rank, one/two MPI ranks, 100,000 matched particles, 5.602212334 nC, a 64×64×512 mesh, dt=3 ps, batch size 64 and the original OPEN longitudinal model. Both sides restart the same checkpoint and retain the original input settings.

| MPI ranks | Process wall before → after [s] | Steady SC before → after [ms/call] |
|---:|---:|---:|
| 1 | 16.280 → 16.153 | 79.972 → 79.777 |
| 2 | 8.962 → 8.874 | 51.407 → 50.687 |

Each configuration has one pair; the small timing differences do not establish a speedup. All 100,000 IDs, charge and final times are preserved. RMS and emittance differences are below 1.69×10⁻¹⁴ relative. Maximum endpoint position difference is 3.40×10⁻¹³ m and momentum difference 1.10×10⁻¹². Tracking is equivalent at reduction roundoff, rather than bitwise identical.

![Before/after CPU timings](timings.png)

Inputs, logs, statistics, runner commands, executable identities and audits are retained under `provenance`. Particle snapshots remain in `/Users/adelmann/git/opalx/tmp/2026-11-07-fft2d5-cleanup`; none are placed in this report. Reproduce with `analyze.py` in the OPALX Python environment, setting `OPALX_GEOMETRY_ROOT` if the native/cache directory differs.

No full-turn or 16-turn runs were made. The cleanup source and CPU results are committed and pushed; the following section records the CUDA follow-up.

## CUDA follow-up: one and two A100s

Merlin6 checks out `bf5bf84337e8e9e8839ba1b0fa7fe9960309dd4e` in `/psi/home/adelmann/opalx-dev/dba`. The Release build uses CUDA, Ampere80 and heFFTe CUDA; IPPL is unchanged. The old executable is preserved as `build/gwendolen-cuda/src/opalx.pre-cleanup-20261107`, SHA256 `981ce971edc5485c78f48525e517d8242ddbfd456e8e18ea5cf5f51ca1126c43`. The cleanup executable is `opalx.cleanup-20261107`, SHA256 `f58629eda10bdfcd2e587263ee73850288eba224697420633872075a2b053ea2`; it also remains the active `src/opalx` in that build directory.

The initial CUDA compilation found host-only `std::numeric_limits` calls in the extracted geometry helper. Follow-up commit `bf5bf8433` replaces them with the identical Kokkos numeric constants, without changing the expression or pruning tolerance. The initial jobs were stopped before testing/tracking; the completed replacement jobs are **355063** (build, unit tests, paired one-A100 pilots) and **355064** (two-rank unit tests and paired two-A100 pilots). Both completed with exit code 0. The production CUDA build has no warnings; the test build retains warnings about anonymous diagnostic types, an unused helper and signedness.

All 12 algorithm tests, 67 numerical tests and both parallel tests pass on one A100. One configuration test is skipped as expected on one rank. Both parallel tests also pass on two ranks. GPU probes verify one visible A100 per rank and distinct GPU UUIDs for the two-rank case.

Both sides of each pair run in the same allocation, with the same 100-step source, checkpoint and settings as the CPU pilots above, including longitudinal fields, `FFT2D5MODEL="ORIGINAL"`, `PIPEMODE="OPEN"`, `PARFFTZ=TRUE` and `STATDUMPFREQ=10`. The old executable is rerun rather than comparing wall times from different days. `source_commit` in each run JSON identifies the checkout at execution; the executable SHA identifies the before/after build.

| A100s / MPI ranks | Process wall before → after [s] | Steady SC before → after [ms/call] | Geometry + projections before → after [ms/call] |
|---:|---:|---:|---:|
| 1 | 8.367 → 8.474 | 3.924 → 3.902 | 0.4368 → 0.4369 |
| 2 | 10.959 → 10.797 | 5.882 → 5.819 | 0.4726 → 0.4826 |

Steady SC excludes initialization, warmup and the first physical solve (99 calls). Geometry and other phase averages cover all 100 physical steps, including the first; nested phase times must not be summed with their parent timers. Process wall includes launch/startup/reference-path work. Each case has one pair, so these small timing differences do not establish a speedup or regression. The cleanup preserves the previous scaling behavior.

All 100,000 IDs, total charge, final time and step count pass the snapshot audit. Maximum rms/emittance difference is **1.35×10⁻¹⁴ relative** against the previous executable; maximum particle endpoint position difference is **3.56×10⁻¹³ m**, and momentum difference is **1.80×10⁻¹²** in beta-gamma units. Tracking is equivalent at reduction roundoff, not bitwise identical. Across one/two ranks, the new build's maximum position difference is 3.53×10⁻¹² m and momentum difference is 1.47×10⁻¹².

![Before/after A100 timings](gpu-timings.png)

See `gpu-timings.csv`, `gpu-phases.csv`, `gpu-physics-audit.csv` and `provenance/gpu` for the timing breakdown, logs, inputs and audits. Reproduce with `analyze_gpu.py`, setting `OPALX_GEOMETRY_ROOT` to the native/cache directory. The native runs and particle snapshots remain at `/psi/home/adelmann/opalx-dev/dba/validation-cleanup-20261107`; the local cache is `/Users/adelmann/git/opalx/tmp/2026-11-07-fft2d5-cleanup`. No snapshots or executables are included in this repository. No full-turn or 16-turn runs were submitted.
