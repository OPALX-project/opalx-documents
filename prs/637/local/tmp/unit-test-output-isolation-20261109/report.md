# Unit-test output ownership

The directory-ownership fix now covers the remaining registered unit tests that create generated files or remove shared paths. Changes are confined to 29 existing test source files and one shared test-only header. Production code, CMake/CTest configuration, numerical assertions, tolerances and seeds are unchanged by this task. The seven prior uncommitted files remain byte-for-byte unchanged. Nothing is staged, committed or pushed.

## Why these changes are needed

The FM2D static and dynamic fixtures both used /tmp/opalx_fm2d_test and overlapping filenames. In the unchanged Linux Debug/OpenMP build, both passed separately and both failed on their first concurrent pair. The errors included map-parse interference and cleanup reporting that the shared directory was not empty. This is the same ownership defect as the earlier LossDataSink failure. Other fixtures used fixed generated maps, checkpoint files, diagnostic stems, CSV outputs or reference paths that could collide across independent invocations.

The shared TemporaryDirectory helper avoids copying directory-ownership code into every fixture. Atomic filesystem directory creation claims a fresh path; existing paths are never adopted or removed. Only the creator cleans up. Its collective overload broadcasts one root-owned directory on the shared CTest filesystem, so MPI ranks use the same path without assuming node-local temporary files are shared. Creation errors are propagated to all ranks. Cleanup itself performs no MPI collectives, keeping destruction safe during exception unwinding. Callers close resources and synchronize before cleanup.

Explicit file paths preserve filename-resolution behavior without changing the process working directory. The RF autophaser needed a namespaced cavity name because its diagnostic filename derives from that name rather than the input basename. Two ORB fixtures only stopped deleting files they never created.

## Scope

- Seven field-map fixtures: static/dynamic FM2D, FM3D, Astra dynamic/static and G4BL2D/3D.
- Six AbsBeamline/Elements fixtures: field-map element/comparison, scaling FFA, solenoid, RF cavity and RBend settings.
- Seven SpaceCharge/PartBunch sources: Cartesian PIC components/algorithms, FFT2D5 algorithm/numerics, multi-container diagnostics and the two ORB cleanup sites.
- Seven Structure/Distribution/Algorithms/BasicActions fixtures: checkpoint, Dirichlet writer, generated FROMFILE/emitted inputs, index-map SDDS, orbit diagnostics and field dumps.
- Two active Physics spectrum fixtures: muon and pion generated CSV diagnostics.

Existing safe probe paths and the earlier LossDataSink fix are unchanged. Non-writing fixtures with fixed input labels were traced through their constructors and visitors; they do not open output streams. Disabled external-reference Physics tests remain disabled and untouched. Standalone benchmarks retain their explicit user-selected output paths. Native unit tests gain no external Python or data dependencies and no new test cases.

## Validation

The final local OpenMP build passes. The full parallel local suite passes 136/137 targets, including all 29 affected targets. Twenty concurrent repetitions of each FM2D target pass. Two independent checkpoint-test processes also pass while sharing the original working directory. Formatting and independent ownership/lifetime/error-path review pass.

The sole local full-suite failure is the previously identified GaussianTest.largeCutoffDisablesTruncation hard maximum: actual 5.5717775960503042 exceeds 5.5. No Gaussian source, seed or tolerance was changed. This failure remains visible and the full suite is not claimed to pass.

Linux Debug/OpenMP job 355096 completed successfully (0:0). All 29 affected targets pass, and 20 concurrent FM2D pairs pass with 840 actual native case executions. Five manual MPI launches pass: checkpoint and multi-container HDF5 rewind on two ranks, ORB updating on two ranks, ORB load balancing on four ranks, and FFT2D5 multi-rank rejection on two ranks. These execute 18 native cases with zero skips. The default one-rank ORB targets skip their rank-dependent cases; the manual launches provide their actual coverage.

The full Linux suite passes 136/137, with only the same Gaussian maximum assertion failing. It is retained explicitly. All 1,073 source hashes match the expected current checkout, all 29 changed test executables were rebuilt and differ from baseline, and the production library and prior frozen LossDataSink evidence archive remain byte-identical. No further test runs are required.

An initial local helper implementation used mkdtemp, which was hidden by the macOS/MPI feature-macro include order. The accepted helper uses standard atomic filesystem creation and the corrected build passes. The original compile log and superseded staging package remain as provenance; neither is accepted final validation.

Exact files/hashes and target names: intended-files.json. Prior source baseline: baseline-files.json. Local outcomes: LOCAL_RESULTS.json and local-full-suite.xml/log. Raw before evidence: linux/before. Source diff: isolation.patch plus the new unit_tests/TemporaryDirectory.h.

## Final evidence and limits

The Linux checks use GCC 14.3/OpenMPI 5/CMake 4.4 on Merlin6 with Debug/OpenMP and four OpenMP threads. They do not claim parity with the exact Ubuntu CI image. The source snapshot still registers 137 targets. No CUDA runtime test is claimed for this host-only test-output change.

Raw Linux bundle: linux/validation-evidence.tgz, SHA256 e06d7b6d09d549b42d24260608b88633f14c1284a71fb609816c5582e0cf575f. Logs, JUnit, source expectations, binary timestamps/hashes and Slurm accounting are under linux/remote-evidence. The guarded driver is linux/run_after.py. ROOT_VERIFICATION.json independently checks raw results, archive integrity and all source hashes. Exact final outcomes are in RESULTS.json.

An aged dependency submission was rejected before creating an after job; the subsequent single after job ran to completion. A temporary DNS failure delayed retrieval only, then recovered. Neither event restarted tests or changed source. All task jobs are terminal.

The changes remain unstaged and uncommitted on codex/ffa-probes-school-parity at b1551b9c3. No push or PR update was performed for this task. Larger probe performance changes remain deferred.
