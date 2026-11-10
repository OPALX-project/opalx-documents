# PR #637: upstream master merged and pushed

## Outcome

The user authorized merging upstream master, resolving conflicts, committing and pushing to the existing PR branch. This work is complete. PR #637 itself remains open and unmerged.

- Branch: `615-probe-command-does-not-work`.
- Published merge commit: `ec4319acb1d3cf676f2581f4c86c3e691ce2e22d`.
- Parents: published PR head `6a32ba6d` and upstream master `bdf5a47a`.
- Tested and committed tree: `0949495e7d05212340372b2c200be57088165af3`.
- Git remote and GitHub independently confirm the new head. GitHub reports the PR mergeable; review/check requirements still block merging.

## History and preservation

Local a9d38caa and published 6a32ba6d had identical source trees but rewritten histories. Preserved the old local branch as `codex/probe-history-before-master-20261107`, then recreated the intended PR branch from published history. No reset, stash or force push was used. Added the PR branch to the checkout's previously master-only fetch mapping. Tracked source is clean; all pre-existing untracked notes and task outputs remain local.

Merlin6 was not resynchronized by this operation. Its checkout remains at the earlier a9 source until a separate update.

## Merge resolutions

The merge imports 94 upstream files and had three content conflicts: ScalingFFAMagnet.h, DeviceExternalField.h and TestScalingFFAMagnet.cpp.

- Retained upstream ScalingFFASupport, optimized host scalar evaluation, reference aperture-loss reporting and COF behavior.
- Retained additive particle/scalar/reference application and raw-getter overwrite semantics, including the public NVCC-compatible launcher.
- Kept all 22 ScalingFFA cases from both branches. The existing upstream accumulation case now exercises element apply; its assertions and tolerances are unchanged. Existing superposition checks now expect upstream aperture-loss flags.
- Retained both required device-field headers.
- Moved upstream emission-dependent timestep selection before reference terminal trials. This prevents the reference using an old duration while particles/PIC use a newly selected duration.
- Removed one trailing space inherited from upstream documentation.

Independent tracking and ScalingFFA reviews found no remaining blocking issue. Conflict files pass LLVM 21 formatting; the staged diff passed whitespace checks. No new feature, test case, tolerance change or deferred issue #672 implementation was added.

## Build and validation

Configured the existing static Release/OpenMP cache with LLVM 21 and upstream IPPL 3.4.0 (`d6216553e39dcf4405849c027517cc3401fefee5`). The first configure stopped because the disconnected updater lacked that release tag; fetched the tag without patching dependency code, then configuration and the full build passed.

- All **137 native CTest targets pass** in 55.93 s; JUnit has zero failures, disabled tests or skips. Dedicated probe/RF/sector/loss MPI targets use two ranks.
- Two existing ScalingFFA accumulation cases pass on both MPI ranks.
- Probe OFF/HDF5/ASCII coasting and RF comparisons preserve phase space, reference state, time and steps exactly. Coasting records 20 crossings; RF records one. All four rejection contracts pass.
- Charged-bunch one-/two-rank position differences are at most 8.45e-15 m. Near-zero PIC versus NONE passes; resolved collective momentum change is 1.0235e-4.
- All four one-/two-particle by one-/two-rank terminal RF cases reach approximately 73.273098424852 MeV.
- Both deliberate RF-failure cases return the expected 156 and preserve exactly one accepted hit and histogram count.

These tests used the staged tree recorded above, which exactly matches the committed tree. No fresh CUDA/HIP result is claimed for this merge.

Evidence: validation.json, native-tests.xml/log, test-inventory.json, scaling-mpi.log, tracker-audit.md, probe-integration/, bunch-integration/ and rf-review-integration/.

## Automatic CI and next step

The push started new CSCS checks, currently pending:

- GH200: pipeline 3039725036.
- MI300: pipeline 3039725075.
- OpenMP: pipeline 3039725106.

GitHub's skipped Actions jobs are not validation evidence. Inspect these new exact-head CSCS results before any PR merge. No PR merge was requested or performed, no regression references were published, and issue #672 remains deferred.
