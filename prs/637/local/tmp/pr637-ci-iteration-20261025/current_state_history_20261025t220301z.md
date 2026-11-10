# PR 637: active CSCS-clean goal

Updated: 2026-10-25 21:56 UTC.

Goal: repeat fixes and authorized pushes to OPALX branch `615-probe-command-does-not-work` until the complete CSCS matrix is clean. Keep the goal active until all 18 jobs on the latest published source revision succeed, including full regression counts. Earlier no-commit/no-push hold is superseded for this source branch. No GitHub comments/replies are authorized or sent.

## Source and publication

Task checkout: `/Users/adelmann/git/opalx-master`. Cwd checkout `/Users/adelmann/git/opalx` is unrelated; read skills there, do not modify its source.

- Published head: **`a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`**, pushed successfully at20:56 UTC and independently verified with git ls-remote. All six current CSCS builds now pass; runtime verification is continuing on GH200.
- `b17bab1dd` contains the validated collective probe/RF fixes. The history-only merge `23f04f6c8` incorporates independently published `a27c1b392` and has the identical reviewed source tree.
- Local and remote head: `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`. Four files add the ScalingFFA field-superposition fix and native ScalingFFA/analytic MultipoleT coverage. Source is frozen and independently reviewed.
- Tracked tree is clean. Preserve untracked task state/logs. No force push, reset, automatic stash or clean.
- Git origin uses SSH. `gh` is unauthenticated; public GitHub REST and git SSH reads work. Use CLI under `opalx-git-cli` skill, not browser/connectors.

Native unit tests are self-contained C++, with no external Python, supplied fixture data/input decks or OPALX launches. Manual integration/regression scripts and simulations remain separate.

## Previous CSCS verification (23f04f6c, superseded by published a9)

Agent `rf_review_audit` checks the live branch head before exact-SHA attribution. Each backend has six expected jobs: Debug/Release builds, Debug one-rank units, Release one-/four-rank units, Release regression. Dedicated MPI targets actually use two ranks.

| Backend | Project | Pipeline | Latest outcome |
|---|---:|---:|---|
| GH200 |82981356|2987093893|Both builds pass; three unit jobs and regression running at last check|
| OpenMP |83034039|2987093993|Five jobs pass; regression fails 396/401|
| MI300 |83033814|2987093952|Five jobs pass; regression fails 396/401|

All OpenMP/MI300 unit configurations pass 137/137 targets, including the formerly intermittent probe MPI tests. Regression jobs also rerun 137/137 units successfully. Remaining five comparisons are the independently diagnosed FODO and ScalingFFA references below.

Read-only matrix checker: `check_cscs.py` in this directory, invoked with the full SHA and `--output`. Public GitLab API gives pipelines/jobs; raw trace uses job web URL plus `/raw`. Do not expose unfiltered publishing tails containing ephemeral credential fields. Ignore only whole skipped webhook pipelines, not skipped jobs.

## Scientific diagnosis and local validation

FODO: July reference predates September MultipoleT six-fringe-length support/reference-kick correction `fc719154`, already on master. An independently built clean named master `8c1a862369fb05034bb27aa1111d63a7b1e16c02` reproduces the two old-reference failures and matches current results. New native analytic tanh-quadrupole coverage verifies absolute fields and real device/scalar/reference parity, including nonzero fringe tails. No production MultipoleT model change or tolerance widening.

ScalingFFA: input was extended from 10 to 1000 steps while its reference remained a single 10-step row. The full run also exposed a preexisting field bug: element apply overwrote accumulated B, whereas the reference path summed elements. Fix a9 makes element apply additive, preserving raw getter overwrite semantics, formulas, support, SI units and public signatures. A public launcher in internal namespace avoids NVCC's private-enclosing-member restriction without extra views/kernels/fences. New C++ coverage fails before the fix and passes after it, including actual device views, overlapping/outside-support fields and seeded accumulators.

Local OpenMP: 39 cases across three focused field/map targets pass; the new Scaling case also passes on two ranks. The unchanged 1000-step simulation retains all ten particles/charge and reduces final particle/reference separation from 1.222 m to 7.93e-13 m. Energy variation is 8.46e-13 MeV. Reports: `SCALING_SUPERPOSITION_STATE.md`, `scaling-superposition-final/REPORT.md`, `fodo-multipolet/INVESTIGATION.md`.

