> Update, 9 November 2026: the adapter is now general (`tools/probe_frame_adapter.py`), with arbitrary Cartesian origin/basis and unchanged identity/turn/time labels. The school is solely a comparison benchmark. See the current FFA task state for validation. No commits or pushes.

> Implementation update, 7 November 2026: the user approved this plan and native output plus the school adapter. Implementation is on `codex/ffa-probes-school-parity`. CPU and fresh A100 validation and old-school comparisons are complete. See [current state](../ffa-probes-implementation-20261107/STATE.md) and [implementation report](../ffa-probes-implementation-20261107/REPORT.md). The proposal below is retained as the design record; no push is authorized.

# FFA PROBE design for discussion

Status: proposal, 7 November 2026. No production code, public input, branch or simulation has been changed. The current source is the merged Probe branch ec4319ac. The user requested discussion before implementation. The user confirmed native OPALX laboratory output plus a school-reader adapter on 7 November 2026. The remaining implementation design and scope are still proposals for discussion.

**What the supplied examples actually require**

The original FFA25_OPAL.ipynb creates 16 named global radial probes for the 16-cell ring and four for the fourfold ring. The detector lines are explicitly included once. SYMMETRY repeats magnetic components, not the probe list. Automatically making symmetry copies would multiply hits incorrectly.

The legacy probe mechanism is a global PluginElement observer. Authentic local OPAL-2022.1.0 source contains no RingElement/getRingElement API. Its magnetic Ring/RingSection placement is separate from the detector list. Consequently the first FFA milestone should extend the existing global passive PROBE path; it does not require importing a legacy ring-placement hierarchy.

The old input uses endpoints in mm, STEP default 1 mm, WIDTH unused, and a finite segment extruded without a vertical aperture. Both crossing directions are accepted and particles are not removed. The school macro's DANGLE parameter is unused. The 16-cell radial interval is 3.42–5.42 m, with stations every 22.5 degrees; the fourfold interval is 3–5 m, at 0/90/180/270 degrees.

School readers expect PROBE1.loss etc., one header line and ten columns: x,y,z [m], px,py,pz [p/(mc)], particle ID, shared tracker turn, bunch number, time [s]. They do not provide actual saved .loss files, so the repository is an input/reader specification rather than an old-binary numerical baseline.

**Coordinates: agreed output contract**

Keep the existing native OPALX convention for all PROBEs: XSTART/XEND are global laboratory X; YSTART/YEND are the global laboratory Z coordinate of the horizontal plane. Laboratory Y is vertical. Input endpoints and STEP remain mm. Do not silently change the meaning of these attributes according to the magnet type.

The migrated school ring has its native laboratory centre at (-R0,0) in X–Z. Its reader uses radius=hypot(lab_x+R0,lab_z). For that untransformed school geometry, migrate a station at angle phi as:

```opal
P01: PROBE,
    XSTART=1000*(RMIN*COS(phi)-R0),
    XEND=1000*(RMAX*COS(phi)-R0),
    YSTART=1000*RMIN*SIN(phi),
    YEND=1000*RMAX*SIN(phi),
    STEP=1, OUTFN="PROBE1";
```

Here phi is in radians. This formula is for the existing school frame, not a universal rule for every FFA ring. For a translated/rotated ring, transform detector endpoints explicitly into the same laboratory frame as the tracked particles. The initial milestone keeps globally placed stations; occurrence-local, automatically replicated detector elements would be a separate feature.

Agreed: native .loss/HDF5 remains canonical, with coordinate conversion in a school-reader adapter. For this particular frame the adapter reconstructs old(x,y,z)=(native_x+R0,native_z,native_y), with the corresponding momentum permutation. The adapter must use an explicit geometry definition; the ring centre cannot safely be inferred from arbitrary magnets or detector endpoints. No backend legacy export mode is planned. The adapter is a separate school analysis utility and must not become an external Python dependency of native unit tests.

**Shared implementation, with detector policy separated from transport**

