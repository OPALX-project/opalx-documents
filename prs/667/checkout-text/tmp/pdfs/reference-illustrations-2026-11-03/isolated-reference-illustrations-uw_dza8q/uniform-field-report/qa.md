# Report verification, 2026-11-02

## Dubin and SACR model illustrations, 2026-11-03

- Current report: 38 pages. Native vector TikZ figures added on pages 3 and
  13, with their original model equations on pages 4 and 14. The independent
  six-page mapped-grid note is unchanged; full-report Section 15 is now 29--34.
- Independent scientific review covers ellipsoid axes and componentwise
  linear field, nonparallel field/displacement, tapered curved envelope,
  midpoint outward normal, physical source-target separation and both distinct
  straight limits. Surface-only SACR is scoped to uniform physical density.
- The orthogonal/nonconformal clarification states the present method without
  ruling out other mapped formulations. No claim that a conformal map alone
  removes three-dimensional source/longitudinal-field requirements.
- Both standalone previews and integrated pages 3/4/13/14 received root and
  independent visual review. No clipping, overlap, warnings, undefined refs or
  box problems. Eleven new/transition pages were rendered individually.
- All 1045 evidence hashes verify. All 1057 data files and 48 preexisting
  figures match the preceding source ZIP byte-for-byte. No simulations,
  production changes, numerical tolerance changes, commit or push.
- One PDF edit marker for this task (one expected PDF output). Source ZIP
  packaging and independent extracted-source rebuild are checked before delivery.

Earlier entries below describe previous revisions.

## Completed nonlocal OPEN update

- The PDF edit marker ran exactly once. Historical tracking and pipe evidence
  retains its original executable. The new Section 14 occupies pages 23--26
  of the 30-page report. Root approved the equations, figures and final pages.
- All 1045 evidence hashes verify, including 465 new small snapshots. There
  are 11 selected native source/probe pairs: six matched-source longitudinal
  levels and five separate source, transverse-mesh and path controls. Coarse
  levels remain visible and do not enter the fine acceptance gate.
- On the primary 64x32x8192 mesh, maximum radial/vertical/tangential errors
  are 0.07084/0.07789/0.55443% (uniform) and 0.06613/0.08660/0.08299%
  (triangle). Weak centre radial errors are 0.00390/0.00589%. All seven fine
  and control cases have maximum error 0.564124% at the original 43 sampled
  points, at least 5 mm inside either end. Source changes are below 0.02586%,
  transverse changes below 0.15001%, and path changes below 1.55e-12 relative.
- The additional eight diagnostics remain explicit. The uniform 0.1 mm end
  target still has 20.66% tangential error; the 1% claim excludes that target.
  Triangle extra-target errors are below 0.731%. No tracking, relativistic
  curved-beam or general-path accuracy claim is made.
- Independent audits check every selected case's IDs, q/m, actual total
  charge, cell geometry and fields. Curved fields use direct full-minus-probe
  subtraction in all directions. The b9a corrupted-weight smoke is invalid
  and excluded. The remaining default-weight header charge issue is stated;
  physical normalization always uses the actual sum of particle charges.
- Binary 70383ff7 is pinned to 982 source/test hashes, scoped solver and
  isolated checkpoint-preservation patches, and source copies. Preserved
  unrelated tracking edits are identified. Compact source quadratures
  reproduce every full q-attribute hash; large H5 data and binaries stay out.
- Raw CTest output recounts 113 passes and one expected MPI-only skip across
  six executables. A separate actual two-rank guard passes both ranks. No
  existing physical tolerance was relaxed. Unit tests and native OPALX runs
  remain separate validation layers; GPU and remote CI were not rerun.
- The same binary repeats the straight pipe control: OPALX axis/radial
  errors 0.160787/0.028648%; PyORBIT slices 0.286050%, Baartman 0.006603%,
  on one and two ranks. A separate annulus/wall control gives 0.003516%
  nonzero-field error and exactly zero wall field. This is local pipe physics.
- All 30 pages were rendered and inspected. Root approved the new model,
  three-component comparisons, signed SACR residuals, visible weak curvature
  reference, separate controls and explicit end limits. No clipping,
  overlap, box warnings or undefined references remain. An orphaned historical
  line and sparse catalog page were removed without deleting evidence.
- An isolated source-ZIP rebuild passes: all 30 page texts and every figure
  PNG hash match. Final packaging changes only QA/handoff metadata; its code
  and data are identical to the tested build. ZIP integrity, Python compilation,
  evidence verification and scoped whitespace checks pass. Report build runs
  no native simulation or network operation. No commit or push by this agent.

