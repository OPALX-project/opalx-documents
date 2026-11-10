# Current PR637 CI status audit — 2026-11-07

Read-only audit; no jobs, reruns, edits, fetches, pushes or reference publication.

## Exact revision and reported gates

Current PR head: `6a32ba6ddb44730de0c0ac3590b07b16cf089702`, open/unmerged. All 18 expected CSCS jobs are terminal SUCCESS: six builds, nine native unit jobs and three Release regression jobs. Exact pipelines GH2002996719015, OpenMP2996719168, MI3002996719086. The latest recorded executions completed October27–28UTC; they were not rerun today.

Every native job's actual raw trace reports 100% tests passed, zero failed out of137. All nine also explicitly pass TestLossDataSinkMPI, TestRFEventStepMPI and TestCyclotronProbeMPI. Evidence native-summaries JSON preserves exact job IDs/URLs and relevant raw lines.

## Actual end-to-end regression coverage: green badge is incomplete

All three regression jobs launch40cases but only38complete normally and only38appear in comparison XML. All three report394/394comparisons and run_tests exit0. XMLs directly identify source6a32 and actual regression checkout `6c95b46a18599b2247fcc6eaff53a9f692d498bf`. The recorded summary is not a complete pass of all attempted simulations.

Two actual launch failures are silently excluded from the XML/comparison aggregate on ALL THREE backends:

1. **AWAGun-binned-p3m-emittedfromfile**: `validateSpaceChargeConfig`: P3M supports BINS only with MAXBINS=1; multi-bin P3M is not implemented. Exit134 on GH200,156 on OpenMP/MI300.
2. **ScalingFFARealisticLattice**: `PROBE`: PROBE currently requires cyclotron-sector particle tracking; FFA probes are deferred. Exit134 on GH200,156 on OpenMP/MI300. This directly confirms the deferred FFA PROBE phase remains unsupported in the published source.

Both have .rt definitions and references in the tested external revision. This is an observed runner aggregate blind spot, not merely absent test definitions. Do not mark the old full-CI-error-free goal complete based on the green badges or394/394alone. No fix was attempted because the user requested status first.

## Why the old five comparison mismatches now pass

External regression master advanced from737547e6 to6c95b46 through separate published work:

- PR77, commitf2961e48: new FodoCell-multipoleT-fromfile references. Its seven comparisons retain eps1e-5 and all pass on all backends, with numerical deltas near floating point.
- PR79, merge6c95b46/commit5b9166a6: redone ScalingFFA references with reproducible FROMFILE input. ScalingFFABasicPlacements retains all three centroid checks at eps1e-4 and adds ref_x/ref_z at eps1e-6; all five pass. ScalingFFARealisticLattice was also refreshed but aborts due unsupported FFA PROBE as above.
- PR76 renamed/reworked the old nine-check AWAGun P3M case. Its replacement now aborts and is omitted.

Thus394 = former401 − nine omitted replacement AWAGun checks + two added Scaling reference-path checks. The new realistic-lattice case's five checks are also omitted after its abort. The former FODO/Scaling failures were resolved through real external reference work, not removal/widening of those five assertions. The external changes are not identical to our local12-file reference draft.

All three OPALX CI config files at6a32 still select regtests_branch=master. Current source history is rewritten/diverged relative to local a9; do not infer a simple fast-forward from a huge GitHub compare result. Parent separately checks relevant source-file identity.

## Compact evidence

- /tmp/pr637-restart-6a32-matrix.json
- /tmp/pr637-restart-6a32-native-summaries.json
- /tmp/pr637-restart-6a32-regression-traces.json
- /tmp/pr637-restart-6a32-compact-provenance.json
- /tmp/pr637-restart-6a32-{gh200,openmp,mi300}-results.xml
- /tmp/pr637-restart-6a32-hidden-launch-failures.json
- /tmp/pr637-restart-6a32-uncompared-cases.json (GH200 detailed failure blocks)
- /tmp/pr637-restart-6a32-reference-change.json

Primary job URLs:
GH200 https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757981/-/jobs/17521960308
OpenMP https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757983/-/jobs/17521961922
MI300 https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757982/-/jobs/17521961344
