# A100 validation of the small PR #637 audit fixes

Validation is complete. The final six uncommitted source changes passed a fresh shared Release CUDA build, six native one-/two-rank test targets and four actual-tracker GPU checks. No source changes were made by validation, and nothing was committed or pushed.

| Check | Result |
|---|---|
| Native CUDA job 355081 | COMPLETED 0:0, 32m21s |
| Native CTest | 6/6 targets, 29s, zero failed/skipped/disabled |
| Native case execution | 111 RUN / 111 OK |
| New concurrent failure capture | RUN/OK on all three one-/two-rank processes |
| Extended sector support/boundary/nonfinite case | RUN/OK on all three processes |
| Actual tracker job 355083 | COMPLETED 0:0, 35s |
| Valid tracker, one/two ranks | 256 particles; finite physical states; existing 1e-10 bounds pass |
| Expected particle failures, one/two ranks | Captured id=0, field-support cause and laboratory state; exit 156, no timeout/hang |

GPU–CPU position and momentum component differences are at most 6.867e-15 m and 3.220e-15 p/(mc). TIME, global step, mass, ID sets and zero charge match the CPU fixture. One-/two-GPU position difference is at most 2.221e-16 m. Inputs and binaries were unchanged and their hashes verified.

Runtime device proof in job 355083 uses a small standalone C++ metadata probe compiled against CUDA 13.2 headers and shared runtime. It asserts one visible device per rank and records cudaGetDeviceProperties(...).uuid. Both probe/OPALX use the exact same libcudart 13.2.75 realpath. Two-rank UUIDs are GPU-dbbd7375-8fc1-093d-f86b-ae1f64b87448 and GPU-ddaf526c-0266-266a-8606-0f82d8aa1f8d. Native job 355081 used distinct explicit CUDA ordinal masks and NVML UUID records; its UUID evidence is qualified accordingly.

Job 355082 failed only in the first metadata launcher: it called nonexistent runtime symbol cudaDeviceGetUuid. No OPALX simulation started, so the corrected four-case job duplicated no successful simulation. Full failed logs and corrected probe/scripts are preserved. A scp option error during evidence retrieval was also corrected without affecting jobs.

Limits: the tracker fixture is a short NONE-solver, zero-macroparticle-charge case, not a GPU PIC-solver/nonzero-charge or throughput study. FROMFILE rank distribution can change sample-to-ID association; comparison uses ID sets and uniquely separated x-sorted physical states. Failure exits retain existing abort semantics. No tolerance was loosened.

All 1,072 source files and current six intended hashes match snapshot 3320cf6fc490. Original remote checkout and prior 790abac19643 source/build/dependencies are preserved. No task job/monitor remains active. See [terminal state](STATE.md), [native audit](native-audit.json), [tracker audit](tracker-gpu-audit.json), [compact summary](summary.json) and raw archives/directories alongside.

## Reproduce the retrieved tracker analysis

The successful job 355083 archive was extracted without renaming or normalizing paths under `remote-tracker-final/`; its run directory is `gpu-integration-final/`. The original successful analysis used `audit_tracker_gpu_final.py`. The canonical `audit_tracker_gpu.py` now accepts `--run-dir` and defaults to that final directory. The earlier unparameterized draft is retained as `audit_tracker_gpu_legacy_path.py`.

Run from any working directory:

```sh
/Users/adelmann/.venv-h6/bin/python \
  /Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100/audit_tracker_gpu.py \
  /Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100/remote-tracker-final \
  --run-dir gpu-integration-final
```

This command was rerun only on the already-retrieved final files. No simulations or native tests were repeated. All pre-existing JSON files remain byte-identical, including both copies of `tracker-gpu-audit.json`, `summary.json` and `native-audit.json`; hashes and exact commands are recorded in `reproducibility-check.json`.
