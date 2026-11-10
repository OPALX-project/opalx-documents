# Native triangular-pipe regression completed

New case: /Users/adelmann/git/regression-tests-x/RegressionTests/FFT2D5-TriangularPipe
No existing regression cases or unrelated dirty files changed.

Inputs: CIRCULAR_UNIFORM, physicalb20mm, prescribeda5mm, numericalwidth60mm,
400MeV protons,Nreal1e14,fulltriangularL10m,one1e-20s frozenfieldreadout.
DeterministicNs8192x8crosssource=65536MP plus10probes at s=+/-2.5m and
r=0,a/2,a,(a+b)/2,b. Fixturetriangle.dist is6,652,930bytes. prepare.py uses
onlystdlib, regeneratesallfixtures andhashes. Nativeoutputsare not fixtures.

Files: .in/.local/.rt, prepare.py, validate.py, physics_config.json,
analytic_provenance.json, probes.csv, reference_path.dat, triangle.dist,
reference/nativeSTAT+.md5, reference_validation.json/reference_provenance.json,
README.md. Newvalidator requiresh5py/NumPy and independently integrates the
uniformdisk Gauss-law field to the groundedpipe; does not copy productiong.
It checks actualnativeH5IDs/N,Q/q,SIunits,time,referencegamma/straightframe,
frozenprobegeometry and everyfield. NonzeroEs<=1%; wallEs<=1e-4V/m absolute
(~1e-8oftheaxisfield). .rt adds3standardRMSbaselinechecks.

Binary SHA9d3771d58f0de7bf913909955e4ef81aef69a33341202edefa9553bb78ead8b5.
Nativecase+validator PASS: maxrelativeEs=3.51596713e-5=0.00351596713%,
wallEs0V/m,proberesidual1.05e-15m. Nativecompute~0.11s.
Independentprobe-only nativecontrol givesmax|Es|3.075e-15V/m, confirming
same-planeCICselfchargecancellation ratherthanneglectingdiagnosticcharge.
NativelegacyCIRCULARcontrol intentionally failsphysicalvalidator(exit1),
maxrelativeEs2.66217 andwallEs9746.54V/m. Thisguardsagainstregressing to
theformerconstantprofile; successfulgoldenSTATchecks alonewouldnotcatchit.

Existingtools/run_regression_smoke.py runPASS:3/3RMSchecks+physicsvalidator.
Finalartifacts: /Users/adelmann/git/opalx/build-omp/smoke/FFT2D5-TriangularPipe/20261102T205257.477907Z
LocalMacauncherrequires --oversubscribe --map-by slot --bind-to none
--host localhost:1; native.single-rank.local scriptlaunchesbinarydirectly
toavoidmachine-specificslots. .localitselfwasexecutedandpassed.

Preservednativecorrect/legacy/probe-only/localruns andcontrolsummary under
fix-longitudinal/regression-checks, including case-file-hashes.json.
EarlylaunchwithstaleoldbinaryfailednewPIPEMODEparsing;rootidentifiedand
fixedtargetopalx(staticlib)vsopalx_exe(executable). No fixturecodechangeforit.
Defaultlocalmpirunmappingfailedbeforelaunch; explicitmapsmokeresolvedit.

Withrootauthorization, appendedonlynewtest/includeentry andconditional
setup-python3.11/h5pyinstall to opalx/.github/workflows/cpu-serial.yml.
PreexistingUniformBmatrix/hooks untouched. No edits to run_regression_smoke.py.
CIwiringislocal; remoteGitHubActions notrun/pushed. Casesandnewbinarywill
needpublishedtogetherwhenuserauthorizespush. gitdiff--check passes.

No productioncodechanges, build, commit or push bythisagent.
