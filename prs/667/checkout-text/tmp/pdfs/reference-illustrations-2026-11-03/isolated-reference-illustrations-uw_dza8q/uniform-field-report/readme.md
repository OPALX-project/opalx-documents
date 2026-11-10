# Uniform-field thin-ellipsoid validation report

Editable source: `main.tex`. The report covers the completed uniform-field
tracking, force/model diagnostics, numerical controls and test status, including
the completed fine-grid 10 pC FFT2D5/3D OPEN study and the remaining partial
tight-radius refinement.
Section 10 adds the semi-analytic curved-tube reference (SACR), its
33-point-per-geometry Dubin checks, radius convergence and independent static
field tests. Section 11 compares native FFT2D5 fields with SACR for a
constant-section 5 m tube at R=2 m, using matched mesh scans and source/path
controls. These tests do not establish self-consistent curved-beam tracking.
Section 12 compares the closure assumptions and validation observables with
primary literature. It separates known local-model limits from a claim about
all 2.5D methods, and lists controls that have not yet been performed.
Section 13 reproduces the longitudinal-force component of the triangular-bunch
conducting-pipe benchmark before and after the explicit `CIRCULAR_UNIFORM`
model. It separates physical `PIPERADIUS` from the open numerical mesh,
compares the pointwise analytic and repeated PyORBIT fields, and reports
independent unit tests plus an actual OPALX field regression. The older scalar
`CIRCULAR` result and all earlier numerical studies remain archived. No new-mode
tune shift, full-drift evolution or curved-field accuracy is inferred.

Section 14 replaces the slice-based free-space operator under the existing
`PIPEMODE="OPEN"` interface. It uses three 3D convolutions on a uniform
reference-path coordinate array, retaining the full circular
chord and first-order transverse curvature, with one potential for all three
fields. It introduces no uniform/triangle-specific production mode or fitted
g factor. On the primary64x32x8192 mesh, the43 original sampled targets,
at least 5 mm inside either end,
agree with independent SACR within 0.071% radial, 0.087% vertical and 0.555%
tangential for both profiles; weak centre radial errors are below 0.0059%.
The extra uniform 0.1 mm end-distance target still has 20.66% longitudinal
error and is outside that qualified set. Curved tracking has not been rerun.

Section 15 explains this architectural change in detail. IPPL remains
`UniformCartesian`; OPALX adds a coordinate map, coordinate-density
interpretation, custom curved-source kernels, the metric gradient and field
rotations. Native TikZ diagrams distinguish physical images of coordinate
cells from the actual rectangular array, and separate OPALX physics from
IPPL storage/FFTs. The derivation shows why the exact circular kernel must
be expanded before it becomes three translation-invariant convolutions.
Cost, restrictions and the separate PyORBIT validation scope are explicit.
The same six-page section is available as the standalone technical note
`mapped-grid-note.tex`, using `mapped-grid.tex` and the two new TikZ files.

The new operator accepts straight paths or horizontal constant-radius arcs,
an open path shorter than a full turn, max|curvature*u|<=0.01 across its mesh
and halo, one rank, and curved beta<=0.1; validation is at beta=0.001.
Near-full-turn arcs and curved relativistic electrodynamics are unvalidated.
Straight paths retain their Lorentz stretch. The repeated straight pipe
benchmark validates its separate local conducting-boundary model.

Chapter 2 includes a native TikZ schematic in `figures/test-geometry.tikz`.
The affine-model subsection also illustrates Dubin's uniform ellipsoid and
its componentwise linear internal field in
`figures/dubin-ellipsoid-reference.tikz`. Section 10 adds a mesh-free SACR
source/target illustration in `figures/sacr-reference-geometry.tikz`, with
separate straight limits for the tapered ellipsoid and constant-section tube.
These are model schematics; all numerical results and earlier figures are
preserved. Both editable illustrations are included in the source bundle.
The main text focuses on the model and results; software verification and
incomplete-run status are in Appendix A (`appendices.tex`).

The analytic problem has an X-Y orbit and B_Z. Its proper rotation into OPALX
has an x-z orbit, thin y extent and **B_y**. This is the existing experiment;
a literal OPALX B_z would describe a different force geometry.

Build from this directory:

```sh
./build.sh
/Users/adelmann/.venv-h6/bin/python bundle_source.py
```

The script verifies evidence hashes, regenerates tables and all data
figures, then compiles twice/as needed with `latexmk`. It uses
`/Users/adelmann/.venv-h6/bin/python`; override with `OPALX_REPORT_PYTHON` if
needed. Dependencies: NumPy, pandas, SciPy, h5py, Matplotlib, a LaTeX installation including
`latexmk`, TikZ and the packages used in `main.tex`. No OPALX simulation or network
access is launched. The final PDF is copied to:

`/Users/adelmann/git/opalx/output/pdf/fft2d5-uniform-field-validation.pdf`

The build also writes the focused explanation to
`/Users/adelmann/git/opalx/output/pdf/fft2d5-mapped-grid-explanation.pdf`.
For a documentation-only rebuild after evidence and data figures are current,
run `verify_evidence.py` followed by `latexmk -pdf -halt-on-error
-interaction=nonstopmode -outdir=.build main.tex` and the analogous command
for `mapped-grid-note.tex`. The full script remains the complete offline
reproduction path.

Outside the checkout, the build writes to a local `output/` directory. Override
the destination with `OPALX_REPORT_OUTPUT_DIR` when needed.

`data/provenance.json` maps archived evidence to original paths and hashes.
Figure inputs and their hashes are separately recorded in
`data/figure-inputs/provenance.json`. The source HDF5 particle files are not
copied into this report package. `FIGURE-NOTES.md` documents plot definitions
and the historical/current binary distinction in the frozen-field comparison.

