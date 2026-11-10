# FFT2D5 force repair and convergence

Goal: fix confirmed transverse Lorentz-force normalization/sign bugs, prevent endpoint-clamped charge pileup, and rerun 16²/32²/62²/128² convergence at fixed Q=66.729974723 nC.
Findings: lab-coordinate charge deposition gives lab electrostatic slice E; old gather multiplies E by gamma again and sets B opposite beta*t cross E/c. Existing generated path starts within initial bunch; clamping piles upstream charge at s=0. Independent one-bin OPEN rest-frame diagnostic agrees with analytic to 0.6%.
Design: retain lab-density Poisson normalization, remove extra gamma from transverse E, set correct magnetic cross product. Reject particles beyond open reference-path ends before deposition, with actionable error; corrected example supplies explicit path spanning whole bunch. Closed-ring behavior unchanged. Add independent physics tests (not fitted reference values), update existing E/B reference expectations according to derived factor/sign, no tolerance loosening. Update numerics documentation.
Status: implementation starting. Tests/build not yet run for changes.
Next: implement, prove new tests fail on old code, rebuild, unit suite, force audit then corrected grid scan. Single-rank FFT2D5 only; run supported MPI tests in full suite. Keep all prior outputs archived; no push authorized.

Implemented lab-density E normalization and correct magnetic cross product in FFT2D5Algorithm.hpp; helper renamed to setTransverseLabMagneticField. Added GPU-capable open-path coverage reduction before dt mutation; throws actionable REFPATHFNAME error for endpoint-extrapolated particles. Closed rings unchanged. Tests: independent speed-invariance/cancellation and path-rejection tests both failed before fix; after rebuild passed, with one old out-of-bounds-Z test requiring new error expectation. Added deterministic uniform-cylinder Gauss-law test (2% discretization tolerance at 32 cells/radius; no loosened existing tolerances). Existing pz=1 reference E now static-lab values, B derived beta*E/c with corrected sign. README documents physics/path behavior. Full rebuild in progress.
Final rebuilt FFT2D5 tests pass, including independent uniform-cylinder Gauss-law normalization and magnetic cancellation. Full registered CTest suite running. Manual updated with lab-density/magnetic convention and open-path coverage requirement; source validator passes, HTML render running. Corrected scan scripts prepared in OPALX-2D5/run_fixed_transverse_grid_scan.py and analyze_fixed_transverse_grid_scan.py, preserving all old runs. Await full CTest then run scan using final binary hash.
Full CTest suite passed 138/138 (44.73 s), including registered MPI tests. Actual-distribution one-step force rerun: corrected FFT2D5 interior E/net-force ratio=1.007018, magnetic/E=-0.137931 and kick/dumped-force=1.0; matched OPEN rest-frame net force=1.006215. Both conserve particle count and charge. Corrected 16/32 scan cases complete, finer cases running; same charge/timestep/NZ, explicit straight 0–1.4 m path. Main 80-grid example also rerunning with explicit path, prior main outputs archived in runs/pre-fix-80. Full manual HTML render passed; rendered validator running. GPU builds and multi-rank FFT2D5 unsupported/not exercised.

Complete: corrected four-grid scan at fixed charge/path (all cases exit0, count/Q/time validated) gives final RMS x/y [mm]:16=2.847047/2.842349,32=3.761520/3.759217,62=4.028692/4.026322,128=4.114240/4.111843; analytic4.180920/4.176548. Finest deficit1.59%/1.55%;62→128change2.12%; no claim of full spatial/time/NZ convergence. Corrected plots reviewed at OPALX-2D5/plots/fixed_transverse_grid_convergence.png/.pdf. Full source build, 138 CTests, format and whitespace checks pass; manual full HTML+reports/link validation pass. Main80example rerun with full path. Documentation/provenance in OPALX-2D5/fixed_solver_findings.txt. Diff reviewed; only intended source/test/README and manual page edits made; no commits/pushes. GPU builds not checked; FFT2D5 remains single-rank.