### Full local regression: PASS

`full-local-regression-a9d38caa/REPORT.md` and manifests establish:

- Exact committed a9 executable SHA256 `68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590`.
- Exact regression master base `737547e6ae38cf3001d6bc45cf38dd1a47d78402`, plus only reviewed 12 generated reference files.
- Standard NightlyBuildX `5539fa31b56d4952d923e6641557d6683c68725a` comparison driver, unchanged.
- 39/39 simulations completed normally at actual a9 runtime revision; 401/401 comparisons; runner exit 0 in 172.8 s. One MPI rank and OpenMP thread per simulation.
- All 451 original fixture/reference files match expected post-patch hashes; all 212 non-reference input/data/launcher/test-definition files stayed unchanged. No tolerance changes, exclusions or 0/0 false success.
- Fresh output tree `/tmp/pr637-full-regression-a9d38caa-20261025`; no website upload/publication. Maintained regression checkout remains clean.

## A100 validation: PASS

Merlin clone `/data/user/adelmann/opalx-dev/opalx-probe-615` is tracked-clean at exact a9. It was safely synchronized by reversing only the hash-guarded old task patch and fast-forwarding a verified local Git bundle; untracked logs are preserved.

- Completed Slurm job: **354773**, COMPLETED0:0 in14m06s, partition/account Gwendolen on cluster gmerlin6.
- Remote logs: `tmp/pr637-scaling-a100-20261025-r2/`.
- Independent audit is complete; evidence copied to local `a100-scaling-a9d38caa/` (verification.json, remote-logs, terminal-metadata.txt and readable report).
- Shared Release CUDA+SERIAL cache `build/gwendolen-cuda132-shared-release`; GCC14.3, CUDA13.2.78, OpenMPI5.0.10, CMake4.4, AMPERE80, two A100s/two tasks, 16 build workers, 192 GiB/90min allocation.
- All6 native CTest targets pass in26.92s: MultipoleT, MultipoleTBase, MultipoleTStraight, ScalingFFAMagnet, DeviceExternalField, TrackReferenceStep. All64 actual GTest cases pass, zero skips/disabled/failures, both new cases explicitly RUN/OK. The actual two-rank new Scaling case passes on each rank. opalx executable also built. All1015 source files match committed a9 and pass post-run hash checks. Dependency source commits/status unchanged. Executable SHA256892ff495ede45e475ee503bfe91e6ffea78c4fed4d8985b3c7a41eaf52c9d015; sharedlib SHA256f4ce20f795a2a7f4aafcbc814a2d8fae2b3a5c0e149b3b6585e2ee80a0066c27. Actual GPU/backend/cache/Slurm metadata independently reviewed.
- First job 354771 failed 128:0 after 11 s BEFORE compilation: root's provenance loop incorrectly used `_deps/ippl` rather than actual `_deps/ippl-src`. Failed logs retained separately. All four corrected dependency source paths/revisions were verified before replacement submission. 354772 was only `--test-only`; do not confuse IDs.

Earlier probe/RF A100 validation 354769 passed 10 targets on one/two ranks; evidence stays separate under `tmp/pr637-followup-20261025/a100-final/`. No need to repeat those checks solely for the history merge.

## External references: keep local, by explicit user instruction

`reference-drafts-a9d38caa/PROVENANCE.md` documents the standard-generated 12-file reference-only patch, SHA256 `05b649a08c40f351a048f9b4b051e832a2288032ab19a48d40a35cea9865ea4e`. Inputs/data/.rt/tolerances unchanged, affected-case independent checks 10/10 and MD5 6/6. Standard generator runtime headers report committed a9. Full-suite pass above uses this exact patch.

The user explicitly answered **Keep the reference update local**. Do not push the reference branch, create an external PR, select an unpublished branch in CI, or publish the same content through an OPALX overlay. The subsequent user instruction is to prioritize production fixes rather than adding more tests; no further test cases are being added. Source-branch pushes are already authorized. A local candidate reference commit is now prepared in isolated clone `/tmp/pr637-regression-publication-20261025`: `b8e4f8a6605b7e41e57fa31d2f7b51424fd82157`, branch `codex/pr637-reference-refresh`, exact parent 737547e6. Its diff SHA256 equals the reviewed patch 05b649a0 and contains exactly the 12 generated files. The maintained regression checkout is unchanged. No external push or PR has occurred. Current CI must continue to select regression master. Its five known reference comparisons will remain failing under this constraint; distinguish that from the real production fixes and do not claim full CI success.

