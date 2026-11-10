# Space-charge model comparison

New concise paper, separate from the historical field-validation report.
The paper covers original 2D5, the first-order transverse curvature extension,
SACR and the actual PyORBIT slice+gradient model. It presents the straight
case before the R = 2 m circular case for L = 5 m, Q = 10 pC and nominal 10 mm transverse
RMS (uniform disk radius 20 mm), with uniform and triangular longitudinal
profiles. Figures use signed fields/residuals with zero retained.

The SACR section derives the integration by parts, defines the two end faces
of the finite charge volume, and explains free-space source-target chords.
It distinguishes the original tapered ellipsoid used for the Dubin limit
check from this paper's constant-radius tube.

The independent SACR extension adds curved off-axis/end vector checks and
a fixed-source radius sweep to the straight cylinder. A separate tracking
section compares the original OPALX and native PyORBIT slice models in a
straight drift and an R = 2 m bend: exactly ten steps and one metre of
nominal flight, with same-source ZeroSC companions.

Compile from this folder:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
```

The published local copy is
`/Users/adelmann/git/opalx/output/pdf/fft2d5-model-comparison.pdf`.
The underlying native study is
`/Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper`.

The source archive includes small field/source CSVs and `analyze_models.py`.
To replay all plots and result tables without OPALX, PyORBIT or large H5 files:

```sh
python analyze_models.py --from-csv --paper-dir .
python plot_reference_extension.py --paper-dir .
python tracking/analyze_tracking.py --from-csv --paper-dir .
latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
```

Use Python with NumPy, pandas and Matplotlib. On the author's host use
`/Users/adelmann/.venv-h6/bin/python`. The paper's result tables and plots
are generated from the same CSV records; full native inputs, source samples,
H5 outputs and per-case executable/source hashes remain in the native study.
Reference-generation commands in `reference/MODEL.md` describe the author's
workspace; the portable archive supports replay from the included CSVs.

Model distinction: at zero curvature the corrected slice model equals the
original. The straight comparison uses the immutable original e85 baseline,
not the separate current straight OPEN 3D backend. The curved corrected runs
use two 2D slice FFTs and a 1D arc integral. No 3D FFT is used for those runs.

Native source/charge/frame and reference audits pass. All 3,060 primary
scalar fields/residuals were independently checked. The correction recovers
the sampled weak radial field; the local longitudinal approximation and
source/kernel sampling still limit the full field comparison. Two meshes
do not establish asymptotic convergence.

The ten-step tracking cases pass source/ID/charge/time/frame checks. Total
RMS and endpoint growth agree within 1%, but weak bend centroid responses
do not. Native transport and geometric discretization differences are
recorded explicitly. These runs establish a first consistency screen for
the original models; they do not validate corrected-curvature tracking or
step convergence. Native results remain under the study's `tracking/` folder.
