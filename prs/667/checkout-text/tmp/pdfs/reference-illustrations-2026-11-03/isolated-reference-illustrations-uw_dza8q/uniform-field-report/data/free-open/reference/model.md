# SACR triangular physical-density tube

The geometric tube, density and Coulomb model are specified independently of
OPALX. Let h=2.5 m, R=2 m, a=5 mm and c=0.5 mm. Source coordinates obey
u²/a²+y²/c²≤1 and −h≤s≤h. In global Cartesian coordinates,

    X(s,u,y) = ((R+u) cos(s/R) − R, y, (R+u) sin(s/R)),
    J = 1+u/R,   dV = J du dy ds.

The physical density is either uniform or triangular:

    rho_uniform = Q/(2 h pi a c),
    rho_triangle(s) = rho_peak w(s),
    rho_peak = Q/(h pi a c),   w(s)=1−|s|/h.

Here Q=10 pC. The odd u contribution to J integrates to zero, so these
normalizations give exactly the same total charge. This is physical density,
not charge per du dy ds. The density gradient is grad w=w′ e_s/J.

For a target X_t and source X, put D=|X_t−X|. Coulomb's law and integration
by parts give the exact identity

    F = E/(k rho_peak)
      = integral_boundary w n/D dS − integral_volume grad(w)/D dV,
    k = 1/(4 pi epsilon_0).

The triangular profile vanishes on the end caps. Parameterize the side by
u=a cos(phi), y=c sin(phi); its outward vector area is

    n dS = J [c cos(phi) e_r + a sin(phi) e_y] dphi ds.

The density-gradient term is −integral_A integral_s w′ e_s/D ds du dy: its
Jacobian cancels exactly. The result has no local-line approximation, image
charge, softening, transverse-density assumption beyond the specified uniform
section, or fitted coefficient.

## Longitudinal analytic primitives

In the target basis let delta=(s−s_t)/R,
A=(R+u_t)(R+u), r²=(u−u_t)²+(y−y_t)², and
D²=r²+4 A sin²(delta/2). The gradient term's radial component has primitive

    integral sin(delta)/D ds = R D/A.

Because w′=+1/h on the left half and −1/h on the right half, its integrated
radial correction is R[2D(0)−D(−h)−D(h)]/(h A). For the remaining primitives,
t=(s−s_t)/(2R), m=−4A/r², and F_inc,E_inc denote the standard incomplete
elliptic integrals of first and second kind:

    P(s) = integral ds/D = (2R/r) F_inc(t|m),
    C(s) = integral cos(delta) ds/D
         = (2R/r)[(1−2/m) F_inc(t|m) + (2/m) E_inc(t|m)].

Thus the gradient tangent correction is −[2C(0)−C(−h)−C(h)]/h integrated
over the cross section. At R=infinity, both P and C reduce to
asinh((s−s_t)/r), and the radial gradient correction vanishes.

## Independent longitudinal and volume checks

Directly integrating the original Coulomb tangent kernel along every source
filament, using d(1/D)/ds = −A sin(delta)/(R D³), gives independently

    F_s = −integral_A (R+u)/(R+u_t)
                    [2P(0)−P(−h)−P(h)]/h du dy.

This expression is checked against the sum of weighted-side and
density-gradient tangent contributions. Selected points are also checked by
adaptive integration of the original three-dimensional Coulomb volume kernel,
without a boundary identity or elliptic primitive. Both integrals include the
same explicitly stated physical-volume Jacobian J.

The cross-section rule originates polar rays at the target, intersects each
ray with the exact ellipse, and integrates r=r_max t^4 using Gauss-Legendre
nodes. This resolves the logarithmic primitive at r=0 without regularization.
The independent original volume check instead uses the linear radial map.
Periodic side quadrature, cross-section Gauss quadrature and adaptive
longitudinal quadrature are separately converged.

For interior smooth-density targets the additional checks are div F=4 pi w
and curl F=0, evaluated with the curvilinear metric J. The cusp at s=0 is
excluded from differential checks. Reflection checks use y parity and s
parity; radial reflection is not a symmetry of a curved physical tube.
