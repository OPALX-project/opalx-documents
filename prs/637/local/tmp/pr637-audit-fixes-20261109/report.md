# PR #637 audit fixes

Changes remain uncommitted on `codex/ffa-probes-school-parity`, based on `b1551b9c3`. Do not commit or push until the user asks.

## Changes

- Replace per-particle, per-step diagnostic storage with one persistent failure record per rank. Only a failing particle attempts an atomic claim; the winner writes a coherent stable ID and complete diagnostic payload. Host code reads after kernel completion. Selection is the first device claimant, rather than the lowest local array index.
- Return support status from the shared cyclotron field evaluator, removing the descriptor's duplicated coordinate calculations and support predicate. Preserve half-open angular seams and inclusive radial/vertical bounds. Nonfinite coordinates are safely rejected in all callers.
- Validate SINGLEGAP container, species, spin and restart requirements once during preparation. Extract immutable descriptor upload and host stepping, and remove the unreachable guard. Keep the device lambda in the existing public integration method for NVCC, without adding a public tracker API. Preserve the unrestricted host gap count, the 64-gap device limit and lazy upload when particle population changes.

Finite valid-input stepping arithmetic, time integration order and physical output remain unchanged. No numerical tolerance was changed.

## CPU validation

Final executable SHA256: `1b24f376cf40132bd529d1313f2a84dc7d87da3d40806a2daba06686727fd98b`.

- Focused build and all 9 CPU/OpenMP CTest targets pass with four threads, including two-rank RF, sector and probe targets.
- Coasting/RF probe integration passes ten-turn closure, probe ON/OFF passivity, ASCII/HDF5 output and four negative contracts.
- Four accelerating-bunch cases, each with 256 particles, match the preserved baseline `58bd5db2` byte-for-byte in particle, charge, reference, time and step data. Input and map hashes match. No tolerance was used.
- Eight dispatch/failure guards pass. New and baseline host paths accept 65 gaps with identical statistics, excluding only the SDDS generation timestamp. The two-rank device path rejects more than 64 gaps. Unsupported species are rejected, and actual particle field-support failures on one/two ranks report coherent IDs/states without a hang.
- Expected particle failures retain exit code 156 and the existing abort behavior. Fully orderly shutdown remains deferred in issue #672.
- LLVM 21 formatting, diff checks and independent source review pass.

Evidence: `focused-tests-final.xml`, `probe-integration-final/report.json`, `bunch-before-after-final.json` and `guard-integration-final/report.json`. Reproducible integration drivers remain separate from native C++ unit tests.

## CUDA validation

Fresh shared-Release A100 job **355081** completed successfully (exit 0:0, 32m21s). All six RF/sector/probe CTest targets pass on one and two MPI ranks: **111/111 actual case executions, zero skipped**. The concurrent failure-capture and extended sector-boundary tests each pass on all three processes. All 1,072 source files and six local changed-file hashes match snapshot `3320cf6fc490`.

Actual tracker job **355083** then passed four short checks using the same shared library and executable: valid and deliberately failing 256-particle inputs on one/two ranks. Valid runs retain all particles, exact charge/mass/time/step data and finite states. Maximum GPU/CPU position difference is **6.867e-15 m**, and momentum difference is **3.220e-15 p/(mc)**, within the existing 1e-10 bounds. Runtime device properties confirm one visible device per rank and two distinct physical GPUs in the two-rank cases. Expected support failures exit 156 promptly with coherent ID/cause/laboratory-state records, without hanging.

These GPU integrations use TYPE=NONE and zero bunch charge. They validate the actual tracker storage/lifecycle and external RF path; CPU checks include charged PIC. No production throughput or mesh-convergence claim is made.

The first follow-on launcher, job **355082**, failed before OPALX started because it called a nonexistent runtime UUID function. Its archive is retained. A separate metadata utility compiled against the installed CUDA headers now uses `cudaGetDeviceProperties(...).uuid`; it links to the same runtime as OPALX. This correction changed no production source or comparison bounds. All task jobs and monitors are terminal.

Evidence: `a100/native-audit.json`, `a100/tracker-gpu-audit.json`, `a100/validation-evidence.tgz` and `a100/tracker-final-validation-evidence.tgz`. Root independently verified both successful archive hashes, counts, source hashes and device mappings.

## Follow-up and publication

[Issue #674](https://github.com/OPALX-project/OPALX/issues/674) tracks deferred probe communication batching, history storage, cumulative summaries, lattice metadata caching and adapter memory. It is linked from [PR #637](https://github.com/OPALX-project/OPALX/pull/637).

The published PR remains at `b1551b9c3`. Its description explicitly identifies the current audit fixes as local and unpublished. No commit, staging or push has been performed for these changes.

Changed files: `CyclotronSector.h`, `ParallelTracker.cpp/.h`, `TrackReferenceStep.h`, `TestCyclotronSector.cpp` and `TestRFEventStep.cpp`. Exact paths and hashes are in `intended-files.json`.