Longitudinal benchmark follow-up: user requested credible longitudinal test. Independent constant-g parabolic fluid oracle and quiet Q1nC distribution created (N131072). At NZ64/128/256, initial tests found spurious positive mean Ez630.95/360.53/191.15 V/m, approximately C*dz/2, with off-center gather int(s/dz+0.5). Added manufactured parabolic line-density test (analytic linear force, zero symmetry force, gamma^-2 at ps0/.4/1, both deposition modes) and periodic cell-center wrapping test; both fail on old code. Implemented matching cell-centered longitudinal gather: CIC interpolation for 3D scatter, cell selection for single-slice scatter; periodic indices wrap, open indices clamp to end cell. No g constants changed. Full rebuild running. Need update old hard-coded longitudinal field snapshots to derived centered values, rerun full tests and before/after parabolic scan, document model-vs-physical-g validation distinction.
Longitudinal follow-up complete: added and ran credible cold parabolic constant-g force/tracking benchmark, independent exact fluid oracle, zero-longitudinal-field and half-dt controls, NZ64/128/256/512. Fixed shifted longitudinal gather (cell-center interpolation consistent with deposit; periodicwrap). Manufactured parabolic force/gamma/symmetry and endpoint wrap tests pass; old symmetry-field snapshot expectations corrected from derived source geometry, tolerances unchanged. Full138CTests pass. Finestgrowth10.196988um vsoracle10.221295um (-.2378%); meanEz<1e-12V/m; halfdtchange5.65e-7% ofgrowth. Independent physical disk-field Coulomb integral vs matched one-bin OPEN near-axis error.1366%; fixedOPENg6.36 is a geometry approximation with larger finite-end errors. Detailed report and provenance OPALX-2D5/longitudinal_benchmark_findings.txt; acceptance.json passes. Source diff/format/whitespace reviewed. Full manualHTML+reports rendered; final rendered-link check running. No commits/pushes. Prior transverse convergence data predates this additional longitudinal gather fix and retains original binary hashes; do not mislabel it as rerun with the latest binary.

User-requested branch transfer: fix committed on original branch 271-implement-interation-point-element as4d55f2f41. Fetched user-created issue656 branch at a35175fee; switched to tracking branch656-fft2d5-cold-uniformkv-limit-beam-expansion-exceeds-the-analytic-prediction and cherry-picked successfully as60a001fcd, no conflicts. Only intended4files committed; unrelated untracked files preserved. Branch currently ahead oforigin1; no push authorized/performed. Build and relevanttests on newbase underway.
Branch transfer verification complete: full build succeeded on issue656 branch; FFT2D5Algorithm and FFT2D5Numerics CTests passed2/2. Current HEAD60a001fcd; original branch retains4d55f2f41. Branch ahead origin1. No tracked uncommitted changes; unrelated untracked files retained. No push performed. Test log /tmp/issue656-ctest.log, buildlog /tmp/issue656-build.log.

PR created per user request: https://github.com/OPALX-project/OPALX/pull/657, master <- 656-fft2d5-cold-uniformkv-limit-beam-expansion-exceeds-the-analytic-prediction, onecommit60a001fcd. Branch pushed with user PR authorization. Description covers all5changes with clarifications: Frenet geometry not Lorentz frame; lab-density field vs rest-frame binned3D; straight-beam equivalence only; curved-beam model/validation remainsopen; explicit endpointpileup example0–200mm vs115mm pathstart; gconstant unchanged. Full131testsonactualPRbranchpassed41.15s; fullbuildpassed; diffcheckpassed. PR attached to chat. No unrelated untracked files included.
Approved single-axis publication figure added to PR657: commitb8fb811fc adds docs/validation/fft2d5/beam-expansion-comparison.png(259104bytes) and .pdf(27259bytes). Pushed user-authorized update; PRdescription embeds immutable-commit PNG and links vectorPDF. Caption clearly labels analyticblackdashed, beforefixreddashdot, fixedmeshescolours, and notes storedfixedcurvespredate final longitudinalgather. Code unchanged; prior131testresult remains applicable. Remoteasset and PRbody verified.

