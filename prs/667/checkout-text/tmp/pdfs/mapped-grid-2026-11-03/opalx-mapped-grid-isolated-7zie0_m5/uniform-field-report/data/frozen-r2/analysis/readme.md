# Direct FFT2D5 / SACR frozen-field analysis

Run with the OPALX Python environment:

```sh
/Users/adelmann/.venv-h6/bin/python analyze_fields.py --require-all
```

For portable, offline figure rebuilding from the archived CSV files:

```sh
/Users/adelmann/.venv-h6/bin/python analyze_fields.py --replot --output-dir /tmp/frozen-figures
```

This mode needs no OPALX executable, H5 files or absolute helper paths. It
preserves the cached inputs and writes only figures into the output directory.
Keep `analysis/` beside `reference/`, including `reference/tube_reference.py`.

The script analyzes only complete native OPALX main/probe companion pairs.
Stopped pilot directories whose archived manifests retain their original run
names are explicitly excluded. `--cases` can restrict analysis; the three
plot selectors `--transverse-cases`, `--longitudinal-cases` and `--field-cases`
can name complete cases explicitly. With no plot selectors, the script chooses
independent matched-source transverse and longitudinal mesh sequences by
number of mesh levels, then by transverse/longitudinal sampling density.
`plot_selection.json` records the cases actually drawn. Exploratory data and
source/path controls remain in the CSV files.

## Matched geometry and fields

The prescribed source has full arclength 5 m, R=2 m, constant elliptical
cross-section with radial/vertical semiaxes 5/0.5 mm, uniform physical density,
and beta=0.001. The latter two small-scale/velocity parameters are benchmark
choices. The physical charge source includes the bend Jacobian. The independent
SACR reference is in `../reference/`; it uses no OPALX field or fitted factor.

OPALX runs take one tiny step (1e-17 s), with zero external fields. The H5
`Step#0` fields are in the tracker reference frame, not global coordinates.
The analysis rotates them using the saved reference momentum, then projects
onto the exact circle's radial/vertical/tangential basis at each of the 43
fixed material targets. It independently verifies that the closest polyline
tangent at each target matches the exact circle tangent. Field evaluation
occurs during the tiny step; the measured few-picometre displacement is
recorded and checked.

The main distribution contains the source plus 43 charged diagnostic particles.
A companion run contains just those 43 particles with the identical macrocharge.
Their computed fields are subtracted, isolating the source distribution.
Because the two containers have slightly different mean momentum, companion
tangential fields are first multiplied by gamma_probe²/gamma_main². At this
low beta the correction is small, but it makes the subtraction consistent
with the production longitudinal model. Transverse E has no such factor.
Input/source/path/binary hashes, particle IDs, count, charge, time, selected
field finiteness and reconstructed target positions are checked.

## Error definitions and limits

All three components use fixed characteristic fields; zero-field targets
are retained. In F=E/(k rho) units, the transverse scale is
4*pi*a*c/(a+c). The tangential scale is the maximum absolute converged SACR
tangential field over the declared 43 targets. These are **not pointwise
relative errors**, and the points are not a charge-weighted volume sample.

The full source charge is Q_bulk=Q_total*Nsource/(Nsource+43). Actual charge,
V/m fields and errors are exported. The continuous end-profile and centre
radial plots rescale linearly to exactly 10 pC, allowing direct comparison
between sampling controls with slightly different Q_bulk. This rescaling
does not fit a field or model parameter.

Regions are reported separately: `interior` is at least 50 mm from either
end, and `near_end` contains the 5/10 mm targets. Mesh-change errors and
SACR differences are separate quantities. Source/path control changes are
reported separately, including redistribution between longitudinal and
transverse source samples. No accuracy pass is inferred from convergence
alone. The 1% line in the mesh plot is a component-scale target.

At the tube/reference-path midpoint `(u,y,s)=(0,0,0)`, the radial field is due
to curvature. This point is not the whole curved beam's charge centroid. The separate
absolute centre-field plot prevents a small percentage of the transverse
boundary scale from hiding a large error in this small curvature response.
These are frozen-field comparisons and do not establish tracking accuracy.

The centre plot also shows an analytic limit of the current flat transverse
operator, independently checked by angular quadrature. Depositing the uniform
physical tube into `(u,y,s)` gives `rho_slice=rho*(1+u/R)`. Its ideal 2D
free-space field at the section centre is

    Er(0)/(k*rho) = -(2/R) integral_A u²/(u²+y²) dA
                 = -2*pi*a²*c/[R*(a+c)].

At 10 pC this is -0.0163410 V/m, while the independent finite curved-tube
SACR field is +0.055092 V/m. This line explains the local flat-slice model's
limit; it is neither a fit nor an additional physical curved-field reference.
The separate native longitudinal scan's centre values remain in CSV, but
the final centre plot uses only the quiet Cartesian transverse mesh sequence.

## Outputs

- `fields_comparison.csv`: all 43 targets, three directions and complete cases;
  actual fields, SACR fields, charge, characteristic scales and signed errors.
- `field_summary.csv`: maxima/RMS over the declared target sets and regions.
- `mesh_and_control_changes.csv`: common-target changes for matched meshes
  and particle/path controls. A `sampling_redistribution` changes both source
  resolutions and is not a one-parameter refinement.
- `run_integrity_checks.csv` and `acceptance.json`: evidence hashes and checks.
  The latter establishes data integrity, not 1% physical accuracy.
- `frozen-field-comparison.{pdf,png}`: finest selected transverse/longitudinal
  cases against SACR in all three components, with signed differences.
- `frozen-mesh-convergence.{pdf,png}`: independent matched-source mesh scans.
- `frozen-longitudinal-end.{pdf,png}`: positive-end centreline field and residual,
  with the independent SACR endpoint integral as a continuous curve.
- `frozen-centre-radial.{pdf,png}`: absolute curvature-only radial field.
- `frozen-native-longitudinal-end.{pdf,png}`: optional dense end profile from
  one fixed transverse source point on every longitudinal station. The native
  field and SACR field are projected onto the same nearest-polyline tangent;
  the diagnostic charge is removed using a 1D CIC calculation independently
  checked against all companion probes. The cached station comparison is
  `native_profiles_comparison.csv`. The independent SACR curve is checked
  under quadrature refinement and log-distance interpolation refinement;
  fixed-target accuracy metrics do not use that interpolation.

The 5e-12 m position-reconstruction roundoff allowance accounts for independently
reduced H5 reference momentum at about ten million particles. The observed
~1e-12 m residual corresponds to a ~1e-12 rad frame difference over a 4 m
span and remains negligible relative to the smallest transverse cell. Actual
residuals and the allowance are exported instead of being hidden by the check.
