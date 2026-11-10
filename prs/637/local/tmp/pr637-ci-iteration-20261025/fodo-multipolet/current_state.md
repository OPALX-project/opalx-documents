Goal: explain and resolve FodoCell-multipoleT-fromfile CI mismatch without changing input/data/eps or hiding a physics discrepancy.

Diagnosis: unchanged candidate reproduces old CI errors exactly. July17 reference predates intended Sep4 fc719154c expansion to six-fringe support and reference-field application; old reference momentum is frozen. Current remote regression737547 fixture remains unchanged from local a8bd50c. Strong stale-baseline evidence, not new RF/probe or backend precision behavior.

Changed tracked file: only unit_tests/AbsBeamline/TestMultipoleTStraight.cpp (+61lines), independent analytic tanh-fringe/device/scalar/reference parity and support test. No production source, maintained references, particle input, or existing tolerance changes.

Tests: fresh TestMultipoleT/TestMultipoleTBase/TestMultipoleTStraight, one rank OMP2:3/3targets25/25casesPASS. Main build and opalx_exe relink complete; resources released to root baseline build. Logs/native-LastTest.log preserved here.

Fresh executable e4e8b35004a178b0f8fc2d3cd3bd644874d1043ffcce537e64275f37f9a0a9cc reports23f04f6. Draft standard makeReference.sh reference under draft-standard-generated/reference; input/data/rt unchanged, MD5checks3/3PASS, held-out comparisons7/7PASS. Draft only; regression checkout clean.

Next: root's isolated named-origin/master8c1a862 baseline build/run and comparison; root decides whether to publish focused test and reference refresh. No commits/pushes by this child.
