> Latest status, 7 November 2026: see [Probe restart status](../probe-status-20261107/STATUS.md). Published 6a32 has tracked contents identical to local a9. Old reference mismatches are resolved upstream; green CI badges conceal two failed regression launches. The October 25–26 blocked-reference narrative below is historical and is superseded by the new live audit.

# PR 637: final CSCS audit and blocked goal

Updated: 2026-10-25 22:03:01 UTC.

## Objective and outcome

The goal remains **all 18 CSCS jobs error-free on the latest published OPALX revision**. It is not achieved. All jobs are terminal: **15 SUCCESS, 3 FAILED regression jobs**. Every backend has the same five known reference mismatches. The production fixes pass all builds and native unit configurations. No further actionable production failure was found.

Blocked audit passes: the user explicitly required **Keep the reference update local**. This same constraint and its known regression failures persisted over consecutive goal turns (including the 21:42, 21:47, 21:52 and 21:56 UTC checkpoints in the archived history). Independent GH200 validation continued during those turns. It is now complete, with no remaining live job or independent production error to resolve. Correcting the published comparison data requires user authorization or an external repository change. Do not mark the goal complete, publish references, revert correct physics, widen tolerances, skip comparisons, or rerun unchanged jobs to obtain green status. The next action is to record the goal as blocked.

## Source and permissions

- Task checkout: `/Users/adelmann/git/opalx-master`, branch `615-probe-command-does-not-work`.
- Local, Git SSH remote, GitHub PR637 and every current CI job identify **a9d38caa4f88433a5de1508b3d5c7d01bdfea95a**. Tracked source tree is clean; untracked task state/logs remain.
- Published source fixes: b17bab1dd (probe collective I/O and terminal RF handling), history-only merge23f04f6c8, a9d38caa (ScalingFFA field superposition).
- Source-branch pushes were authorized for this goal. Separate regression-reference publication was explicitly declined. All three `ci/cscs/config/{openmp,cuda,rocm}.conf` still select `regtests_branch="master"`.
- Current external regression master remains `737547e6ae38cf3001d6bc45cf38dd1a47d78402` by fresh Git SSH read.
- Cwd `/Users/adelmann/git/opalx` is unrelated work: do not modify its source. Read skills there. `gh` is unauthenticated; use public REST/Git SSH under the Git CLI skill, not GitHub browser/connectors.
- Native unit tests must be self-contained C++, with no external Python, supplied input/data, or OPALX launches. No more test cases were added after the user's instruction to prioritize production fixes. Regression simulations/analysis are separate from unit tests.
- No GitHub comments/replies, external reference push/PR/overlay, CI rewiring, job restart or duplicate job was performed during the final audit. All monitoring agents have stopped.

## Final authoritative evidence

See **FINAL_CI_AUDIT.md**, **final-18-job-matrix.json**, **final-github-statuses.json** and **a9-all-native-cdash.json** in this directory. All three CSCS GitHub contexts are failure through their regression jobs; seven separately skipped GitHub Actions checks are not validation evidence.

| Backend | Pipeline | Builds | Native jobs | Regression job / result |
|---|---:|---|---|---|
| GH200 | 2987151470 | Debug/Release pass | 3/3 pass | 17451990424: 396/401 |
| OpenMP | 2987151576 | Debug/Release pass | 3/3 pass | 17451990959: 396/401 |
| MI300 | 2987151523 | Debug/Release pass | 3/3 pass | 17451990683: 396/401 |

Every one of the nine actual CDash native configurations reports **137 passed, 0 failed, 0 notrun**, identifies build-a9d38caa-* paths and passes TestLossDataSinkMPI, TestRFEventStepMPI and TestCyclotronProbeMPI with actual `srun -n 2`. Probe/RF are unfiltered; Loss uses the intentional four-case contract filter matching CMake. Passed-test output is truncated at1024bytes, so CDash does not independently expose final per-rank case counters.

GH200 Debug/Release compiler XML each has zero errors and two existing NVCC20011-D Diagnostic/Snapshot destructor warnings. Neither original private-payload nor private-TestBody access error remains. Build durations43m20s/42m02s; long aggregated-output gaps were normal and no job was restarted. Filtered compiler proofs: gh200-a9-build-summary.json and gh200-a9-*-compiler-diagnostics.json.

GH200 regression logged all39 actual case launches,39 matching normal input-end markers and39 ParallelTracker completion markers. Its internal native rerun also passed137/137. It ended21:59:00UTC with the comparison exit1. Proof: gh200-a9-regression-filtered.json and gh200-a9-regression-case-audit.json.

