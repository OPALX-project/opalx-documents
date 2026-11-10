# PR #637 complexity, duplication and performance audit

Audited 9 November 2026: `b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93` against `bdf5a47a0fc209e288d8cd94448e171fe8679a8a`. Full PR:41files,+3730/-228lines. Review made no source changes.

The shared algorithms are appropriately consolidated. The principal concerns are per-step synchronization, diagnostic scratch allocation and duplicated history data. There is no justification for a broad tracking rewrite.

## F1 [P2] One global error reduction per station per accepted endpoint

[src/Algorithms/CyclotronProbeRecorder.cpp:130](/Users/adelmann/git/opalx-master/src/Algorithms/CyclotronProbeRecorder.cpp:130)

Each station executes scalar host-result device reduction, MPI_Allreduce at159, count mirror at162 and compact-hit mirror at163. Empty ranks and no-hit intervals participate too. 16 stations imply 16 error collectives per observed endpoint.

Proposed action: Batch station validity into one collective per observation, then consider batched counts/transfers. Continue observing every accepted interval; do not optimize by dropping samples.

Timing: Dedicated performance follow-up, as previously agreed.

## F2 [P2] Full per-particle failure array allocated on every accelerating-PIC step

[src/Algorithms/ParallelTracker.cpp:1346](/Users/adelmann/git/opalx-master/src/Algorithms/ParallelTracker.cpp:1346)

Fresh default-initialized Diagnostic array every step; diagnostics(i)=diagnostic at1366 for successful particles too; host only reads on global failure and prints first record per rank. Diagnostic layout is64 bytes,16MiB for262144 local particles before allocation/initialization costs.

Proposed action: Reuse capacity-managed scratch storage; preferably retain one atomically selected first-failure record per rank and write only on failure, preserving collective failure propagation.

Timing: Small cleanup before merge recommended.

## F3 [P2] Duplicated endpoint history costs160 bytes per station per allocated particle

[src/Algorithms/CyclotronProbe.h:36](/Users/adelmann/git/opalx-master/src/Algorithms/CyclotronProbe.h:36)

Two directed State records each hold the previous Endpoint; the same accepted endpoint is also duplicated across stations. All histories are registered migratable IPPL attributes. Local compile-time sizes verified: Endpoint56, directedState72, cyclotronState160, Hit96 bytes.

Proposed action: Future compact state: one migratable accepted endpoint per particle plus station-specific arming/passage information. Retain stable-ID association and out-of-line CUDA lifecycle ownership.

Timing: Dedicated performance follow-up, as previously agreed.

## F4 [P2] Cyclotron flush reduces every historical turn and rewrites unchanged summaries

[src/Algorithms/CyclotronProbeRecorder.cpp:208](/Users/adelmann/git/opalx-master/src/Algorithms/CyclotronProbeRecorder.cpp:208)

Flush every100 accepted global steps. Sink no-hit return does not skip subsequent summary work. One MPI_Reduce per turn0..maximumTurn, plus histogram reduction and full file replacement. maximumTurn200 means201 tiny peak reductions per station per flush. FFA radialSummaries=false correctly bypasses this branch.

Proposed action: Pack turn sums/counts into one array reduction and use globally agreed dirty state to skip unchanged summary rewrites. Preserve flush cadence and cumulative output semantics.

Timing: Focused performance follow-up.

## F5 [P2] Sector support predicate and coordinate calculations have two owners

[src/AbsBeamline/CyclotronSector.h:168](/Users/adelmann/git/opalx-master/src/AbsBeamline/CyclotronSector.h:168)

New DeviceField::add recomputes radius/angle/support at168..172, then shared cyclotron_field::field repeats it at59..63. Boundary rules could drift. Inlining may eliminate some redundant arithmetic; actual double-transcendental execution was not measured.

Proposed action: Let shared evaluator report support while accumulating B; forward its boolean from the descriptor. Preserve boundary and nonfinite-input semantics explicitly.

Timing: Small cleanup before merge recommended.

## F6 [P3] RF transport dispatch repeats validation and contains dead guard

