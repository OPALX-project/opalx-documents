# Independent uniform and triangular SACR reference

Goal: frozen Coulomb fields of the physical-density finite elliptical curved tube,
L=5 m, R=2 m, a=5 mm, c=0.5 mm, Q=10 pC. No conducting pipe, fitted
coefficient, production field, softening or particle sampling enters.

The uniform reference is an exact snapshot of the previous independently checked
boundary-integral implementation (`uniform_reference.py`). The new triangle is
rho(s)=rho_peak (1-|s|/h), h=L/2, with rho_peak=Q/(pi a c h).

Implementation decision: Coulomb integration by parts gives a weighted side
boundary plus a density-gradient volume term. The longitudinal primitive of the
gradient term is analytic (incomplete elliptic integrals). A target-centred polar
cross-section rule resolves its remaining logarithmic singularity. A separate
filament integration verifies the tangent component. See `MODEL.md`.

Status: COMPLETE. `build_reference.py` regenerates the original 43 targets plus
8 extra axis targets (near the density cusp and at 1 mm / 0.1 mm from each end),
both profiles, side angular levels 256/512/1024/2048/4096 and radial refinements.

Final reference files: `uniform_fields_reference.csv`,
`triangle_fields_reference.csv`, and combined `fields_reference.csv`. Columns
`F_r_m,F_y_m,F_s_m` are E/(k rho_normalization); columns
`E_r_V_m,E_y_V_m,E_s_V_m` are SI at nominal Q=10 pC. For a discrete source with
bulk charge below 10 pC because diagnostic particles carry part of BCHARGE,
multiply these SI references by Q_bulk/(10 pC).

Validation in `acceptance.json` passes. Maximum final (2048→4096) change in a
nonzero individual field component is 7.56e-12 relative. Independent direct
3-D volume Coulomb quadrature agrees at selected centre/off-axis/near-end
points to 5.97e-9 relative for nonzero components. The independent exact
tangent-filament identity differs by at most 2.38e-19 m in F units. Elliptic
primitives vs elementary adaptive integrals: 1.48e-14 relative. Interior
divergence error: 1.8e-12 relative; curl/(4 pi): 1.36e-13. Charge normalization:
8.1e-16 relative. Uniform original results reproduce the previous SACR well
within 1e-15 m in F units. These are numerical consistency checks, rather than
rigorous interval error bounds.

The nearby native harness scripts are now ready; no native solver was launched
by this reference subtask. Root will signal when the rebuilt executable is ready.

Only this directory is owned by this subtask. Existing SACR files remain unchanged.
