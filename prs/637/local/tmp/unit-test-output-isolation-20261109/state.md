# Unit-test output isolation

Complete, 9 November 2026. All relevant ownership checks pass on local OpenMP and Linux Debug/OpenMP. Both full suites retain one separate unchanged Gaussian assertion failure (136/137 targets). No task builds/tests/jobs remain active. Nothing is staged, committed or pushed.

Checkout: /Users/adelmann/git/opalx-master, branch codex/ffa-probes-school-parity, HEAD b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93. Seven prior uncommitted source/test file hashes are unchanged. This task modifies 29 other existing test cpp files and adds unit_tests/TemporaryDirectory.h (30 files). The new helper is untracked and must be explicitly included if a later commit is authorized. Exact files/hashes: intended-files.json; prior state: baseline-files.json.

Design: test-only RAII owner claims unique directories with atomic filesystem create_directory using PID/steady-clock/counter candidate names. Never adopts/removes pre-existing paths. MPI creation broadcasts a root-owned path on the shared CTest filesystem plus creation errors; cleanup never calls MPI. Callers close writers and synchronize before cleanup. Explicit filenames preserve default-path behavior without cwd or CMake changes. RF autophaser diagnostics require an owned absolute cavity name. Two ORB fixtures only stopped deleting files they never created. Existing safe probe/LossDataSink paths and all numerical assertions/tolerances/seeds are unchanged. No new native tests or external data/script dependencies.

Scope: field-map fixtures, checkpoint/Dirichlet writers, generated distribution inputs, diagnostics/FFT reference paths, multi-container HDF5 output, active muon/pion CSVs and RF autophaser output. Non-writing fixed stems were audited through actual call paths and left alone. Disabled external-reference tests remain disabled/untouched; standalone user-output benchmarks are unchanged. See REPORT.md and per-agent inventory notes.

Reproduction: original FM2D static/dynamic pass alone but fail on first concurrent Linux pair, including ENOTEMPTY/shared map interference. Before job355094 completed0:0 with expected failures preserved. Local initial mkdtemp helper compile failed under a macOS/MPI include order; final helper uses standard atomic filesystem creation and both platform builds pass. Superseded logs/package retained, not accepted as final validation.

Validation: all29affectedtargets pass locally and on Linux. Local20FM2Drepetitions pertarget and two simultaneous checkpoint executables in sharedcwd pass. Linux20FM2Dconcurrentpairs pass (40CTest targets,840native cases). Five manual2/4ranklaunches pass (18native cases,0skips): checkpoint, multiH5rewind, ORBupdater, ORBloadbalance and FFT2D5 reject. Full local and Linux suites each136/137; onlyGaussianTest.largeCutoffDisablesTruncation fails with5.5717775960503042 vs5.5. It is unchanged and no full-suite success is claimed.

Provenance: all1073current source hashes verified; all29changedtestobjects/relinks/hashes verified fresh; productionlibrary and priorfrozenLossDataSink archive unchanged. FinalLinux job355096 completed0:0 (13m37). Source/core algorithms/CMake are unchanged by this task. LLVM21 formatting, diffchecks and independent lifetime/MPI/error-path/implicit-writer review pass.

Evidence: REPORT.md, RESULTS.json, LOCAL_RESULTS.json, ROOT_VERIFICATION.json. Linux raw archive linux/validation-evidence.tgz SHA e06d7b6d09d549b42d24260608b88633f14c1284a71fb609816c5582e0cf575f. Rawlogs/JUnit/source/binaryguards/accounting: linux/remote-evidence. Reproducible driver linux/run_after.py. Temporary DNS retrieval failure resolved without restarting or duplicating jobs.

Next: user review. Do not commit or push without explicit new instruction. Separate Gaussian test bound and larger probe performance work remain outside this completed ownership task.

## Gaussian follow-up resolved

The subsequent one-file Gaussian statistical-check change resolves the remaining assertion. Local and Linux full suites now137/137pass, includingGaussian1/2rank×1/4thread checks48nativeexecutions0skip. All37earlier sourcefiles listed here remain unchanged. No staging/commit/push. Current report/state: ../gaussian-statistical-check-20261109/REPORT.md and STATE.md.