Generalize the existing recorder in place rather than creating a second FFA tracking or output implementation. A neutral internal recorder name is reasonable if it makes ownership clear; the important part is one shared implementation.

Reuse PassiveProbe's device-safe crossing primitive, the current finite-segment clipping, stable-ID/migratable history, compact hit transfer, LossDataSink, collective I/O decisions and periodic flushing. Existing CyclotronProbe state already supplies both crossing directions for planar segments. Preserve its out-of-line libopalx allocation/destruction helpers and public device payload visibility: those boundaries fixed real shared-CUDA ownership/compiler problems.

Retain a sidecar detector registry outside OpalBeamline's magnetic placement/selection list. Current ParallelTracker::visitProbe already does this. Generalize its configuration and eligibility so supported native FFA RING tracking can observe those stations. Do not put a zero-length PROBE into the magnetic candidate list: doing so can alter placement-mode validation, field support, boundary retries, OrbitThreader and TURNS capability checks.

COF should accept a PROBE as passive and skip its diagnostics, analogous to MONITOR. The same ring can then be used for COF and TRACK, with no hit files or side effects during preparation, trial orbit searches or finite-difference rays. All real hits come from accepted TRACK endpoints. Probe ON/OFF must preserve particle/reference states, accepted timesteps and turn stopping.

The observer must not change the solver or claim new FFA space-charge/transport capability. First integration cases should use the already validated bare school rings; it can observe any existing supported tracking mode once that mode's transport contract is established.

**Crossing and turn semantics**

For endpoints a,b in the horizontal plane, use normal n=(-delta_z,0,delta_x). With accepted signed distances d0,d1, alpha=-d0/(d1-d0) locates a bracketed crossing. Interpolate position, momentum and time with the same alpha. Record only when the segment projection lies within [0,1], with the existing endpoint roundoff allowance. Keep both directions, initial-plane suppression, rearming tolerance and duplicate prevention.

Do not copy legacy adaptive-width/extrapolation numerics: old OPAL projects from the current state and retains current-step momentum, whereas OPALX's coherent accepted-endpoint interpolation has second-order event error for resolved smooth transverse crossings. Hidden multiple crossings and RF discontinuities remain unresolved; this is a diagnostic, not an event integrator.

The turn column must identify the shared reference revolution, not a local array index or a per-probe crossing count. Existing native zero-based, step-start labels should remain consistent with cyclotron output; old OPAL starts its shared counter at one. Any legacy conversion must explicitly test boundary ordering and initial-plane behavior. Stable particle ID, station identity and time remain essential; the school helpers' assumption that IDs are contiguous and row counts align must not become a core contract.

**Radial summaries need a separate decision**

The school requires phase-space records for orbit and tune analysis. Current cyclotron .hist/.peaks are specifically lab-origin radial counts and unweighted turn mean radii. They are not automatically the physical ring radius of a translated FFA ring.

The proposed first FFA milestone makes phase-space output primary and leaves existing cyclotron radial products unchanged. If radial FFA summaries are required immediately, agree an explicit radial origin or an along-detector coordinate first; do not silently use lab-origin distance as machine radius. This is an open scope point, not an implemented omission.

Old PeakFinder also mixes metre bounds with millimetre hit coordinates, so its histograms should not be a numerical correctness oracle. Compare raw crossings and independent analytic geometry.

**MPI, device execution and performance**

Priority agreed by the user on 7 November 2026: establish parity with old OPAL results first; measured efficiency optimization can follow. PR #667 was inspected at bf5bf843 (open/unmerged). It accelerates FFT2D5, independently of probe recording, and introduces temporary projected-coordinate particle migration. Preserve laboratory probe histories through this migration and observe only after coordinates are restored. The concrete recorder costs, performance evidence limits and follow-up sequence are recorded in [PERFORMANCE.md](PERFORMANCE.md).

Only diagnostic state is writable. Histories remain associated with stable IDs through sorting, deletion and ownership migration. Each physical station has independent state. Keep unique output names and reject ambiguous repeated global probe definitions rather than silently duplicating stations. The RF path's 64-gap mask must not limit the number of probes.

