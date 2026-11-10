# Figure provenance and interpretation

Frozen constant-section comparison (`make_frozen_results.py`, archived
`data/frozen-r2/`):

- `frozen-field-comparison`: all three components at the 43 fixed targets,
  showing the finest member of each independent mesh scan. Lower panels use
  archived signed normalized differences and retain zeros.
- `frozen-mesh-convergence`: Cartesian-source transverse scan and independent
  fixed-transverse longitudinal scan. All-target/interior SACR differences
  are distinct from successive mesh changes. The 1% line is a component scale,
  not a relative error in the weak curvature field.
- `frozen-native-longitudinal-end`: native source-particle column fields and
  a checked dense SACR interpolant in the same nearest-polyline direction.
  This is not a centreline profile. Direct quadrature supplies the separate
  43-target error metrics. Fields are rescaled to exactly 10 pC.
- `frozen-centre-radial`: absolute centre field at 10 pC under the matched
  transverse scan. The full SACR prediction and analytic ideal flat-slice
  prediction are separate reference lines; the latter is not a fit.
- `frozen-longitudinal-end` is additionally rebuilt from the 43 direct targets
  but is not included as a duplicate report figure.

The final cached `plot_selection.json` is passed explicitly to offline replot;
otherwise an older, longer exploratory polar scan could be selected by default.
Source-quadrature controls reconstruct only the flat 2D slice backend; they
are not native OPALX runs or a full curved-field error bound.

SACR additions (`make_sacr_figures.py`, archived `data/sacr/`):

- `sacr-flat-limit`: all three straight-limit fields at 33 points in each of
  three geometries, compared with Dubin. Bottom panels retain signed errors
  and symmetry zeros using characteristic component scales.
- `sacr-radius-limit`: maxima over the same 33 points for the 5 m tapered
  source. Solid lines are physical finite-curvature differences from the
  straight Dubin field; dashed lines are changes under the last numerical
  quadrature refinement. Infinity is summarized separately, never assigned a
  finite logarithmic-axis location. These are static field checks.

`figures/test-geometry.tikz` is compiled directly by LaTeX. It shows the
clockwise OPALX x-z orbit (z right, x up), positive By out of the page, and
local r/s axes. The two initial-shape projections preserve their 10:1 aspect
ratios with independent magnifications. The source semiaxes are 50/5/0.5 mm.

Run `~/.venv-h6/bin/python make_figures.py` to rebuild the eight vector PDFs and
PNG previews. The script reads only copied CSVs under `data/figure-inputs/` and
checks their SHA-256 hashes against `provenance.json`. The provenance records the
original local data paths. No OPALX run is started and no parameter is fitted.

- `baseline-rms`: archived accepted zero/0.1/0.3/1 pC STAT/model comparisons.
- `baseline-refinement`: maximum RMS differences between the accepted 1 pC run
  and four separately refined controls. These are changes from the baseline,
  rather than errors against the independent model.
- `strong-charge-rms`: completed coarse/fine FFT2D5 and 3D OPEN 10 pC cases,
  with all 128/128/256 STAT samples. Input CSVs are in `data/10pc-completed/`.
  Independent model curves are drawn last in black dashes so agreement with
  OPEN does not hide them. Residuals use each run's recorded reference axes.
- `collective-growth`: the three completed 10 pC cases minus their actual
  matched zero controls. Residuals are absolute errors in that increase, in mm.
- `radius-similarity`: four completed radius/intensity-scaled cases. The upper
  curves nearly overlap. The black dashed prediction uses the R=1 m projection;
  the error panels use each case's own independent model/reference projection.
- `initial-fields`: all-particle frozen initial-field moments and particlewise
  L2 errors. IMPORTANT: historical coarse binary is `415fff3...`; current fine
  binary is `ba08fdd...`. This is not a controlled mesh-convergence pair. Label
  and caption must preserve the historical/current distinction.