Added publication longitudinal PNG/PDF in commit b3b35dc14, pushed and embedded in section 3 of PR #657. Preserved all other PR text. Media-only change; verified published body.

Curved study first pass 2026-10-30: external scripts/references and original-binary force controls at OPALX-2D5/curved-study/REPORT.md. Independent Qiang round Gaussian and leading curvature equations checked. Rotated straight input/path controls fail (45/75 coverage; manual aligned path45 zero fields); static path versus transformed particles needs frame-contract audit. Corrected initial hypothesis: meanPz is read after solve-frame rotation/update, not global. Gaussian mesh amplitude .871/.966/.990 on64/128/256; particlewise error not converged. Path refinement1mm→.5mm .00821% RMS vs expected local curvature .04174% atR1m. One-step kick check1.35e-9 relative. No fullbend validation, no source changes, no PR update/push.

Experiment checkout prepared: switched to user branch 658-fft2d5-keep-particles-and-reference-path-in-a-consistent-frame, fast-forwarded from a35175fee to b3b35dc14 to include all3commits from PR657. No conflicts, no new code edits. Local branch aheadorigin3; no push requested/performed. Relevant FFT2D5 CTest verification run on unchanged existing build; source tree identical to previously validated PR657 head.

Active implementation of issue658 four steps: reuse CoordinateSystemTrafo composition and existing frame entry/exit. Immutable path is lab, pc arrays reference-local; labToSolve=context.trackerToSolve*primary.toLab.inverted(), each pcToSolve=labToSolve*pc.toLab. Reusable transformed path view, no context API change. Agents implementing focused rotation tests and manufactured smooth-Gaussian comparison in existing test files. Need demonstrate old failure, implement, rebuild/test, rotations force/kick/Q checks, Qiang curvature reference/resolution comparison, documentation. No pushes authorized.

Issue658 four steps complete: sourceframefix +4rotation/container/exception tests +smooth manufactured density benchmark64/128/256/512. Existing transforms/storage/Poisson/gather reused. All131CTests pass OMP1; unrestrictedparallel130/131 withindependentunchangedGaussian tail-bound failure; allFFTtests pass. Sourcebuild,format,diffreviewpass. FullOPALX0/45/75force+5cmdrift invariantE/B<1.6e-12;Q/countretained;MPI2rejectsunsupported. Qiangcomparison isolates omittedcurvatureincrement. No curvatureoperatorimplemented;fullbend/GPUunvalidated. Validation docs+reproducibleplot/data under docs/validation/fft2d5/frame-consistency*. Sourcebranch658, changesuncommitted, no push. Details externalcurved-study/RESULTS-658.md.

User requested independent thinvertical bunch model inuniformBz, confirmedmotionxy. Implemented externalcurved-study/uniform-bz/ellipsoid_model.py andMODEL.md: exactaffinecolduniform-volumeellipsoid electrostatic/nonrelativisticcontinuum, noOPALXchanges. Protonsβ.01,R1m,Bz.0312974T,a/b/c5/50/.5mm,initialrigidcorotation,Q0/.1/1pC,halfturn. Ellipticcoefficients, Q0circle, energy/canonicalLz, tighterintegrationchecksallpass (~1e-10). 1pCfinalRMS2.928/22.622/2.132mm. Uniformellipsoidprojectionnotuniformsheet; zexpands; modelnotcontrolledatpreviousp.4. Properaxisrotation(x,z,-y)mapsphysicalmodeltoOPALXhorizontalpathconvention. NoOPALXrunyetforthismodel.

