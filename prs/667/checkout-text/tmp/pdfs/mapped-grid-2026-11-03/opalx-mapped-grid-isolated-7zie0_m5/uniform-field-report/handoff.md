# Uniform-field and SACR validation report

## Mapped-coordinate explanation, 2026-11-03

The report now has 36 pages. New Section 15 occupies pages 27--32 and is also
compiled independently as the six-page focused technical note
`output/pdf/fft2d5-mapped-grid-explanation.pdf`. Section 14's introduction and
the abstract now explicitly call the OPEN change a replacement nonlocal 3D
operator. IPPL still uses UniformCartesian. OPALX supplies the mapping,
coordinate-density interpretation, custom G/H/F kernels, metric gradient and
field rotations; no general curved-mesh Poisson capability was added.

New editable sources: mapped-grid.tex, mapped-grid-note.tex and native TikZ
figures mapped-grid-geometry.tikz / mapped-grid-pipeline.tikz. build.sh compiles
both outputs; README, FIGURE-NOTES and the developer longitudinal-model.md
clarify the architecture. All archived data and 46 preexisting figure files
are byte-identical to the preceding source ZIP. No simulation, production
source change, numerical tolerance change, commit or push.

Scientific review passed against current implementation and source evidence.
Both final LaTeX logs have no warnings, undefined references or box issues.
Root reviewed changed report pages and the note; an independent agent visually
approved all six note pages. Actual PNG header pixels confirm every running
header is present (the image display suppresses some repeated content).
The PDF edit marker ran exactly once for this documentation task, with two
expected PDF outputs. Packaging and isolated source rebuild are the remaining
checks; final artifact hashes are recorded outside the ZIP to avoid self-reference.

Earlier report states and hashes below are historical.

## Completed OPEN update, 2026-11-02

The final report has 30 pages: new Section 14 on 23--26, appendices on 27--29,
and bibliography on 30. PDF: 1004355 bytes; SHA-256
44ff6d9078955efe50222faf056d1a89a57399e12bdbe024d4eb040b83ede077.
Outputs are /Users/adelmann/git/opalx/output/pdf/
fft2d5-uniform-field-validation.pdf and its -source.zip companion.

The existing OPEN operator uses one finite-source potential on the thin
Frenet 3D FFT mesh, first-order transverse curvature and the full circular
chord. Independent SACR covers uniform and triangular profiles. No fitted g
or profile-specific production mode was added. Source-frozen binary 70383ff7
includes the isolated no-emitter q/m preservation fix; unrelated FFA edits
are preserved and identified. Actual sumq is authoritative; the existing
weighted-source header-charge limitation is explicit. No tracking claim.

All 11 selected source/probe pairs and five separate controls pass independent
native audits. At 43 sampled points at least 5 mm inside the ends, primary
radial/vertical/tangential errors are below 0.071/0.087/0.555%, and weak centre
errors below 0.0059%. Across seven fine/control cases the worst error is
0.564124%. Source/transverse changes are below 0.02586/0.15001%; path changes
are below 1.55e-12 relative. The extra uniform 0.1 mm end target has 20.66%
tangential error and is outside the qualified set; triangle extras are below
0.731%. Repeated pipe controls, 113 unit tests and the actual two-rank guard
pass. One MPI-only unit test is skipped in the single-rank invocation.

All 1045 hashes verify, including 465 new small snapshots. Compact quadratures
reproduce exact q-attribute hashes. Large particle H5/distributions and binaries
are excluded. An isolated source-ZIP build produces identical 30-page text
and all PNG hashes; final metadata-only packaging retains the same code/data.
Root scientific and visual reviews pass. QA.md has details. The PDF marker
ran once for this operation; do not run it again for this handoff. No commit
or push by the report agent. Native state is in the study's HANDOFF.md.

The source-ZIP hash is recorded externally with final artifact metadata to
avoid a self-referential hash. Earlier report states below are historical.

## Completed pointwise-pipe model update