Final PDF: 1004355 bytes; SHA-256
44ff6d9078955efe50222faf056d1a89a57399e12bdbe024d4eb040b83ede077.
The source-ZIP hash is recorded outside the bundle to avoid self-reference.
Earlier verification records below are historical.

# Report verification, 2026-11-01

## Explicit pointwise-pipe model update

- This new PDF operation used exactly one marker immediately before authoring.
  Saved the previous Section13 source and retained all before-change evidence.
  FinalSection13 spans20--22 in a25page report. Historical tracking, SACR and
  frozen-curve results keep their original binaries and interpretations.
- Added147small immutable snapshots underdata/triangle-fixed. All579global
  evidence hashes verify; earlierdata/triangle-pipe is unchanged. New snapshots
  include implementation.patch/base provenance, both binary hashes, model
  documentation, unit XML/logs, rank2 guard, native fields and independent
  audits, actual regression fixture sources/reference STAT, and gate reports.
  Binaries, large NPZ/distributions and H5 data remain external.
- The offline builder independently recomputes the physical field for each
  physical pipe radius, all tabulated errors and numerical-control differences;
  it verifies matching before/after source and binary identities and recounts
  unit XML:100pass/1expectedskip. Native field regression maximum error0.003516%
  andwallzero pass their1%/1e-4V/m criteria; the legacy control is rejected.
  Existing OPEN tracking regressions pass only as compatibility controls.
- The new fine model reaches0.160787%axis and0.028648%radial error against the
  uniform-round physical reference. PyORBIT repeated slice/RB results remain
 0.286050%/0.006603%. Before/after plots distinguish the historical scalar
  model from the new model; residuals use the common fixed positive Eaxis scale,
  while table errors are local-relative on nonzero accepted targets.
- Root scientific review approved the equations, legacy/new API distinction,
  full numerical widths versus physical radius, assumptions and unit/native
  test separation. The PyORBIT common-slice-potential approach and OPALX's
  analytic hybrid closure are explicitly distinguished without a general PIC
  Hamiltonian or symplecticity claim. No new-mode tracking/curvature or finite
  end-field accuracy is inferred.
- Root visually approved the three new report pages and both publication
  figures. The native TikZ schematic accurately separates beam radius5mm,
  physicalpipe20mm and full numericalwidth20mm. Final minor label separation
  and near-zero marker padding were re-rendered and inspected. Updated first
  page/appendix also inspected. Zero stays visible; no numerical data changed.
- Latest25pageLaTeX log has no warnings, boxproblems or undefined references.
  PDF886633bytes,SHA256
  935713be3b005fb7a274c4c6c11a6e5ba5920d77731e94b93e3fd8d39c79bba6.
  Full offline build and scoped diff checks pass. No additional native runs,
  numerical-tolerance changes, commit or push by the report agent.

## Triangular-bunch conducting-pipe extension, 2026-11-02

- PDF edit marker ran exactly once immediately before the first authoring
  command. Section13 adds two pages20--21; the final report has24pages and
  sixteen data figures plus the original TikZ geometry. Prior scientific
  tests and results remain unchanged; date and bibliography are updated.
- Parent and independent native auditor reviewed the final equations,
  physical/native-coefficient distinction, source/mesh/rank controls,
  accepted-target qualification and frozen longitudinal-force scope.
  The published tune shifts and self-consistent drift are not claimed.
- Archived152small study files with hashes, including all6OPALXpairs,
  16PyORBITconfigurations, both harness snapshots, raw probe CSVs,
  build/native-binary provenance and independent audits. All431global
  evidencehashes and the new triangle manifest verify. NativeH5/distribution
  andNPZsourcearrays,compiledpackages andfullcheckouts areexternal; no paper
  PDF is added. UpstreamPyORBITlicense/package metadata is included.
- build.sh succeeds entirely from local snapshots. The new figure/table
  builder independently recalculates the physical analytic fields and all
  tabulated maxima; no source fit or native run occurs in the report build.
  Independent analytic charge/average/Gauss-law-potential checks pass.
- Tableaxis andradial errors are LOCAL-relative physicalEs errors; the
  144acceptedreferencefields are nonzero. Signed figure residuals and all
  quoted numericalchanges instead use Eaxis*=10681.1990178V/m. Cusp/ends
  remain excluded, with their native data retained. A1e-12m coordinate
  inclusion tolerance preserves exact target-boundary IDs; no physical
  accuracy tolerance changed.
