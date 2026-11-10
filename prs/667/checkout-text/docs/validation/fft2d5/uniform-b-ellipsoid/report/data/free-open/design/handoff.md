# Nonlocal FFT2D5 free-space operator: design and implementation state

Goal: repair the existing OPEN solver for the 5 m, R=2 m free-space beam,
including weak curvature fields and finite longitudinal ends, without a fitted
g factor or a charge-profile-specific mode. SACR remains an independent reference.

## Implemented files

- `/Users/adelmann/git/opalx/src/SpaceCharge/FFT2D5/FFT2D5FreeSpace.h`
- `/Users/adelmann/git/opalx/src/SpaceCharge/FFT2D5/FFT2D5FreeSpace.cpp`
- `/Users/adelmann/git/opalx/src/SpaceCharge/FFT2D5/FFT2D5FreeSpaceKernel.h`

The root agent owns integration in existing Algorithm/CMake files and backend
unit tests. This subagent did not modify those files. No commits or pushes made.

`solve(rho,E,signedCurvature,gamma=1)` returns 0 for an empty source and 1 for a
physical solve. Existing FFT2D5 remains single rank. Empty solves clear E without
allocating an FFT. Density input is charge per coordinate volume, not physical
density with a second Jacobian to be applied.

## Operator derived here

