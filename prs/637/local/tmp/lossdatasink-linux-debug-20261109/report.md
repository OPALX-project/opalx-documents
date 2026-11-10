# Loss-data test isolation fix

The Linux Debug/OpenMP investigation reproduced the TestLossDataSink failure and confirmed a race between the single- and two-rank test fixtures. The fix changes only unit_tests/Structure/TestLossDataSink.cpp. All relevant tests now pass. The broader suite has a separate Gaussian assertion failure and is not fully green. Nothing is staged, committed or pushed.

## Cause

Both CTest targets run in the same working directory. The MPI target runs four unrelated cases from the same fixture, whose teardown unconditionally removed four fixed checkpoint HDF5 filenames after every case. It could therefore delete the serial target's retained data between rewind and append. H5hut's H5_O_APPENDONLY implementation creates a new file on ENOENT; appendingstep 8 after that deletion produces only{8}, explaining CI's expected{4,8}/actual{8} result. Missing-file exceptions are another timing-dependent symptom.

The original test source matches the actual CI merge209e1e955 byte-for-byte. On Linux, both original targets passed in isolation, then the first concurrent pair failed in RewindH5RemovesCheckpointAndLaterStepsBeforeAppend and the keep-all case. The Linux run showed missing-file symptoms, not the literal{8}vector. The original concurrent macOS run also failed in the rewind case. Raw output is preserved.

## Change

The four existing HDF5 tests now use the fixture's existing process-specific temporary-directory helper. It broadcasts the root-generated path so ranks in one MPI job share it, while independent jobs use different directories. Cleanup deletes only directories owned by that fixture instance. The existing repeated-rewind case also checks thatstep 4 survives its second rewind before append. An explanatory source comment records why ownership matters.

There are no new native tests, targets, external Python/data dependencies, production changes, numerical tolerances or test serialization. The six prior audit-fix files remain unchanged. The production shared library is byte-identical before and after this fixture fix.

## Validation

| Check | Result |
| --- | --- |
| Linux original targets in isolation | Both pass |
| Linux original targets concurrently | Rewind and keep-all cases fail with deleted/missing-file symptoms |
| Linux fixed loss-data, checkpoint and probe targets | 5/5 pass, no skips |
| Linux fixed concurrent pairs | 100/100 pass ; 200 CTest targets, 2,500 native case executions, no skips |
| macOS fixed concurrent loss-data targets | 50 repetitions each pass |
| macOS related targets | 5/5 pass |
| Broader Linux Debug/OpenMP suite | 136/137 pass; separate TestGaussian failure |
| Source/binary provenance | 1,072 file hashes verified; corrected test executables recompiled; unchanged production library |
| Formatting and review | LLVM21 clang-format, git diff --check and independent review pass |

The MPI loss-data target runs its registered four-case subset on two ranks; it does not execute all seventeen single-rank cases. Native tests remain independently runnable with CTest. The temporary evidence scripts orchestrate existing commands and are not unit-test dependencies.

## Separate Gaussian failure

GaussianTest.largeCutoffDisablesTruncation fails at line 369: maximum 5.5717775960503042 exceeds the hard 5.5 sigma assertion. Its other seven cases pass. Exactly one isolated rerun with the same binary, library and default seed 123456789 reproduces the same maximum. The Gaussian test source, seed and tolerance were not changed.

An untruncated normal has unbounded support. For100,000 samples, the chance of exceeding5.5 sigma is about 0.379% per coordinate, or about 1.88% across the five approximately independent coordinates tested. The assertion can reject a valid tail sample. The isolated failure is retained; it does not erase the original broader-suite failure or justify claiming a fully passing suite.

## Reproduction limits and evidence

Linux validation used Merlin6 RHEL8/GCC 14.3/OpenMPI 5/CMake 4.4 in Debug/OpenMP, with four OpenMP threads. HDF5 2.2/H5hut match CI. Kokkos 5.2.2 differs from CI 5.2.0, and CI uses Ubuntu 26/GCC 15.2. The branch snapshot registers 137 targets versus 138 at CI's synthetic merge, while the failing test source is identical. This validates the race and fix on Linux Debug/OpenMP without claiming exact runner-image parity.

Final focused validation job 355093 completed 0:0. The verified full-suite job 355092 exited 8 for the separate Gaussian failure. Earlier wrapper attempts include a post-test fingerprint-path mistake and a cancelled stale-binary run; their logs are retained and excluded from accepted after-fix evidence. All task jobs are terminal.

Reproducible audit: linux/audit_linux.py. Raw logs/JUnit/manifests/accounting: linux/remote-evidence. Independent root checks: ROOT_VERIFICATION.json. Archive: linux/validation-evidence.tgz, SHA256 3260c12c40b93741ad335e48b5f908d860db4c0cc6f88c04f85df9988e793bb2. Exact structured results: RESULTS.json. The source diff is fix.patch.

Next is user review; no commit or push is authorized yet. The larger probe performance changes remain deferred.
