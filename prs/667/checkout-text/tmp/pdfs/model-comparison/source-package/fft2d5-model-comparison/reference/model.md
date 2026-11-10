# Finite round-cylinder reference

The prescribed bunch has charge Q=10 pC, length L=2h=5 m, and uniform
transverse disk radius a=20 mm. Thus sigma_x=sigma_y=a/2=10 mm in the
straight case. The physical volume density is rho(s)=lambda(s)/(pi a²),
with either lambda=Q/L or lambda=(2Q/L)(1-|s|/h), on |s|<h. Charge vanishes
outside the finite bunch. There is no conductor, periodic Coulomb image,
softening, fitted coefficient, or assumed longitudinal g factor.

## Exact straight axis field

For uniform rho, analytic integration of charged disks gives, for every s,

\[
 E_s(0,s)=\frac{\rho}{2\epsilon_0}
 \left[|s+h|-|s-h|-\sqrt{(s+h)^2+a^2}
                    +\sqrt{(s-h)^2+a^2}\right].
\]

This includes the finite end field and the exterior field. The centre field
is zero by symmetry. The disk-axis kernel before longitudinal integration is
sign(t)-t/sqrt(t²+a²), where t=s-s'. For a density segment w(s')=A+B s',
the exact integral is evaluated between t=s-hi and t=s-lo using

\[
 F_0(t)=|t|-\sqrt{t^2+a^2},\qquad
 F_1(t)=\tfrac12\left[t|t|-t\sqrt{t^2+a^2}
                     +a^2\operatorname{asinh}(t/a)\right],
\]

\[
 E_s=\frac{\rho_{\rm peak}}{2\epsilon_0}
 \sum_{\rm segments}\left[(A+Bs)\Delta F_0-B\Delta F_1\right].
\]

The triangular profile uses (A,B)=(1,+1/h) on [-h,0] and (1,-1/h) on [0,h].
Implementation uses algebraically rationalized forms to avoid cancellation
when a is small relative to the bunch length. The potential is independently
integrated with its zero at infinity; finite differences confirm E=-grad Phi.

## General straight field

`straight_reference.py` analytically integrates the original Coulomb kernel
along s' for each piecewise-linear density segment. It then integrates only
over the exact physical transverse disk. Target-centred rays with
r=rmax*t^4 resolve the integrable local singularity without a cutoff.
The transverse force uses q² times the longitudinal kernel so no artificial
1/q² overflow appears near a ray origin. These formulas are independent of
the existing curved SACR implementation.

The round geometry permits an independent 90-degree rotation check and
reflection in each straight coordinate. The full finite-cylinder result is
not identical to an infinite/local slice: the longitudinal end response and
finite-profile contribution to transverse fields remain present.

## Curved reference

The same physical u,y,s source is placed on the R=2 m circle,

\[
 \mathbf X=((R+u)\cos(s/R)-R,\ y,\ (R+u)\sin(s/R)),
 \qquad dV=(1+u/R)\,du\,dy\,ds.
\]

`build_reference.py` evaluates the already audited exact SACR boundary
identity anew for this round 20 mm geometry. Snapshots and hashes of its
two source modules are recorded in `provenance/` and `acceptance.json`.
No previous thin-ellipse field values are rescaled or reused.

The physical-volume Jacobian gives mean_u=a²/(4R)=50 micrometres and
sigma_u about that centroid=9.999875 mm; sigma_y remains 10 mm.
The stated 10 mm transverse RMS is the nominal round-section value, with
this 12.5 ppm curvature-coordinate correction explicitly recorded.
Radial reflection is not a curved-tube symmetry; y and s reflections are.

New SACR centre radial values are +0.040935976012 V/m uniform and
+0.063687106181 V/m triangular. Independent literal Cartesian volume
integrals reproduce them within 1.05e-10 V/m. The new first-order slice
expansion predicts +0.040936282897 and +0.063496387230 V/m, respectively:
continuum errors +0.000750% and -0.29946%, before particle/mesh error.

## Checks and outputs

- `straight_{uniform,triangle}_fields.csv`: independent finite-cylinder
  electrostatic fields at all 51 targets.
- `curved_R2_{uniform,triangle}_fields.csv`: new exact SACR fields at the
  same physical material targets, projected onto the exact circular basis.
- `straight_points.csv` and `curved_R2_points.csv`: common IDs and u/y/s,
  with the appropriate Cartesian positions for each geometry.
- `acceptance.json`: parameters, source/output hashes, axis, direct-volume,
  potential-gradient, Poisson/curl and curved-centre checks.
- `symmetry-checks.json` and `curved-pde-checks.json`: all-target parity,
  straight round rotations and exact-curved-metric differential checks.
- `quadrature-convergence.csv`: independent angular/radial refinements.

The final straight-axis discrepancy is below 2.9e-15 V/m. Independent
original-volume straight checks differ by at most 8.4e-10 V/m. The final
curved uniform end-field refinement changes at most 3.4e-11 V/m.
The original 32/64/96-node cap sequence did not meet the 2e-8 V/m change
criterion for the 0.1 mm end probes; adding 160 radial nodes resolved it.
The acceptance threshold was not relaxed.

Reproduce using the OPALX Python environment:

```sh
/Users/adelmann/.venv-h6/bin/python create_points.py
/Users/adelmann/.venv-h6/bin/python build_reference.py
/Users/adelmann/.venv-h6/bin/python check_symmetry.py
/Users/adelmann/.venv-h6/bin/python check_curved_pde.py
```

A suitable primary reference for disk-based electrostatics is V. Bochko and
Z. K. Silagadze, *On the electrostatic potential and electric field of a
uniformly charged disk*, Eur. J. Phys. 41 (2020) 045201,
[doi:10.1088/1361-6404/ab87aa](https://doi.org/10.1088/1361-6404/ab87aa),
[arXiv:2004.04540](https://arxiv.org/abs/2004.04540).
The cylinder formulas above were derived directly from Coulomb's law;
the off-axis disk formula from that paper is not used by this implementation.