All three existing result XMLs directly record source **a9d38caa4f88433a5de1508b3d5c7d01bdfea95a** and external regression **737547e6ae38cf3001d6bc45cf38dd1a47d78402**, with401 comparisons:396pass,2fail,3broken. Provenance, exact artifact URLs and checksums: **ci-checkout-provenance-a9d38caa/README.md**. GH200 XML SHA2561836ed577eb963bf6b67c56a378906960762503a7b237777fbddca5498927a33. The external NightlyBuildX runner full SHA is not recorded; do not infer it from current remote main. XML device/backend metadata is incomplete; GPU execution is established separately from actual job/build/launcher configuration.

## Production fixes and remaining reference differences

Probe I/O: root alone decides create/append/stat-error and broadcasts before collective header/body paths. This fixes rank-local filesystem existence races that shifted MPI collectives. Accepted hits flush on root reference-trial failure before the common exception. One-/two-rank native and actual failure-path evidence is preserved in the earlier follow-up reports.

Terminal RF: all tracking paths share reference time/state/stop flags. Terminal-only arithmetic endpoint allowance is64*N*epsilon*L, withN accepted global steps plus current andL lab scale at least1m; normal crossings remain strict. This is an arithmetic allowance, not an ODE error bound: physically later arrivals within it may receive a full kick. All four one-/two-particle by one-/two-rank real integration runs reach73.273098424852MeV; deliberate failure runs retain exactly one accepted probe hit. Reports: ../pr637-followup-20261025/VALIDATION.md and rf-integration-accumulated/REPORT.md.

ScalingFFA: element apply now adds its contribution to accumulatedB, preserving earlier magnets/self-fields even outside its support. Raw getter overwrite semantics, formulas, support, SI units and public signatures remain unchanged. Internal public launcher struct is necessary because NVCC extended lambdas cannot be enclosed by private members; it shares existing private math without extra views/kernels/fences/atomics/MPI. Doxygen explains this. Unchanged1000step simulation improves final particle/reference separation1.222m→7.93e-13m with all10particles/charge retained and energy variation8.46e-13MeV. Evidence: SCALING_SUPERPOSITION_STATE.md and scaling-superposition-final/REPORT.md.

The five current failed comparisons are:

- **FodoCell-multipoleT-fromfile:** rms_x(avg) andemit_y(avg), around1.306e-5 and1.318e-5 versus unchanged1e-5 tolerance. The July reference predates intended September MultipoleT fringe-support/reference-field correctionfc719154. Independently built clean master8c1a862 reproduces the old-reference failures and matches current physics. Analytic native fringe coverage verifies absolute fields and nonzero tails. No new MultipoleT production model change or tolerance widening is warranted. See fodo-multipolet/INVESTIGATION.md.
- **ScalingFFABasicPlacements:** mean_x/mean_y/mean_s row-size mismatches. Fixture MAXSTEPS changed10→1000 while its old reference remained a single row; current intended1000step run has10rows. The actual field-overwrite bug was fixed before generating corrected references. Do not shorten the fixture or accept the former1.2m separation.

NightlyBuildX avg metric is sqrt(sum(diff**2))/N in absolute column units, not relative error or ordinary RMS. The two affected checksum checks pass in CI, confirming unchanged old references rather than corrupt downloads.

## Local-only reference correction

The exact reviewed12generated-file patch remains solely local:

- reference-drafts-a9d38caa/combined-reference.patch
- Patch SHA256 **05b649a08c40f351a048f9b4b051e832a2288032ab19a48d40a35cea9865ea4e**.
- Candidate commit **b8e4f8a6605b7e41e57fa31d2f7b51424fd82157**, branchcodex/pr637-reference-refresh, parent737547e6, isolated clone `/tmp/pr637-regression-publication-20261025`.
- Verified durable bundle: reference-drafts-a9d38caa/local-only-reference.bundle, SHA256 **a14cba01ec5f2df4b7dcc29bfdfa71b87bec1b038c4bd117bfc98b50dc9f3067**.
- Standard makeReference generation from committed a9; affected checks10/10 andMD5checks6/6. All inputs/data/testdefinitions/tolerances unchanged.
- **Full local standard regression PASS:39/39simulations,401/401comparisons**, oneMPIrank/OMPthread, exacta9 executableSHA68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590; unmodified NightlyBuildX5539fa31b56d4952d923e6641557d6683c68725a. All451fixture/reference hashes and212nonreference inputs/launchers/.rt/tolerances verified unchanged after run. See **full-local-regression-a9d38caa/REPORT.md** and manifests.
- Current OpenMP/MI300 artifacts omit raw statistics; they contain reports/PNGplots only. Therefore a pass against the local correction has **not** been recomputed from actual GPU statistics. See ci-checkout-provenance-a9d38caa/RAW_STATS_LIMITATION.md. Local401/401 evidence isCPU-only; do not claim new-referenceGPU/CSCSsuccess.
- reference-publication-plan/ contains a superseded proposal, not authorized actions. Do not select an unpublished external branch or publish the same reference content in an OPALX overlay.