- `longitudinal-model`: the independent ellipsoid's moment-equivalent g at
  1/10 pC and the configured constant 6.36. The moment-equivalent quantity is a
  diagnostic, not a fitted or proposed replacement field model.
- `centroid-covariance`: archived 1 pC FFT2D5 baseline plus completed fine 10 pC
  FFT2D5 and OPEN runs. Centroid response uses matched controls. Covariance
  uses actual HDF5 snapshots: only the final point at 1 pC, 16 times for each
  10 pC case. Missing covariance times are not reconstructed.

Coordinates: labels `r`, `s`, and `y_OPALX` denote local radial, tangential and
vertical axes. The modeled physical B_Z problem is rotated to OPALX B_y with
the orbit in its x-z plane. All size, growth, field-moment and covariance axes
include zero. Signed residual axes retain both signs where present.
# Triangular-bunch pipe figures, 2026-11-02

`triangle-pipe-fields` compares selected native on-axis fields with the physical
uniform-disk round-pipe analytic field. All curves use a single common SI
reference (400MeV protons, physical constants pinned in analytic.py). Black
dashes are the analytic solution; code/model symbols are observations. The
common accepted axis set contains62fixedtargetIDs at1<=|s|<=4m. The cusp and
end regions are gray and excluded; the displayed cusp transition has no
pointwise physical accuracy claim. Signed residuals use constant positive
Eaxis*=10681.1990178V/m, retainingzeroandthe±1%band.

`triangle-pipe-controls` uses the same selected fine runs in its radial panel,
at s=+2.5m,y0 and signed x/a from-1to1. The table includes boths=±2.5m
radialsets(82points). Its second panel plots physical on-axis maximum errors:
PyORBITtransversemesh64/128/256/512 atfixedNz128and16-ringsource; OPALX
coupled128³→256³ withonefinerlongitudinalsource. It doesnotshowajoint
asymptoticextrapolation. TheprimaryPyORBITsliceprofileinsteaduses32rings,
whoseindependentCoulomb-logquadraturepredictstheobserved-.286%residual.

The table's axis/radial columns are both maximum LOCAL-relative physical
errors, because all accepted analytic fields are nonzero. They differ from
the fixed-scale signed plot residuals and controlchanges. OPALX's actual
nativeg=.67+2ln(W/a) is NOTdrawnorlabeledasthephysicaluniform-diskanalytic
solution. NumericalwidthW20mm servesaseffectivepipeb20mm inthatformula;
thetransversesolverhasnoconductingwall. W40mmcontrolchangesgandisnota
paddingtestatfixedpipephysics. No source/solver coefficient was fitted.

The offline builder verifies hashes and independently recomputes physical
analytic fields and table maxima from the local raw CSV. All unresolved
sampling cases and separate source/boundary/MPI controls remain archived,
even though only selected completed controls supply the publication panels.

# Explicit pointwise-pipe before/after figures

The report now uses triangle-pipe-fixed-fields and triangle-pipe-fixed-controls.
Historical gray crosses come from the archived pre-change CIRCULAR source16384
case on256³. Blue circles are fixed256, the new CIRCULAR_UNIFORM model with
physicalb20mm on the same physical source/targets/mesh. Red/green are repeated
PyORBIT slice/Baartman native kicks. The physical black analytic curve remains
independent; no model coefficient or field scale is fitted.

Acceptedtargets are the same62axis and82radial IDs. Table errors are maximum
local-relative physical field errors; all accepted reference fields are nonzero.
Signed residuals use Eaxis*=10681.1990178V/m and retainzero. Gray regions
exclude cusp/ends. The lower residual plot displays the historical model bias
and corrected/Py differences without subtracting or relabeling that bias.

The new numerical mesh plot uses correctedOPALX64³/128³/256³ with one fixed
source. Its error is not monotonic as source sampling is held fixed; all
errors remain below0.161%, and the last control change is0.1373% ofEaxis.
The historicalPy transverse scan retains fixedNz128and16rings. No joint or
asymptotic convergence is claimed. Near-zero marker padding retains the zero
line without clipping the smallest corrected-model symbols.