Uniform-B goal results: portableexampleinputs (uniform-bz/example) createdandrun. ZeroSC NONE98,304protonsβ.01,R1m,Bz31.297mT,quietuniformellipsoidsemiaxes5/50/.5mm; oneconstantCartesianFIELDMAP(properxy/Bz→xz/Byaxisrotation) avoidssegmentedSBENDseampiloterror. Every STAT step verified: OPEN32×32×64,128steps,Q0/.1/.3/1pCmaxsizeerrors.0299/.2461/.3535/.4017%. Mesh64×64×128strongcase .0614%;dt2change<.00831%;N2change<.0252%;MPI2vsserial<3.5e-13. Exactrelzero512orbitRMS9.85um. FFT2D5coarse64x128x256128stepsQ1pCvertical22.6%error NOTconverged; frozenforceXYslopeimproves.513→.836→.927 andfinershortz.957, dominatedunderresolution/noise, cannotassignresidualpurelyphysics. Strongfixedgforcebiasseparate. Noanalyticalfit;3Dgoalmet;FFTnot1%validated. Fullresults/rootuniform-bz/RESULTS.md,exampleREADME,resultsPNG/PDFandallstepCSV. No newproductionchanges,commit/push.

FFT2D5 uniform-B goal achieved 2026-10-31: native rectangular-cell integrated2DlogGreen + correct convolutionpotentialhalos/centeredgradients + reusableworkspace/emptysliceskip, meaningfulkernel/force/edge/smallgrid/neutral/staletests. Earlierframefixretained. Portable OPALX-2D5/curved-study/uniform-bz/fft2d5-example inputs SCoff/.1/.3/1pC all128steps pass<1% totalRMS vsindependentellipsoid; maximum .90323%. IndependentXY/NZ/dt/Nrefinements allpass; largestrefinederror.985827%, largestRMSchange.311011%. All131CTestOMP1 and66numericalcasesOMP4 pass; MPI2explicitunsupportedcheckpass; build/format/diffreviewpass. Finalbinary ba08fdd0b0bb1e90a64ba0fd3763a8b6d044b128c0af9b9dfd215ad0ffac8fd4. Detailedreport/provenance/sourcepatch/testlogs externaluniform-bz/fft-goal/RESULTS.md. No physicsfits orchangedbenchmark; g6.36unchanged, GPU/generalcurve/CSRnotvalidated; totalRMSagreementdoesnotmeangrowthincrement1%. Sourceworkingtreechangesuncommitted, nopush.

User requested local commit and exact next validation steps, excluding Qiang correction work. Created local commit fd6ba8dc5 (Fix FFT2D5 frame consistency and thin-beam field accuracy), branch658,28files; no push. Includes11solver/README/testfiles plusversioneduniform-b-ellipsoid model/generator/analyzers/fieldmap/path/results/figure andNEXT-STEPS.md. Sourcefilesmatchedvalidatedsnapshot beforecommit; generatorproducesidenticalsource/input; regeneratedfigureidentical; modelcheckspass. Trackedworkingtreeclean; unrelateduntrackedfilesandhistoricalframecomparisonpreserved. CurrenttestDOESvalidatecurvedtrackingatR1m/beta.01/5.7degbunchspan/180degorbit. Criticalmetricqualification:charged-minus-zeroRMSgrowth radialmodel.69117mm/OPAL.71695mm(+3.73%); tangent.26135/.34593mm(+32.36%); vertical1.90807/1.90156mm(−.34%). Nextplan(versioned):promoteOPALXrunregression,separategrowth/covariance/centroid/initialforceaudit,thenradius-similarityscanR2/1/.5/.25m withB~1/R,Q~1/R²,t~R,physicalspacingfixed,path/mapcoverageandinitialrigidvelocitiesadapted. Currentgunchanged,nocurvatureoperatorplanned.


## Original slice-model scope review, 2026-11-03

User refocuses on original efficient FFT2D5 for L=5 m, R=2 m, radial
semiaxis5 mm. Current nonlocal OPEN 3D-FFT result is a separate control,
not evidence that the old slice closure now meets SACR. Two structural
deficits remain: local g*lambda-prime misses uniform finite-end fields,
and flat transverse slices give inward centre Er=-0.017629 V/m rather
than SACR +0.055092 V/m (10 pC). Preserve prior numerical/frame/charge fixes.
A proposed reduced-potential extension would retain 2D slices plus controlled
nonlocal longitudinal and curvature corrections; 1% feasibility is unproven.
PyORBIT3 inspected at28df66018aebe4e2b780b9747f4a2d7b8430a5c0: standard
2.5D calculators have no reference-path/radius input; slice longitudinal
kicks disabled with no conducting boundary, Baartman requires pipe radius.
Can compare identical local profiles, not treat it as native full curved
free-space Coulomb oracle. Cartesian3D frozen control possible in principle
but needs another harness and global-box resolution, no run performed.
Recommended next: matched original-slice / PyORBIT local / SACR frozen
comparison to separate model deficits, then assess reduced-potential
corrections before tracking. This turn is scope analysis only; no solver
change, simulation, commit or push.


