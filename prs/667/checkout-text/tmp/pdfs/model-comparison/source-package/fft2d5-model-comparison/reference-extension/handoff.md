# SACR tube validation extension — complete

2026-11-04. Both user-authorized reference checks pass for the current
constant-section round tube: a = 20 mm, L = 5 m, Q = 10 pC, uniform and
triangular physical density. Existing reference outputs remain unchanged;
`acceptance.json` verifies their hashes. No production edits or native
OPALX/PyORBIT jobs were used for this extension.

`run_volume_checks.py` compares SACR with an independently implemented
original Cartesian Coulomb vector volume integral. Eight targets per
profile include five points with all three components nonzero, mixed bulk
and 10/5-mm end points, and a 0.1-mm axis end control. All 48 scalar
components pass independent quadrature refinements. The largest difference
is 2.187612e-11 V/m; the last refinement changes a component by at most
1.455568e-10 V/m. No fitting, softening, exclusion or charge renormalization
was used.

`radius-sweep/radius_sweep.py` evaluates the same curved SACR producer at
R = 2, 5, 10, 20, 50, 100, 200, 500, 1000 m and infinity for 15 fixed
material targets and both profiles. The maximum discrepancy from the
independent straight-cylinder method at infinity is 6.883383e-15 V/m.
Independent angular/radial changes are at most 3.774759e-15 V/m. The
maximum selected-target difference in each component decreases with R.
Physical finite-radius differences are reported separately from numerical
quadrature changes.

`finalize_extension.py` verifies producer/input/output hashes, coverage,
fixed coordinates, convergence summaries and the unchanged prior outputs.
`README.md` describes methods, reproducibility, table schemas and limits.
Root owns paper integration, figures and subsequent ten-step tracking.
The new extension figures and generated paper text were independently
reviewed against these outputs and visually inspected; no issue found.

Remaining limits: sampled frozen-field checks are not a uniform error bound
for arbitrary sources/targets, do not validate tracking or energy
conservation, and concern free space rather than conducting boundaries.