- Figures use clear independent black analytic dashes, native markers and
  visible zero axes. Mesh/source/boundary controls are kept distinct; the
  Pytransverse series holdsNz128and16rings while the primarycurve uses32.
  OPALX's series changes the coupled128³→256³ grid with matchedsource. No
  joint/asymptotic convergence claim is made. Unresolved sampling cases are
  retained and explicitly identified rather than silently discarded.
- Root visually approved both publication figures and finalnewPDFpages;
  all24pages rendered with Poppler and inspected, including date and linked
  bibliography. LatestLaTeX log has no warnings, overfull/underfull boxes or
  undefined references. FinalPDF874698bytes,SHA256
  5c9016f96b807610b55bd6f20ec714bafaf9a31a7aed50a9939a6006eed5cd72.
- gitdiffcheckPASS. No production code edit, g-factor adjustment, numerical
  threshold relaxation, commit or push in this report/native-study task.

## Historical verification, 2026-11-01

- Compiled 22-page A4 PDF with latexmk/pdfLaTeX. Fourteen data figures plus the
  native TikZ test schematic. No LaTeX warnings, overfull/underfull boxes or undefined
  references in the final build log.
- Rendered all pages with Poppler and inspected them visually; re-rendered and
  inspected the pages affected by the final typography/equation corrections.
- Figure/table generation reads only copied evidence. Main evidence and figure
  inputs have separate SHA-256 manifests; both verify successfully.
- Independent physics review corrected the covariance notation and made the
  initial-phase rotation and basis for the longitudinal equivalent explicit.
- Original results review excluded three incomplete runs. The completed 10 pC
  replacements now supply the report; only the R=0.25 m refinement remains
  incomplete. Historical/current frozen-force binaries remain labeled.
- Re-ran seven smoke-runner integration checks: all passed. Re-ran the native
  validator positive control and six deliberate corruptions: positive passed,
  all corruptions correctly rejected. No new OPALX simulation was started.
- All twelve solver/test/build source hashes in the archived final provenance
  (excluding the general README) still match this checkout. The current build
  executable has a different SHA after a later build; the report identifies the
  archived run binary rather than asserting current executable identity. No
  historical result is relabeled as a run of the current executable.
- Original CTest131 / OMP4 numerical66 / MPI guard evidence is copied in data/;
  those are prior recorded tests, not a new C++ test run for this report.
- No source commit or repository push performed for this reporting task.
- Chapter 2 TikZ geometry received independent physics/visual review. Orbit
  direction, field normal, local basis, initial phase and semiaxes agree.
- Shortened the text by about 40% and moved the former Section 10 into Appendix
  A. Independent comparison against the previous draft found no changed
  scientific meaning after correcting two wording ambiguities. Recompiled and
  inspected all revised pages. No numerical data or simulations changed.

## Completed 10 pC update

- Copied 21 new CSV/JSON/manifests into data/10pc-completed; all 55 main
  evidence hashes and the legacy figure-input hashes verify. No archived pilot
  snapshot was overwritten or relabeled.
- Rebuilt total-RMS, growth and centroid/covariance plots directly from the new
  copied tables. Independent black model dashes are drawn after observations
  so close OPEN agreement cannot hide them. Size axes include zero.
- Sections 6/7 and the abstract/conclusion use the completed controls. Mesh
  changes remain separated from model error; the 1.92395% vertical change is
  explicitly outside the 0.5% convergence criterion.
- The response table reports final covariance error (OPEN 0.073%), not its
  maximum over all snapshots (0.13717%). The heading/caption states this scope.
- Compiled 13 pages without LaTeX warnings, box overflows or undefined
  references; all pages visually inspected. Python generation scripts compile.
- Source bundle refreshed. No solver edit, new simulation, commit or push by
  this reporting task; the parent ran the authorized simulations separately.

## SACR multipoint and radius-limit extension

- Section 10 defines the curved material map and volume Jacobian, the exact
  uniform-density Coulomb surface operator, the tapered Dubin-limit family,
  the independent finite-endpoint tangential identity and zero-safe component
  scales. Local material coordinates distinguish matched targets from global
  laboratory positions.
- Archived the final 33-point study in three geometries and 11 radii for the
  5 m family, including raw/all-resolution fields, endpoint checks, scalar
  implementation checks, independent differential/volume checks and numerical
  sources. All 79 main evidence hashes and the separate SACR manifest verify.
- Reran the copied field_study.py into .build/sacr-recheck: 429 point/radius
  cases and 1287 component values pass; all acceptance extrema reproduce
  exactly. Maximum straight-limit difference is 3.974664e-14 of the component
  scale; last quadrature change is at most 3.638479e-9 against 1e-8 requested.
  No numerical tolerance was relaxed.