Let u be outward radial displacement, y vertical displacement, s arc length,
and kappa=1/R signed curvature. For a circular reference, define x=u-u',
v=y-y', tau=s-s', xi=2*sin(kappa*tau/2)/kappa, and D²=x²+v²+xi².
The exact source-target separation is

    d² = D² + xi²*[kappa*(u+u') + kappa²*u*u'].

The full longitudinal bend angle is retained; this is not an expansion in L/R.
Expansion in small transverse kappa*u gives

    G=1/D, H=xi²/D³, F=x*H,
    Phi/kC = G*rho - kappa*u*(H*rho) + (kappa/2)*(F*rho).

Here `*` is ordinary 3D convolution on the existing thin Frenet grid, and
rho=dq/(du dy ds). The identity u'=u-x removes source-moment arrays and leaves
three convolutions of the same density. This is a general density operator;
uniform and triangular distributions use identical production code.

All field components follow the same potential:

    Eu = -d_u Phi, Ey = -d_y Phi, Es = -(1+kappa*u)^(-1)*d_s Phi.

The implementation uses fourth-order centered differences at every physical
cell and second-order differences only in E's exterior halo. Potential has two
halo cells. Padding is the next even 2/3/5-smooth length >=2*N+4; ordinary 2*N
padding is insufficient for the exterior two-cell halo with general sources.

For a straight reference only, gamma stretches xi=gamma*tau and the source-cell
longitudinal width. The convolution still multiplies by the original coordinate
cell volume: the rest-frame charge density's 1/gamma cancels the longitudinal
volume stretch. Lab electric fields are gamma*(-d_u Phi), gamma*(-d_y Phi),
and -(1/gamma)*d_s Phi. Curved gamma!=1 is rejected by the backend. The caller
must explicitly constrain curved moving beams to its electrostatic validity.

## Finite-cell regularization

Point-sampling a highly elongated cell cannot resolve the near field. Flat
singular kernels are integrated analytically over each rectangular coordinate
cell. The exact curved-minus-flat kernel is nonsingular and receives 2x2x4 Gauss
quadrature near the source. For distant cells, four longitudinal Gauss points
and analytic transverse second moments avoid subtracting nearly equal corner
primitives and keep kernel generation economical.

The analytic G primitive is the standard rectangular-prism Coulomb integral,
already present privately in IPPL's `FFTOpenPoissonSolver.hpp`. Two useful
identities derived for the additional kernels are

    H_flat = G_flat - d_z(z*G_flat),
    integral_box H_flat = integral_box G_flat - [z*integral_xy_face G_flat]z0^z1,

    integral_box F_flat = W(x0)-W(x1),
    W(a) = integral_yz z²/sqrt(a²+y²+z²),
    3*W = integral_boundary ((y,z)*z²/r).n - a²*integral_yz H_flat.

The face and line integrals have elementary logarithm/asinh/atan primitives.
Exact kernel parity is enforced publicly: G,H are even in all displacements;
F is odd in x and even in y,s. This protects weak curvature fields from
asymmetric last-bit cancellation in analytic corner primitives.

## Validation completed by this subagent

Run using `/Users/adelmann/.venv-h6/bin/python`:

1. `check_kernel.py` compiles `check_kernel.cpp` against the actual production
   header and compares its output with independent 100^3 Gauss quadrature.
   Results are in `kernel_checks.csv`. Cube self G is
   `[24 log((1+sqrt(3))/sqrt(2))-2*pi]/8=1.19003868199`; H=G/3 and F=0.
   Cube relative errors are below 7e-16. Flat near and elongated-cell errors
   are below 3e-14; curved near errors below 8e-11; distant curved checks are
   near machine precision. A deliberately isotropic distant cell has worst
   relative error 1.32e-8. A straight gamma=10 check is below 6e-10.

2. `check_curvature_expansion.py --order 40` independently integrates the exact
   curved Coulomb force over an elliptical source volume, including the Frenet
   Jacobian, and compares it with derivatives of the expanded potential. This
   does not use SACR or production FFT kernels. Outputs are
   `curvature_expansion_R2_order40.{csv,json}`. For 10 pC, a=5 mm, b=0.5 mm,
   L=5 m, R=2 m, exact centre radial fields are 0.055092023709 V/m (uniform)
   and 0.091838868594 V/m (triangular). Relative expansion errors there are
   2.35e-7 and 2.43e-7. Across centre, radial, vertical, end and off-axis-end
   probes the worst expansion error is 0.05834%, at the triangular weak radial
   end field. The remaining values are below 0.002%.

3. Root reports independent backend ellipsoid tests pass for all three field
   components at gamma=1 and gamma=2. Root owns their formal test record.

Order-64 direct-volume integration completed. Centre radial fields and end
tangent fields are well resolved; centre exact values are 0.055092022497 and
0.091838866169 V/m, with unchanged expansion differences. However, the raw
off-axis transverse force has a slowly convergent interior singularity: some
bulk values shift 1--6% between orders 40 and 64. These raw bulk values must
not be used as <1% reference fields. The exact-minus-expanded difference is
much better converged and its worst relative size remains only 0.0604%, at
the triangular weak off-axis end radial field. SACR is the authoritative
physical-field reference for production convergence.

## Accuracy and scope

- Production enforces max|kappa*u|<=0.01 over mesh and target halo. With epsilon
  this small, |delta|<=2*epsilon+epsilon² for the exact distance expansion. A
  Taylor bound for the dropped potential terms is
  `0.5*epsilon² + (3/8)*(2*epsilon+epsilon²)²/(1-2*epsilon-epsilon²)^(5/2)`
  times G, about 2.1e-4 at epsilon=.01. This is an absolute potential bound,
  not a universal relative bound on a field component that can vanish. The
  independent force check above addresses the weak field in the requested case.
- Constant circular curvature is required. Varying curvature cannot use an
  averaged radius with this convolution. A general path would need a genuinely
  nontranslation-invariant operator, e.g. a singular-aware volume FMM.
- No full turn or self-intersecting path: xi has additional singularities at
  multiples of 2*pi/kappa. Root was advised to reject closed rings/full turns.
- Curved relativistic electrodynamics is not established by these electrostatic
  tests. Root intends an explicit beta<=0.1 restriction, validated beta=.001.
- First-order curvature truncation is already comfortably below 1% for the
  specified probes. That does not guarantee a coarse FFT mesh reaches 1% at
  sharp ends. Source deposition, grid differentiation, and field gathering
  remain separate convergence errors. Nz4096 gives about 2 mm spacing on an
  8 m path, compared with 5 mm radial size; Nz8192 or higher may be needed.
- Explicit workspace is one padded real field plus two half-complex fields,
  but IPPL FFT also caches real/complex temporary arrays and a backend
  workspace. Peak RSS should be measured before the finest run. Kernel
  streaming avoids retaining three huge Green spectra, at the cost of their
  regeneration on repeated solves.

## Next step

Root completes build/tests, runs production frozen-field mesh convergence for
both profiles, compares each component against SACR with component-appropriate
absolute tolerances near zeros, reruns the existing PyORBIT pipe benchmark,
and updates the report with measured results and these explicit limitations.
