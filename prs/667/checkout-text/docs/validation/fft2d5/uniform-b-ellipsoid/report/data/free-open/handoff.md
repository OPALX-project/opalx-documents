# FFT2D5 free-space physical-profile SACR study

Goal: compare frozen FFT2D5 all three field components with independent SACR for
L=5 m, R=2 m, ellipse radial a=5 mm / vertical c=0.5 mm, Q=10 pC, beta=.001.
Uniform and triangular physical longitudinal densities must converge to ~1%,
including the weak outward radial field at the bunch centre. No conducting
pipe and no smoothing of the physical longitudinal profiles.

## Completed

- Independent reference in `reference/`; derivation in `reference/MODEL.md`.
  All reference numerical/physics consistency checks pass; see its HANDOFF.
- `run_study.py`: native FROMFILE source + 51 charged probes, and a matched
  probe-only companion. Exactly reflected s sampling; equal-area transverse
  quiet sampling with exact physical Jacobian angular-CDF inverse. Triangular
  inverse-CDF phases are staggered across reflection quartets, improving tail
  sampling without changing the density. Every node keeps identical charge.
- 8 m open reference circle retained. Root's production fix will infer its
  exact smooth circle, so default path step .02 m and .01 m path control can be
  compared. Diagnostic-centred segments do not overlap even for new end probes.
- Provenance: source/input/path/reference/executable hashes; archived executable
  snapshots permit later verification after builds change the main executable.
- `analyze_fields.py`: H5 global frame/ID/charge/time/frozen displacement checks;
  probe subtraction; actual bulk-charge reference normalization; both component
  and individual nonzero-component relative errors; explicit weak centre Er
  acceptance; source/path/MPI/mesh changes; publication PDF+PNG and data CSV.

## Validation performed

Reference full build (uniform+triangle, 5 refinements, 51 targets) passed.
Native-source moment/reflection/CDF tests passed. Actual tiny FROMFILE sources
(ns16,nrad4,nphi16 for each profile) were serialized and re-read: headers,
particle count, diagnostic order, coordinate/momentum serialization and exact
s reflection passed. Analyzer smoke run correctly reports no successful native
run. No OPALX solver was launched by this subtask.

## Active native campaign (2026-11-02)

Exploratory equal-charge native pairs completed on binary44f02d57...:
`uniform-m64`, `triangle-m64` (64x32x2048, Ns2048, Nc1024),
`uniform-m64-aligned` (Ns1280), `uniform-m64z4096` (Ns2560).
Aligned Ns eliminates the spurious interior uniform Es oscillation: s=1.25 m
error12.3% becomes0.0007%. Uniform5mm-end Es error26.3%→2.46% when Nz2048→4096.
Weak centre Er remains12% and coarse vertical field4–6%, requiring transverse
and source refinement. These are exploratory, not accepted1% results.
Measured child maximum RSS:3.35GB at64x32x2048;6.67GB at64x32x4096.
Read-only sysctl confirmed64GiB installed RAM; large runs must remain sequential.

Weighted checkpoint initialization is implemented in `run_weighted_study.py`,
using existing `--restart` + `QM_MODE="ATTRIBUTES"`. Uniform spatial positions,
analytic q_i∝w(s), m_i∝q_i preserving proton q/m; diagnostics retain nonzero
matched q and are subtracted with a companion. Fixed analytic centre reference
frame. `--box` supports tighter free-space mesh, e.g.0.012x0.0015m. Area-CDF
Cartesian source is available alongside polar quadrature.

First `triangle-weighted-smoke-final` used b9a4d4cd... and MUST remain FAILED
physical evidence: strict output-q hash audit caught `emitFromEmissionSources`
broadcasting first QAttr/MAttr to all particles even with no samplers. Root is
fixing only the no-sampler path and rebuilding. Wait for root's new hash before
launching. Existing unrelated CHARGE header uses first q*N; do not use it in
weighted mode. Analyzer independently sums authoritative q, verifies every q
by sorted ID and optionally every q,m from the output checkpoint.

