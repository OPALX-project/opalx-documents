# Pointwise longitudinal model implementation

User approved allthree steps: independentphysics regression, explicitpointwise
model, physicalpipe radius independentofnumericalmesh; rebuild/rerunOPALX and
PyORBIT triangular benchmark andupdateLaTeXreport. No push/commit requested.

API/design: PIPEMODE="CIRCULAR_UNIFORM", PIPERADIUS=b required metres,
BEAMR=a fixedcoaxialuniformroundbeam, b>=a. New enumUniformRound and optional
configpipeRadius. PIPESIZEX/Y remainfullnumericalwidths. Insidebeamg(r)=
1+2ln(b/a)-r²/a²; vacuumannulusg=2ln(b/r); wallEs0; activeparticlesr>b
rejectedallowingonly32machineepssquared-radiusroundoff. Source/fieldformula
straightlongbeam localclosure, no nonlocalend orQiangcurvature correction.

LegacyCIRCULAR momentg.67retained; optionalPIPERADIUS decouplesitslogscale
butifabsentpreservehistoricalminwidthfallback. OPEN/PLATES/NONE rejectthe
newradiusattribute. ExistingOPEN trackingresults arehistoricalunchanged.

Ownership: root FFT2D5Algorithm.{h,hpp},builds/nativebenchmarkpipeline;
longitudinal_api ownsFieldSolverCmd/config/builder+configtests;
longitudinal_physics_tests ownsTestFFT2D5Numerics.cpp newindependentGauss
law/potentialtests;longitudinal_docs ownsnewdeveloper/user/physicsdocs.
No concurrentbuilds; rootwillbuildonceAPI/tests landed. Existingdirtyfiles
preserved; currentbranchcontinuesexisting658experiment.

Core implementationauthored: radiallydependentcoefficientandseparateb,
coveragecheck beforescatterandgather. API/tests/docsinparallel.
Next: reviewdiff+buildexistingbuild-omp;runconfig/numerics/APItestssingle
rankandrank2rejection;fixissues;nativefixedbenchmark+mesh/width/source
controls; rerunPyORBITcomparator withpinnedunchangedsource. Preserveprevious
e85binaryresults immutableandarchiveoldbinarybeforesuccessfulnewlink.
UpdateReportSection13 withbefore/afterandanalytic/Pycomparison pluslimits.
NEWPDFeditmarker notyetperformedforthisoperation;reportownerwillrunonce.