- Finite-radius differences are explicitly physical differences from the
  straight ellipsoid, not numerical SACR errors. Per-component quadrature
  changes are separately plotted. Infinity is tabulated separately, and field
  zeros remain in all maxima and signed residual plots.
- Independent checks include 99 tangential endpoint comparisons, reflection
  and midplane symmetry, Cartesian divergence/curl at three interior points
  at R=2 m, and exterior volume-versus-surface integration at R=2/20 m.
  These checks do not establish global force/torque or tracking accuracy.
- Flat residuals use the archived precomputed normalized differences;
  round-trip CSV parsing avoids adding serialization/subtraction noise at
  machine precision.
- Rebuilt both vector PDF/300 dpi PNG figures and tables from the immutable
  local snapshots; Python generation scripts compile and git diff --check is
  clean. Final 16-page PDF has no LaTeX warnings, box problems or undefined
  references. Rendered every final page with bundled Poppler and inspected
  all pages; SACR pages were also reviewed individually at larger scale.
- The tested source is a uniform-volume-density tapered family with a
  parabolic line density. The actual constant-section 5 m beam, OPALX field
  comparison and self-consistent evolution remain future tests. The 0.5 mm
  vertical semiaxis is a verification choice. Existing tracking data and
  software-test claims are unchanged; no OPALX/C++/MPI rerun, commit or push
  was performed by this report extension.

## Frozen constant-section FFT2D5/SACR comparison

- The PDF edit marker ran exactly once before authoring this extension.
  Section 11 adds three pages, preserving all earlier tests and the Chapter 2
  TikZ figure. Software verification remains in Appendix A. Stale SACR scope
  statements now point to the new direct field comparison.
- Archived 192 final study files under data/frozen-r2, including 21 completed
  main/probe run pairs' inputs/manifests/logs, reference and all-component
  field tables, independent audit/profile data, source controls and scripts.
  Large H5/distribution files remain external. The 272 global evidence hashes
  and both SACR/frozen snapshot manifests verify.
- The transverse scan holds one Cartesian source (640 x 32180 particles) and
  5 mm reference-path step fixed over Nx/Ny=128/64,256/128,512/256 at NZ512.
  The longitudinal scan holds 5120 x 1024 particles, path step 20 mm and
  NX/NY=128/64 fixed over NZ512/1024/2048/4096. The report rebuild asserts
  identical source/path hashes within each selected scan. There is no joint
  finest-mesh run or assertion of joint end-field convergence.
- Final transverse mesh changes are 0.004688% radial and 0.048822% vertical
  of their fixed component scales. Final interior differences from SACR are
  0.5563% radial, 0.04136% vertical and 10.9002% tangential; transverse-scan
  end differences remain about 4.24/2.65/34.51% (r/y/s) at fixed NZ512.
  The finest longitudinal case misses essentially 100% of the tangential
  reference field at the 5 mm targets. The all-component 1% goal fails.
- Centre explicitly means reference-path midpoint (u=y=s=0), not the global
  charge centroid. At exactly 10 pC, SACR Er=+0.055092 V/m versus FFT2D5
  -0.017629 V/m, a 132% centre-field difference. The independent analytic
  flat-slice model predicts -0.016341 V/m without fitting. A 1% band of the
  13.07 V/m transverse scale exceeds the whole SACR centre field; the report
  explicitly rejects that scale as a sufficient curvature-field acceptance.
- Native single-rank integrity checks pass for all 21 completed pairs; no
  pending cases enter the data. Tiny-step/zero-external-field setup, actual
  source charge, probe-only subtraction, frame/basis checks and few-pm motion
  retain the frozen-field scope. This extension makes no tracking claim and
  adds no solver fix, g-factor fit, new C++ tests, commit or push.
- The auxiliary flat 2D source-quadrature reconstruction is separately
  labeled in README/evidence: changes below 0.0586%, then 0.0104%, of the
  transverse scale do not bound the full curved-operator error.
- Offline rebuild uses explicit cached selectors and verifies immutable
  inputs. All five regenerated frozen PNGs match the original final analysis
  byte for byte. Four are included in the report; the direct-target end
  figure is retained without duplicating the native-profile plot.
- Native end-profile SACR interpolation is illustrative and independently
  checked; all 43-target metrics use direct quadrature. Signed residuals and
  zero fields remain visible, and SI end/centre fields scale to exactly 10 pC.
- Final PDF is 19 pages with no LaTeX warnings, box overflows or undefined
  references. Rendered every page with bundled Poppler and inspected all
  pages; reviewed new pages 15-17 individually at larger scale. Parent review
  independently approved the science, plots, layout and stable running
  headers. Python compilation, evidence checks and scoped diff check pass.