`run_grid_study.py` is the additional initialization quadrature: one particle
per occupied source-cell centre, q=normalization*∫ellipse-cell Jdu dy*∫profileds.
Physical ellipse boundary cell integrals use split Gauss quadrature, and
longitudinal profile cell integrals are analytic. It supports fixed
`--source-mesh` independently of solve mesh, allowing matched-source convergence.
This is a physical source quadrature, not a field fit. q16→q32 cross-cell charge
changes<1.7e-10 ofQ and source centroidu matches physical moment to3.2e-5 relative
on64x32. Checks in reference/cell_source_quadrature_checks.csv. Allscriptscompile.

Root owns code/tests/build, infrastructure agent owns straight pipe control and
independent weighted audit, report agent owns report/bundle.

FINAL production hash is now70383ff72345d869db40d42d2ff5aee8ceaa2f1f4fa656fcf2e8fc75e35647c1,
including the no-emitter Q/M preservation fix. All accepted new runs use this hash.
Coarse cell pairs `uniform-cell-m64-final`, `triangle-cell-m64-final` passed every
input→output q/m attribute hash by sorted ID, with exact10pC bulk source charge.
Independent infrastructure audit using adaptive ellipse/J integration agrees
with Gauss16 source cell weights to L1=1.54e-9Q. Source fields now agree transversely:
uniform Er.0708%,Ey.0779%,centreEr.0039%; triangle Er.148%,Ey.134%,centreEr.0102%.

Controlled longitudinal series uses one FIXED source64x32x8192(4,976,640points)
per profile, tightbox.012x.0015m, path.02m, Gauss16 cross-cell integration; field
mesh is64x32xNz with Nz2048,4096,8192. Case names `profile-cell-z<Nz>-final`.
That full six-case primary driver has completed successfully.
Uniform primary8192 PASSES every original43 nonzero component: Er.0708%,Ey.0779%,
Es.5544%,weakcentreEr.0039%. Uniform Es converges26.40%→2.494%→.5544%.
Triangle Es1.635%→.2086%→.0830% at2048→4096→8192; finestEr.0661%,Ey.0866%,
centreEr.00588%, so both profiles pass all original43 nonzero components. Added8 diagnostics
are explicit: uniform finestEs20.66% near0.1mmend, so no1%claim there.

COMPLETED, root explicitly approved full matched source96x48x8192 controls for each
profile: solve64x32x8192(same fine transverse source) then96x48x8192(same source)
to isolate transverse source vs field effects. Driver
`driver-transverse-controls-final.log` executed all four
controls then the .01 path case sequentially and exited0. Source files generated,
10,803,200points each; predicted96field peak~30GB fits64GiB. Run sequentially,
~10min additional. Suggested names profile-control-source96-final and
profile-control-mesh96-final. First uniform-control-source96-final is complete and
independent audit passes: Er.04499%,Ey.09272%,Es.54986%pointwise; change due to
finer source only is Er.02585%,Ey.01483%,Es.00457% of each localSACR component.
Every10.803M q/m value preserved. Both transverse field/source controls and
uniform-control-path01-final completed successfully using
primarysource64x32x8192, solve64x32x8192 and --path-step.01. Root approved no
native q32 duplication because integration q16→32 is independently <1e-9Q.

`export_source_quadratures.py` writes compact source quadratures under
analysis/source_quadratures: physical cross-cell weights, longitudinal integrals,
probes and model parameters; every full original q-attribute hash is reproduced.
These are suitable for the reduced report bundle (no huge raw H5/dist needed).

Final qualification is COMPLETE and PASS: `qualify_results.py` regenerated all11
selected-case CSVs, source quadratures and explicit `selection.json` plus
`final-acceptance.json`. Seven qualified fine/control cases pass every original43
nonzero field component; worst is0.564124% (uniformEs on96field mesh). Uniform
primary maximum(Er,Ey,Es)=.0708/.0779/.5544%; triangle=.0661/.0866/.0830%.
Weak centreEr primary=.00390%uniform/.00588%triangle. Source refinement changes
any local nonzero reference component by at most.02586%; matched transverse field
mesh changes at most.15001%; path.02→.01 changes less than1.55e-12 relative.
Every qualified q/m native attribute and actual10pC bulk charge passes strict audit.
Peak native RSS27.065GB; no live OPALX process or running driver remains.