## PyORBIT ring-model clarification after web search, 2026-11-03

Important correction to the preceding scope review: PyORBIT has a separate
SC1D_AccNode/LSpaceChargeCalc ring module. The slice calculator's no-boundary
longitudinal suppression is not a global PyORBIT limitation. The ring module
Fourier-transforms line density, applies built-in pipe-form-factor SC and
user impedance harmonics, and uses periodic phases/phase length commonly C.
Built-in g=1+2ln(b/a), |Zsc/n|=Z0*g/(2*beta*gamma^2); frequency-dependent
impedances are supported. Native transverse field kernels remain local/flat.
Thus same5m profile can run in R2 ring with reduced models; it is not the
same complete free-space curved Coulomb operator as SACR. Long global
angular extent alone does not invalidate2D5. Model assumptions, physical
chamber, density smoothness and observable determine scope. No1%pointwise
weakcurvature/end-field accuracy follows from ring emittance benchmarks.

Primary web sources checked:
- https://proceedings.jacow.org/icap06/PAPERS/MOA2IS01.PDF : developer description
  separate longitudinal1D FFT impedance and transverse2.5D, often one LS kick/turn.
- https://proceedings.jacow.org/ipac2024/pdf/THPC69.pdf : modern PyORBIT Booster
  full-cycle study, transverse2D weighted by line density, separate longitudinal.
- https://epaper.kek.jp/p03/PAPERS/TOAA005.PDF : SNSbunch>160m, smoothdensity,
  2.5D/3D comparison of accumulated emittance profiles. 1e-3 is population
  level, not0.1%field accuracy.
- https://indico.ess.eu/event/618/contributions/4860/attachments/4908/6669/accumulator_nov-07.pdf :
  2.5Dtransverse+1Dlongitudinal; bunchfills85%of376mring.

This turn adds research clarification only; no simulation, source correction,
report rebuild, commit or push. The previous full report remains38pages.


Centre radial sign follow-up: circular OPEN now uses FFT2D5Curvature
(two occupied-slice2D FFTs+finite-part1D line integral) instead of curved3D
FFT. Scalar/vector independent CartesianCoulomb checks confirm SACRpositive.
Nativeuniform/triangle L5m,R2m,Q10pC,a5mm,c.5mm on128x64x512 and
256x128x1024 pass weakcentre<.45%, evenradialfield<.476%; all4pairs q,ID,
frozenpositions, field/provenance audits pass. Five relevant suites OMP1/4
andMPI2rejection pass. Source/derivation/report/tests and limits in external
curved-study/sacr/original-2d5-pyorbit-r2/radial-fix/README.md. Original
localgEs retained; longitudinal, tracking, ends andgeneralcurvature remain
open. StraightOPEN prior3Dpath retained explicitly. No commit/push.


## Current workspace and executables (4 November2026)

Work from /Users/adelmann/git/opalx, PR667 branchcodex/fft2d5-explicit-original-model,
HEADd47703aff. TrackedSRCmatchesPR; localnon-srcchangespreserved. Serial
build/src/opalx andOpenMP build-omp/src/opalx bothbuilt andsmokeverified;
useOpenMPforNEWruns. UNIT_TESTSOFF becausepreservedlocalexperimentaltests
needreconcilingwithPRsource. Fullprovenancein../opalx-build-667-record.
Ongoing100stepORIGINALcampaign in../OPALX-2D5/curved-study/straight-round-paper/
tracking/bend-10m-100steps-local-original usesfrozenarchiveda2binaryfrombefore
checkout; finishwithoutmixingversions. PR667descriptionhascase/modelchoices.
Oldlocal658branchdeleted withallcommitsretainedoncodex/fft2d5-local-work;
GitHub658branchdeleted peruser,andtipbackedupinPRclone. Previousuncommitted
SRCbackup+allnon-srcpreservationrecordin../opalx-checkout-667-record.

