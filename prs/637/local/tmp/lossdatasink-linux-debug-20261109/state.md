# TestLossDataSink Linux Debug/OpenMP fix

Complete, 9 November 2026: the file-ownership race is fixed and all relevant checks pass. The broader Linux suite has one separate Gaussian assertion failure, recorded below. No files are staged, committed or pushed. No task jobs remain running.

Checkout: /Users/adelmann/git/opalx-master, branch codex/ffa-probes-school-parity, HEAD b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93. The six earlier audit-fix file hashes are unchanged. This task adds only unit_tests/Structure/TestLossDataSink.cpp to the unstaged diff, for seven changed source/test files total.

Cause and fix: single- and two-rank LossDataSink CTest targets share a working directory. Every original fixture teardown deleted fixed HDF5 paths, including MPI cases that did not create them. Concurrent cleanup could remove the serial target's retained step4 data; H5hut append creates missing files, explaining CI's replacement containing onlystep8. Four existing HDF5 tests now use the existing process-specific, MPI-broadcast temporary-directory helper, and teardown removes only owned directories. One assertion in the existing repeated-rewind case checks retainedstep4 before the second append. Native tests remain self-contained C++, with no new cases, scripts/data dependencies, tolerances, production changes or CTest serialization.

Reproduction: actual CI merge209e1e955 used the same original test source (SHA8334e99b84b8). Original Linux Debug/OpenMP targets pass in isolation and fail in the first concurrent pair in the same rewind case, with missing-file symptoms rather than the literalCI{8}vector. Concurrent original macOS tests also fail.

Validation: independent diff review, clang-format and git diff --check pass. Local fixed targets pass50concurrent repetitions each and5/5related targets. Linux fixed targets pass5/5related targets plus100concurrent pairs:200CTest target executions,2500native case executions,0skips. All1072source hashes match the expected snapshot with only the one-file C5 test fix; corrected binary hashes/literals/object timestamps confirm recompilation. Production library is byte-identical before/after this fix. Final job355093 completed0:0; no further tests are needed.

Broader Linux suite:136/137targets pass. Only GaussianTest.largeCutoffDisablesTruncation fails atline369: samplemaximum5.5717775960503042 exceeds its hard5.5bound. One isolated rerun with the same binary/library/default seed123456789 reproduces it. Untruncated normals have unbounded support; this is a separate test bound. No Gaussian source, seed or tolerance was changed, and no full-suite success is claimed.

Environment: Merlin6 RHEL8, Debug/OpenMP, GCC14.3/OpenMPI5/CMake4.4, four OpenMP threads. HDF5/H5hut match CI; Kokkos5.2.2 differs from CI5.2.0 and CI uses Ubuntu26/GCC15.2. The branch snapshot has137targets versus138in the CI merge; the failing test file is identical. This is not an exact CI-image reproduction.

Evidence: REPORT.md, RESULTS.json, ROOT_VERIFICATION.json and linux/validation-evidence.tgz (SHA3260c12c40b93741ad335e48b5f908d860db4c0cc6f88c04f85df9988e793bb2). Full raw logs and task-wrapper history are preserved under linux/remote-evidence and linux/STATE.md. Source fix SHA c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6.

Next: user review. Do not commit or push without new explicit instruction. Gaussian remains a separate reported failure. Larger probe performance work remains deferred in issue674.

## Remaining test-output ownership fixes completed

The subsequent ownership task changed29other test cpp files and added a shared test-only helper, preserving the seven earlier file hashes. Relevant local/Linux29targets, concurrent FM2D and manual2/4rank checks pass; full suites retain only the known Gaussian failure. No staging/commit/push. Current state/report: ../unit-test-output-isolation-20261109/STATE.md and REPORT.md.
