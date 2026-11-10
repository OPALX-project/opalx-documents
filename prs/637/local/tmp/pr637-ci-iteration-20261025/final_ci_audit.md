Final read-only CI audit — PR #637
Checked 2026-10-25 22:01 UTC. Both git ls-remote and the GitHub PR API identify head a9d38caa4f88433a5de1508b3d5c7d01bdfea95a.

All 18 CSCS jobs are terminal: 15 successful and 3 failed. Each backend has both Debug/Release builds and all three native-test configurations successful; only its Release regression job fails.

Backend | Pipeline | Build Debug / Release | Native Debug1 / Release1 / Release4 | Regression
GH200 | 2987151470 | success / success | success / success / success | failed (known reference differences)
OpenMP | 2987151576 | success / success | success / success / success | failed (known reference differences)
MI300 | 2987151523 | success / success | success / success / success | failed (known reference differences)

Independent CDash GraphQL checks cover every native configuration: exactly 137 passed, 0 failed, 0 notrun. Every configure command identifies build-a9d38caa-*. Every configuration includes TestLossDataSinkMPI, TestRFEventStepMPI and TestCyclotronProbeMPI as PASSED, with actual srun -n 2 commands. RF and Probe are unfiltered; Loss uses the intentional four-case MPI contract filter matching CMake. CDash truncates passed-test output at 1024 bytes, so final per-rank Google Test counters are not available there. It shows two process-start banners for the RF/Probe tests.

GH200 CDash IDs: Debug1 4375360, Release1 4375358, Release4 4375357. Runtime durations: 270.43 s, 228.12 s, 220.83 s respectively.
OpenMP: Debug1 4375307, Release1 4375305, Release4 4375304.
MI300: Debug1 4375306, Release1 4375303, Release4 4375302.

GH200 compiler artifacts independently show 0 errors and 2 warnings in each Debug/Release build. Both warnings are the existing NVCC #20011-D Diagnostic/Snapshot destructor annotation pattern at TestRFEventStep.cpp:104 (compiled once per RF executable). Neither private-payload nor private-TestBody access errors remains.
Release job 17451990420: compiler summary 21:36:40.501 UTC, job completed 21:38:07.722 UTC (2521.945801 s).
Debug job 17451990419: compiler summary 21:37:44.004 UTC, job completed 21:39:25.509 UTC (2600.295008 s).

All three full regression runs compare 401 quantities: 396 passed, 2 FODO failed, 3 Scaling broken. Exact failure IDs/values match the previously diagnosed fixture differences:
- FodoCell-multipoleT-fromfile: rms_x(avg) 1.3061724278480717e-5 and emit_y(avg) 1.3184285918197022e-5 exceed tolerance 1e-5.
- ScalingFFABasicPlacements: mean_x, mean_y, mean_s reference/simulation row-size mismatch.
Both affected fixture reference checksum checks report OK. No extra comparison failure or new simulation/compiler/MPI failure appeared.
GH200 alone was additionally audited from its existing raw log: 39 actual case launches, 39 matching normal input-end markers, 39 Done executing ParallelTracker markers. Its internal native-unit rerun also passed 137/137 in 227.99 s. Its final regression exit1 is explicitly propagated to terminal job 17451990424 at 21:59:00 UTC.

The provenance agent independently retrieved all three final result XMLs: source a9d38caa4f88433a5de1508b3d5c7d01bdfea95a, actual regression checkout 737547e6ae38cf3001d6bc45cf38dd1a47d78402, and identical 396/2/3 counts. Exact NightlyBuildX runner SHA is unavailable in those XMLs; no inferred runner SHA is claimed.

GitHub combined status is failure, with all three CSCS contexts failed through their regression jobs. Seven separate GitHub Actions checks are skipped; they are not runtime validation evidence. The PR remains open at the exact monitored head.

The user requires reference updates remain local. No external baseline, CI wiring, job, source, test, or authentication changes were made during this audit. There were no reruns or new tests. All further polling has stopped.

Evidence:
- /tmp/pr637-a9-final-18-job-matrix.json
- /tmp/pr637-a9-final-github-statuses.json
- /tmp/pr637-a9-all-native-cdash.json
- /tmp/pr637-gh200-a9-build-summary.json
- /tmp/pr637-gh200-a9-release-compiler-diagnostics.json
- /tmp/pr637-gh200-a9-debug-compiler-diagnostics.json
- /tmp/pr637-gh200-a9-release-runtime-cdash.json
- /tmp/pr637-gh200-a9-release-runtime-mpi-outcomes.json
- /tmp/pr637-gh200-a9-regression-filtered.json
- /tmp/pr637-gh200-a9-regression-case-audit.json
- Provenance agent report in master/tmp/pr637-ci-iteration-20261025/ci-checkout-provenance-a9d38caa/
