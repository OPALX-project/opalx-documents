# Space-charge and PartBunch output-isolation changes

Status: implementation and static review complete. No builds/tests run by this worker; root coordinates shared build after all agents finish. No commit/push.

Owned files/targets:
- unit_tests/PartBunch/TestMultiContainerPartBunch.cpp / TestMultiContainerPartBunch
- unit_tests/SpaceCharge/TestCartesianPIC3DAlgorithms.cpp / TestCartesianPIC3DAlgorithms
- unit_tests/SpaceCharge/TestCartesianPIC3DComponents.cpp / TestCartesianPIC3DComponents
- unit_tests/SpaceCharge/TestCartesianDomainLoadBalancing.cpp / TestCartesianDomainLoadBalancing
- unit_tests/SpaceCharge/TestCartesianDomainUpdaterORB.cpp / TestCartesianDomainUpdaterORB
- unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp / TestFFT2D5Algorithm
- unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp / TestFFT2D5Numerics

Design: reuse root's unit_tests/TemporaryDirectory.h with create(prefix, MPI_Comm). The helper creates one unique shared directory on root and broadcasts the path; reset performs no collective. Fixture cleanup closes bunches/sinks/solvers, synchronizes peers, restores OpalData input filename, removes only the owned directory, then synchronizes again. No cwd changes or CMake changes.

PIC algorithm/components and MultiContainer fixtures now assign a per-case absolute owned input basename so all DataSink stat/lbal output is isolated. MultiContainer HDF5 paths and rewind basename also stay under that directory. Inline fixed-name removals (some executed while local writers were live) are removed in favor of fixture ownership cleanup. The two ORB fixtures create no DataSink or output files, so their unconditional removal of unowned stat/lbal files is simply removed; no directory is needed there.

FFT2D5Algorithm creates its generated reference path under an owned shared directory; root writes and all ranks synchronize before reading. FFT2D5Numerics assigns an owned absolute input basename and replaces default/explicit reference-path literals with fixture members. OpalData.getInputBasename preserves directory components, and Util.combineFilePath uses filesystem::path /=, so its absolute default basename replaces the hardcoded auxiliary data prefix. Default resolution is still exercised, with no production override or changed reference contents. Fresh owned directories remove the need to delete a shared default path at setup/teardown.

Static checks pass: LLVM21 clang-format dry run, git diff --check, exact test-name and assertion-operator sequence comparisons against HEAD. No tests, numerical tolerances or mathematical expressions added/changed.

Recommended validation: rebuild/run seven targets. LoadBalancing skips unless four ranks, ORB has a meaningful manual two-rank path, and FFT2D5Numerics has an existing two-rank Configuration_MultipleRanksRejected subset. MultiContainer HDF5 rewind can be selected on two ranks to validate shared directory use. Tests remain self-contained native C++ with generated data; no external Python/data dependencies.
