# Probe restart status — 7 November 2026

This review supersedes the October 25–26 CI/reference status notes. It was read-only apart from saving these audit records. No source, reference, CI configuration or dependency changed; no build, simulation, fetch, push or job was started.

## Source and working locations

PR #637 is open and unmerged: https://github.com/OPALX-project/OPALX/pull/637

- Published branch: `615-probe-command-does-not-work`, head `6a32ba6ddb44730de0c0ac3590b07b16cf089702`.
- Mac checkout: `/Users/adelmann/git/opalx-master`, at `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`. Tracked files are clean; task outputs remain untracked.
- Merlin6 is reachable. Checkout: `/data/user/adelmann/opalx-dev/opalx-probe-615`, also at a9d38caa and tracked-clean.
- Existing A100 build: `build/gwendolen-cuda132-shared-release/bin/opalx`. Validation logs: `tmp/pr637-scaling-a100-20261025-r2/`.
- The live `squeue -M gmerlin6` query returned no jobs for this user.

The Git history changed, but an exact tree audit found all **1,060 tracked file blobs identical** between local a9d38caa and published 6a32ba6d. There are no tracked-content differences. Reconcile the differing Git histories carefully before development; preserve untracked outputs and do not assume a fast-forward pull. Evidence: `source-tree-audit.json`.

## Completed cyclotron implementation

Cyclotron PROBE uses finite laboratory X–Z segments, with legacy endpoints and STEP in mm. It observes accepted particle endpoints, records crossings in both directions, interpolates crossing states, suppresses duplicates, and carries stable-ID histories through MPI migration and compaction. It remains separate from field selection and step selection.

Outputs include HDF5 or existing ASCII .loss records, cumulative .hist counts, and .peaks containing unweighted mean radius per reference turn. Charge-weighted radial density profiles are derived offline from hit charges. Periodic flushing occurs every 100 accepted global steps, with final flushing and preservation of accepted hits on the implemented reference-trial/SINGLEGAP error paths.

The MPI writer decision race and CUDA ownership/access problems were fixed. Native tests are self-contained C++, without external Python, supplied fixture data or OPALX launches.

The coasting sector-selection error was fixed: ten-turn particle/reference separation decreased from about 23 m to 1.2e-11 m. Accelerating SINGLEGAP/PIC tracking was implemented and consolidated into DeviceExternalField and TrackReferenceStep. The temporary CyclotronSectorCandidates/CyclotronBunchStepper headers were removed. ScalingFFA field superposition was corrected separately; this does not implement legacy FFA probe placement.

## Completed studies

The saved 8³ mesh / 4,096-particle / 2 mA diagnostic run reached 580.470767685 MeV. It retained 4,049 particles, lost 47, and recorded 759,907 probe hits. The last eight complete passages, 178–185, have verified particle/charge accounting and PNG/PDF/CSV outputs.

- Profiles: `../ring-space-charge-profiles-20261023/profiles-8-580/`.
- Old OPAL comparison: `../old-opal-comparison-20261023/comparison.pdf`.

This is one bunch on successive turns, without neighbouring-turn/bunch space charge or a septum. It is not a mesh/timestep convergence result. The old OPAL comparison has a maximum turn-centroid difference of 1.058 mm, with different integrator, self-field and loss rules.

Previous A100 jobs 354769 and 354773 validated native CUDA and dedicated MPI behavior. These are historical completed runs; nothing was rerun today.

## Current CI evidence and a newly found blind spot

The latest published CSCS executions, from October 27–28, report all 18 expected jobs successful: six builds, nine native unit jobs and three regression jobs. Each native job actually reports 137/137 passed, including ProbeMPI, RFEventStepMPI and LossDataSinkMPI. See `CI_AUDIT.md`, `ci-matrix.json` and `native-summaries.json`.

However, the regression badges conceal two real failures on **all three backends**. Forty cases launch, only 38 complete normally, and only those 38 enter the XML's 394/394 passing comparisons. The runner still returns zero:

1. `ScalingFFARealisticLattice` aborts because PROBE requires cyclotron-sector tracking; FFA probes are deferred.
2. `AWAGun-binned-p3m-emittedfromfile` aborts because multi-bin P3M is unsupported; BINS requires MAXBINS=1.

Both exit 134 on GH200 and 156 on OpenMP/MI300. Both have comparison definitions. Their exclusion is an observed runner error-accounting problem, not merely absent tests. Evidence: `hidden-launch-failures.json` and the three saved result XMLs.

