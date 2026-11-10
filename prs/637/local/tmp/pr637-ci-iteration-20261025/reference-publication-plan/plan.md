# Superseded: references must remain local

The user explicitly chose **KEEP THE REFERENCE UPDATE LOCAL**. The publication sequence below is historical preparation only and must not be executed. Do not push or open an external PR, select an unpublished reference branch in CI, or publish the reference content through an OPALX overlay. The temporary CI patch and PR text are unexecuted drafts only. Local candidate commit `b8e4f8a6605b7e41e57fa31d2f7b51424fd82157` remains isolated under `/tmp/pr637-regression-publication-20261025`, parent737547e6, with exactly the reviewed12 generated files. Parent may publish a9 source only under its existing authorization after A100 validation. The five old-reference CI comparisons will remain by the user's choice; local401/401 validation uses the local candidate references and is distinct.

# Minimal paired source/reference publication plan

Status: read-only investigation and local drafts only. No external commit, branch, PR, push or source/config edit was performed. The current user authorization covers OPALX source-branch pushes; publication to `OPALX-project/regression-tests-x` requires a separate explicit authorization. Wait for the complete local suite and exact committed A100 validation before seeking publication approval.

## Verified branch-selection path

All three active architecture jobs select their corresponding config: `ci/cscs/openmp/regression_openmp.yml` selects `openmp.conf`, CUDA selects `cuda.conf`, and ROCm selects `rocm.conf`. All three configs currently set `regtests_branch="master"` and `do_unittests='yes'`.

`ci/cscs/regression-common.yml` clones NightlyBuildX **main** and invokes its `scripts/run_tests` with the selected config, existing release executable/build directory, `--reg-tests --unit-tests`, and no positional test filter. The current pipeline documentation still mentions an older NightlyBuildX branch; the active YAML is authoritative for this plan.

Current NightlyBuildX main is `5539fa31b56d4952d923e6641557d6683c68725a`. Its implementation:

- Defaults `regtests_branch` to master, sources the selected config, and applies an optional `--regtests-branch=BRANCH` override afterwards (lines15,245-256,299-305,415-416).
- Clones/updates `https://github.com/OPALX-project/regression-tests-x.git` and passes `regtests_branch` into `update_repo()` (lines204,1782-1784).
- Resolves a local named branch, `origin/<branch>`, or a `pr<N>-...` alias fetched from GitHub's `refs/pull/N/head` (lines697-728). It does **not** accept a raw commit SHA or tag through this selector. Setting `regtests_branch` to a SHA would fail rather than produce an immutable pin.
- Records the actual checked-out external commit in `run-state.json` as `inputs.regressionTestsCommit`, alongside `regressionTestsBranch`, OPALX commit, runner commit and architecture (lines529-580). Use those recorded revisions to verify each CI result.
- With no test names, scans all enabled case directories and does not skip comparisons after a reference mismatch. The current exact737547e6 inventory is39 enabled simulations /401 comparisons. The standard runner exits nonzero when passed count differs from total.

