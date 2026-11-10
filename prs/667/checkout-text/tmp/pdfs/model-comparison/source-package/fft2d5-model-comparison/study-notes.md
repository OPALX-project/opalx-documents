# Straight and circular round-beam model comparison

User-defined case: L5m,Q10pC,nominal transverseRMS10mm in both directions,
uniform round cross-section radius20mm. Straight geometry first, then R2m.
Both uniform and triangular longitudinal profiles are included. This is a
frozen-field test, with free boundaries and the same physical source in all
models. PyOPAL was clarified to PyORBIT.

Paper source: `/Users/adelmann/git/opalx/docs/validation/fft2d5/model-comparison-paper`.
Compiled PDF: `/Users/adelmann/git/opalx/output/pdf/fft2d5-model-comparison.pdf`.
The older report is preserved.

## Data and models

- `opalx/`: archivede85 original2D5 straight runs. Final `*-octets-*`
  sources enforce the round beam's D4 symmetry within slices. Earlier
  quartet source controls remain unchanged.
- `curved/opalx/`: original2D5 R2 runs with physicalJ-weighted round sources,
  equal charges and original reference-polyline projection.
- `curved/corrected/`: two2Dslice +1Darc corrected model. Same Cartesian
  distributions as the original; exact-circle geometry/period is recorded.
- `pyorbit/`: native free slices+gradientg6.36; matches original projected
  coordinates, charge, grid and period.14 cases include controls/MPI checks.
- `reference/`: independent straight cylinder and exact curved SACR fields,
  exact on-axis checks, quadrature controls and source/target definitions.
- `audit/`: independent full-source/native, model derivation, potential-sign
  and all3,060 paper scalar-field/residual checks.
- `analysis/`:20 primary field cases, joined fields, even radial fields,
  centres, source histograms, exact selection and summary.

All primary sources have8,388,608 equal-charge particles. The transverse
box is48mm. Meshes are128²×512 and256²×1024. Straight x/y RMS is exactly
10mm without rescaling. In the curved source the physical Jacobian gives
mean_u50µm, rawRMS10mm and centredσu9.999875mm; this is recorded separately
from the nominal disk cross-section. The charge and physical radius are
unchanged. Longitudinal periods are12m straight, original chord-sum4π-like
circumference for original/PyORBIT curved, and exact4π for corrected curved.
Each has one charged5m bunch and a vacuum gap; no conducting pipe/images.

## Reproduction

```sh
cd /Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper
/Users/adelmann/.venv-h6/bin/python analyze_models.py
# Or replay from existing small CSVs without reading native/H5/source files:
/Users/adelmann/.venv-h6/bin/python analyze_models.py --from-csv
```

Native drivers and command/provenance records are under each model folder;
`curved/run_corrected.py` runs the corrected source/probe pair. The paper
source archive supports portable CSV replay with `--paper-dir .`.

## Acceptance and limits

Corrected centre radial errors on the two grids are0.016–0.174%; sampled
even radial errors are at most0.67434%, measured against that weak component.
Original2D5/PyORBIT centre fields remain inward. Straight triangular
Es(s1.25m) is already33.46% low in the localg model. Fine uniform PyORBIT
transverse sampling errors can exceed1%; numerical refinements are not
monotonic. Results are not a claim of full3-component1% accuracy.

Five relevant CTest suites pass with OMP1/4 after the numerical-padding guard
correction; MPI2 unsupported rejection passes. The physical thin bound.01
was unchanged: it applies to actual particles, with one CIC spacing for
occupied source cells. Empty padding only requires positive metric. A new
padding-invariance/invalid-source test covers this change. No source/kernel
formula or field tolerance was fitted to this benchmark. Test logs are in
`ctest-final-omp*.log` and `mpi2-final-guard.log`.

Tracking, general varying curvature, sharp-end model accuracy and a complete
nonlocal longitudinal correction remain outside this paper's acceptance.
No commit or push was performed.
