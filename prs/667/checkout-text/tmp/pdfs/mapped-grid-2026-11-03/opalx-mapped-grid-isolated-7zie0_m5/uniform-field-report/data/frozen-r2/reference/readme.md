# SACR frozen reference: constant-section 5 m tube, R = 2 m

This is an independent Coulomb field reference for a prescribed finite beam.
The physical volume density rho is uniform inside the elliptical tube. The
radial/vertical semiaxes are 5/0.5 mm; full reference arclength is 5 m; the
bend radius is 2 m (143.239 degrees). The 0.5 mm vertical size is a benchmark
choice inherited from the preceding validation, not a newly measured real-beam
parameter. There is no tracking, fitted g-factor, softening or OPALX input in
the reference field calculation.

Local coordinates and returned field components have order `(u,y,s)` =
`(radial,vertical,tangential)`. The OPALX laboratory map is

```
X(s,u,y) = ((R+u) cos(s/R)-R, y, (R+u) sin(s/R)).
dV = (1+u/R) ds du dy.
Q = rho pi a c L.
```

The physical Jacobian is essential. Equal-weight sampling uniformly in the
unweighted material measure `ds du dy` would instead make physical density
proportional to `1/(1+u/R)`. Uniform physical density has material marginal
weight `1+u/R`. Its material mean u is `a^2/(4R)` (3.125 micrometres here).

## Equations

The exact uniform-density Coulomb boundary identity gives all three components:

```
F(X) = E(X)/(k rho) = integral_boundary n'(X')/|X-X'| dS',
k = 1/(4 pi epsilon0).
```

With side parameters `(s,phi)`, `u=a cos(phi)`, `y=c sin(phi)`, the outward
vector area is

```
(1+u/R) [c cos(phi) e_r(s) + a sin(phi) e_y] ds dphi.
```

Both planar elliptical end caps have outward vector area
`+/-e_s(+/-L/2) du dy`. The cap areas do not acquire the volume Jacobian.
The implementation rotates every source normal into the target's local basis.
It then performs adaptive longitudinal quadrature, periodic midpoint side
angle quadrature, and polar Gauss/ring quadrature over each cap. Distances use
the stable chord expression

```
d^2 = (u_t-u_s)^2 + (y_t-y_s)^2
    + 4 (R+u_t) (R+u_s) sin^2((s_s-s_t)/(2R)).
```

A separate exact filament integration checks the tangential result:

```
F_s = integral_A (R+u_s)/(R+u_t) [1/d_plus-1/d_minus] du_s dy_s,
d_plus/minus = |X(s_t,u_t,y_t)-X(+/-L/2,u_s,y_s)|.
```

These are common end planes for this constant-section source, whereas the
previous tapered Dubin-limit source has transverse-dependent filament ends.

## Reproduce and use

```
/Users/adelmann/.venv-h6/bin/python build_reference.py
```

The module API is

```
from tube_reference import field
F = field(a, c, half_length, (u_target,y_target,s_target), radius,
          nphi=4096, nrad=128)
```

`F` has units metre. Convert to SI with
`E = F * Q / (pi*a*c*L) / (4*pi*epsilon0)`.
The field is electrostatic: the OPALX comparison must use matched density,
charge, basis and field conventions and a stated low-beta approximation.

`points.csv` fixes 43 exact interior targets. These include the centre,
signed radial and vertical axes (0.5 and 0.9 of the respective semiaxis),
centreline and signed off-axis bulk points, and centreline targets 50, 10 and
5 mm from either end. `fields_reference.csv` gives the final fields, fixed
component scales, normalized values and last refinement changes.

The common transverse scale is the exact infinite straight ellipse's boundary
field: `F_r,* = F_y,* = 4*pi*a*c/(a+c)`. The fixed tangential scale is the
maximum absolute converged SACR tangential field over the 43 declared targets.
Normalization never divides by a vanishing local field. Bulk and end-target
errors should also be reported separately; a large end field should not hide
an inaccurate but weaker bulk field.

`fields_all_resolutions.csv`, `quadrature_changes.csv` and
`quadrature_summary.csv` retain all refinements, using angle nodes
128/256/512/1024/2048/4096. Near-vertical-wall targets require the finer levels.
The final 2048-to-4096 changes are below 6.8e-12 of the component scales.

`acceptance.json` records source hashes, scales, tolerances and independent
checks. Separate CSVs contain endpoint comparisons; both geometric reflection
symmetries; Cartesian divergence/curl checks at four interior points (including
10 mm from an end); and a volume/surface Coulomb comparison at the exterior
bend centre. The straight long-cylinder limit is also checked against the
exact interior elliptical-cylinder field. These are sampled static checks;
they do not validate subsequent beam deformation or tracking.
