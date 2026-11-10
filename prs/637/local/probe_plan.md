> Published, 9 November 2026: FFA probes and the general probe-frame adapter committed as `b1551b9c3` and pushed to PR #637. Exact 12-file publication recorded in `tmp/ffa-probes-implementation-20261107/PUBLISH.json`.

> Update, 9 November 2026: the adapter is now general (`tools/probe_frame_adapter.py`), with arbitrary Cartesian origin/basis and unchanged identity/turn/time labels. The school is solely a comparison benchmark. See the current FFA task state for validation. No commits or pushes.

> FFA implementation, 7 November 2026: shared native PROBE support and the school adapter are implemented locally on `codex/ffa-probes-school-parity`. See [current FFA task state](tmp/ffa-probes-implementation-20261107/STATE.md) and [validation report](tmp/ffa-probes-implementation-20261107/REPORT.md). No commits or pushes have been made for this phase.

> FFA design discussion updated 7 November 2026: see [the evidence-based FFA proposal](tmp/ffa-probe-design-20261107/PLAN.md). The supplied old-school probes are explicit global plugin detectors, not symmetry-replicated magnetic occurrences. The historical step-two outline below is superseded where it assumed occurrence-local RingElement semantics. No FFA implementation has started.

# Issue 615: cyclotron PROBE implementation and step-two plan

Status: cyclotron implementation complete within the scope below, 2026-10-23.
Workspace: /Users/adelmann/git/opalx-master
Branch: 615-probe-command-does-not-work
Base: 6d2f011572f9cb1aa38c01e1b9d529e1ab58eb21
Issue: https://github.com/OPALX-project/OPALX/issues/615
No commits or pushes performed. FFA/RingElement implementation is deferred.

## Implemented behavior and decisions

- ParallelTracker collects global probe configurations outside the field/placement
  lattice. Probes cannot change field support, reference transport or step selection.
- Existing XSTART/XEND and YSTART/YEND inputs remain in mm. They denote laboratory
  X and Z respectively: the OPALX cyclotron machine plane is X-Z, vertical Y is
  unrestricted. Common placement attributes do not position the detector; L is zero.
- Device crossing kernel reuses two tested directed passive observers to record
  both directions, clip to the finite segment and include its endpoints. Initial
  plane points are suppressed; 1 nm excursions arm returns. Segment projection
  permits 16 machine epsilons for rounding at an endpoint.
- Optional container-owned history attributes follow stable IDs through IPPL
  migration and compaction. Stored lab coordinates survive tracking-frame changes.
  Scratch hit storage is reused; only compact crossings leave device memory.
- Crossing positions, normalized mechanical momenta, IDs, time [s], charge [C],
  mass [GeV/c^2], reference turn and container number use LossDataSink. HDF5 stores
  charge/mass; ASCII uses the established .loss schema and precision.
- Histograms use metres internally and mm output metadata, with positive STEP and
  at most 10 million bins. .peaks contains unweighted radial means by zero-based
  reference turn, not fitted histogram peaks. Multiple containers pool same-turn
  hits. The step-start reference turn labels the accepted interval.
- Independent reference counters never modify transport turn counting. A stationary
  endpoint refresh preserves timestamps and hysteresis when a container resumes
  after another container has advanced the global clock.
- No-hit runs create a zero .hist and header-only .peaks, without a phase-space
  file. Existing probe outputs are rejected to prevent stale-hit interpretation;
  normalized basename aliases and duplicate probe outputs are rejected.
- Explicit checkpoint restart/tracking continuation is unsupported. Independent
  fresh TRACK runs start new recordings and require fresh output basenames.

## Changed files

OPALX:
- src/Algorithms/CyclotronProbe.h: device segment kernel/state.
- src/Algorithms/CyclotronProbeRecorder.{h,cpp}: recording, histogram and output.
- src/Algorithms/ParallelTracker.{h,cpp}: separate registration and accepted endpoints.
- src/PartBunch/ParticleContainer.hpp: optional migratable diagnostic storage.
- src/Elements/OpalProbe.cpp: input conversion/validation and global geometry.
- src/AbsBeamline/Probe.h: document active configuration/recorder interface.
- Algorithms source/test CMakeLists and unit_tests/Algorithms/TestCyclotronProbe.cpp.
- tools/check_cyclotron_probe.py: reproducible integration/passivity checks.

Manual checkout /Users/adelmann/git/opalx-manual:
- user-guide/elements.qmd: syntax, coordinates, output, supported configurations.
- physics/overview/index.qmd: interpolation, clipping, radial bins, grouping/accuracy.

The originally supplied manual-opalx/physics-manual-opalx paths do not exist;
PhysicsManual is empty. The current manual's physics/ tree is authoritative here.

## Validation completed on final source

OpenMP build completed using the existing build_openmp toolchain.
The cached IPPL fb5cebc revision lacked getCutoff/shiftedGreensFunction required by
this branch's existing P3M code. The build-cache IPPL_GIT_TAG was pinned to current
upstream master 704932fdaa390f883524cf53588c92386294add4. No upstream source or
repository dependency defaults were patched.