Superseded publication proposal and local drafts: `reference-publication-plan/PLAN.md`. Minimal proposed OPALX patch changes three `regtests_branch` values to `codex/pr637-reference-refresh`. NightlyBuildX accepts named branches rather than arbitrary SHA; verify the actual external revision from each run-state.json. Keep branch unchanged during validation. Once compatible OPALX source reaches master, merge external references and restore configs to master; retain feature branch while jobs depend on it. Do not silently rebaseline further.

## Other preserved work

Attached clean managed baseline worktree: `/Users/adelmann/.codex/worktrees/pr637-master-baseline/opalx`, exact 8c1a862. Preserved executable `master-baseline/opalx-master-8c1a862`, SHA256 `de8fd16697d9dcaeae8af96fdeac25c936e1a9ff2ddf7729806c2b1ea19d9d17`. Use app archive_worktree only when no longer needed, after preserving ignored artifacts.

Unified manual `/Users/adelmann/git/opalx-manual` has earlier uncommitted cyclotron docs plus field-sum clarification. Source/render/link checks pass. Reference uses external fields only; particles self+external. Do not publish manual without authorization.

## Next

1. Exact a9 A100 validation/evidence review and source-only push are complete. No more test cases are being added.
2. Keep all external reference changes local by explicit user instruction. All three CI configs remain regression master; no external branch or overlay publication. Local proposed reference commit b8e4f8a remains available for review.
3. Verify automatic new exact-SHA pipelines and distinguish build/native runtime results from the five expected stale-reference comparison failures. Investigate any different failure in production code first.
4. Diagnose the first concrete new error if any and repeat. Mark goal complete only after complete latest-head CI success.

## New a9 pipelines confirmed (20:58 UTC)

Exact a9 pipelines are live: GH2002987151470/project82981356, OpenMP2987151576/project83034039, MI3002987151523/project83033814. Root independently ran full matrix checker and saved matrix-a9-initial.json: expected18jobs present,6builds running/12runtime jobs waiting. Agent rf_review_audit continues read-only exact-head monitoring; no jobs manually restarted/canceled.

Superseded23f GH200 builds both passed. Before automatic supersession cancellation, Release4 explicitly passed TestCyclotronProbeMPI in2.59s and TestRFEventStepMPI in2.55s. That is partial old-source runtime evidence only; do not count it as whole-suite success or as a9 results. User priority remains production fixes; no further test additions. Current source fix is published and A100 verified, all references remain local. Full latest-head CSCS remains unverified and the5known reference comparisons remain a material constraint; goal stays active.

## Goal continuation 2026-10-25 21:03 UTC

Previous goal turn classification: PROGRESS (published production fix a9 after complete A100 validation). Current turn is a VERIFIED WAIT: root freshly polled exact a9 GitLab pipeline/job handles at21:03:19 UTC, live branch still a9. MI300 both builds now SUCCESS; its3unit configurations and regression are RUNNING. OpenMP/GH200 both builds each RUNNING; their runtime jobs wait. All18 expected jobs present, no concrete new error. Snapshot matrix-a9-2103.json. Agent rf_review_audit inspects filtered running build logs approximately3min as well as exact-head/status checks about100s, without job mutations.

Small direct production audit confirmed current reference field accumulation initializes each local field to zero before rotating/adding, and IPPL Vector default constructor explicitly initializes to zero; no new field-initialization fix is needed. No source/test edits or new test cases were added this turn. Native runtime and full regression outcomes are still needed before diagnosing the latest complete matrix. The local-only external reference instruction persists; do not claim full CI success or bypass comparisons.

At21:07 UTC root re-polled the same exact a9 pipeline handles; current snapshot matrix-a9-2107.json. CI agent also confirms OpenMP both builds now pass, joining MI300; both backends' unit/regression jobs run. GH200 both builds remain live, no concrete compile error in filtered raw logs. Still a verified live-job wait, not a stopped/failed job and not a reason to resubmit.

