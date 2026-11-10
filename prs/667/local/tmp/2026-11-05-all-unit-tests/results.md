# Unit-test results, 5 November 2026

Build: `/Users/adelmann/git/opalx/build-omp`, Release/OpenMP, current working tree.
The previous executable is preserved; identity is in build-identity.json.

Two uncommitted test targets cannot compile: TestScalingFFAMagnet refers to
missing ScalingFFAMagnetConfig::outsideAperture/contains; TestDeviceExternalField
refers to missing device_external::Lattice::fieldOracleSupported. Stale binaries
for these two targets were excluded from execution.

All other 129 targets were rebuilt and run with one MPI rank:
- OpenMP 1: 128 pass, TestOpalBeamlinePlacement fails.
- OpenMP 4: 127 pass, TestOpalBeamlinePlacement and TestGaussian fail.

The placement failures are the added SchoolScalingFFACellEntrancePosesAndSignedRadii
and ScalingFFAExitFramesPlaceFollowingDrift cases. GaussianTest.largeCutoffDisablesTruncation
fails with four threads: maximum5.5717775960503042 exceeds5.5; a focused repeat
reproduces it. No source or tolerance changes were made.

Python:1,194 pass,1 optional native-artifact test skipped, covering the regression
runner and all current conversion-tool unit/development suites. The two-rank
FFT2D5 rejection test passes on both ranks. Both CTest runs pass the FFT2D5 targets.

Complete commands, build errors, JUnit output and logs are in this directory.