[src/Algorithms/ParallelTracker.cpp:1252](/Users/adelmann/git/opalx-master/src/Algorithms/ParallelTracker.cpp:1252)

Host/device branches repeat proton/spin/restart validation at1262 and1291. Nested cardinality rejection1255..1260 is unreachable because outer condition already proves those requirements. Immutable descriptor construction1300..1331 is inline in step routine.

Proposed action: Prepare/validate common RF capability once, remove dead guard, keep concise host/device step helpers within existing code. No additional tracker hierarchy.

Timing: Small cleanup before merge recommended.

## F7 [P3] Lattice classification and gap collection repeatedly allocate sets and sort

[src/Algorithms/ParallelTracker.cpp:1108](/Users/adelmann/git/opalx-master/src/Algorithms/ParallelTracker.cpp:1108)

hasCyclotronGaps plus reference gap assembly1118..1132 existed in base; extension adds calls. OpalBeamline::getElements at89 reconstructs std::set by value. This is inherited debt amplified by PIC, not a newly introduced helper.

Proposed action: Cache immutable gap/sector occurrences during preparation, preserving current ordering.

Timing: Follow-up.

## F8 [P3] General adapter retains and copies whole files in memory

[tools/probe_frame_adapter.py:66](/Users/adelmann/git/opalx-master/tools/probe_frame_adapter.py:66)

Retains HDF5 batch DataFrames, concatenates, globally sorts and repeatedly validates/copies records. Ten64-bit columns alone cost80 bytes/hit;10million hits require800MB before copies, sorting and Python integer lists.

Proposed action: Consider an explicitly ordered batch-export mode and efficient typed integer validation when production analysis needs it. Streaming must not silently change documented global ordering.

Timing: Future analysis-scale follow-up.

## Quantified storage

Local ABI sizes verified with the existing recorder compile flags and the enclosed `probe-sizes.cpp` static assertions. These are storage calculations, not runtime measurements.

| Particles |16-station histories|Shared hit scratch|PIC diagnostic array|
|---:|---:|---:|---:|
|4,096|10MiB|0.375MiB|0.25MiB|
|32,768|80MiB|3MiB|2MiB|
|262,144|640MiB|24MiB|16MiB|
|1,000,000|2.38GiB|91.55MiB|61.04MiB|

History is160bytes per station per allocated particle, including unused capacity. Hit scratch is96bytes per local high-water particle count, reused across stations; do not multiply it by the station count. PIC diagnostics are64bytes per local particle. History adds to particle migration payload through registered IPPL attributes.

## Consolidations worth retaining

- `rf_event::advance` shares host/device event ordering and localization; `CyclotronRFKick` shares kick physics.
- Cyclotron and FFA use one passive recorder, crossing kernel and standard loss writer.
- Read-only device descriptors are necessary GPU representations; they borrow map data rather than duplicating maps.
- The out-of-line history factory/custom deleter fixes an observed shared-library CUDA problem and adds no per-particle owner state.
- Native tests are self-contained C++. Of3730added lines,1690are native tests,1511production source,406Python tools and123docs/CI. Independent numerical test oracles should stay independent.
- Separate stop/probe counters are a minor potential consolidation, but their initialization/lifecycle and step-start labels must be proven equivalent before merging them.

## Inherited costs and limits

Root-gathered ASCII output and per-record std::endl in LossDataSink, and HDF5 batch moment calculations, predate this PR. New probe usage exposes those costs more often. Repeated lattice set construction is also inherited. None should be described as entirely introduced by the new FFA commit.

Structural costs and local ABI sizes are established; actual wall-clock slowdowns/speedups are unmeasured. Existing small GPU runs establish correctness, not representative beam-scale performance. No source fix, commit, push or GitHub review/comment made for audit.

Recommendation: make the small F2/F5/F6 cleanups before merge. Preserve the previously agreed separation for larger F1/F3/F4 performance work. Benchmark identical physical input with probes OFF and1/4/16stations at representative particle counts, recording accepted steps, kernel/synchronization time, migration traffic and peak memory. Reducing observation frequency is not a valid optimization because crossings can be missed.
