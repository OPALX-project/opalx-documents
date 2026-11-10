# Linux Debug/OpenMP TestLossDataSink validation

The original fixture race was reproduced on Linux. The one-file fix passes all relevant tests and 100 concurrent target pairs. The broader suite has a separate Gaussian failure, which is retained and reported below. Nothing was staged, committed or pushed.

## Cause and source fix

`TestLossDataSink` and `TestLossDataSinkMPI` share the Structure CTest working directory. The old fixture used four fixed HDF5 filenames and unconditionally removed them in every teardown, including the MPI target's four tests that create no HDF5 data. Those teardowns could delete the serial target's live HDF5 records.

The root agent changed only `unit_tests/Structure/TestLossDataSink.cpp`: the four HDF5 cases now use the existing owned temporary-directory helper; teardown removes only owned directories. The repeated-rewind case also checks the retained record before appending again. Production `LossDataSink` code and numerical tolerances are unchanged.

Original test SHA256: `8334e99b84b8b7ccfa1bff245219c3fd3ec333bbed042bbc5b15003f6360647f`, identical to CI. Fixed test SHA256: `c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6`. All 1,071 other files in source snapshot `3320cf6fc490` match both the remote checks and the current local checkout.

## Results

- Original targets pass in isolation; the first concurrent pair fails the exact rewind case and the keep-all case, with a concrete missing-file error. Linux did not show the literal CI vector `{8}`; it exposed the same shared-file deletion through missing files.
- The fixed five related targets pass: loss sink, its two-rank MPI subset, checkpoint file, probe, and its two-rank MPI target.
- All 100 concurrent pairs pass: 200 CTest target executions; 1,700 single-rank case executions and 800 MPI subset case executions; no skipped or failed cases in these logs.
- Actual Debug/OpenMP cache, source hashes, explicit recompilation/relinking, changed binary hashes, object/link times and filename literals were independently checked. Both corrected test binaries have SHA256 `242c4d29ff3550cbfcdd7b14f274b673c039b7025a38e0acd56fd038aa6a3446`, versus baseline `79b94b9cd71f7594ad22fd9ead199ce6983b4a0923185d99b52f6750bc03c436`. They compile the same source and differ through runtime GTest filters, so identical hashes between the two targets are expected.
- Production `libopalx.so` remains byte-identical: SHA256 `b8c48c6930df7121b0bd0e39dba18239808f64dc50146652d5b5f10cad3bc859`.
- The full suite passed 136/137 targets. Only `GaussianTest.largeCutoffDisablesTruncation` failed at line 369: sampled maximum `5.5717775960503042` exceeds the test bound `5.5`. One isolated rerun with the unchanged Gaussian binary, library, four-thread environment and default seed `123456789` repeats the exact same failure; its other seven cases pass. No Gaussian source, seed or tolerance was changed.

The optional traced original pair passed, with timing altered by tracing. Its traces show 16 cross-process attempts to unlink fixed HDF5 filenames from a process that did not create them; all returned ENOENT. No successful live cross-process deletion was captured by strace. The untraced first-pair failure, source ownership defect, unchanged production library and after-fix stress provide the before/after evidence.

## Environment and coverage limits

Remote root: `/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490`, node merlin-g-100, partition/account gwendolen. CPU Debug/OpenMP only; no GPUs requested. GCC 14.3, OpenMPI 5.0.10, CMake 4.4, four OpenMP threads per test process. HDF5 2.2 and H5hut match CI. RHEL 8/GCC 14.3/Kokkos 5.2.2 differ from CI's Ubuntu 26/GCC 15.2/Kokkos 5.2.0. This is not an exact CI image. The frozen source registers 137 targets while the synthetic CI merge registers 138; the loss-sink test source itself is identical before the fix. The two-rank loss-sink target intentionally runs four fixture/collective contracts, not the seventeen single-rank HDF5 cases.

GCC emitted two existing dangling-else warnings at unchanged GTest macro calls, and the runtime emitted an existing libxml version warning. No new production compilation error occurred.

## Job and harness history

- 355089: original build and isolated/concurrent tests completed; expected race reproduced. The wrapper then exited 1 from fingerprint paths copied from a CUDA preset rather than the CPU output layout. Correct hashes were collected separately; original logs remain intact.
- 355090: cancelled before starting because its afterok dependency was blocked by that metadata failure.
- 355091: broad build completed; cancelled after proving the loss-sink binaries stayed stale because copy2 preserved an old source mtime. No stale-binary pass is claimed.
- 355092: both fixed targets explicitly rebuilt and verified. Full suite completes 136/137, then exits 8 at the unrelated Gaussian failure before its planned stress phase.
- 355093: unchanged verified binaries; Gaussian checked exactly once and its failure recorded; five relevant targets and all 100 concurrent pairs pass. COMPLETED 0:0, elapsed 6m39s. All task jobs are terminal, and the task job queue is empty.

## Evidence and reproduction

Bundle: `validation-evidence.tgz`, 334632 bytes, SHA256 `3260c12c40b93741ad335e48b5f908d860db4c0cc6f88c04f85df9988e793bb2`. Its remote SHA and downloaded bytes match. Raw files are under `remote-evidence/`; corrected audit output is `audit.json`.

Useful raw files:

- `remote-evidence/evidence/isolated.log` and `parallel-001.log`
- `remote-evidence/evidence-final/rebuild-fixed-targets.log`, `binary-verification.json`, `source-verification.json`, `full-suite.log`, `full-suite.xml`
- `remote-evidence/evidence-stress/related.log`, `related.xml`, `gaussian-isolated.log`, `parallel-summary.json`, `parallel-001.log` through `parallel-100.log`, `terminal-verification.json`
- `remote-evidence/job-accounting.txt`, `task-jobs-terminal.json`
- `remote-evidence/build/CMakeCache.txt` and actual CTest/compile/link definitions

Recheck locally with the OPALX Python environment:

```sh
/Users/adelmann/.venv-h6/bin/python /Users/adelmann/git/opalx-master/tmp/lossdatasink-linux-debug-20261109/linux/audit_linux.py --evidence /Users/adelmann/git/opalx-master/tmp/lossdatasink-linux-debug-20261109/linux/remote-evidence --checkout /Users/adelmann/git/opalx-master --output /Users/adelmann/git/opalx-master/tmp/lossdatasink-linux-debug-20261109/linux/audit.json
```

No further tests are required for this worker. Root should independently review the evidence and preserve the separate Gaussian limitation in the final task report.