Primary source: [run_tests at5539fa31](https://github.com/OPALX-project/NightlyBuildX/blob/5539fa31b56d4952d923e6641557d6683c68725a/scripts/run_tests#L697), [case discovery and failure accounting](https://github.com/OPALX-project/NightlyBuildX/blob/5539fa31b56d4952d923e6641557d6683c68725a/scripts/run-reg-tests.py). Frozen downloaded source and public REST responses are adjacent for review.

The public REST response for open external PRs was empty when checked on2026-10-25. External master still points to737547e6ae38cf3001d6bc45cf38dd1a47d78402. Recheck both immediately before publication to avoid duplication or stale-base changes.

## Recommended minimal sequence

1. Finish the isolated full standard local suite against the reviewed patch. Require all39 launches to succeed and401/401 comparisons, with unchanged enabled inventory, plus the exact a9 A100 native validation. The full suite is running; do not claim its final result yet.
2. Obtain explicit authorization to publish the external reference branch and PR. The concrete proposal is exactly the12 generated reference files already reviewed, based on737547e6. No inputs, particle data, launchers, `.rt` definitions, tolerances, disabled markers or unit tests change.
3. In an isolated external checkout, create `codex/pr637-reference-refresh` from the verified external master base. Apply the reviewed combined-reference.patch, stage only its12 explicit paths, commit using `external-reference-commit-message.txt`, push that feature branch, and open an external PR to master with the draft title/body. Record its resulting commit hash and URL. Root must attach the newly created PR to this task. Recheck existing PRs first; no force push or direct master push.
4. Keep that external PR unmerged. Apply the prepared `proposed-opalx-ci-branch.patch` to OPALX PR637: one `regtests_branch` line in each of openmp.conf, cuda.conf and rocm.conf, pointing to `codex/pr637-reference-refresh`. This selects compatible references for all three backends while old OPALX master continues using compatible old references. The existing `branch="master"` and all unit/test invocation flags stay unchanged. Push the OPALX source branch under its existing authorization.
5. Let automatic CSCS CI run. For OpenMP, GH200 and MI300 separately, verify the OPALX tested revision includes a9 plus this config change, the external checked-out commit equals the recorded reference commit, and the NightlyBuildX revision. Require401/401 regression comparisons and the complete native unit-test result for each backend. A successful compile does not substitute for GPU runtime tests. Keep the external feature branch unchanged during this validation; the runner selects a branch, not an immutable SHA.
6. Once compatible OPALX source is merged to master, merge the reviewed external reference PR. Merging the Scaling reference before its source fix would cause old OPALX master to fail against corrected near-zero centroids. The FODO update is independently compatible with pre-PR master, but splitting the reference PR is unnecessary if this paired sequence is followed.
7. Restore all three OPALX `regtests_branch` lines to master after external master contains the accepted reference commit. Verify the external commit selected by fresh jobs again, then remove the temporary external branch only after no active pipeline or configuration still depends on it. This leaves normal CI maintained on regression master with all401 comparisons.

A single `--regtests-branch` override in common YAML would also select all three backends, but the three existing config values are the established, explicit selection points and require only three changed lines. No NightlyBuildX modification or new pin mechanism is needed for this review. The exact external commit is not known until the authorized external commit exists; do not invent it.

## Preserved validation scope

The reviewed patch SHA256 is05b649a08c40f351a048f9b4b051e832a2288032ab19a48d40a35cea9865ea4e. It changes only six generated files per case: `.out`, `.stat`, `timing.dat`, and their existing `.md5` files. A patch check against isolated exact737547e6 passes. Nine original non-reference files in the two affected fixtures have identical pre/post SHA256. The full-suite agent independently inventories39 cases/401 checks and verifies only those12 reference paths changed in its isolated tree.

Committed source a9d38caa4f88433a5de1508b3d5c7d01bdfea95a was rebuilt with disconnected dependencies; preserved executable SHA256 is68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590. The full local runner uses that executable, one MPI rank and OpenMP1. The final validation result will be recorded in `../full-local-regression-a9d38caa/`; until it completes, this plan does not claim401/401.

Current completed evidence: both generated headers report exacta9, all6 generated checksum checks pass, all10 affected-case comparisons pass against independent outputs, FODO retains1000 particles/2001 rows, corrected Scaling retains10 particles/10 rows and final mean separation7.93e-13m. Native tests are self-contained C++ and retain their separate one/two-rank validation; the external regression fixtures/scripts are end-to-end integrations only.

## Reviewable local files

- `proposed-opalx-ci-branch.patch`: minimal three-config change; `git apply --check` passes, not applied.
- `external-reference-commit-message.txt`, `external-reference-pr-title.txt`, `external-reference-pr-body.md`: publication drafts, with pending validation explicitly marked.
- `opalx-ci-commit-message.txt`: paired CI branch-selection commit draft.
- `../reference-drafts-a9d38caa/combined-reference.patch` and `PROVENANCE.md`: exact external generated-file patch and scientific rationale.

No external action is required to review these files. Update the pending full-suite/GPU validation sentences in the PR body with their actual results before authorized publication.
