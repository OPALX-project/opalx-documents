# FFT2D5 frame consistency and curvature comparison

Issue #658 follows the straight-beam corrections in PR #657.

## Frame repair

Design-path points are fixed laboratory coordinates. Particle arrays use each
container's moving reference coordinates. Each solve now maps both into the same
aligned frame, reusing `CoordinateSystemTrafo`, `enterSolveFrame` and
`leaveSolveFrame`. The path uses one reusable buffer rebuilt from immutable
points. Coverage exceptions restore particle reference coordinates.

Four C++ tests in `TestFFT2D5Algorithm.cpp` check changed reference poses,
0/45/75-degree rigid planar rotations, differently framed active containers,
and exception restoration. They verify nonzero E/B, deposited charge and restored
positions, momenta and time steps. Three tests were demonstrated to fail before
the repair. These angles describe rotations of a straight setup, not bends.

Full OPALX controls use 32768 cold Gaussian protons, p/(mc)=0.4, Q=1 nC,
transverse RMS=1 mm and longitudinal RMS=50 mm. At 0/45/75 degrees, one-step
fields and 20-step, 5 cm drift outputs agree within 1.6e-12 relative RMS for E/B;
all retain the particle count and charge. Tiny one-step momentum increments have
roundoff from reference rotations; their transverse spread agrees with the
applied Lorentz force within 4.1e-8 relative RMS.

## Numerical and physical comparison

`SmoothGaussianSlicesConvergeWithoutParticleNoise` in
`TestFFT2D5Numerics.cpp` reuses density storage, the Poisson solve and gather.
It prescribes a smooth Gaussian density with sigma=1 mm and lambda=1 nC/m,
removing particle noise. The straight-field relative RMS errors on 64², 128²,
256² and 512² meshes are 6.920%, 1.863%, 0.497% and 0.132%.
The new test requires refinement ratios below 0.35 and final error below 0.2%;
no existing tolerance changed.

![Gaussian convergence and the omitted curvature contribution](frame-consistency-comparison.png)

The right panel isolates the even field at mirrored probes ±sigma. The present
flat slice model gives essentially zero. Qiang's regularized leading curvature
term gives -2.952, -0.2952 and -0.02952 V/m for R=1,10,100 m, respectively.
The plot divides by lambda/(4 pi epsilon_0 R) to compare all radii.
This identifies an omitted model term; it does not establish general curved-beam
accuracy. The frame repair adds no curvature operator or new g-factor model.

Reference: Ji Qiang, [arXiv:2606.26484v1, Eq. (98)](https://arxiv.org/html/2606.26484v1).
Its linear harmonic normalization is retained; this is not an independent
absolute centroid-force reference or a full electromagnetic calculation.

## Reproduction

From the build's `unit_tests/SpaceCharge` directory:

```sh
OPALX_FFT2D5_FORCE_CSV=/absolute/path/smooth-gaussian-force.csv \
  ./TestFFT2D5Numerics \
  --gtest_filter=TestSolve2d5.SmoothGaussianSlicesConvergeWithoutParticleNoise
```

`plot-frame-consistency.py` regenerates PNG/PDF from the accompanying CSV, or
accepts a replacement CSV argument. Use the OPALX Python environment.

The solver remains limited to one MPI rank and horizontal planar paths. A
2-rank OPALX control rejects execution with the documented single-rank error.
GPU execution and full sector-bend tracking remain unvalidated.

## Validation

Full CPU/OpenMP build and all 131 registered tests pass with
`OMP_NUM_THREADS=1 OMP_PROC_BIND=false`. With unrestricted OpenMP concurrency,
130/131 pass: the unchanged `GaussianTest.largeCutoffDisablesTruncation` samples
5.572 sigma against a 5.5-sigma maximum bound. The isolated test passes with one
and two threads. All FFT2D5 tests pass in both configurations.