Five CTest targets passed:
- TestCyclotronProbe (8 test cases)
- TestCyclotronProbeMPI (same cases on 2 ranks)
- TestPassiveProbe
- TestPassiveRingProbe
- TestLossDataSink

Coverage includes actual device execution, orientations and reversed endpoints,
finite segment misses/boundaries, initial/on-plane duplicates, zero/tangent
momentum, jitter, stable ID replacement, invalid inputs, resumed-clock refresh,
input mm conversion, histogram units, distinct reference-turn groups, laboratory
frame changes, real IPPL migration, empty ranks, HDF5 charge/mass/IDs/timestamps,
ASCII output, collective invalid-endpoint/I/O errors and stale-file rejection.

Integration command (all transport runs on one rank):

    ~/.venv-h6/bin/python tools/check_cyclotron_probe.py \
      --executable build_openmp/src/opalx \
      --regression-root /Users/adelmann/git/regression-tests-x \
      --output build_openmp/probe-final

Passed coasting and RF-stop OFF/HDF5/ASCII comparisons. Coasting records two hits
and RF-stop one hit per probe. Reversed endpoints agree; a no-hit probe produces
zero profiles. Final particle arrays, reference arrays, time, path length and
GlobalTrackStep are exactly equal to OFF. Also passed STEP=0, degenerate geometry,
non-cyclotron and repeated-output rejection cases. Inputs and executable hashes
are retained in build_openmp/probe-final/report.json; logs are beside each case.
No regression references or existing numerical tolerances were changed.

Manual source validation passed (58 chapters); both edited pages rendered;
rendered HTML validation passed (64 pages). git diff --check passed in both repos.
Production diff and new source/tests were reviewed.

Test-development failures were resolved without relaxing tolerances: missing
standalone logger, a borrowed mesh/layout lifetime in the MPI fixture, and a
synthetic momentum reversal that incorrectly interpolated zero crossing momentum.
The task-owned faulty MPI test was stopped; unrelated processes were untouched.
A test also confirmed legacy process-wide follow-up flags are inactive for fresh
TRACK construction; independent fresh runs are checked through output reuse,
without changing general tracking lifecycle behavior.

## Limits and remaining risks

- No FFA/RingElement placement or compatibility implementation in this step.
- COF currently rejects PROBE in its input lattice. Use a separate field-only
  RING for solving; ordinary cyclotron tracking is implemented here.
- Newly created/emitted particles need a first accepted endpoint. Missing
  intervals are not reconstructed; particles lost before observation have no
  accepted crossing pair.
- Linear interpolation has O(dt^2) event error for smooth transverse crossings;
  hidden multiple crossings and RF impulses inside an interval are unresolved.
  Keep probes away from SINGLEGAP impulse planes and resolve crossings with DT.
- Reference-turn grouping near the return plane is limited to accepted-step
  resolution. Histogram counts/IDs are exact; diagnostic floating-point sums can
  differ in their final bits across MPI partitions.
- The initial probe milestone retained SINGLEGAP single-proton restrictions. The subsequent accelerating PIC extension is tracked in [ACCELERATING_SC_STATE.md](ACCELERATING_SC_STATE.md).
- Validation was OpenMP, not CUDA/HIP. Large-scale diagnostic memory/collective
  overhead was not benchmarked. Histories scale with particles times probes;
  the existing loss writer buffers hit records until final save.
- The integration harness is maintained in tools/ and uses existing regression
  fixtures; the NightlyBuildX pipeline itself was not changed.

## Step two: old OPAL FFA/RingElement probes

1. Pin authoritative old OPAL source and a working FFA input; verify local/global
   transforms, symmetry copies, azimuth/length, apertures, direction and schema.
2. Adapt legacy occurrence placement to the common passive recording backend,
   keeping global cyclotron segments distinct and avoiding seam duplicates.
3. Validate analytic drift/FFA rings, rotated/offset/repeated occurrences, losses,
   ownership changes and turn labels against old OPAL; verify unchanged transport.
4. Document compatibility and differences. Any new input syntax/public API needs
   explicit agreement. Consider COF passive-element handling and checkpointed
   diagnostic continuity as separately tested extensions.

## PSI Ring demonstration (2026-10-23)

Completed full 72→590 MeV Ring acceleration with two radial probes and the old
manual extraction geometry: 189 hits per radial probe, three extraction hits,
590.3268245 MeV final energy. Probe-off controls match all saved transport and
statistics exactly. Inputs, hashes, CSVs, plots and report are under
`tmp/ring-probes-20261023/`; see its `HANDOFF.md` and `summary.json`.
A separate ten-turn coasting check develops a 22.998 m particle/reference
separation identically with probes off; recorded for follow-up, not diagnosed
or changed in this task. No production code changes were made for these runs.

## Coasting follow-up (2026-10-23)

The ten-turn separation is now fixed: conservative spatial sector candidates replace repeated first-turn path-index sector membership for RING callbacks. Final separation is 1.19e-11 m; radial probes each see ten crossings. Ten-turn OFF/ON and two-rank statistics match exactly; full RF states are unchanged. See [COASTING_FIX_STATE.md](COASTING_FIX_STATE.md) for diagnosis, tests and artifacts. This supersedes the unresolved coasting limitation recorded above. FFA probes remain deferred.
