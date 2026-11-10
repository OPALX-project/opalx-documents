# Semi-analytic curved-tube reference (SACR)

SACR is the user-selected name for the independent curved-beam field reference.
The target beam is 5 m full arclength on a 2 m radius, with 5 mm radial extent.
This directory currently contains a **static field prototype and limit check**,
not a completed OPALX benchmark or a self-consistent tracking reference.

## Exact comparison with Dubin

Straightening a constant-section tube gives a finite cylinder, not an ellipsoid.
For the Dubin comparison, use uniform physical volume density and tapered
cross-section semiaxes

    a(s) = a0 sqrt(1 - s²/b²),
    c(s) = c0 sqrt(1 - s²/b²),    |s| <= b,    L = 2b.

The curved map in OPALX coordinates is

    X(s,u,y) = ((R+u)cos(s/R)-R, y, (R+u)sin(s/R)),
    dV = (1+u/R) ds du dy.

At fixed a0,b,c0,Q, the limit R→infinity gives the Cartesian uniform ellipsoid.
Its volume is 4πa0bc0/3 even when bent, since the odd radial Jacobian term
integrates to zero. The line density is parabolic, not uniform.

Compare the full field with Dubin's Appendix A, using consistent SI units:

    E_i = rho D_i x_i / epsilon0,    sum(D_i)=1,
    D_i = A_i(Dubin)/2.

Reference: https://nnp.ucsd.edu/pdf_files/PFB_5_295_1993.PDF

## Uniform-density surface formulation

The Coulomb volume field can be written exactly as a boundary integral:

    E(x)/(k rho) = ∫boundary n'(x') / |x-x'| dS',
    k = 1/(4πepsilon0).

This is the divergence theorem applied to the source-coordinate gradient of
1/|x-x'|. The script evaluates all three components with two-dimensional
quadrature over the curved tapered boundary. It uses no OPALX field, fitted
g-factor, softening length or 3D mesh.

The independent tangential endpoint reduction also remains exact for the taper
when its limits depend on the transverse point:

    s_plus/minus(u,y) = +/-b sqrt(1-u²/a0²-y²/c0²).

Using common end planes would instead describe the constant-section tube.

## Initial one-point verification

Run with the OPALX Python environment:

```sh
/Users/adelmann/.venv-h6/bin/python validate_dubin_limit.py
```

The script refines 64/128/256 angular nodes with adaptive longitudinal surface
quadrature. It checks a sphere, the previous 100 mm ellipsoid, and a 5 m
ellipsoid at one off-axis interior point each. The 0.5 mm vertical semiaxis of
the latter two is a verification-case choice, not a newly confirmed real-beam
parameter.

At 256 angular nodes, the largest component-relative straight-limit difference
from Dubin is **2.70e-11**. The independent tangential surface and endpoint
forms agree within **2.10e-12** relative over R=2,20,200,2000 m and infinity.
Full-precision results and script hash are in `results/`.

These are initial field-operator checks; the expanded study is below. Full
Dubin tracking would additionally require representing its evolving affine
distribution and matching external fields/initial velocities.

## Expanded point and radius study

`field_study.py` checks 33 interior points for each straight-limit geometry,
then the 5 m source at R=2,5,10,20,50,100,200,500,1000,2000 m and infinity.
This gives 429 point/radius cases and 1,287 final field components. Zero-field
targets are retained by normalizing each component with its characteristic
Dubin boundary field, not the local field value.

The maximum straight-limit difference is **3.97e-14** of that component scale.
Adaptive angular refinement (128 to at most 4096 nodes) gives a largest final
change of **3.64e-9** of the scale. All three finite-radius differences from
Dubin decrease toward the straight limit. These physical geometry differences
are distinct from quadrature errors.

At R=2 m, maximum radial/tangential/vertical differences are
**0.385901% / 0.411193% / 0.00280090%** of their component scales. At R=2000 m
they are **0.000384765% / 0.0000932668% / 0.00000281235%**. These are maxima
over the selected points, not uniform bounds or pointwise-relative errors.

Independent checks include tangential endpoint integration, Cartesian
Poisson/curl identities, reflections, geometry normals and a separate
Coulomb volume integral. Data, settings, hashes and definitions are in
`study-results/` and `independent-results/`.

```sh
/Users/adelmann/.venv-h6/bin/python field_study.py --workers 6
/Users/adelmann/.venv-h6/bin/python independent_checks.py
/Users/adelmann/.venv-h6/bin/python independent-results/volume_surface_check.py
```

The expanded checks validate sampled static fields on the tapered family.
The actual constant-section source, OPALX comparison and self-consistent
tracking remain separate tasks. The compiled LaTeX report includes the SACR
model, normalization, numerical results and vector plots.

A second shared limit is a straight, infinitely long elliptical cylinder at
fixed density. It checks transverse fields, but its vanishing longitudinal
field cannot validate finite-length longitudinal forces.
