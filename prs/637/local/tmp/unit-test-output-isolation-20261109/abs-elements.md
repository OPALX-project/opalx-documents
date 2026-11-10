# Beamline and element test output isolation

Status: implementation and source review complete; builds/tests delegated to root for coordinated execution. No staging, commits or pushes.

Changed five existing fixtures using the shared native TemporaryDirectory helper:

- TestFieldmapElement: owned map directory; release all registered cached maps before resetting directory. Absolute input filename also contains any future diagnostics; the previous OpalData input filename is restored before removing the owned directory.
- TestFieldmapVsAnalytic: each generated comparison map lives in an owned directory; release fieldmap before cleanup.
- TestSolenoid: owned maps and diagnostic outputs. An absolute input/output stem routes OpalData/IndexMap/MeshGenerator writers into the same directory because Util::combineFilePath uses filesystem path composition. No process working-directory mutation. Explicit DataSink/FieldSolver shared pointers are released before cleanup, then the previous OpalData input filename is restored before removing the directory. Removed fixed-name pre-test deletion and manual output list.
- TestScalingFFAMagnet: move b_twod.out, convergence_y.out and convergence_endlength.out from fixed /tmp paths into the owned directory. Streams close at test-body exit before fixture cleanup.
- TestRBendSettings: profile.map lives in a unique owned directory instead of a fixed per-case name shared by concurrent executable invocations.

No numerical assertions, tolerances, test registration, runtime production code or field-map data contents changed. No external Python or data dependencies. TestCyclotronSector and TestCyclotronRF were protected and not edited; their paths already use process IDs. The remaining AbsBeamline/Elements tests were audited: no generated output or only non-writing DataSink constructors. Those unchanged constructors inspect filename existence but do not write. TestMonitor explicitly avoids output checks.

Validation completed: LLVM21 clang-format --dry-run --Werror and scoped git diff --check pass. No builds or tests started by this agent. Relevant targets: TestFieldmapElement, TestFieldmapVsAnalytic, TestSolenoid, TestScalingFFAMagnet, TestRBendSettings. All are registered one-rank targets; collective filesystem semantics are unchanged.

Source hashes:

- unit_tests/AbsBeamline/TestFieldmapElement.cpp: d9723338eebdee1e52f8a2a4302a634d4f1fc4bd79fab87f6ee776507ce22f1a
- unit_tests/AbsBeamline/TestFieldmapVsAnalytic.cpp: 4973bd98879f4ce8e0c15198d3d69a36095f72be77703fe6afbd85ea1d2f4db8
- unit_tests/AbsBeamline/TestScalingFFAMagnet.cpp: 07e20a613c66a7ad0f80b47a5f3762b584f5e19ee9f2623cf4067d7e451c145f
- unit_tests/AbsBeamline/TestSolenoid.cpp: ddc92999a001e787b83f5bf4ecbd00cbf7e380fb7566793f8c3af7589aebf207
- unit_tests/Elements/TestRBendSettings.cpp: aec923429f194b995fabfc5b599db76bcee215a7b66dc78e9378ac2757c3bc0a

Final ownership review: FieldmapElement and Solenoid now save the previous OpalData input filename in SetUp and restore it in TearDown before directory reset. Formatting and scoped diff checks pass; no builds/tests were run. All owned files are frozen after this change.