Coarse convergence cases stay in plots/data but do not enter the scoped fine
pass status. Uniformextra0.1mm-end Es still20.66% error: explicit unresolved end
diagnostic, not covered by the43-point1% claim. Triangle extra8 all under.731%.
This remains a frozen low-beta electrostatic validation, not finite-step curved
tracking or relativistic validation. Root/report agent received selection+acceptance
and now own final report/bundle assembly. Infrastructure agent independently audits
all completed cases; its script/results are under audit-weighted/.

Analyzer
q/m checks remain strict, and finite curved OPEN always uses direct companion
subtraction (no historical gamma rescale). Known failedb9a smoke is explicitly
flagged invalid; default analysis writes exclusion CSV instead of treating it as
physical evidence. Do not rebuild production or launch concurrent large solvers.

## Initial next-step commands

Wait for root's rebuilt executable signal. Candidate first run (generate only
until --run is explicitly appended):

    ~/.venv-h6/bin/python run_study.py uniform-64x32-z2048 --profile uniform --mesh 64 32 2048 --ns 5120 --nrad 16 --nphi 64
    ~/.venv-h6/bin/python run_study.py triangle-64x32-z2048 --profile triangle --mesh 64 32 2048 --ns 5120 --nrad 16 --nphi 64

Then meshes 96x48x4096 and 128x64x8192, initially using the same source. The
8 m path gives longitudinal cell sizes 3.91 / 1.95 / 0.977 mm. Original closest
targets are 5 mm from the full-density uniform end; new 1 mm / 0.1 mm targets
are diagnostics and must not be quietly dropped if unconverged.

Independently increase source ns and transverse (nrad,nphi), compare a .01 m
path control and at least one two-rank run. The default 5.24M source uses about
0.8 GB of text plus H5 output; refine deliberately. Triangle near-end charge
is small, so source sampling must be checked separately from mesh convergence.

Potential limitation: a native source remains a finite quadrature;
reference convergence does not prove native source convergence. The new finite
curved OPEN operator is electrostatic with gamma=1, so subtraction is DIRECT in
all three directions. The inherited historical probe-Es gamma rescale was removed
on code review (its effect was below1e-7 for the exploratory beta=.001 runs).

## Root integration / freeze (2026-11-02)

Production now implemented in new FFT2D5FreeSpace.{h,cpp}, FFT2D5FreeSpaceKernel.h,
and FFT2D5Geometry.{h,cpp}; existing Algorithm/CMake integrates OPEN replacement.
No new free-space input mode; old OPEN g=6.36 removed. Local pipe modes unchanged.
Exact lab geometry transformed into common solve frame. All three E from common
finite-arc potential; fourth-order derivatives; singular G/H/F cell integration.
Three same-source convolutions: Phi/k=G*rho-kappa*u H*rho+kappa/2 F*rho.
Curved OPEN rejects beta>0.1 (electrostatic contract, not 1% error proof),
closed rings/arbitrary paths, |kappa*u|>0.01 mesh+halo, missing CIC source margins.
Straight OPEN uses common-gamma source stretch and E boost, unequal active mean
gamma rejected. Curved local B remains approximation, tracking not validated.

FINAL EXECUTABLE FROZEN: b9a4d4cda121c4f43589759bbe68d72b481eb4b6747a28b5d5186f5e9bb70a62.
Archived binaries/opalx-final-b9a4d4cda121c4f4. provenance/final-build.json pins
HEAD, scoped implementation patch/new source copies and 982 source/test file
hashes; no source changed during final build. No further production rebuild
planned; selected profile and pipe reruns MUST use this hash. Earlier44f02...
exploratory cases have older kernel parity/header and are not final evidence.

Tests so far: new FreeSpace3 pass (cube singular integral, analytic finite
ellipsoid all3 E at gamma1/2, empty source); Geometry7 pass, also rank2;
Algorithm9 pass incl circular frame invariance and high-beta rejection frame
restoration; Config23 pass; Numerics69 pass +1expected skip, skipped rejection
passes on both ranks with -n2. Root removed unused6.36 after these tests; final
Ctest rebuild/recheck pending. No tolerance relaxed.

