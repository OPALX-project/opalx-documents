Deferred follow-up from #637 and #615. No implementation is requested as part of the current cyclotron PROBE work.

The operator has confirmed that the field map is no longer physically valid at the high-energy end of the historical run near 584 MeV. Future studies should stop earlier, within the map's valid operating range. This issue concerns how OPALX diagnoses and terminates an out-of-validity run; it does not propose extending the map, relaxing its support, or establishing a universal energy cutoff of 584 MeV.

**Observed case**

The original case used a 16³ OPEN PIC mesh, 32,768 proton macroparticles, 2 mA equivalent current, one MPI rank, four OpenMP threads, MIDPOINT self-field sampling, five SINGLEGAP cavities, dt = 1.6452780519907864e-10 s, and a 590 MeV reference-energy target.

The last logged reference event was RF3 at 584.1575 MeV. Tracking then reported:

```text
User error detected by function "ParallelTracker"
SINGLEGAP particle left field support or received an unphysical kick.
MPI_ABORT was invoked on rank 0 ... Errorcode: -100
```

The launcher returned 156. This is a caught transport error followed by an explicit MPI abort; the log does not show a segmentation fault.

The historical message merged magnetic-support rejection and RF-kick rejection. The map's stored support was radial 1.9–4.7 m and vertical ±50 mm, with half-open sector angles. The largest saved vertical extent was 44.36 mm at mean energy 581.88 MeV. Vertical halo leaving support is plausible, but the exact failing particle and guard were not recorded. A nonfinite trial state can also fail geometric support comparisons. A gap-profile radial miss alone is skipped and is not sufficient to explain the fatal error.

The saved HDF5 file contains metadata only and no particle-step groups. The old particle-level cause therefore cannot be reconstructed from these outputs. This is not the terminal EKINSTOP endpoint issue: the requested 590 MeV target had not been reached. An 8³ rerun is not a physical reproduction of the original 16³ case.

**Current implementation and remaining defects**

The current PR source is `6a32ba6ddb44730de0c0ac3590b07b16cf089702` (tracked contents identical to the historical local `a9d38caa` checkout):

- [ParallelTracker.cpp:1359–1399](https://github.com/OPALX-project/OPALX/blob/6a32ba6ddb44730de0c0ac3590b07b16cf089702/src/Algorithms/ParallelTracker.cpp#L1359-L1399) reduces particle failures collectively and records a category, ID, time and laboratory state. However, the detailed message uses `*gmsg`, constructed as the default rank-zero-only logger in [Main.cpp:184](https://github.com/OPALX-project/OPALX/blob/6a32ba6ddb44730de0c0ac3590b07b16cf089702/src/Main.cpp#L184). A failure confined to another rank can therefore lose its detailed diagnostic while all ranks still throw the generic exception. This was not the reason the original one-rank run lacked detail: that older implementation did not yet record it.
- [ParallelTracker.cpp:850–858](https://github.com/OPALX-project/OPALX/blob/6a32ba6ddb44730de0c0ac3590b07b16cf089702/src/Algorithms/ParallelTracker.cpp#L850-L858) flushes previously accepted probe hits before rethrowing particle-step errors. [TrackReferenceStep.cpp:88–94](https://github.com/OPALX-project/OPALX/blob/6a32ba6ddb44730de0c0ac3590b07b16cf089702/src/Algorithms/TrackReferenceStep.cpp#L88-L94) does the analogous collective cleanup for reference-trial failures. Existing deliberate one-/two-rank RF-failure checks preserve one accepted hit and return nonzero promptly.
- [Main.cpp:488–501](https://github.com/OPALX-project/OPALX/blob/6a32ba6ddb44730de0c0ac3590b07b16cf089702/src/Main.cpp#L488-L501) still calls `MPI_Abort(MPI_COMM_WORLD, -100)` after printing an OpalException. Normal field cleanup and runtime finalization at [lines 572–579](https://github.com/OPALX-project/OPALX/blob/6a32ba6ddb44730de0c0ac3590b07b16cf089702/src/Main.cpp#L572-L579) are bypassed. Other current GH200 fatal-error logs show secondary `cudaErrorCudartUnloading` teardown errors.
- Failure is not a whole-bunch transaction: some particles may have committed an attempted step before another particle rejects it. Accepted probe hits are valid, but the live bunch must not be saved or advertised as a consistent restart checkpoint without rollback or a preserved last-accepted state.

**Desired behavior when this is implemented later**

- Report the first relevant failure reliably regardless of the owning MPI rank, including category, stable particle ID, rank, accepted step/time, and sufficient-precision laboratory/local position and momentum. Include the violated map/domain bounds or RF-kick invariant; distinguish a domain exit from a nonfinite state.
- For a failure already detected collectively, propagate one coherent fatal status before cleanup. Preserve and close accepted diagnostic output, unwind runtime-owned objects in the supported order, and return a nonzero job status without hanging peers or producing secondary GPU teardown exceptions.
- Retain an abort fallback for unsafe or uncoordinated failures. Do not replace all MPI_Abort calls indiscriminately with MPI_Finalize: asymmetric exceptions can otherwise deadlock.
- Make the last accepted step and the absence of a restartable checkpoint explicit. Save a consistent last-accepted state only if it is actually available; do not serialize the mixed attempted-step state as valid physics output.
- Keep out-of-domain handling explicit. Do not silently enlarge the field map, drop offending particles, continue with missing fields, or widen numerical tolerances to suppress the error. Any particle-loss versus whole-run-stop policy needs a separate physics decision.
- Verify one- and two-rank behavior, including a failure owned only by a nonzero rank, and allocated CPU/GPU shutdown. Native unit checks must remain self-contained C++; input-file integration checks are separate. Controlled software failure checks do not establish the original beam's high-energy physics.

Historical input, maps, distribution, launcher metadata and log are preserved in the task workspace under `tmp/ring-space-charge-profiles-20261023/accelerating-pic-16/`. The read-only accounting script and findings are under `tmp/probe-status-20261107/failure-584/`. These are local task artifacts, not files currently tracked in this repository. A future exact trajectory replay requires staging the original 16³ data; it should not be used to infer valid physics beyond the map's operating range.