History storage scales with particles times stations; the existing bidirectional state duplicates accepted endpoints. Initially preserve the validated storage/ownership design, measure 4- and 16-station overhead, and optimize only with evidence. Avoid gathering all particle states to the host. The internal PassiveRingProbe gathers selected IDs and is useful as a test model, not as the all-particle production backend. Review whether collective error checks can be aggregated across stations so 16 probes do not impose 16 MPI synchronizations per accepted step.

Periodic flushing, fresh-output checks and accepted-hit preservation should remain shared. Checkpoint restart and tracking continuation remain unsupported until history/output rewind is designed. Graceful out-of-map shutdown remains deferred under issue #672.

**Implementation sequence after agreement**

1. Native laboratory frame/output plus the school adapter is agreed. Settle initial-plane and shared-turn rules and whether FFA profiles belong in the first milestone.
2. Generalize the common recorder and admit supported FFA RINGs; make COF skip probes. Preserve the existing cyclotron path and all its rejection/output contracts.
3. Add focused self-contained native C++ coverage for planar FFA station geometry and actual device/MPI histories. Unit tests must not call OPALX or external Python or depend on supplied input/data files.
4. Add probes to fresh copies of the three native school cases: 16-cell, 55-degree D-off and fourfold. Keep original notebooks/helpers unchanged. Use separate input-file integration runs and native COF/INITIALORBIT.
5. Establish old/new comparisons with recorded executable hashes and matching full six-dimensional initial conditions. The old notebook's nominal 12 MeV launch actually has extra radial-momentum energy; matching only nominal E0 is insufficient. Keep tune-estimator work separate from detector sampling.
6. Validate one/two MPI ranks and allocated A100, then the relevant CSCS backends; document geometry, coordinate/turn differences and interpolation limits.

Use a new implementation branch after agreement, based on updated master after PR #637 merges, or on its published head if work begins earlier. No new branch or push has been authorized by this discussion request.

**Concrete verification criteria**

- Exact analytic drift intersections and known circular crossings at cardinal and oblique angles; finite misses, reversed endpoints, both directions and no vertical clipping.
- Initial-on-plane, shared endpoints, tangencies, jitter and 0/2pi seam behavior; define counts explicitly rather than infer them from a possibly duplicated old log.
- Four and 16 physical stations produce four and 16 outputs, without symmetry multiplication.
- Migration, compaction, empty ranks, single-value/array charge-mass storage and repeated flushing preserve identity/counts.
- COF/OrbitThreader preparation creates no hits. Probe ON/OFF tracking retains identical physical states/reference/time/steps.
- Compare HDF5 and ten-column ASCII, retaining existing six-significant-digit ASCII expectations rather than claiming full-precision file equality.
- Refine timestep for event-location error; do not rebaseline physics or widen existing tolerances to match legacy extrapolation.
- School analysis joins station/ID/turn records explicitly and rejects missing data; it must not copy the old random-data missing-file fallback or full-turn FFT spacing used for concatenated station samples.

**Evidence**

- School originals: /Users/adelmann/git/FFA25-school/FFA25_OPAL.ipynb, migration-audit/legacy-16-cell.in and legacy-fourfold.in.
- Consumers: read_dat.py, probes_tune_calc.py, plot_dat.py and optimiseCO.py.
- Native school: FFA25_OPALX.ipynb and opalx/school.py; it currently uses HDF5 section interpolation and contains no native PROBE input.
- Authentic legacy source: OPAL-2022.1.0, commit 0d1bf29f85c1799203116a6781db7fbb178b918c. The inspected source files are copied under legacy-source/ with SHA256 manifests, without changing the old checkout.
- Current source: OpalProbe, CyclotronProbe/Recorder, PassiveProbe, PassiveRingProbe, ParallelTracker, ParticleContainer, PlacementResolver and CofCmd in the current OPALX checkout.
