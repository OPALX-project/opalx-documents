# Curved-orbit FFT2D5 validation

This test validates actual curved tracking in a uniform magnetic field, including
space charge and a reference frame that rotates through a half-turn. All three
total RMS sizes agree with an independent ellipsoid model to within 1% at every
STAT sample. This is a validation of the specified case and accuracy metric.

## Model and input

The source is a cold uniform-volume ellipsoid of 98,304 quiet protons. Its
initial radial, tangential and vertical semiaxes are 5, 50 and 0.5 mm. The
centroid has beta=0.01 and orbit radius R=1 m in B=31.297388 mT. Initial velocities
are rigid corotation. Tracking covers 180 degrees in 128 steps. The physical
xy/Bz problem is rotated to OPALX xz/By with `(x,y,z) -> (x,z,-y)`.

For a uniform unit-ball vector u, write `r=C+A*u`. The independent cold-fluid
reference solves

```text
rho = 3 Q / (4 pi det A)
C'' = Omega J C'
A'' = q rho D A / (m epsilon_0) + Omega J A'
Omega = q B / m,    J = [[0,1,0],[-1,0,0],[0,0,0]]
cov(r) = A A^T / 5
```

The internal electric field is linear, with the depolarization tensor D obtained
from Carlson elliptic integrals. This electrostatic, nonrelativistic model uses
no mesh, OPALX fields, fitted charge, time scale or g-factor. Its sphere, oblate,
quadrature, zero-charge orbit, energy, canonical-angular-momentum and tighter-ODE
checks pass. Magnetic self-fields and relativistic effects are small at this
speed; a separate relativistic zero-space-charge control was checked.

The ellipsoid equations follow D. H. E. Dubin,
[Physics of Fluids B 5, 295 (1993)](https://nnp.ucsd.edu/pdf_files/PFB_5_295_1993.PDF),
with no electrostatic trap. The independent implementation is
[`ellipsoid_model.py`](ellipsoid_model.py).

## Results

The accepted mesh is 128x256x1024 over a 24x12 mm transverse box and the full
4.18877 m design path. Longitudinal CIC is enabled. Predictions use the full model
covariance projected onto the actual reference axes at the same physical time.

| Charge | Radial maximum error | Tangential maximum error | Vertical maximum error |
|---|---:|---:|---:|
| Space charge off | 0.0295% | 0.0100% | 0.0000% |
| 0.1 pC | 0.0679% | 0.0358% | 0.3962% |
| 0.3 pC | 0.1882% | 0.0973% | 0.4542% |
| 1 pC | 0.9032% | 0.3838% | 0.4550% |

![Independent ellipsoid model and OPALX](results/opalx_all_step_comparison.png)

Dashed lines are the independent model; circles and solid lines are OPALX. Size
axes include zero. The lower panels show relative errors in total RMS size.
[Vector PDF](results/opalx_all_step_comparison.pdf).

Independent 1 pC controls give maximum RMS changes of 0.31101% for a doubled
transverse mesh, 0.17054% for doubled NZ, 0.00214% for half the time step, and
0.00793% for twice the particle count. All refined cases remain below 1% model
error; the largest is 0.9858%. Full duration, particle count and charge are
checked for every case. Data, acceptance and source/binary hashes are in
[`results/`](results/).

The fix uses consistent particle/path frames, cell-averaged 2D logarithmic Green
functions, centered gradients with convolved potential halos, and one reusable
workspace that skips empty slices. All 131 CTest entries pass with one OpenMP
thread; all 66 applicable numerical cases pass with four threads. The existing
explicit rejection of unsupported MPI execution passes with two ranks. GPU
execution is unverified.

## What this establishes

The bunch traverses a curved orbit through 180 degrees. Its instantaneous full
angular span is about 0.1 rad, or 5.7 degrees. These are different measures: this
test establishes accurate total RMS sizes for this geometry, not all possible
angular extents or all force components at 1%.

At 1 pC, subtracting the matched zero-space-charge result exposes the accuracy of
the smaller collective changes:

| Final charged-minus-zero RMS increase | Model | OPALX | Relative error in increase |
|---|---:|---:|---:|
| Radial | 0.69117 mm | 0.71695 mm | 3.73% |
| Tangential | 0.26135 mm | 0.34593 mm | 32.36% |
| Vertical | 1.90807 mm | 1.90156 mm | -0.34% |

Thus the sub-1% total-size result does not imply sub-1% space-charge growth.
The existing longitudinal OPEN approximation still uses g=6.36. Full covariance,
centroid and force comparisons provide additional checks beyond three RMS
numbers. The proposed next work is recorded in [`NEXT-STEPS.md`](NEXT-STEPS.md).

## Reproduction

Use the OPALX Python environment, or Python with numpy, scipy, pandas, matplotlib
and h5py. From this directory:

```sh
python ellipsoid_model.py
python plot_saved_results.py --outdir /tmp/fft2d5-figure
python prepare_opalx.py q1 --solver fft2d5 --charge-pc 1 --mesh 128 256 1024 --run
python analyze_stat.py --manifest opalx-runs/q1/manifest.json --require-one-percent
```

The generator defaults to this repository's `build-omp/src/opalx`; set
`OPALX_BINARY` for another build. It generates the quiet distribution and a
native OPALX input, uses the included uniform field map and reference path, and
preserves existing completed runs. Repeat with charges 0.1 and 0.3 pC. For the
space-charge-off control use `--solver none --charge-pc 0`: nominal finite charge
is retained for macro charge/mass, while the field solver is disabled. Its STAT
charge is therefore not zero.

These are reproducible OPALX tracking checks. The zero-space-charge and 1 pC
cases and independent all-step validators are now prepared locally in
`regression-tests-x`; remote CI has not run them. See
[`regression-integration.md`](../regression-integration.md) for the integration
scope. The C++ checks are unit tests.

The editable LaTeX report in [`report/main.tex`](report/main.tex) collects the
uniform-field model, completed baseline and refinement tests, 3D controls,
10 pC stress result, collective-response diagnostics and radius scan. Rebuild
its tables, vector figures and PDF with [`report/build.sh`](report/build.sh).
The report distinguishes physical xy/Bz coordinates from their OPALX xz/By
representation and excludes incomplete cases from acceptance.