The actual external regression revision is `6c95b46a18599b2247fcc6eaff53a9f692d498bf`. The former FODO/ScalingFFA reference mismatches were genuinely resolved by external regression PRs #77 and #79. FODO retains all seven checks at eps=1e-5. Scaling retains three centroid checks at eps=1e-4 and adds two reference-path checks at eps=1e-6; all pass.

The changed comparison total is 401 minus nine omitted replacement AWAGun checks plus two added Scaling checks, giving 394. The new realistic FFA lattice's checks are also omitted after its abort. Therefore green badges do not establish error-free execution of every attempted simulation.

Our old 12-file reference patch is not the upstream correction. It needs review against the changed upstream inputs/references before any use. Its patch and bundle remain preserved under `../pr637-ci-iteration-20261025/reference-drafts-a9d38caa/`; the temporary candidate checkout `/tmp/pr637-regression-publication-20261025` is gone. No reference publication was newly authorized.

## Still unfinished

- Old OPAL FFA/RingElement-style PROBE remains phase two and is explicitly unsupported. PassiveRingProbe is an internal selected-ID CSV diagnostic, not legacy compatibility.
- PROBE checkpoint restart, tracking continuation and COF with PROBE remain unsupported.
- The original 16³ PIC failure near 584 MeV remains unclassified. Better diagnostics and flushing exist, but the successful 8³ run stopped below it at 580.47 MeV.
- Accepted-endpoint interpolation does not resolve multiple intra-step crossings or RF impulses. Detectors should be kept away from thin RF planes and crossings resolved with DT.
- The accelerating PIC path is restricted to one container, unpolarized positive protons and at most 64 RF gaps. Vertical RF focusing is not modelled.

## Suggested restart order

Reconcile local/Merlin Git history with the published branch while preserving outputs. Make failed regression launches fail the aggregate CI result. Keep future tracking inside the field map’s valid operating range, with an earlier stop. Diagnostics and graceful termination for out-of-validity cases are deferred to issue #672. The current user request was status first, so none of these actions was performed today.


## Follow-up: quick 584 MeV failure analysis

See [failure-584/ANALYSIS.md](failure-584/ANALYSIS.md), its reproducible `quick_analysis.py` and saved JSON evidence. The old failure is a detected SINGLEGAP transport rejection followed by MPI_Abort, not orderly finalization. Vertical halo approaching the ±50 mm magnetic-map support is plausible but unproven. No particle checkpoint exists to identify the failed state retrospectively. Current accepted-hit flushing improves output retention, but orderly MPI/GPU shutdown and a consistent error checkpoint remain absent. A concrete nonzero-rank diagnostic logging defect was identified. No code or simulation was changed by this analysis.


## Deferred issue and branch decision

The user confirmed that the field map is no longer physically valid at the historical failure's energy and that future studies should stop earlier. No universal numerical cutoff was inferred; the existing 590 MeV input remains preserved as failure evidence, not a valid high-energy physics case. Reproducing that invalid operating point is no longer an immediate study recommendation.

At the user's explicit request, opened and read-back verified issue [#672](https://github.com/OPALX-project/OPALX/issues/672), “Cyclotron: graceful shutdown and complete diagnostics outside field-map validity”. It records the observed failure, missing historical particle state, nonzero-rank logging defect, output/checkpoint limitations, and coordinated MPI/GPU cleanup requirements. Implementation is explicitly deferred. The reviewed published body and JSON are preserved under failure-584/github-issue-672.*.

Fresh `gh pr view` confirms PR637 remains OPEN and unmerged at published head6a32ba6d. Probe source is committed and pushed; no new source commit, branch, merge, simulation or job was created in this follow-up. Review corrections can stay on the existing PR branch. Separate follow-up work should use a new branch, preferably from updated master after merge; if started before merge it should be based on the published PR head. Reconcile the local/Merlin rewritten history carefully first, preserving untracked artifacts.


## Upstream merge and final PR push

At the user's explicit request, merged upstream masterbdf5a47a into the publishedPRhistory and pushed commit **ec4319acb1d3cf676f2581f4c86c3e691ce2e22d** to615-probe-command-does-not-work. Threecontentconflictsresolved; one timestep-order semantic merge corrected. The exactcommittedtree passes137/137nativeOpenMPtargets plus dedicated2rankScaling andexistingprobe/bunch/RF/failure-flush integrations. See ../pr637-upstream-merge-20261107/STATE.md andvalidation.json. PR637remainsOPENandMERGEABLE,withnewCSCScheckspending; itwasnotmerged. Localoldhistory is preservedonbackupbranch;Merlin6remainsa9untilseparatesynchronization.