Agent rf_endpoint_docs independently found existing regression XML records Revisions/code_full and tests_full even on failed runs. Old completed23f OpenMP public artifact directly proves source23f and regression737547e6, whereas run-state.json intentionally only exists for all-pass results. Architecture/backend XML fields sayunknown, so use actual job/artifact path. Runner full SHA is not recorded; do not infer it from remoteHEAD. Agent will retrieve exact a9 XML when available, guarding source/full timestamp/path; no CI logging edits/reruns are needed.

## Goal continuation checkpoint 2026-10-25 21:14 UTC

Latest authoritative a9 evidence: OpenMP and MI300 Release1/Release4 jobs have terminal SUCCESS. Root matrix21:12:22 has8successful jobs,6running,4created, no failures. Subsequent raw Debug logs also prove runtime PASS137/137 on both sites: MI300 job17451990680 at21:12:11 UTC,453.83s; OpenMP17451990956 at21:12:28 UTC,199.44s. They progressed normally through TestDecayChain; no hang/timeout. Publication/job-status completion remained pending at the last monitor call. Thus all6 native unit configurations on these two backends have actual successful runtime summaries, while whole pipelines remain incomplete.

MI300 Release1/4 CDash builds4375303/4375302 explicitly identify build-a9d38caa and137passed/0failed/0notrun. ProbeMPI testIDs547289734/547289597,RFEventStepMPI547289721/547289584,LossDataSinkMPI547289707/547289570 allPASS with actualsrun-n2. Probe/RF have no filter; LossMPI has precisely the source's intentional4casefilter. No hidden skipped-test green.

GH200 both builds still live and compiling, no concrete compiler error in filtered logs. OpenMP/MI300 regression jobs still run; keep all18gate objective intact. Current turn classification: VERIFIED WAIT with newly verified required unit-stage completions; no source/test/CI edits and no newtestcases. No genuine impasse audit is started while these remaining jobs can still reveal production errors.

Provenance agent has read-only /tmp/pr637-fetch-regression-xml-provenance.py ready to fetch existing current-job XML once terminal. XML Revisions/code_full/tests_full records actual fullsource/regressionSHA even on comparisonfailure. Guard source=a9 and currenttimestamp; runnerSHA may remain unrecorded. Do not poll absent artifacts repeatedly or trust oldrun-state.json. External reference updates remain explicitly local-only; current regression configs still master. No job was manually restarted/canceled and no external branch was pushed.

Subsequent21:14 monitor update: both Debug unit jobs are now terminal SUCCESS too. Exacta9 OpenMP and MI300 each5/6jobsSUCCESS, theirregressionsstillRUNNING; all6unitconfigurations137/137. Tenof18jobs nowhaveconfirmedterminalsuccess;GH200's2buildsremainrunning/4runtimejobswaiting. No currenta9jobfailedyet.

## Goal continuation 2026-10-25 21:22 UTC

Previous goal turn classification: VERIFIED WAIT with six completed unit configurations. Current source/remote remain exacta9, tracked-clean; no source/CI/test edits or new tests. Root freshly verified the same live pipeline handles: OpenMP now terminal5success/1regressionfailure;MI3005success/regressionrunning;GH2002buildsrunning/4runtimejobswaiting. Snapshot matrix-a9-openmp-terminal.json. This remains a verified wait for the other backends; no restart is justified.

The current a9 OpenMP regression XML is public and directly proves code_fulla9d38caa4f88433a5de1508b3d5c7d01bdfea95a, tests_full737547e6ae38cf3001d6bc45cf38dd1a47d78402, MPI1/OMP1,401totalcomparisons:396pass,2FODOfail,3Scalingbroken. Same known mismatches, no new case. FODOdelta rms_x1.3061724278502996e-5m/emit_y1.3184285918234021e-5m vsunchanged1e-5eps. Scalingmean_x/y/s brokenbecause10actualrowsvs1oldrow;epsunchanged1e-4m. XMLSHA25667c02a2c69255405ce7ffb776ea1f223c0fba64fd360ce7bd9cb0e12bb225ef5. Evidence ci-checkout-provenance-a9d38caa/README.md,openmp-results.xml,openmp-provenance.json. RunnerfullSHAunrecorded, no currentremoteHEADinference.

