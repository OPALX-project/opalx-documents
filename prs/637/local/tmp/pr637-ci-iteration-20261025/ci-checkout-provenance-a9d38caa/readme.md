# PR 637 external checkout provenance

Updated: 2026-10-25T22:01:21.833724+00:00.

Source: `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`. Public GitLab artifacts were read without credentials, login or access workarounds. No CI, source, maintained fixtures or references were changed; no rerun or publication was launched. References remain local.

## Direct checkout evidence

| Backend | Job | Artifact | Source guard | Regression checkout | Comparisons |
|---|---|---|---|---|---|
| openmp | 17451990959 | [XML](https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757983/-/jobs/17451990959/artifacts/raw/regression-results-cpu-zen2-openmp/regressionTests/pr-637_Implement_cyclotron_PROBE_and_accelerating_space-charge_tracking/cpu-zen2-openmp/results_2026-10-25_22-08.xml) | Exact a9 SHA | `737547e6ae38cf3001d6bc45cf38dd1a47d78402` | 396 passed, 2 failed, 3 broken |
| mi300 | 17451990683 | [XML](https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757982/-/jobs/17451990683/artifacts/raw/regression-results-gpu-rocm-mi300/regressionTests/pr-637_Implement_cyclotron_PROBE_and_accelerating_space-charge_tracking/gpu-rocm-mi300/results_2026-10-25_22-03.xml) | Exact a9 SHA | `737547e6ae38cf3001d6bc45cf38dd1a47d78402` | 396 passed, 2 failed, 3 broken |
| gh200 | 17451990424 | [XML](https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757981/-/jobs/17451990424/artifacts/raw/regression-results-gpu-cuda-gh200/regressionTests/pr-637_Implement_cyclotron_PROBE_and_accelerating_space-charge_tracking/gpu-cuda-gh200/results_2026-10-25_22-42.xml) | Exact a9 SHA | `737547e6ae38cf3001d6bc45cf38dd1a47d78402` | 396 passed, 2 failed, 3 broken |

Each accepted XML explicitly reports `Revisions/code_full` equal to the complete source SHA above and `Revisions/tests_full` equal to the complete regression checkout SHA shown. These are actual job results, rather than an inference from current remote HEAD. Runtime/build provenance is separately checked by the CI monitoring agent.

### openmp

- Artifact architecture path: `cpu-zen2-openmp`; job `17451990959`.
- XML `Date/start`: `2026-10-25T22:10:18.180738` (no UTC offset encoded). Queried `2026-10-25T21:20:16.759092+00:00`.
- XML SHA256: `67c02a2c69255405ce7ffb776ea1f223c0fba64fd360ce7bd9cb0e12bb225ef5`.
- MPI ranks: 1; OpenMP threads: 1.

### mi300

- Artifact architecture path: `gpu-rocm-mi300`; job `17451990683`.
- XML `Date/start`: `2026-10-25T22:08:59.743414` (no UTC offset encoded). Queried `2026-10-25T21:28:21.174382+00:00`.
- XML SHA256: `f4933cfd952712d7186a060b7105ae8d527ae89a7b8eb7c2c675d4e64f72217e`.
- MPI ranks: 1; OpenMP threads: 1.

### gh200

- Artifact architecture path: `gpu-cuda-gh200`; job `17451990424`.
- XML `Date/start`: `2026-10-25T22:46:17.244267` (no UTC offset encoded). Queried `2026-10-25T22:00:56.475092+00:00`.
- XML SHA256: `1836ed577eb963bf6b67c56a378906960762503a7b237777fbddca5498927a33`.
- MPI ranks: 1; OpenMP threads: 1.

Raw-stat coverage: see [RAW_STATS_LIMITATION.md](RAW_STATS_LIMITATION.md). Current OpenMP and MI300 artifacts omit simulation statistics, so no pass against the local reference draft is inferred from PNGs or XML deltas.

The five non-passing comparisons are the previously diagnosed stale-reference checks: FodoCell-multipoleT-fromfile `rms_x` and `emit_y` fail; ScalingFFABasicPlacements `mean_x`, `mean_y` and `mean_s` are broken because the old reference has one row versus ten current simulation rows. No additional mismatch appears in the accepted current XMLs. Adjacent parsed JSON preserves every failed comparison, tolerance and delta.

## Metadata limitations

XML architecture/backend fields are `unknown`, and device is `none`; backend association comes from the specific job and architecture artifact path, not those incomplete fields. This record does not use XML device metadata to establish GPU execution.

`run_tests` records `run-state.json` only when all unit and regression failed/broken counts are zero. Failed suites can legitimately omit it. The correct old failed OpenMP path returned 404. The exact external NightlyBuildX runner SHA is not present in the always-generated XML and is not inferred from current remote main. Local runner clone `5539fa31b56d4952d923e6641557d6683c68725a` establishes parser semantics, not the external checkout SHA.

The old completed OpenMP job `17451643780` is retained separately as a parser/provenance demonstration only. It records source `23f04f6c8e57f497e6f1a722038f9e1cef010803` and regression `737547e6ae38cf3001d6bc45cf38dd1a47d78402`; it is not current a9 evidence.