Studies: coarse uniform/triangle physics qualitatively correct. Coarse64x32x2048
has centre radial~12%, vertical~4%, uniform5mm endEs26% errors. Aligned uniform
Ns=5/8*Nz eliminates 12% spurious weak interiorEs caused by source aliasing;
Nz4096 reduces endEs to2.46%, centreEr stays12% (transverse/source issue).
No1% success yet. Study agent owns weighted checkpoint source using EXISTING
QM_MODE=ATTRIBUTES and --restart, q(s)*J and m proportional q, tiny frozen step.
This avoids triangle tail equal-macrocharge noise; q!=0 probes+companion used.
Actual q datasets/weight hashes audited because existing getTotalCharge() uses
first QAttr*count and H5 header CHARGE is wrong for variable weights. Do not
silently fix unrelated total-charge utility. Direct field deposition uses q_i.
Installed RAM64GiB confirmed by agent; native jobs sequential. Tight numerical
box.012x.0015m instead of.016x.004m improves transverse resolution at same memory;
retain source/mesh/path/numerical-width controls. Native study agent preparing
weighted grid-cell source (analytic physical cell charges) to remove quadrature
asymmetry, with independent subcell integration controls.

Agent ownership: free_sacr_profiles executes uniform/triangle convergence and
analysis; free_infrastructure_audit reruns separate native pipe and actual
PyORBIT slice/Baartman1+2rank controls under pipe-control/; free_algorithm_design
owns LaTeXreport/bundle/PDF. PDF edit marker for THIS task was successfully run
EXACTLY ONCE by report agent; do NOT run it again. Root owns remaining tests,
manual docs, implementation review, final acceptance. No commits/push requested.

Docs: developer longitudinal-model.md and actual manual user-guide/field-solver,
physics/field-solver updated with model/limits. 56chapter validator, both HTML
renders (standard Quarto cache required escalation),63rendered-link checks pass.
Retain prior last-reviewed dates because scoped update, not full audit; REMEMBER
register/log updated. Tiny final metadata-date rerenders pending.

Preserve unrelated dirty FFA work and all historical report datasets/results.
Final report must honestly show any remaining failed original43 targets; no
tracking/relativistic/high-intensity accuracy may be inferred from frozen E.


## Latest root update — new final hash supersedes b9a

Essential native restart bug found by strict audit: ParallelTracker's emission
hook broadcast first QAttr/MAttr onto every restored particle even with no
emitting sampler, doubling total charge and erasing the triangular weights.
The failed b9a weighted smoke is INVALID PHYSICS and preserved/excluded. Minimal
auxiliary fix skips containers with no emitting samplers; actual emitting-source
behavior is unchanged. Source-mass proportionality preserves proton q/m.

LATEST final executable:70383ff72345d869db40d42d2ff5aee8ceaa2f1f4fa656fcf2e8fc75e35647c1.
Archived binaries/opalx-final-70383ff72345d869. All982source/test hashes stable
through build. provenance/weighted-checkpoint-preservation.patch isolates only
our new ParallelTracker hunk; actual file snapshot labels preserved unrelated
FFA line edit. The older b9a metadata remains archived. All final selected
free-space and pipe cases must use70383ff; no more production changes planned.

Ctest FINAL passes all6executables:113unit tests pass,1expectedrank2-only skip.
Actual-n2 MPI rejection test passes on both ranks. Initial Ctest MPI launcher
failed before tests because sandbox slot discovery reported no slots; mapping
slot:OVERSUBSCRIBE/no-binding fixed launch; no test/tolerance changed. checks/
contains fulloutput/test JSON and both logs. Physical tests and curved reference
frame invariance/high-beta-exception frame restoration pass.

