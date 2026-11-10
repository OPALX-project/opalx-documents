# Next validation steps

## Real-beam target

The user specified a 5 m long beam with 5 mm radial extent and selected a
2 m bending radius. Treat 5 m as full reference-path arclength: the bunch spans
2.5 rad (143.239 degrees), with radial size/radius 0.0025.

This target is a finite curved tube, not the Cartesian ellipsoid used in the
completed tests. Dubin's affine ellipsoid remains a straight-beam reference,
but is not an exact oracle for this curved geometry. The proposed independent
curved-field reference is named **semi-analytic curved-tube reference (SACR)**.
It uses finite-cross-section Coulomb integration, normalized by total charge,
with the physical volume Jacobian included. Begin with
zero-self-field tracking and frozen-field comparisons before claiming a
tracking oracle. Vertical size and longitudinal density profile must be stated
before constructing a charge distribution; they are not fixed by the new
radius alone. Native 5 m frozen-field OPALX comparisons are now available;
no 5 m curved-beam tracking validation has yet been produced.

SACR's field prototype passes expanded Dubin straight-limit checks:
use an ellipsoidally tapered cross-section and uniform physical density, then
take R to infinity. Straightening a constant-section tube alone gives a
cylinder and is not an exact finite-ellipsoid comparison. The prototype's
three-component checks use 33 points per geometry and a 2--2000 m radius sweep
for the 5 m source. The largest sampled straight-limit difference is 3.97e-14
of the characteristic component field; independent quadrature, endpoint,
Poisson/curl and volume-integral checks pass. Results and source hashes are
recorded under OPALX-2D5/curved-study/sacr and included in the LaTeX report.
The constant-section source now has a separate 43-point SACR/FFT2D5 frozen
comparison under `OPALX-2D5/curved-study/sacr/frozen-r2`. Benchmark choices are
vertical semiaxis 0.5 mm, beta 0.001 and charge 10 pC. It uses a matched
Cartesian quiet source for transverse mesh refinement and a separate matched
longitudinal sequence through NZ=4096, with charge, frame, sampling and path
controls. The finite-end longitudinal field is not reproduced by the current
line-density-gradient model: at fixed probes 5 mm inside the end it approaches
zero while SACR predicts about 3.25 V/m. The fine centre radial field is inward
(-0.0176 V/m), close to the ideal flat-slice prediction (-0.01634 V/m), whereas
SACR predicts an outward curvature field (+0.0551 V/m). These are frozen
electrostatic comparisons, not a uniform accuracy bound or tracking result.
Final mesh/control tables and the LaTeX report record the transverse limits.
SACR/OPALX self-consistent tracking remains a separate validation task.

## Current status and priorities (2026-11-01)

Completed: baseline 0--1 pC scan and refinements; four-radius scan and matched
controls; collective-response audit; fresh same-executable 10 pC coarse/fine
FFT2D5, 3D OPEN and matched zero controls; local regression cases and validators;
LaTeX report with TikZ setup figure.

The completed 10 pC fine FFT2D5 errors are 18.8904% radial, 5.6461% tangential
and 0.7179% vertical. OPEN stays below 0.0700% in all directions. The transverse
refinement changes sizes by at most 0.1188%, 0.00374% and 1.92395%, respectively:
the large radial/tangential bias persists, while vertical convergence is not
established at the 0.5% refinement criterion.

Next, in order:

1. **Complete the R=0.25 m refinement.** The fine-grid run stopped at 61/128
   samples. Check the tightest-radius result against its coarse run and model.
2. **Run a controlled initial-field study.** Keep the executable fixed and
   resolve longitudinal sampling. The existing historical/current pair changes
   both mesh and binary, so it does not establish pointwise force convergence.
   Include the remaining 10 pC vertical-resolution uncertainty.
3. **Finish regression integration.** Exercise the 1 pC case through the full
   smoke hook; only ZeroSC has passed that hook so far. Cases and CI changes
   remain local. Update the report with completed controls before publishing.

Deferred at the user's request: reproducing Dubin's trapped-plasma results.

## Approved measurement plan

Keep the existing field model and g-factor unchanged for these measurements.
No additional curvature operator is part of this plan.

0. **Increase the charge to 10 pC.** Keep the same source, magnetic field,
   radius and half-turn duration, then compare total RMS sizes and
   charged-minus-zero growth. The analytic maximum vertical semiextent rises to
   25.9 mm, so enlarge the transverse box to 40x64 mm before running. Check mesh
   refinement rather than interpreting an underresolved or clipped beam as a
   solver-model discrepancy. Do not fit the longitudinal g-factor.

1. **Preserve this as an automated OPALX tracking regression.** Add the
   zero-space-charge and 1 pC input/oracle checks to the existing
   `regression-tests-x` structure. Check all three RMS sizes, full duration,
   particle count and charge. Retain the present 1% total-RMS criterion and the
   independent model; distinguish this tracking regression from the C++ unit
   tests.

2. **Audit the space-charge response in existing data.** Compare charged-minus-zero
   RMS increases, full position covariance, centroid and the three components of
   the force on the initial distribution. The present tangential increase differs
   by about 32% despite a 0.38% error in total tangential RMS. Compare the existing
   longitudinal approximation with the ellipsoid's analytic field before
   attributing a discrepancy to curvature. Report absolute and relative errors
   near zero response; do not fit g to this case.

3. **Measure dependence on curvature with a similarity scan.** Keep beta=0.01,
   the 5/50/0.5 mm semiaxes and the quiet unit-ball sample. Change R, scaling
   `B=B1*(1 m/R)`, `Q=Q1*(1 m/R)^2`, and duration/time step proportionally to R.
   The independent model then predicts identical size-versus-orbit-angle curves,
   while the bunch's angular extent changes.

   Regenerate the initial rigid-corotation velocities using the new Omega, and
   generate the reference path and constant-field map for each radius. The map's
   Cartesian bounds must contain the entire orbit and bunch.

   | R | B | Q | Approximate full instantaneous angular span |
   |---:|---:|---:|---:|
   | 2 m | 15.6487 mT | 0.25 pC | 2.9 degrees |
   | 1 m | 31.2974 mT | 1 pC | 5.7 degrees |
   | 0.5 m | 62.5948 mT | 4 pC | 11.4 degrees |
   | 0.25 m | 125.1896 mT | 16 pC | 22.6 degrees |

   Preserve physical mesh spacings, scale NZ with path length, and extend the
   reference path on both sides to contain the whole bunch plus CIC support.
   Widen the radial mesh when required, adding cells to retain its spacing. Keep
   the same orbital-angle step. Refine the tightest-radius or first failing case
   separately to distinguish discretization error from model error.

The output is a measured accuracy range versus bunch angular extent, with total
RMS and collective-growth errors reported separately. Only after these results
should another solver-model change or more complex accelerator test be chosen.
