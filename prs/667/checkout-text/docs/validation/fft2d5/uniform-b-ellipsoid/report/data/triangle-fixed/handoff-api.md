# Longitudinal input/config implementation

Owner: longitudinal_api. Input/config plumbing is complete; no builds run by
this agent so the parent can compile the shared checkout without conflicts.

## Contract

- `PIPEMODE="CIRCULAR_UNIFORM"` maps to
  `FFT2D5LongitudinalFieldMode::UniformRound` (appended to preserve existing
  enum values).
- `FFT2D5Config::pipeRadius` is `std::optional<double>`. The physical radius
  is required by UniformRound, optional for legacy Cylindrical/CIRCULAR.
- `FieldSolverCmd` exposes `getPipeRadius()`, `hasPipeRadius()` and
  `setPipeRadius(double)` for the `PIPERADIUS` attribute. Absence is distinct
  from explicitly supplied zero.
- Explicit radius must be finite, positive and at least `BEAMR`. OPEN,
  PLATES and NONE reject it. Non-FFT2D5 field solvers also reject it.
- Legacy CIRCULAR without an explicit radius retains an absent optional;
  the algorithm owner retains the old width-based fallback. No default or
  legacy coefficient changed here.
- PIPESIZEX/Y are full numerical widths. Help text and printed solver info
  distinguish these widths from a supplied physical PIPERADIUS.

## Changed files

- src/Structure/FieldSolverCmd.h / .cpp
- src/SpaceCharge/SpaceChargeConfig.h / .cpp
- src/SpaceCharge/SpaceChargeConfigBuilder.cpp
- unit_tests/SpaceCharge/TestSpaceChargeConfig.cpp

The seven added tests cover required/invalid radius, unsupported modes and
solver types, preservation of old absent-radius configuration, and keeping
the physical radius unchanged when either numerical width changes. Builder
tests use an IPPL-initializing fixture and skip construction on multiple
ranks because FFT2D5 remains single-rank.

## Verification

All six owned files were clang-formatted. Scoped `git diff --check` passes.
The diff has been reviewed. Root must build and run TestSpaceChargeConfig
with the other FFT2D5 tests; no native compile/run was started by this agent.
No core algorithm, manuals, report artifacts, commits or pushes changed here.

## Independent native follow-up audit completed

Read-only review of the new root algorithm/tests is in REVIEW-api-core.md;
no material defect found. Then independently audited all six new OPALX
main/probe pairs (12H5 snapshots), reread the matching historical legacy
main/probe pair (2more H5 snapshots), and checked all three new PyORBIT
repeat cases, including the two-rank source weights and target coverage.

Own audit artifacts are in audit-api/: check_native_independent.py,
snapshot-checks.csv, independent-summary.csv, checks.json and audit.log.
The script does not import the parent's reader or analytic g kernel. It
constructs frame axes using vector products, numerically integrates the
uniform-disk radial Gauss-law field to the grounded wall, and takes a finite
longitudinal potential derivative. Actual input/source/path hashes and both
current9d3771d5... and archivede85bc091... binaries verify.

All183targets per case, including144accepted (62axis/82radial), pass exact
ID/count/charge/time/units/frame and provenance checks. The independently
reconstructed OPALXEs matches the parent's CSV exactly (0V/m difference).

- fixed256 maxaxiserror0.1607871495%; maxradial-localerror0.0286480446%.
  The0.00055747% radialnumber belongs to fixed128/wide256, notfixed256;
  root was notified immediately to avoid using the wrong finest-case metric.
- W20->40mm at fixedphysicalb20mm changesEs by at most5.7662e-10V/m.
- Physicalb20->10mm fieldchange matches independent potential integration
  within0.0234983%, consistent with the known source-gradient sampling error.
- Legacy rebuilt versus reread historicalH5 differs at most2.0612e-10V/m
  over all183targets; historicalH5 matches the immutable cachedCSVexactly.
- Directfixed256 versus PySlice maximumdifference0.4468375671% ofEaxis;
  versus PyBaartman0.1673852739%. PyMPI1/2all-targetEsdifference is at most
  2.6922e-10V/m.

Reviewed the new FFT2D5-TriangularPipe regression source/validator and CI
wiring. It tests nonzero fields at core/surface/annulus/wall, actual charge,
IDs/time/geometry/units, with1% nonzero-field acceptance and explicitabsolute
zero-wall tolerance. It derives its reference from the Gauss-law potential;
the same-plane probe self-contribution has a separate native zero control.
The preserved wrong-legacy-mode negativecontrol fails actual field checks.
No material blocker found. RemoteCIwas not run/pushed by this reviewer.

No production/test/report edits or builds were performed in the follow-up;
only this agent's audit artifacts/state were written.
