# SACR radius-to-straight check

The same curved SACR evaluator was run at R=2, 5, 10, 20, 50, 100, 200, 500,
1000 m and infinity for both uniform and triangular profiles. All evaluations
retain a=c=20 mm, L=5 m, Q=10 pC and the same 15 material target coordinates
selected from the original 51-point set. They cover the centre, signed
transverse cuts, mixed bulk/near-end points and both 0.1 mm end probes.

The physical source is unchanged: rho(s) is uniform over each physical disk,
with dV=(1+u/R)du dy ds and the stated longitudinal profile. Cartesian
source and target positions change only through the specified circular
embedding. The odd-u Jacobian term integrates to zero, so total charge stays
exactly Q at every radius. No coefficient, length, radius, density or field
normalization is fitted, and no softening is introduced.

The producer snapshots are copied and hash-pinned in `provenance/`.
Uniform fields use the curved side/cap Coulomb identity; triangular fields
use its weighted-boundary/density-gradient form. The infinity value is
computed by those same producers using their exact straight geometric limit,
then compared against the independently implemented straight-cylinder
longitudinal primitive and disk quadrature.

Angular refinement 512→1024 is tested with radial order held fixed. Radial
refinement 160→192 (uniform) or 64→96 (triangular) is tested with angular
order 1024 held fixed. The 0.1 mm uniform end probes are included. Changes
are at most 3.78e-15 V/m for this selected set. These are quadrature changes,
not estimates of the physical difference between finite curvature and a
straight beam. The predeclared extra-refinement threshold is 2e-8 V/m;
no extra rule was required.

The R=infinity evaluation agrees with the independent straight reference
within 6.89e-15 V/m. The R=2 results reproduce the existing full 51 reference
within 3.78e-15 V/m. Every component approaches its straight value as R
increases; the weak outward centre radial field approaches zero from above,
approximately in proportion to 1/R.

| Profile | Centre Eu at R=2 m (V/m) | Centre Eu at R=1000 m (V/m) |
|---|---:|---:|
| Uniform | +0.040935976012 | +0.000081274019 |
| Triangular | +0.063687106181 | +0.000126980145 |

Errors use fixed component scales from each entire 51-point straight
reference, including its declared extra diagnostics. No component is divided
by an individual near-zero field. At R=1000 m, the largest selected-target
differences, divided by these fixed scales, are:

| Profile | Radial | Vertical | Longitudinal |
|---|---:|---:|---:|
| Uniform | 5.024e-5 | 6.943e-7 | 6.204e-6 |
| Triangular | 3.952e-5 | 3.496e-7 | 1.300e-5 |

`radius_fields.csv` is the wide plotting table: profile,point_id,R_m,
u_m,y_m,s_m,E_u,E_y,E_s,straight_u,straight_y,straight_s, with SI V/m fields.
`radius-errors.csv` supplies signed finite-R differences and separate
quadrature changes with fixed scales. `radius-error-summary.csv` gives
component maxima over the 15 selected targets; `quadrature-fields.csv` and
`quadrature-convergence.csv` retain every tested rule.

Reproduce with the OPALX Python environment:

```sh
/Users/adelmann/.venv-h6/bin/python radius_sweep.py
```

The run takes about 11 seconds and launches no native solver. `acceptance.json`
records the point list, producer/input/output hashes, normalizations and
independent endpoint checks. This check establishes the radius limit on the
selected set; it does not replace independent Cartesian volume checks at
finite R or validate native tracking.