Finishedarchived100steplocalORIGINALexperiment: bothcases/auditsPASS,localmatchescommitted658,nativecharged1301.88s. Fullresults/plots in../OPALX-2D5/curved-study/straight-round-paper/tracking/bend-10m-100steps-local-original/RESULTS.md. This datasetusesa2archive,notnewPRd477builds. Futureworkfromthischeckout,OpenMPbuild-omp/src/opalx. Allbuild/branch/PRdescriptionsteeringdone.

## 2026-11-04 ZeroSC PyORBIT discrepancy audit
- User requests explanation of PyORBIT ZeroSC emittance discrepancy; PR analytic/plot update still pending.
- Reproducible audit: tmp/zerosc-audit/check.py and plot.py; reference CSV and zero-sc-conventions.png.
- Root cause: comparison mixed common-time OPALX trajectories with common-station TEAPOT trajectories. Native source examined: /Users/adelmann/git/PyORBIT3/src/teapot/teapotbase.cc bend1..4.
- Exact common-time: r=sqrt(R²+2Ra cos(phi)+a²), u=r-R, q_u=-p0*a*sin(phi)/r.
- Exact common-station: r=a*cos(phi)+sqrt(R²-a²*sin(phi)²), u=r-R, q_u=-p0*a*sin(phi)/R.
- Same finite source sample at 10m: time exact .0001294935644607121 mm mrad; station exact .00011021311828058994; Py native .00011024103520422021 (0.02533% station error).
- Re-time saved Py particles using delta_phi=(native_z-initial_s)/R and exact uniform-B propagation: .00012949004126227892 (0.00272% vs time exact).
- Entire 100-step Py station-reference maximum absolute error 7.36031e-7 mm mrad =0.589% of reference peak. No claim of 0.025% whole-curve accuracy.
- This diagnoses ZeroSC only; charged runs need careful common-time/station interpretation and cannot be corrected by field-free propagation without further justification.
- No native source changed or new tracking executed. Latest plots not yet committed/published to PR; publish corrected conventions, avoid obsolete claim of 15% Py physics error.

## PR update completed 2026-11-04
- Commit 7a7dc5ad61cfba48e88e95f26a3c8106495b61ea pushed to PR667.
- Seven benchmark artifact files updated to 100-step data; figures include distinct common-time/station analytic ZeroSC references.
- PR body updated with concise agreement and sampling-convention explanation, immutable image links pinned to published commit.
- Validation: figure replay and quadrature assertion passed; diff --check passed; figures inspected. No source/numerics changes or new tracking required. Unrelated working changes retained.

## PR input attachment completed
- f0abbdedf: exact OPALX local ORIGINAL input and immutable native PyORBIT driver uploaded for 100-step 10pC case, with helper, source metadata, guard check, invocation and checksums.
- PR667 body links both inputs and dependencies README. Original absolute paths retained; external particle/field map assets not bundled. No input edits or new runs.

## Benchmark artifacts relocated 2026-11-04
- User mandates ~/git/opalx-documents/examples/2026/2d5-1; do not store these benchmark artifacts under opalx/docs.
- Documents branch codex/2d5-1-benchmark-archive, commit691d148, pushed. Includes previous15 benchmark files plus independent sampling-audit script/reference CSV/plot; catalog entries and SHA256 added.
- OPALX commit ccfdc1055 removes15 tracked docs artifacts; pushed PR667. Its images and input links now use immutable opalx-documents URLs.
- Figure replay and diff checks pass. Documents full validator has only pre-existing uncataloged movies/2026-10-30-mue4_analytical-trails.mp4 error; new entries pass. Unrelated tutorials retained.
- /usr/local/bin/git-lfs crashes; /opt/homebrew/bin/git-lfs works. Used task-local PATH=/opt/homebrew/bin:$PATH for documents push; no permanent config edits.
