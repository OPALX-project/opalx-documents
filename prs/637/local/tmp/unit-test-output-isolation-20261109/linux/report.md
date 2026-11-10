# Linux validation of unit-test output ownership

The original field-map fixtures share `/tmp/opalx_fm2d_test`. On Linux Debug/OpenMP, both passed separately, but their first concurrent run failed ten cases. One concrete error was `filesystem error: cannot remove: Directory not empty [/tmp/opalx_fm2d_test]`. This confirms the same ownership problem found in the loss-data tests.

The reviewed update contains 29 test C++ sources and one shared temporary-directory header. The helper atomically claims a new directory and removes only that directory; MPI callers broadcast the root-owned path. Production and CMake sources remain unchanged, and all seven previous audit/loss files retain their hashes. Native tests remain self-contained C++, with generated inputs and no external Python or reference-data dependency.

| Linux check | Result |
| --- | --- |
| Original FM2D tests separately | 2/2 targets pass |
| Original FM2D tests together | First pair fails ten native cases |
| Fixed affected targets | 29/29 pass |
| Fixed concurrent FM2D pairs | 20/20 pass; 840 native case executions, no skips |
| Additional MPI checks | All five commands pass; 18 native case executions, no skips |
| Full suite | 136/137 targets pass; known Gaussian failure retained |
| Source/rebuild verification | 1,073 current-checkout hashes verified; 29 fresh objects/relinked binaries; unchanged production library |

The MPI commands cover checkpoint round trips on two ranks, diagnostic HDF5 rewind on two, ORB updating on two, ORB load balancing on four, and FFT2D5's multiple-rank rejection on two. The four-rank ORB and two-rank FFT checks execute paths skipped by their ordinary one-rank registration.

The full suite still fails `GaussianTest.largeCutoffDisablesTruncation`: an untruncated-normal maximum of 5.5717775960503042 exceeds its hard 5.5 assertion. No Gaussian source, seed or tolerance changed, and no additional Gaussian rerun was made for this task. We do not claim a fully passing broad suite.

Job 355094 captured the original race. Job 355096 completed the fixed-source build and planned checks in 13m37s; both are terminal with an empty task queue. The after job records the full-suite exit 8 and retains that separate failure while accepting only the specified known Gaussian case. All affected tests and additional MPI checks passed.

Validation used CPU Debug/OpenMP on merlin-g-100, GCC 14.3, OpenMPI 5 and CMake 4.4, with four OpenMP threads. The compute kernel is Linux 5.14el9_8; the SSH login's RHEL 8.10 release is recorded separately. Kokkos 5.2.2 differs from GitHub CI's 5.2.0, so this is not an exact CI-image reproduction. The production library and prior evidence archive remain byte-identical.

Raw evidence is under `remote-evidence/`. From this directory, re-run the analysis with `/Users/adelmann/.venv-h6/bin/python audit_linux.py --evidence remote-evidence --checkout /Users/adelmann/git/opalx-master --output audit.json`. The source-update package and manifest are included in the raw bundle. Its SHA256 is `e06d7b6d09d549b42d24260608b88633f14c1284a71fb609816c5582e0cf575f`; size 327445 bytes. `STATE.md` records the superseded unsubmitted helper package, rejected redundant dependency and transient monitoring DNS error. No source or numerical fix was made during validation, and no source changes are committed or pushed.
