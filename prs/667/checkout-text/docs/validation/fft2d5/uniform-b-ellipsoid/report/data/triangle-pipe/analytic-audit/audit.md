# Triangular bunch in a conducting circular pipe: analytic audit

Common benchmark, agreed 2026-11-02: uniform circular cross section of fixed
radius a=5 mm; grounded circular pipe radius b=20 mm; triangular laboratory
line density of full length L=10 m; N=1e14 protons; kinetic energy0.4GeV;
one equivalent frozen kick of length1m. Total charge is16.02176634uC.
The source is fixed while fields/kicks are evaluated, not tracked through a
physical1m drift with evolving transverse size.

## Reference equations and observables

For signed position s measured from the bunch centre,

    lambda(s) = 2Q/L * (1 - 2|s|/L), |s|<L/2; zero outside,
    lambda'(s) = -4Q/L^2 sign(s), 0<|s|<L/2.

The fixed-radius, uniform-disk, long-beam conducting-pipe reference is

    g(r) = 1 + 2 ln(b/a) - r^2/a^2, 0<=r<=a,
         = 2 ln(b/r), a<=r<=b,
    E_s(r,s) = -lambda'(s) g(r)/(4 pi epsilon0 gamma^2),
    E_r(r,s) = lambda(s) r/(2 pi epsilon0 a^2), r<=a.

These are laboratory electric fields. The transverse Lorentz force per unit
charge is E_r/gamma^2. A proton's energy change over equivalent length ell
is DeltaW[eV]=E_s[V/m]*ell[m]. PyORBIT stores dE in GeV, so its equivalent
frozen E_s=dE*1e9/ell. This is not divided by beta or gamma again.

On-axis g=1+2ln(b/a). A uniform-disk charge-weighted average has
<r^2>=a^2/2, hence g_mean=.5+2ln(b/a). An RMS radius must not be substituted
for the hard-edge beam radius without changing the formula.

At the triangular cusp and support endpoints lambda' is discontinuous.
The local formula is not a reference for the nonlocal transition there;
analytic.py returns NaN exactly at those locations. Use the fixed primary
window1m<=|s|<=4m, with targets|s|=1,2,3,4m for coarseNz. Keep
the same window at every mesh. Display cusp/end data, but exclude them from
the flat-branch accuracy claim. This exclusion is independent of measured
errors.
Exact1m/4m boundary targets use a1e-12m coordinate comparison tolerance to
preserve the same intended point IDs across decimal/binary CSV round trips.
This is not a relaxation of the field accuracy threshold or exclusion scale.
The omitted physical nonlocal transition has a conducting-pipe
transverse scale: in an eigenmode expansion its slowest homogeneous axial
decay scale is b/(gamma*j01), j01=2.4048255577. Here this is5.83mm.
This eigenmode statement is our PDE inference, not a published1%guarantee.

## What OPALX actually implements

Inspected local sources:

- src/Structure/FieldSolverCmd.cpp: input is PIPEMODE=CIRCULAR, not
  CYLINDRICAL. Options OPEN/CIRCULAR/PLATES/NONE change only longitudinal g.
- src/SpaceCharge/SpaceChargeConfigBuilder.cpp: CIRCULAR maps to the enum
  Cylindrical; input BEAMR becomes beamRadius; no independent pipe radius.
  FFT2D5 requires one MPI rank and open transverse boundaries.
- src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp: grid size equals
  PIPESIZEX/Y, origin=-size/2, spacing=size/N. Thus these values are full
  OPEN numerical grid widths.
- src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp: the variable named pipeRadius
  equals min(fullWidthX,fullWidthY), then
  g=.67+2ln(pipeRadius/BEAMR); gathered E_s is independent of transverse r.
- src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h: CircularPipeG0=.67.

This overload needs explicit mapping. PIPESIZEX/Y=.020 gives the correct
effective b20mm in the g formula, while the open transverse grid spans
[-10,+10]mm. This is a valid numerical domain for the centred a5mm source;
it need not reach the physical wall because the transverse solve is open.
For an axisymmetric centred source the local transverse conducting-wall
image field inside the beam vanishes. PIPESIZEX/Y=.040 instead spans the
literal40mm pipe diameter but uses effective b40mm in g. Do not label both
as the same longitudinal pipe model. Varying width affects both resolution
and model coefficient unless treated explicitly.

The .67 is separately a model-profile convention. Oeftiger/Hegglin2016
p124 Eq1--3 describe an equivalent linear field obtained from the moment
<z E_real> for a parabolic/equivalent ellipsoidal bunch; it is not the
uniform-disk pointwise on-axis coefficient1 or disk-average coefficient.5.
No numerical fit or parameter adjustment can make the native r-independent
coefficient reproduce the full g(r) profile of this constant-radius source.

For b/a=4, matched-effective-b native g=3.4425887222, compared with
g_axis3.7725887222 and g_mean3.2725887222. Thus the expected native OPALX
error is-8.7473%onaxis or+5.19466%for the disk mean after mesh convergence.
The literal40mm numerical-width mapping gives g4.8288830834 and+27.9992%
onaxis. These are analytic predictions from the inspected implementation,
not measured native results. Preserve the unmodified production coefficient
and show its prediction distinctly from the physical analytic curve.

## Primary references

- Shishlo etal, ORBIT2006,p55Fig4:
  https://accelconf.web.cern.ch/icap06/papers/MOA2IS01.pdf
  Triangular-profile tune/longitudinal-force reduced-model benchmark.
  Historical '3D' means sliced2D; conducting walls tie potential gauges.
- Current PyORBIT3 pinned28df66018aebe4e2b780b9747f4a2d7b8430a5c0:
  examples/SpaceCharge/scSliceBySlice2D/sc_Slice2D_driftLatt_longitudinal_test.py
  L10m,a5mm,pipe diameter40mm,triangular source,longTracking(True).
- Baartman1992,arXiv2015: https://arxiv.org/abs/1508.00153
  Explicitly distinguishes on-axis and transversely averaged g.
- Oeftiger/Hegglin2016: https://proceedings.jacow.org/hb2016/papers/mopr025.pdf
  Equivalent parabolic-bunch g=.67+2ln(rp/rb), p124.

## Reproducibility and scope

The primary OPALX run uses numerical full width W=.020m, and the code's
native formula is g=.67+2ln(W/a). The physical pipe radius b=.020m is
independently specified in the analytical and PyORBIT models. A separate
W=.040m control uses twice as many transverse cells to hold the transverse
spacing fixed while demonstrating the log(W) coupling. This is not a
second independent physical b20mm solution.

Run analytic.py with ~/.venv-h6/bin/python. Native-model defaults are the
primary W=b=.020m case; pass full_width_x/y=.040 for the width control.
It writes parameter/expected
values in analytic-reference.json and a SI reference table in
analytic-reference.csv. verify.py independently checks source normalization,
disk averaging and a Gauss-law/potential-quadrature longitudinal gradient;
all checks pass, maximum relative gradient error2.01e-13. No production code,
plotting, report or native runtime changes
were made by this audit. Root owns OPALX and PyORBIT runs and their results.
