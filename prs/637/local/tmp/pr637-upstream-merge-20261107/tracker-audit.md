# PR637 tracking auto-merge audit

Read-only review of the working merge of PR head 6a32ba6d with master bdf5a47a. No edits, builds, staging, commits or pushes performed by this reviewer.

## One integration ordering concern

Upstream moves timestep selection to the beginning of ordinary particle integration, but the automatic merge places changeDT() in the non-boundary block AFTER the PR's preliminary EKINSTOP reference trial. That reference trial caches pendingReferenceR/P using the existing bunch dt. On an emission timestep transition, particularly the first step after emission finishes, changeDT() can then select a different dt for particle prediction/transport and the common clock. The cached reference has already advanced using the old duration. Current guards do not reject SINGLEGAP+EKINSTOP with ongoing/delayed emission.

Recommended minimal merge resolution: select the non-boundary step duration at the start of the inner loop BEFORE terminal reference trials, then remove the duplicate later changeDT(). Reference-terminal clipping already updates bunch dt and particle dt, and selectDT() retains the PR's terminalStepDt_m/boundaryStepDt_m clamps. This combines upstream's whole-step emission duration with the PR's requirement that reference, PIC prediction/gather and particles share one accepted duration. It changes no field formula/support or arithmetic event allowance and adds no kernels/MPI.

The current fixed-dt FROMFILE cyclotron decks do not have this transition, so their passivity checks alone do not cover the concern. A short emitted/delayed source with distinct emission and tracking dt plus SINGLEGAP/EKINSTOP would exercise it if the root chooses an integration check.

## Other reviewed interactions

- The PR's terminalStepDt_m clamp remains in selectDT(); the coasting TURNS clipping and common reference/particle duration code are preserved.
- Upstream's new spin half rotations affect the normal particle path; SINGLEGAP still explicitly rejects polarized particles, so the early RF returns do not omit a supported spin half-step.
- New BEAM reference-momentum overrides are transferred coherently from TrackRun to ParallelTracker. They only apply to file-based sources with explicit BEAM energy/momentum. The saved accelerating cyclotron decks omit those BEAM attributes and continue to initialize reference momentum from the sampled mean.
- ParticleContainer's new ghost-covering charge-storage accessor is independent of the PR's registered probe histories/custom CUDA ownership. Those history hooks remain intact.
- ScalingFFA is now accepted by the upstream localized-TURNS/device-ring capabilities, but PROBE's explicit non-cyclotron rejection remains unchanged. This is consistent with the deferred FFA-probe scope.
- Accepted-hit observations, periodic flushing and collective reference-failure cleanup survive the automatic merge. Deferred issue672 work was not introduced.

No other required semantic correction was found in the four requested tracking files.

## Existing validation targets

Focused native subset: TestCyclotronProbe/TestCyclotronProbeMPI, TestRFEventStep/TestRFEventStepMPI, TestCyclotronSector/TestCyclotronSectorMPI, TestTrackReferenceStep, TestDeviceExternalField, TestScalingFFAMagnet, TestParticleContainer and TestCoordinateSystemTrafo. Include TestBeam and TestSpinTBMTPusher for the imported reference/spin changes, and TestOneTurnMap/TestOrbitThreader for upstream ScalingFFA-ring work. These remain native C++; do not add external scripts/data or OPALX launches to unit tests.

Separate executable integration controls: tools/check_cyclotron_probe.py for ten-turn coasting and RF-stop OFF/HDF5/ASCII passivity; tools/check_cyclotron_bunch.py for near-zero self-field equivalence and one/two-rank physical-state agreement. Existing deliberately unphysical RF-trial cases validate accepted-hit preservation. These are code-path controls, not the invalid-map near584MeV study or a convergence claim. Keep that deferred work deferred.

## Final resolution recheck

Root relocated non-boundary changeDT() to the early inner-loop else branch, before both EKINSTOP and TURNS reference trials, and removed the later duplicate. I inspected the actual staged result against origin/master. Reference trial, PIC predictor/gather, particle transport and global clock now use the same selected duration; subsequent terminal clipping remains authoritative. selectDT still clamps terminalStepDt_m and boundaryStepDt_m, and requested-TURNS clipping still refreshes all per-particle dt views. Upstream whole-step emission semantics are retained. No further must-fix issue was found in the reviewed tracking merge. git diff --check passed. No builds/tests/source edits were performed by this reviewer.
