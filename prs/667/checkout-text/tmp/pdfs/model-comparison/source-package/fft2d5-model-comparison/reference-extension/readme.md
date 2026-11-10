# Independent checks of the current SACR tube reference

Both checks use the same physical source as the paper: a constant circular
cross-section of radius 20 mm, full material length 5 m and total charge
10 pC. The physical density is uniform over each transverse disk, with
uniform or triangular longitudinal profile. The curved test has R = 2 m.
These checks concern free-space electrostatic fields, with potential zero
at infinity, rather than a conducting pipe.

## Original Cartesian volume integral

`direct_cartesian.py` implements the original three-component Coulomb
volume kernel independently of the SACR boundary formulas. In material
coordinates it uses the literal Cartesian embedding

```text
X(u,y,s) = (u cos(s/R) - 2 R sin²(s/(2R)), y, (R+u) sin(s/R))
dq = rho(s) (1+u/R) du dy ds.
```

The kernel is `(X_target-X_source)/|X_target-X_source|³`. Transverse
target-centred rays cover the exact disk with a linear radial rule,
different from SACR's nonlinear radial boundary quadrature. Adaptive
source-s integration resolves the integrable target singularity over the
entire longitudinal domain. The implementation imports no SACR surface or
analytical longitudinal-integral helper. It introduces no softening,
excluded volume, field fit or charge renormalization.

`run_volume_checks.py` selects eight material targets per profile. Five
have all three field components nonzero. Mixed off-axis points are 10 and
5 mm inside an end; an axis control lies 0.1 mm inside an end. The four
angular/radial rules are (64,24), (128,48), (256,96), (512,160). SACR's
comparison values receive a separate boundary-rule refinement.

All 48 components pass. The largest direct-minus-SACR difference is
2.187612e-11 V/m. The largest final volume-rule change is 1.455568e-10 V/m.
Nonzero components have a maximum relative difference of 2.987427e-10;
near-zero components instead use fixed component scales taken from the
full 51-target R = 2 m reference. The declared acceptance goals, 1e-5
relative for nonzero components and 1e-8 of a fixed component scale, were
not relaxed.

`volume_checks.csv` contains the plotting data in long form:
`profile, point_id, u_m, y_m, s_m, end_distance_m, component, sacr_V_m,
direct_V_m, difference_V_m, refinement_delta_V_m, component_scale_V_m,
scaled_abs_error, nonzero_component_relative_error,
all_components_nonzero_case`. `difference_V_m` means direct minus SACR;
the refinement delta means the final rule minus its predecessor, not a
statistical confidence interval. `volume_refinement.csv` retains every
tested rule, and `volume_boundary_refinement.csv` records the separate
SACR refinement.

## Same curved producer in the straight limit

`radius-sweep/radius_sweep.py` evaluates the same curved SACR producers at
R = 2, 5, 10, 20, 50, 100, 200, 500, 1000 m and infinity, using 15 fixed
material targets for each profile. Charge, physical transverse section and
longitudinal density remain fixed. The odd-u Jacobian contribution
integrates to zero, preserving total charge without adjustment.

The actual infinite-radius evaluation agrees with the independently
implemented finite straight-cylinder reference within 6.883383e-15 V/m.
Independent angular and radial changes are at most 3.774759e-15 V/m.
Maximum selected-target component differences decrease as R increases.
Finite-radius differences describe the physical change in geometry; they
are not quadrature errors. Fixed scales from all 51 straight targets allow
zero-field points to remain in the comparison.

`radius-sweep/radius_fields.csv` provides wide plotting rows with
`profile, point_id, R_m, u_m, y_m, s_m, E_u, E_y, E_s, straight_u,
straight_y, straight_s` and additional metadata. Infinity is `inf` in CSV
and `null` in the JSON radius list. `radius-errors.csv` gives signed
differences, separate quadrature changes and scales;
`radius-error-summary.csv` contains maxima over the 15 targets.

## Reproduction and provenance

From this directory, in the existing OPALX study tree:

```sh
/Users/adelmann/.venv-h6/bin/python run_volume_checks.py
/Users/adelmann/.venv-h6/bin/python radius-sweep/radius_sweep.py
/Users/adelmann/.venv-h6/bin/python finalize_extension.py
```

No native solver is launched. Producer snapshots are hash-pinned under
the existing reference provenance and `radius-sweep/provenance/`; the
acceptance JSON files pin source, input and output hashes. The commands
use the study's existing reference inputs and are an author-environment
reference reproduction, separate from the paper archive's CSV-only figure
replay. `finalize_extension.py` also checks that prior reference outputs
remain unchanged. The joined result is `acceptance.json`.

The checks validate selected frozen fields for these two density profiles.
They provide no global numerical bound over every source or target and do
not establish native tracking accuracy, energy conservation or conducting
boundary behavior. Root owns the paper integration and subsequent tracking.
