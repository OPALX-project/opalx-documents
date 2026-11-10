# SACR validation and first tracking — complete

Updated 4 November 2026. No commit or push. No owned simulation remains running.

## Authorized goal and final delivery

User requested the remaining SACR checks, figures/results in the paper, then a
first same-source OPALX/PyORBIT tracking test. While AFK the user authorized a
bend continuation if straight passed, with exactly ten steps for each geometry.
All requested work is complete. The report is ten pages, compiled without
warnings, and all pages were rendered and reviewed.

- Final PDF: /Users/adelmann/git/opalx/output/pdf/fft2d5-model-comparison.pdf
- Editable source/data ZIP: /Users/adelmann/git/opalx/output/pdf/fft2d5-model-comparison-source.zip
- Hashes, exact metrics and final checks: delivery.json in this directory.

Portable replay reproduces all seven PNG figures and seven generated result
TeX files byte-for-byte, and builds the ten-page paper without warnings.
The archive's CRC and complete SHA256 manifest pass. Large H5/NPZ/FROMFILE
payloads remain in the native study; the ZIP includes small data, scripts,
source/provenance records and independent audits.

## SACR checks

Native study: /Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper.
New checks live in reference-extension/. For a uniform round disk radius20mm,
L5m,Q10pC,R2m, both uniform and triangular profiles:

- Independent original Cartesian volume integration: 16 point/profile cases,
  48 components, including all-three-nonzero off-axis bulk and 5/10mm end
  probes, plus axis0.1mm from the end. Largest observed SACR difference
  2.1876112e-11 V/m; largest last-refinement change1.4555671e-10 V/m.
- Same curved evaluator at15fixed material targets, R2..1000m and infinity,
  300vectors/900components. Infinite-radius agreement with independent
  straight cylinder <=6.883383e-15 V/m. Geometry differences decrease toward
  straight, separately from quadrature error. Old reference hashes unchanged.

Root plot_reference_extension.py generates two new figures and the result
section from archived CSVs. Methods, refinement and acceptance are in the
extension README/JSON. All are independently reviewed.

## First tracking cases and results

tracking/ contains shared sources, native cases and combined analysis. Eight
primary cases = two codes x straight/bend x ZeroSC/10pC, exactly ten steps
per case. Cold protons beta0.001, uniform5m source, radius20mm, nominalrms10mm,
1m nominal central flight, common1,048,576 quiet equal-charge particles within
each geometry, physical-J sampling in the bend. ZeroSC retains charge/mass
and disables self-fields. Both source bytes and all ID/q/time/frame controls
pass. No step refinement was run.

OPALX uses immutable original e85 baseline fd6ba8dc5, explicit MIDPOINT. The
current dirty straight OPEN3D and corrected curved model are excluded.
PyORBIT uses native linac drift / sector bend body maps, free transverse
slices and local g6.36. Per-step LS normalization is the algebraic ds/period
encoding, not a fit. Native omitted transverse-work approximation is retained.
Grid128x128x512, box48mm; period12m straight, commonpolylineC12.566367358402m
bend. Uniform+By1.564870mT covers the entire source and flight. Curved local
widths use physical circle coordinates, not whole-bunch Cartesian STAT widths.

Straight max all-step RMS difference0.0076253%; endpoint growth mismatches
u/y0.168511%,s0.108922%. Bend max all-step RMS difference0.0133814%; endpoint
growth mismatchesu0.156665%,y0.168572%,s0.530530%. Root
tracking/analyze_tracking.py exports all moment/comparison rows, combined
12-panel plot and result table/text.

## Important limits

Weak bend centroid responses do not agree at1%: radial0.141817vs2.148679um,
absolute-arc1.091471vs0.278021um. PyORBIT native ZeroSC Cartesian position
components differ from exact continuous uniform-B trajectories by up to95.06um;
OPALX ZeroSC matches its exact DISCRETE Boris map to9.55e-15m. Ten-step Boris
phase lag and native paraxial sector maps differ. OPALX deposits via a polyline
(maxsagitta1.562841um); PyORBIT retains native Frenet coordinates. The sagitta
is a geometry bound, not a force or observable error bound.

Root converts longitudinal means to the same absolute arc: OPALX relative
mean_s+R*actualreferencephase; PyORBIT explicit mean_absolute_s_m. Native
relative mean_frenet_s columns were preserved. RMS is origin-independent.
Do not infer corrected-curvature tracking or exact-curved-force validation
from the excellent RMS screen. Small early-step growth relative errors also
exceed endpoint figures. The original longitudinal closure remains limited.

Independent audit evidence: audit/tracking-contract-audit.json and
bend-tracking-audit.json with reproducible scripts; every OPALX bend H5 and
PyORBIT final Cartesian embedding checked. Old frozen3060field audit remains
valid. No production physics or tolerance changed in this follow-up. Initial
harness import/quoted-MIDPOINT parser issues were corrected and rejected
attempts retained; source moments use compensated sums rather than physical
rescaling. Preserve unrelated dirty FFA and earlier 3D/pipe work.

## Files and next scientific work

Paper changes: paper.tex, generated results/*.tex and figures/*,
README.md, HANDOFF.md, delivery.json. New native-study work: reference-extension/,
tracking/, plot_reference_extension.py; analyze_models.py has frozen-field
wording and deterministic float layout only; package_paper.py includes new
small-data replay. The approved scientific-writing style remains saved in
~/.codex/skills/manuscript-writing-review. PDF edit marker was run once for
this task; do not repeat for this completed operation.

Remaining scientific questions concern transport/coordinate and weak-centroid
responses, step convergence, and self-consistent curvature-corrected tracking.
They are not unfinished requirements of this first ten-step comparison.