The baseline FFT2D5 results use binary SHA-256
`ba08fdd0b0bb1e90a64ba0fd3763a8b6d044b128c0af9b9dfd215ad0ffac8fd4`.
The completed 10 pC study pins
`e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf`.
All five new runs use that executable; archived solver/test source hashes match.
The copied evidence is in `data/10pc-completed/`. The previous pilot snapshots
remain archived but no longer supply the 10 pC tables or tracking plots.
The earlier frame/slice fix is saved in local commit `fd6ba8dc5`; new validation/report edits
remain local. No commit or push is performed by the report build.

The SACR point/radius data, numerical scripts and independent checks are copied
under `data/sacr/`; `snapshot-provenance.json` verifies these files separately.
`make_sacr_figures.py` rebuilds both SACR figure sets and tables from those
snapshots. It does not run the numerical field study during a report build.
To rerun the archived multipoint study separately (also requires SciPy):

```sh
/Users/adelmann/.venv-h6/bin/python data/sacr/field_study.py \
  --outdir .build/sacr-recheck --workers 6
```

The archived `data/sacr/README.md` records the original study and independent
check commands. Numerical rechecks write separate results; the report uses
the immutable copied evidence until its manifests are deliberately refreshed.

The frozen comparison evidence is copied under `data/frozen-r2/`.
`make_frozen_results.py` checks the matched-source/path design, rebuilds tables
and calls the archived analysis in offline replot mode with explicit cached
case selectors. Native H5/distribution files remain in the original study;
report generation reads only local CSV/JSON/source snapshots. Four frozen-field
figures are included; the auxiliary 43-target end-profile figure is also rebuilt.

The auxiliary `source-controls/` study reconstructs only flat-slice CIC and
cell-averaged-logarithm fields in Python. Increasing Cartesian cross-section
sampling changes fields by at most 0.0586%, then 0.0104%, of the transverse
scale. This is a source-quadrature check, not another native OPALX run or a
bound on the full curved-field error; it is retained as supporting evidence.

`literature.tex` and `references.tex` contain the concise critical comparison
and linked primary references. `data/literature/` archives only the four
review/synthesis JSON files, the research handoff and hash metadata. Paper PDFs
are not bundled. The 2025 Qiang paper and improved 2026 preprint are cited
separately; the accepted Zhou 2026 paper is limited to its accessible abstract.

The triangular-pipe snapshots are in `data/triangle-pipe/`. The archived root
analysis includes all 22 completed configurations, including unresolved
source-sampling diagnostics; `analysis/selection.json` identifies the primary
curves and matched numerical controls. The snapshot contains input scripts,
all small raw probe tables, run/build/harness provenance and independent audits.
Large NPZ/distribution/H5 files, compiled libraries and source checkouts remain
in the original study. The `pyorbit/provenance` directory includes the upstream
license and native-package metadata. `make_triangle_results.py` verifies the
local evidence, independently recomputes analytic fields and tabulated errors,
and produces both figures without reading any external study path.

`archive_triangle.py --study /absolute/study/path` is the deliberate evidence
refresh step; it is not called by the report build. `bundle_source.py` produces
a deterministic ZIP of this self-contained report folder, excluding build and
Python caches. The native study's README and scripts describe simulation
reproduction separately from this offline report rebuild.

The new pointwise-model archive is `data/triangle-fixed/`; the previous
`data/triangle-pipe/` is immutable before-change evidence. New snapshots include
the implementation patch and its base/source provenance, unit XML and native
gate logs, independent raw-data audits, full input/probe tables and the small
regression-case fixture sources (its large distribution is regenerated by
`prepare.py`). Both executable hashes are recorded; binaries stay external.
`make_fixed_triangle_results.py` checks the two snapshot sets, unit-result XML,
physical reference, target metrics and matched before/after source identity.
The historical plot files remain in the source bundle; the report shows the
new before/after figures and a native TikZ schematic of the independent
physical and mesh lengths. `archive_fixed_triangle.py` is the explicit evidence
refresh tool and is not called by the offline build.

The corrected free-space evidence is in `data/free-open/`; `selection.json`
defines the plotted matched-source longitudinal series, finest cases and
separate numerical controls. Selected runs and repeated pipe controls use
binary SHA-256
`70383ff72345d869db40d42d2ff5aee8ceaa2f1f4fa656fcf2e8fc75e35647c1`.
`provenance/` pins the actual 982 source/test hashes, scoped solver patch,
isolated checkpoint-preservation patch and source copies. The authorship note
distinguishes preserved unrelated tracking edits from this task's change.

The source is specified by integrated physical cell charges, with compact
quadrature arrays under `analysis/source_quadratures/`; their reconstruction
recovers every archived full q-attribute hash without large H5 files.
`make_free_open_results.py` verifies these hashes, recomputes actual-charge
SACR references and direct full-minus-probe fields, checks independent native
q/m/geometry audits, recounts the CTest results, and regenerates the new
publication figures and tables without native runs or external study paths.
The earlier corrupted-weight smoke is explicitly invalid and excluded from
physical acceptance. Exploratory unselected runs remain historical evidence.
The existing header charge diagnostic can be wrong for nonuniform weights;
all new normalization uses the actual sum of particle charges instead.

`archive_free_open.py` deliberately refreshes this new snapshot namespace;
the historical evidence directories are preserved. It includes small raw
probe/field tables, input/checkpoint/source/path hashes, source generators,
independent SACR and audit scripts, unit/native controls and exact helper
provenance. Native binaries, full particle distributions/H5, compiled
packages and build trees remain external.