The pipe-model-geometry.tikz schematic shows independent lengths: hard beam
radiusa5mm, physical longitudinal-modelpipe radiusb20mm, and open transverse
numericalfullwidthW20mm. The physicalwall circle is separate from the numerical
grid square. It does not depict a newly implemented transverse pipe boundary.

These pipe figures rebuild from copied immutable small snapshots. Their builder checks
per-case physical radii, field/error/control metrics, source/binary identity,
unitXML counts and native gates; no H5/NPZ/native executable is needed for
offline figure generation. Older pipe figures remain archived below.

## Corrected OPEN uniform and triangular profiles

`free-open-uniform` and `free-open-triangle` are rebuilt by
`make_free_open_results.py` from the selected source-frozen native CSV fields.
Each has radial, vertical and tangential columns. The black dashed identity
is explicitly the independent exact SACR Coulomb reference. Lower panels show
signed differences divided by E_i,*=max|E_i,SACR| over the original43 points,
separately for each physical profile. This scale differs from the older
ideal-cylinder transverse scale in Section11; numerical values are not mixed.
Zero physical fields remain visible on linear axes. The gray band is +/-1%
of the fixed component scale, while the tables and mesh plot use individual
nonzero-reference relative errors. Reference magnitudes below1e-10 of the
component scale identify floating-point symmetry zeros only; they never
remove the weak physical centre radial field.

The selected longitudinal mesh series uses one source64x32x8192 and one
reference path per profile, with solve64x32xNz at Nz2048/4096/8192. Its compact
source quadratures reconstruct the exact full q-attribute SHA256. All selected
fields use binary70383ff7, direct full-minus-probe subtraction in all3components,
and actual source-charge normalization. No inherited fixed-g gamma adjustment
is applied to these curved electrostatic fields. Independent native extraction
and q/m audits are separately checked by the offline builder.

`free-open-mesh` gives maximum original-target nonzero-reference errors in
its first3panels and the weak signed centre field in the fourth. Black dashed
lines are exact SACR values; the gray dotted negative line is the archived
uniform slice result fromxy512-z512-cart, a separate source/mesh/binary study.
That historical line illustrates the repaired sign and is not a matched
convergence datum. All field/error axes include zero; only the positive mesh
count axis is logarithmic. Fine centre agreement is also tabulated relative
to the weak centre force itself, preventing the larger bulk field from hiding
an erroneous curvature response.

The original43 targets lie at least5mm inside the ends. Extra8diagnostics,
including1mm/.1mmend distances and the triangular cusp neighbourhood, retain
separate explicit errors. The uniform0.1mmend tangential error is20.66%; no
1%claim extends to those unresolved diagnostics. The straight pipe repeat is
reported separately and does not qualify the curved free-space operator.

# Mapped-coordinate explanation, 2026-11-03

`figures/mapped-grid-geometry.tikz` is native vector TikZ. It shows the physical
image of logical coordinate cells and the actual uniform IPPL array separately.
The physical beam has L=5 m, R=2 m and a 143.24 degree source angle. Its
thickness is enlarged; transverse semiaxes are 5 mm and 0.5 mm. The coordinate
array represents a 12 mm by 1.5 mm by 8 m domain with 64 by 32 by 8192 cells;
only schematic grid lines are drawn. Source-to-observer connections illustrate
nonlocal interactions, not computed E directions or magnitudes. The explanatory
s origin is the charged-beam midpoint, whereas implementation s starts at the
first reference-path point.

`figures/mapped-grid-pipeline.tikz` distinguishes OPALX geometry/field operations
from IPPL uniform-array storage/FFT operations. Geometry, not deposited density,
determines the kernels; the same source spectrum supplies all three convolutions.
Neither graphic claims native curved-mesh or mapped-Poisson support in IPPL.
They contain no new numerical data and are included in both the full report
and the focused technical note. The older numerical figures are unchanged.