All six unit configurations on OpenMP/MI300 are already terminalsuccess137/137. Their regression-internal137unitreruns also pass. OpenMP regression completed ScalingFFA normally before later cases; MI300 remained in DBA-COF-Track-1 at last filteredlogcheck and was still doing simulations, not publication. CI/provenance agents continue read-only monitoring and will inspect currentMI300/GH200XMLwhenavailable. No external reference push/PR/CIoverlay is authorized; user'slocal-onlychoiceandproduction-fixpriorityremaininforce.

## Goal continuation checkpoint 2026-10-25 21:31 UTC

Previous turn classification: VERIFIED WAIT with exact OpenMP regressionfailure proof. Current turn also polls the same confirmed-live GH200 jobs, and completes MI300 regression attribution. Root matrix/head checks still exacta9/cleantrackedtree. OpenMP and MI300 now each terminal5SUCCESS/1FAILEDregression;10of18jobsSUCCESS,2FAILED,2GH200buildsRUNNING,4GH200runtimejobsCREATED. No source/test/CI edits or newtests this turn. Fullobjective remains all18errorfree, not merely native-stage success.

MI300 current regressionjob17451990683 raw and publicXML prove137/137internalunits,401comparisons(396pass,2FODOfail,3Scalingbroken), same five knownrefmismatches and no newlaunch/runtime/comparisonerror. DirectXMLcode_fulla9d38caa4f88433a5de1508b3d5c7d01bdfea95a/tests_full737547e6ae38cf3001d6bc45cf38dd1a47d78402,MPI1/OMP1;XMLSHA256f4933cfd952712d7186a060b7105ae8d527ae89a7b8eb7c2c675d4e64f72217e. Evidence ci-checkout-provenance-a9d38caa/mi300-provenance.json/mi300-results.xml and updatedREADME. Artifactmetadataarchitectureunknown/deviceNone does not establishGPUuse; actualbackend association usesjob/build/launchconfiguration, not those incompleteXMLfields. RunnerfullSHAunrecorded.

Independent GH200 timing diagnostic under gh200-build-timing/REPORT.md comparedprior23fsuccessfuljobs17451643237/17451643236. Compiler phases36m01.7s/36m10.8s, totalGitLabjobs41m04.4s/41m56.3s;aggregated249K→299Koutputgaps26m56.1s/27m38.6s, thencompilercompletion~3minlater. Currenta9compilerbegan~20:59:41/42,249K~21:05:55/58;earlypacewithin~3–4sofprior. Current21:30silence~24m40sisstillshorterthanpriorsuccessfulquietgaps.249KisOUTPUTBYTESnotpercentorheartbeat. No process/scheduler visibility;45minSlurmcapcannotbederivedfromGitLabdurationclock. This supports waiting, not diagnosing a stall or restarting. CIagentcontinuesfilteredraw/error/current-headchecks;provenanceagentawaitsGH200regressionXMLoncefinished.

User's KEEP REFERENCES LOCAL remains binding. Candidate b8e4f8a remains solely local; allCIconfigsselectexternalmaster. Do not publishrefs/PR/overlayorhidefailingcomparisons. No completion/blocked claim while GH200 can still expose required production failures. Refusal to publish is a persistent constraint; once remaining gates are known, assess full goal honestly rather than reverting correct physics to old outputs.

## Goal continuation checkpoint — 2026-10-25 21:40 UTC

The exact a9 GH200 Release build (17451990420) is now SUCCESS. Its one-rank and four-rank Release unit jobs and Release regression have started. Debug build 17451990419 remains RUNNING; Debug units wait. Fresh root matrix/head check confirms the same exact published a9: eleven jobs SUCCESS, two known reference-regression failures, four RUNNING, one CREATED. Snapshot: /tmp/pr637-a9-current-matrix.json. A successful build is separate from pending GPU runtime validation. No compiler/linker error has been reported in either build.

OpenMP and MI300 are each terminal with five successful jobs and the same regression result: 396/401 comparisons (two FODO numeric mismatches and three ScalingFFA row-count mismatches), and all 137 native targets passing in all unit configurations and regression reruns. Their existing XML directly verifies source a9 and regression 737547e6; no new production failure is evident.