Current report has25pages, with updated Section13 onpages20--22, appendices
23--24 and bibliography25. FinalPDF886633bytes,SHA256
935713be3b005fb7a274c4c6c11a6e5ba5920d77731e94b93e3fd8d39c79bba6.
The24/22pageartifacts and hashes below are superseded historical snapshots.

ExplicitCIRCULAR_UNIFORM uses fixed uniform-round a and required physical b
independent of open numerical widths. The hybrid longitudinal model now has
the pointwise radial coefficient; legacyCIRCULAR/OPEN remain separate.
Fine256³ errors:0.160787%axis,0.028648%radial. RepeatedPyORBIT errors:
slices0.286050%,Baartman0.006603%. Directintercodedifferences <0.447%.
No coefficient fit or physical tolerance relaxation. This is a straight,
frozen local-field validation; new-mode tracking/curved/end fields remain open.

Preserved data/triangle-pipe unchanged. Added147small snapshots under
data/triangle-fixed, including all six newOPALXpairs/threePyrepeats, unitXML,
native gates, independent audits, regression sources/goldens, implementation
patch/base provenance and model documentation. Large arrays/H5/binaries stay
external. Both native binary hashes are recorded. All579global hashes verify.
The offline builder checks hashes, XML test counts, physical reference,
target metrics, source/binary identities and numerical-control differences.

Evidence:100unitspass+oneexpectedskip; rank2 rejectionverified; actualOPALX
field regression passesat0.003516% withwallzero; legacynegativecasefails;
oldOPENZeroSC/1pC compatibility checks pass with baselineRMSchange<4.05e-10.
These OPEN reruns do not qualify the new model fortracking. RemoteCIunrun.

The NEWPDFeditmarker ran once immediatelybeforeauthoring. Saved the earlier
Section13 in triangle-pipe-before-uniform.tex. Newbefore/afterfigures and
API/TikZgeometry received root scientific/visual approval. FinalLaTeX25pages
has no warnings/boxissues/undefinedrefs. Newpages20--22 and changed first/
appendix pages were rendered and checked; latestpage21 cosmetics checked.
README/QA/FIGURE-NOTES and reproducible offline build/archive scripts updated.
No commit or push by this report agent. SourceZIP is refreshed separately.

## Completed triangular-pipe extension, 2026-11-02

Current report is24pages, with Section13 onpages20--21 and bibliography24.
NewPDF SHA256:5c9016f96b807610b55bd6f20ec714bafaf9a31a7aed50a9939a6006eed5cd72;
874698bytes. Stableoutput is output/pdf/fft2d5-uniform-field-validation.pdf.
The earlier22pagePDF/hash below is a historical superseded artifact.

Native longitudinal-force control is complete:6OPALXsource/probe pairs and
16PyORBITconfigurations, with independent raw-data/native-binary audits.
Selected pointwise physical errors: OPALXaxis8.874568%,radial24.200713%;
PyORBITslicesaxis/radial.286050%; PyORBITBaartman.006603%. Frozenkicks,
no tune shift, full-drift evolution or curved-field claim. OPALX unmodified
g=.67+2ln(W/a) differs from this fixed-radius uniform-disk reference and
has no radial dependence. Width/model coupling is explicitly documented.

152immutable new snapshots(2.91MB) archive all22successfulconfigurations,
including unresolved sampling diagnostics, bothPyharnessversions, input/log
and build metadata. LargeNPZ/distribution/H5 files, compiledpackages and full
checkouts areexcluded. All431global evidencehashesverify. Offlinefigures
andtablegeneration independently recompute the physical reference and errors.
Bothnativecodes use the same62axis/82radialtargetIDs and fixed acceptance
window1<=|s|<=4m. Numerics and physical errors retain separate denominators.

NewPDFeditmarker ran exactlyonce immediatelybefore firstauthoring. Two
publicationfigure sets(vectorPDF/300dpiPNG) received rootvisual and independent
physicsreview. Final24pageLaTeX has no warnings/boxproblems/undefinedrefs;
allpages rendered/inspected, finalnewpages/rootreviewPASS. Scoped/rootdiff
checkPASS. bundle_source.py creates the verified sourceZIP; no production
solver edit, numerical tolerance relaxation, commit or push in this extension.