Controlled tight-box physical-cell source now resolves noise: uniform coarse
64x32x2048 radial/vertical maxpointwise0.0708/0.0779%, centreEr0.0039%; triangle
0.1479/0.1342%, centreEr0.0102%. EndEs stillcoarse uniform18.95%, triangle1.313%.
Independent audit verifies EVERY q,m byID bitwisethrough nativeoutput+checkpoint,
true sourceQ10pC, actualgeometry/frame/motion and exactprofile physicalcharge.
Independent adaptive ellipse/J integration matches sourceGauss16 L1within1.54e-9Q.
No SACR/field fitting in source weights. Fixedfine source64x32x8192 now used
across solveNz2048,4096,8192 for both profiles. Root also approved full matched
source96x48x8192→solve64x32x8192 then→96x48x8192 controls (sequential,30GBpeak
within64GiB RAM,8min estimated). Do not stop before meaningfulsource/xy controls.
Extra8closerend probes are diagnostics; agreed43 originaltargets include5mm
insideends andweakcentreEr. Report must expose any unresolved1mm/.1mmregion and
cannot claim global1% tracking/entire-beam accuracy.

Pipe side-control re-run on70383ff PASSES metricsunchanged: OPALXaxis.160787%,
radial.028648%, PySlices.286050%, Baartman.006603%; OPALX−PySlice.446838%.
Annulus/wallmaxnonzero.003516%, wallzero, probe-only3.08e-15Vm. Allnative703hashes
and actualPyORBIT1+2rank runs/independentphysicschecks pinnedinpipe-control/.

PDFreportagent has authored model/reference draft and verifier but not frozen
acceptance/evidence or overwritten stablefinalPDF yet; awaitsconvergedselected
free cases/controls. PDFeditmarker alreadyranEXACTLYONCE forcurrenttask—do not
repeat. Keep olddata/historyimmutable. Root owns finalscientific/visualreview.

## Primary acceptance achieved; final controls/report still active

BOTH PRIMARY cases7038 under controlled source64x32x8192 pass original43points
allnonzero relativecomponents<1%, allsymmetryzerosabsolute-scaled<1%, centreEr<1%:
- uniform-cell-z8192-final errorsEr/Ey/Es=.070837/.077887/.554429%; centreEr.00390%.
- triangle-cell-z8192-final=.066129/.086603/.082990%; centreEr.00588%.
Independent audit-weighted reproduces these directly fullminusprobe(no gamma
rescale); EVERY q,m byID bitwise matchesinput; true sourceQ10pC. Main analyzer's
inheritedlegacyEs gammarescale was removed (newcurvedOPEN gamma1); no native
input/binary changed. Symmetryzeroabsoluteerrors<=2.1e-11Vm. Triangleall51
passes<.731%; uniformextra0.1mmendEs still20.66%—explicitqualifiedrange is43
historicalsamplepoints at least5mm insideends, NOTeverypoint/wholetracking.

Latest controlsPASS (all7038, no source/code issues):
- uniform-control-source96-final, source96x48x8192→solve64x32x8192:
 Er/Ey/Es=.04499/.09272/.54986%; source-onlychange<=.0259%localreference.
- uniform-control-mesh96-final same96source→solve96x48x8192:
 .01575/.05728/.56412%; mesh-onlychanges<=.0511/.1500/.0143%localreference.
- triangle-control-source96-final errors.07394/.10143/.08680%, sourcechanges<.026%.
- triangle-control-mesh96-final fullsnapshotdone, companionrunning; thenlast
 uniform-control-path001-final (.01vs.02m path) pair. ~3–4minremainingnative
 atlastagentupdate;96fieldpeak27.06GB(<64GiB), full~125–138s per snapshot.

Studyagent willwrite selection.json/final-acceptance.json scopedtoqualified
primary+source+xy+pathcontrols, notcoarseintentionalfailures. Rootapprovedfull
controls; do notstop beforependingtriangle96/pathaudits+reportcompletion.
Reportagent hasalreadycompiledprimaryfigures/modelinto stablePDFbut final
bundle/QAawaitcontrols. Rootscientificreviewfree-open.texPASS; rootvisualreview
free-open-uniform.pngandupdatedfree-open-mesh.pngPASS(no clipping, SACRdashes
clear, zerovisible, archivednegativeuniformlineexplicitseparatehistory).
FinalPDFnewpages/rootvisualQA plus ZIP/evidencehash verification remain.
Allsourcepatches reverse--check PASS, scopedwhitespacePASS. Manual56chapter/
63renderedchecksPASS andbothaffectedpagesrenderedafterdatepreservation;
REMEMBER nowpins7038. No productionchangesplanned, no commit/push requested.