Local reference candidate b8e4f8a has additionally been preserved in reference-drafts-a9d38caa/local-only-reference.bundle. Git bundle verification passed; prerequisite is external master 737547e6. Bundle SHA256: a14cba01ec5f2df4b7dcc29bfdfa71b87bec1b038c4bd117bfc98b50dc9f3067. Nothing was published to the regression repository, and all three CI configurations remain on regression master. No source, test, or CI changes and no additional test cases were made during monitoring. This is a verified wait for live required GH200 gates, not full CI success.

## GH200 builds both pass — 2026-10-25 21:42 UTC

Both exact-a9 GH200 builds are now terminal SUCCESS. Release17451990420: compilation ended21:36:40Z, job succeeded21:38:07Z, total42m01.95s. Debug17451990419: compilation ended21:37:44Z, job succeeded21:39:25Z, total43m20.30s. Each reports zero compiler errors and two warnings; the original private-payload/private-TestBody NVCC access errors are absent. Filtered metadata/source proof: gh200-a9-build-summary.json. This completes all six backend build gates. Current matrix: twelve successful jobs, two known reference-regression failures, four GH200 runtime jobs running. Native GPU runtime and full regression remain separate required gates. No source/test/CI edits, job restarts or reference publication.


Structured Build.xml independently confirms both GH200 warnings are the existing NVCC #20011-D Diagnostic/Snapshot destructor pattern at unit_tests/Algorithms/TestRFEventStep.cpp:104, emitted for the two RF executables. Neither original private access error occurs. Filtered diagnostics are preserved as gh200-a9-release-compiler-diagnostics.json and gh200-a9-debug-compiler-diagnostics.json. This turn is classified VERIFIED WAIT with newly completed required GH200 build gates and exact source proof; live GPU runtime handles remain. Full goal remains active, with the local-only reference constraint unchanged.

## Goal continuation — 2026-10-25 21:47 UTC

Previous turn: VERIFIED WAIT, completing both exact-a9 GH200 build gates. This turn freshly re-polled all 18 exact-a9 gates and confirmed live GH200 runtime handles (17451990421–424); no source/test/CI changes were made. All external reference changes remain explicitly local-only.

GH200 Release unit runtime summaries now pass completely: Release1 job17451990422,137/137 in228.12s at21:46:10Z; Release4 job17451990423,137/137 in220.83s at21:45:55Z. Release4 raw log additionally reports job succeeded21:46:38Z; Release1 publication was pending at that sample. Both pass the six serial/MPI probe, RF-event and loss-data targets. ProbeMPI2.81/2.91s, RFEventStepMPI2.67/2.77s, LossDataSinkMPI3.13/2.58s. Agent is verifying structured exact-revision/actual launch/zero-notrun evidence separately. Debug reached81/137 and regression internal unit rerun136/137 with no reported failure, timeout, MPI abort or CUDA error. These partial counts are not final success claims. Current turn remains a verified wait for the live required Debug and full regression gates; no meaningful new production error is yet available to fix.


Independent CDash Release runtime evidence: build4375357 (Release4) and4375358 (Release1), both137passed/0failed/0notrun, build-a9d38caa-release paths. All three critical MPI targets explicitly use /usr/bin/srun -n2 and pass. RF/Probe have no gtest filter (14/11 cases); LossMPI uses the intentional four-case filter matching CMake. Existing 1024-byte CDash output truncation prevents per-rank end-counter proof from those artifacts, so do not claim independently counted per-rank results. CTest records Completed/success. Evidence copied to gh200-a9-release-runtime-cdash.json and gh200-a9-release-runtime-mpi-outcomes.json. No rerun or added tests.


Current exact-head matrix checkpoint: matrix-a9-release-runtime-pass.json proves14/18jobsSUCCESS,2knownreferenceFAILED,2GH200jobsRUNNING(Debug1 and full regression). Both GH200 Release jobs are terminal SUCCESS. Regression's separate native rerun137/137 in227.99s completed21:46:16Z; simulation comparison stage is still running. All claimed runtime results are separate from build success. No source/test/CI changes, additional tests or external publication. This turn remains a VERIFIED WAIT with newly completed Release native gates; keep full goal active while remaining live jobs can reveal production errors.

## All builds and native configurations pass — 2026-10-25 21:52 UTC