## Historical report state, 2026-11-01

Completed 2026-11-01. Latest user request: research the 2.5D literature and
contrast the completed frozen curved-tube results. Final report: 22 pages,
14 data figures, the original Chapter 2 TikZ figure, two concise literature
pages (18-19) and linked bibliography (22). Appendix A remains software
verification. All prior numerical results and plots are preserved.

Deliverables:

- /Users/adelmann/git/opalx/output/pdf/fft2d5-uniform-field-validation.pdf
- /Users/adelmann/git/opalx/output/pdf/fft2d5-uniform-field-validation-source.zip
- Editable sources, local evidence and reproducible build.sh in this folder.

Final PDF SHA-256: 5a1a2bada0ee3491fdd02c8b2815bb6c62badb4833c1f0cb1bbec2a1664f1a42

Latest changed sources: literature.tex, references.tex, main.tex,
appendices.tex, README.md, QA.md, this file and data/literature metadata.
The new PDF edit marker ran once before authoring. No new simulation, plot,
production code, physics tolerance, C++/MPI test, commit or push in this update.

Parent scientifically reviewed the literature text and its scope caveats.
The comparison distinguishes the 2.5D family and our independent-slice/fixed-g
closure; hard-ended local-gradient failure is not failure of all reduced
methods. OpenG0=6.36 matches one published example, not a universal constant
or established original developer intent. de Hoon's R is pipe radius and its
kernel is straight/circularized/transversely averaged, not our open ellipse.
Qiang 2025 and improved 2026 versions are separate; 2026 r0 matching is not
assigned to 2025. The displayed regularized correction's zero on-axis
radial derivative is our inference, not inferred author intent. Zhou 2026
is abstract-only. Small local a/R does not imply a restriction on total angle.

Current field metrics are raw laboratory components at matched material
points. The proposed charge-weighted slice average uses rho*J with J=1+u/R
and has not been computed from the 43 diagnostic points. New controls are
proposals: matched straight constant tube/padding; existing tapered family
before a nonuniform-rho reference extension for controlled smooth tails;
then nonlocal longitudinal/curvature-aware models. They are not implemented
or run here. No tracking-error percentage follows from the frozen deficit.

Metadata-only evidence archive: four JSON review/synthesis files and research
handoff, with hashes; no paper PDFs. All 278 global evidence hashes verify.
Final PDF has no warnings, box problems or undefined references. All 22 pages
were rendered and inspected; running headers also checked in fresh renders
and by pixel/text checks. Bibliography links and line breaks are clear.
Scoped diff check and source ZIP integrity pass. QA.md records the details.

Preserved frozen findings: 21 complete native main/probe pairs. Quiet T
source640x32180/path5mm scans128/64,256/128,512/256 at NZ512; L source
5120x1024/path20mm scans NZ512/1024/2048/4096 at NX128/NY64. Last T changes
r/y=.004688/.048822% of scales; final interior SACR differences r/y/s=
.5563/.04136/10.9002%. T ends remain4.24/2.65/34.51% at NZ512; no joint
fine-mesh end-convergence claim. Finest L misses nearly the entire5mm end
field. All-component1% physical target fails for this source/closure.
At reference-path midpoint, SACR Er=+.055092 V/m versus FFT2D5-.017629 V/m
(132% centre-field difference), consistent in sign with the unfitted ideal
flat-slice prediction-.016341 V/m. Characteristic transverse scale13.07 V/m
alone cannot certify this weaker curvature response. No solver fix added.

Earlier tracking results remain unchanged: fine10pC FFT2D5 maxr/s/y errors
18.89036/5.646114/.717867%; OPEN .053816/.004736/.069920%. Fine/coarse
changes .118828/.003740/1.923949%; no all-axis convergence claim. R=.25m
fine tracking remains incomplete(61/128). Physical xy/Bz is rotated to OPALX
xz/By for that tracking study; the frozen test has no external field.
