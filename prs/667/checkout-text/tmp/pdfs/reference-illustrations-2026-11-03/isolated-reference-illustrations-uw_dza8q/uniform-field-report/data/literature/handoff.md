# Literature review: 2.5D assumptions versus the frozen curved tube

User request: research the extensive 2.5D space-charge literature and contrast
our setup/results. No new simulations, solver changes, commits or pushes.

Goal: identify model families, trace OPALX's fixed g=6.36, assess finite-end
and curvature assumptions, distinguish physics-model accuracy from numerical
convergence, and give primary-source citations with explicit inferences.

Case: constant elliptical section, uniform physical rho including J=1+u/R,
L5m/R2m/a5mm/c0.5mm/beta0.001/Q10pC, sharp ends, free-space electrostatic
SACR frozen reference. All21 native main/probe pairs complete. Fine T bulk
errors r0.5563%,y0.04136% of13.07V/m scale; lastTmeshchanges .00469/.04882%.
At reference-path midpoint ErFFT=-.017629 vs SACR+.055092V/m, idealflat
slice=-.016341. At5mm insideend EsFFT~0 vs SACR3.25V/m; finerNz produces
a narrowing/rising density-step kick. These are not tracking results.

Owners: literature_longitudinal -> longitudinal/ (g, finite ends/impedance);
literature_curvature -> curvature/ (Qiang2026 and new FFA2026);
literature_model_scope -> scope/ (classical slice methods and limitations).
Root -> synthesis/source/code cross-check and final answer. JSON evidence
and primary document copies are permitted; do not edit existing report yet.

Early verified primary findings:
- Oeftiger/Hegglin HB2016 MOPR025 explicitly uses an equivalent parabolic
  longitudinal model; pipe validity zm>3rp. Its6.36 is a free-space example
  value, not a demonstrated universal constant. Need trace exact derivation.
- Qiang arXiv2606.26484 (published PRAB DOI10.1103/npx1-nclt) derives all
  kicks from one potential, assumes smooth longitudinal variation and fits
  reference radius r0 against a3D model. Distinct from OPALX's fixedg.
- Local small-curvature parameter a/R=.0025 differs from total angular
  spanL/R=2.5rad. Do not claim143deg alone invalidates a local expansion.
- Curvature potential regularization/homogeneous linear term requires care;
  do not identify Qiang's local correction with our finite-tube hoop field.
- PATRIC slice methods assume long relative bothbeam/pipe dimensions;
  cold-fluid literature (deHoon2003) explicitly discusses g-model end failure.

Next: complete primary-source review; verify exact equations/bench parameters,
make a source-to-assumption matrix, synthesize case-specific conclusions and
research priorities. State what existing results do NOT establish. No blanket
1% validity claim from aspect ratio, symplecticity or successful lattice tests.

## Research complete; report extension in progress

All three evidence JSONs are final. Root synthesis is in synthesis.json.
deHoon primary manuscript was read via the author-uploaded original2002 LBNL
preprint; official2003 journal metadata/DOI verified. It derives a nonlocal
straight-pipe averaged kernel and obtains g as a local expansion, explicitly
noting end failures. Its pipe radius must not be confused with our bend R.

Version correction: Qiang paper was published17Nov2025, PRAB28,114602;
arXiv2606.26484June2026 is an improved version. Explicit r0 minimization is
new in the latter. The curvature regularization adds linear x to remove a
divergence; no author-intent reference-force-subtraction claim is supported.

Important interpretation: frame remapping, physical curvature operator and
longitudinal closure are distinct. Our full-E stress case does not disprove
all2.5D models. The source has RMS beam-frame radial aspect~577, local
a/R=.0025 and discontinuous ends; no imported universal1%validity criterion.
No source establishes6.36 as universal. A constant adjustment cannot repair
the nonlocal tail where lambda-prime=0. RawE/coherentcurvature benchmarks
must not be identified with transverse-averaged kicks or tune/emittance tests.

sacr_report_figures owns a concise new literature section and bibliography
in the existing report, using only metadata copies (no paper PDF redistribution).
It will run a NEW PDF edit marker exactly once before this task's first edit,
send prose for root scientific review, then compile/render/verify/sourceZIP.
No simulations or production edits made for the research. Next: review draft,
verify citations/version/scope and deliver the source-backed comparison.