Previous turn was a VERIFIED WAIT with completed GH200 Release runtime gates. Fresh authoritative matrix now confirms15/18jobsSUCCESS,2knownreferenceFAILED,1RUNNING(GH200regression17451990424). Exact source/remote head remains a9, tracked-clean. GH200 Debug1 job17451990421 is terminal SUCCESS:137/137 in270.43s, runtime summary21:48:42Z and job success21:49:23Z. No source/test/CI edits or additional test cases this turn.

All six current CSCS builds and all nine native unit configurations now pass. Agent independently queried all nine actual CDash configurations: each identifies build-a9d38caa-*, reports137passed/0failed/0notrun, and includes all three critical MPI targets PASSED with actual srun-n2 launch commands. Evidence: a9-all-native-cdash.json; exact job matrix: matrix-a9-all-native-pass.json. GH200 Debug CDash build4375360, LossMPI547300526, RFMPI547300540, ProbeMPI547300553. The full native matrix confirms the production probe/RF/ScalingFFA fixes across CPU, MI300 and GH200; it does not prove full end-to-end regression success.

GH200 full regression remains live after137/137 internal native tests; keep monitoring that exact handle without restart. OpenMP/MI300 are terminal396/401 with exactly the previously diagnosed reference mismatches. Existing local-only external reference instruction remains binding across consecutive goal turns. Once GH200 completes, inspect full401 counts/exact source+reference revisions and any first new error before assessing whether the remaining task is truly blocked by the unpublished reference correction. Full goal remains active while this required live stage can still expose production errors.

## Goal continuation — 2026-10-25 21:56 UTC

Previous turn: VERIFIED WAIT with completed full native matrix. Current turn freshly polled the exact source/job handles at21:52 and21:55:19Z: fifteen successful jobs, two known reference failures, sole live gate GH200 regression17451990424. Snapshot matrix-a9-gh-reg-2155.json. Git SSH independently confirms OPALX branch still a9 and regression master still737547e6. GitHub PR637 also identifies a9; combined statusfailure, GH200pending, OpenMP/MI300failure tied to the expected exact pipelines. No superseding source or external reference update.

Read-only GH200 trace proves continued simulation progress beyond DBA: Drift-4 cases21:53:14–18Z, Quad-Simple-Test-1-fromfile21:54:11Z, RBend-legacy-dogleg21:54:23Z. No concrete launch/runtime error. Do not restart a confirmed-live job or infer a hang from intermittent output. Agent continues final full401-table audit; provenance agent awaits terminal XML.

Additional artifact audit found current OpenMP/MI300 uploads contain reports and430plotPNGs perarchitecture, but no rawstat/smb/csv/dat outputs. NightlyBuildX publish() copies onlyPNG files and CI archives only regression-results architecture trees. Thus we cannot recompute the five existing comparisons against the reviewed local draft using actual GPU rawstats from these artifacts. Evidence/listings: ci-checkout-provenance-a9d38caa/RAW_STATS_LIMITATION.md. Do not infer a new-reference GPU401/401pass from PNGs, XML deltas or approximate backend agreement. Local full401/401proof remains CPU-only; published current-backend result remains396/401 against oldrefs. No new tests/simulations/CI edits/reruns/publication were added for this audit. User's local-only reference constraint persists across consecutive goal turns; full goal stays active while the final live required job can still expose an actionable production error.


GH200 internal regression comparison finished21:55:34Z, run_tests exit1 at21:55:37Z. Exactly396/401: FODO rms_x(avg)1.3061724278480717e-5 andemit_y(avg)1.3184285918197022e-5 versus unchanged1e-5; Scalingmean_x/mean_y/mean_s size mismatches. Both affected referencechecksumchecksOK. No additional mismatch/launch/runtimefailure. Filtered current-source proof gh200-a9-regression-filtered.json. Job17451990424 still publishes at fresh21:58:14Zrootcheck; finalterminalstatus/currentXMLsource+referenceprovenance pending. Do not treat publication latency as stopped execution or rerun jobs. Full local report was reread directly: exacta9/unmodifiedNightly5539/737base+reviewed12refpatch,39simulations/401comparisons pass,inputs/tolerances/executableunchanged. It remains localCPUevidence, notGPUpasswithnewrefs.