## A100 and other preserved work

A100 Slurm354773 completed0:0 in14m06s on Gwendolen,2A100s,sharedReleaseCUDA13.2.78/GCC14.3/SM80/OpenMPI5.0.10. Six focused targets/64actualcases and actual2rankScalingcase pass; all1015source hashes match a9 before/after, dependencies unchanged. See a100-scaling-a9d38caa/REPORT.md. Earlier probe/RFA100354769 passes10targets and remains separate under ../pr637-followup-20261025/a100-final/. No active Merlin task processes remain.

Baseline managed checkout `/Users/adelmann/.codex/worktrees/pr637-master-baseline/opalx` is tracked-clean at8c1a862. Its preserved executable master-baseline/opalx-master-8c1a862 still hasSHAde8fd16697d9dcaeae8af96fdeac25c936e1a9ff2ddf7729806c2b1ea19d9d17. Archive attempt returned **protected by a pinned task or workspace**; retain the checkout and do not bypass that protection.

Unified manual `/Users/adelmann/git/opalx-manual` retains earlier uncommitted cyclotron/field-sum docs; source/render/link checks passed. No manual publication was authorized. Reference uses external fields; particles use self+external. No upstream dependency source was changed.

## Resume condition

Resume meaningful CI work if the user authorizes the reviewed reference publication/CI selection, the external regression master is corrected independently, or a concrete new production failure appears. Recheck actual source/reference heads and patch hashes first; then run the complete automatic18job matrix and verify exact external checkout revisions/full401 counts. Do not reduce success to native-only checks. Until such a change, all current jobs are terminal and unchanged-code reruns cannot resolve these deterministic reference mismatches.

Archived chronological state: CURRENT_STATE_HISTORY_20261025T220301Z.md.


## Pre-push reference review — 2026-10-26

User requested showing the FODO/ScalingFFA reference changes and explaining them before any push. This is review authorization only, not authorization to publish; the goal remains blocked and references remain local. Read-only root and independent agent audits verified local candidate b8e4f8a, exact parent737547e6,12generated files matching patch05b649a0,9unchanged input/data/launcher/tolerance files and6validMD5 checks. No new tests, simulations, source/CI/reference changes or push were performed. The untracked provenance report's obsolete GPU-pending sentence was refreshed to distinguish current native GPU success from unverified external comparisons against the local correction.

FODO endpoint200.1ns: old/new2001rows; rms_x14.36635148665814→13.60558491043789mm, rms_y24.86274013968008→25.31376694895573mm, rms_s9.931991621616522→9.961108194326143mm; normalized emit_x2.277543692508736e-3→2.194295200896983e-3m,emit_y3.505292099015799e-3→2.866604802621306e-3m,emit_s3.047598927349794e-4→3.131835832652092e-4m; energy1000MeV within roundoff,finalparticles999→1000. Existing master already implements September fringe/reference changes; clean master reproduces the old-baseline mismatch.

Scaling old stored reference:1row at1ns. Proposed reference:10rows at10,20,...100ns,10particles with charge1.602176633999999e-15C and energy46.72604383544903MeV atfinaltime. Distinguish this coverage change from the independently matched100ns old/fixed-code comparison:1.222m→7.931939441046071e-13m centroid/reference separation after additive-field correction. Existing fixture history also changed magnet ordering when extending MAXSTEPS10→1000; current input stays untouched. Undefined normalized correlation columns xpx/ypy/zpz containNaN/Inf in both old/newzero-emittance data; they are not Twiss beta/alpha columns and are not used by the three finite existing centroid assertions. Generatedlogs/timings account for substantial text churn. Full patch hash remains unchanged. The branch review UI was queued for the isolated local candidate.