## Primary-literature comparison

- The new PDF edit marker ran exactly once before authoring this extension.
  Section 12 occupies two pages (18-19); the twelve linked bibliography
  entries occupy a separate page (22). Prior results, figures, TikZ and
  numerical evidence are unchanged. No numerical run or new plot was made.
- Parent reviewed the science before finalization. The text distinguishes
  2.5D model families, numerical convergence, closure accuracy and tracking
  observables. It diagnoses this local-closure stress test without a claim
  that all 2.5D solvers fail or that field deficits equal tracking errors.
- The local gradient formula and hardcoded OpenG0=6.36 were checked in the
  current tested source. The literature comparison treats the matching
  PyHEADTAIL example value as a provenance clue; it does not infer a
  universal constant or original developer intent. Pipe/open-space and
  on-axis/transverse-average conventions are kept separate.
- de Hoon uses the original author manuscript (2002) plus verified journal
  metadata (2003). Its pipe radius R and straight circularized,
  transverse-averaged kernel are explicitly not the curved-tube oracle.
  Qiang's 2025 publication and improved 2026 preprint are separate entries;
  the 2026 reference-scale matching is not attributed to 2025. The
  zero-on-axis derivative of the displayed regularized correction is labeled
  our inference, without inferring intentional reference-force subtraction.
  Zhou 2026 is limited to the accessible accepted abstract.
- The local metric a/R=.0025 and total angle L/R=2.5 are distinct. RMS
  gamma*sigma_s/sigma_r is approximately 577; no strict 1% threshold follows
  from the cited Gaussian aspect-ratio illustration. Physical outer matching
  and reference-force conventions are distinct from numerical vacuum padding.
- Raw laboratory field metrics and the proposed charge-weighted slice
  average with J=1+u/R have separate definitions. The latter has not been
  computed from the 43 diagnostic points. Proposed straight/padding controls
  are unrun; arbitrary smooth rho(s) scans require extending the current
  uniform-density boundary reference. No new kernel or correction is implied.
- Archived only four review/synthesis JSON files and the research handoff,
  plus hash metadata. No downloaded paper PDF is in data/literature or the
  source bundle. All 278 global evidence hashes verify. Derived paper
  summaries are brief paraphrases with primary links; no paper figure or
  extended text is reproduced.
- Final 22-page PDF compiles with no warnings, overfull/underfull boxes or
  undefined references. Every final page was rendered and visually checked;
  new pages and references were also inspected individually. Fresh per-page
  renders and pixel checks confirm consistent running headers. Bibliography
  line breaks and URL links are legible. Source ZIP integrity is verified.
- Scoped diff check passes. No solver/API change, C++/MPI test rerun,
  commit or push was performed for this literature update.
# Mapped-coordinate explanation, 2026-11-03

- Full report: 36 pages; added Section 15 on pages 27--32. Focused note: six
  pages. Both use identical mapped-grid.tex and native TikZ source files.
- Reviewed the coordinate map, metric/Jacobian, exact circular distance,
  first-order G/H/F decomposition, FFT padding, gradient/gather and frame
  treatment against the production source. Independent scientific review
  passed; corrected the guard wording to two-cell potential halo.
- The description explicitly separates UniformCartesian storage from OPALX
  geometry/physics, and classifies the replacement OPEN operator as a nonlocal
  3D calculation. The separate local pipe/PyORBIT comparison is not represented
  as curved-source cross-code validation.
- All 1045 archived evidence hashes verify. Independent preservation audit
  confirms all 1057 archived data files and 46 preexisting figure files are
  byte-identical to the preceding source ZIP. No source/evidence refresh.
- Both final LaTeX logs contain zero warnings, undefined references or box
  issues. bash -n build.sh passes. Root and an independent agent reviewed
  the six-page note; root also inspected the changed report abstract, Section
  14 and both new figures in the full report. Seventeen single-page renders
  cover new/changed pages and appendix/bibliography transitions. Header pixels
  are present and consistent even where the image display suppresses repeats.
- No new simulations, solver changes, C++/MPI tests, numerical tolerance
  changes, commit or push are part of this documentation update. Previous
  numerical test results and limitations remain exactly scoped as before.
- The PDF edit marker ran once for this task (two expected PDF outputs).
  Independent extraction of the 1165-file source ZIP passes CRC, byte matching
  and all 1045 evidence checks. Both extracted documents compile without
  warnings; all 36 full-report and six focused-note page texts exactly match
  the delivered outputs. Final rebundling changes only HANDOFF.md, QA.md and
  MAPPED-GRID-STATE.md metadata; all tested LaTeX, figures and data are identical.

