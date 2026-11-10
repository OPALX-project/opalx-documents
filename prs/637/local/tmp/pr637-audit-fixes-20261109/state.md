# PR #637 small audit fixes

Status: complete, 9 November 2026. No commit or push. Source changes remain unstaged on `codex/ffa-probes-school-parity`, based on published PR head `b1551b9c3`.

Goal: fix audit items 2, 5 and 6; run relevant tests; issue the deferred work and link it from the PR.

Changed six files are listed and hashed in `intended-files.json`; the reviewable diff is `audit-fixes.patch`.

- Persistent scalar failure storage replaces per-particle/per-step global diagnostics. Only failing threads claim/write a coherent record; the host reads after kernel completion.
- The common sector evaluator returns support status and owns the predicate. Finite field arithmetic/boundaries are unchanged; nonfinite coordinates are safely rejected.
- Common RF validation runs once. Setup and host stepping are extracted. The device kernel stays in the existing public integration method for NVCC, without adding public API. Host 65-gap acceptance and device 64-gap cap are preserved.

Validation: 9/9 focused CPU targets; 6/6 A100 CUDA targets with 111/111 case executions and no skips; four byte-identical CPU before/after bunch cases; eight dispatch/failure guards; four actual GPU tracker cases on one/two ranks. Source snapshot `3320cf6fc490` verifies all 1,072 files and all six local hashes. GPU/CPU position difference is at most 6.867e-15 m. No numerical tolerance changes.

Jobs: 355081 native CUDA completed 0:0; 355082 launcher-only failure before any simulation, retained for provenance; corrected 355083 actual tracker checks completed 0:0. No task jobs/monitors remain active. Old snapshots/builds/dependency sources are untouched.

Limits: GPU integration uses zero-charge TYPE=NONE; charged PIC is checked on CPU. These are correctness checks, not production performance/convergence. First device claimant supplies failure diagnostics, rather than lowest local index. Existing abort156 behavior remains; issue #672 covers graceful shutdown.

Deferred work is in issue #674 and linked from PR #637. The PR description identifies these fixes as local and unpublished. Full report and exact results: `REPORT.md`, `RESULTS.json`; detailed evidence under `a100/` and integration directories.

Next: user review. Do not commit or push without a new explicit instruction.

## Linked CPU/OpenMP CI failure checked, 9 November 2026

Run 42600761674 / job 129104342419 completed with a successful build and 137/138 passing CTest targets. The only failure is TestLossDataSink, case RewindH5RemovesCheckpointAndLaterStepsBeforeAppend: readGlobalTrackSteps returns {8}, expected {4,8}. Probe targets both pass. The run reports PR head b1551b9c3; checkout logs identify synthetic merge 209e1e955be58e96e0eefd0ae4bf62d06af55f3f.

Rebuilt existing local TestLossDataSink target against the current uncommitted checkout, then ran TestLossDataSink and TestLossDataSinkMPI with OMP_NUM_THREADS=4. Both pass: all 17 single-rank cases, including the exact failing HDF5 case, and the registered four-case MPI subset on each of two ranks. The HDF5 rewind case is not part of the MPI subset. Local is macOS Release/OpenMP LLVM21; CI is Ubuntu Debug/OpenMP with parallel CTest. The recent nine-target audit did not include this target; an earlier complete 137-target local suite did. CI failure not reproduced locally and remains unresolved. No production or test source changed, staged, committed or pushed. Logs: ci-42600761674/github-job.log and ci-42600761674/local-lossdatasink.log.

## Follow-up loss-data fixture fix completed, 9 November 2026

The six audit-fix file hashes above remain unchanged. A subsequent TestLossDataSink investigation adds one unstaged test source file (seven source/test files total). Concurrent single/MPI cleanup deleted shared HDF5 test files; tests now use the existing owned temporary directories. Linux Debug/OpenMP reproduced the original race; fixed related5/5targets and100concurrentpairs pass, no skips. Fullsuite136/137 has a separate reproducible Gaussian maximum assertion failure, left unchanged. Detailed current state and evidence: ../lossdatasink-linux-debug-20261109/STATE.md and REPORT.md. No staging, commit or push.
