# OPALX triangular-pipe setup audit

Goal: independently audit a native one-step FFT2D5 triangular bunch benchmark
without changing production code. Parent owns run generation and execution.

Confirmed current source and existing frozen harness:

- Input token: `PIPEMODE=CIRCULAR`. This changes only the longitudinal model;
  transverse slice Poisson boundaries remain OPEN. The input help explicitly
  says so. Use a centred circular source so the axisymmetric conducting-pipe
  image contribution to the interior transverse force vanishes in the model.
- `BEAMR=0.005`, `PIPESIZEX=PIPESIZEY=0.040` means full computational width
  40 mm, origin -20 mm and transverse spacing 0.040/N. The algorithm uses the
  same full width as `pipeRadius` in its g logarithm. For physical pipe radius
  20 mm this is a factor-of-two radius convention issue, independent of the
  additional constant/profile issue.
- Native g = 0.67 + 2 ln(0.040/0.005) = 4.828883083359671.
  Uniform-round on-axis g = 1 + 2 ln(0.020/0.005) = 3.772588722239781.
  Uniform-disk transverse-average g = 0.5 + 2 ln(0.020/0.005)
  = 3.272588722239781. Native expected biases are respectively +27.9991920%
  and +47.5554521% when longitudinal density deposition is converged.
- Setting PIPESIZE=0.020 would supply the desired logarithm radius but would
  also halve the computational domain. It must be labelled as an explicit
  parameter-convention control, not silently interpreted as a 40 mm pipe.
- MPI rank1 only. FFT2D5Algorithm::solve explicitly rejects either tracking
  context mpiSize !=1 or ippl communicator size !=1. Parallel decomposition
  flags must all be FALSE. A rank2 guard run can verify expected rejection.

Smallest safe native frozen run:

- FROMFILE with uniform reduced momentum pz=beta/sqrt(1-beta^2), px=py=0.
- Straight path from z=-6 to +6 m, x=y=0, full beam length10m. Only two nodes
  are required because the projector uses line segments; loader computes
  path length from Cartesian nodes and does not use the nominal s column.
- Equal-charge quiet source representing triangular lambda and uniform
  circular cross-section. Add probes after source IDs; a probe-only companion
  with matching macrocharge subtracts diagnostic self-fields by linearity.
- Inactive far drift: D1:DRIFT,L=1,ELEMEDGE=1000; TRACK MAXSTEPS=1,
  DT=1e-20, ZSTOP={100}; RUN METHOD=PARALLEL, TURNS=1. Enable PSDUMPFREQ1,
  STATDUMPFREQ1, EBDUMP=TRUE. No actual magnetic field or active lattice
  element is needed; using active drift tinyDT previously caused orbit
  threading to attempt a full element with impractically many steps.
- Run binary directly with input and --info4, OMP_NUM_THREADS4. Native binary
  hash equals the completed SACR study hash:
  e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf.
- DT1e-20 at beta.1 moves3e-13m. DT1e-17 would move3e-10m, exceeding old
  hard-coded frozencheck tolerances; check expectedvelocity displacement.

H5 readout checks:

- Exactly Step#0; time equals promisedDT; CHARGE and sum(q) equalinputcharge.
- IDs are exactly0..N-1; wanted probe IDs start at Nsource.
- H5 keys Ex/Ey/Ez, x/y/z, px/py/pz, Bx/By/Bz. Verify all finite.
- H5 positions and vectors are tracker-frame. Reconstruct Rglobal=R@basis.T
  +RefPartR and Eglobal=E@basis.T, with basis from RefPartP. Straight positive
  z beam gives identity up to floating-point transversemean residual.
- Companion/main must match mesh, path, binary, DT and macrocharge. For
  small different mean gamma, multiply companion Es by gammaProbe^2 /
  gammaMain^2 before subtracting.
- For triangle profiles exclude a few longitudinal cells near s=0 cusp and
  s=+/-5m endpoints when assessing the local analytical constant-slope kick.
  Plot those excluded regions rather than claiming end-field validation.

Source files inspected: FieldSolverCmd.cpp/.h, FFT2D5FieldStorage.cpp/.h,
FFT2D5Algorithm.cpp/.h/.hpp, ReferencePath.cpp and existing frozen-r2
run_study.py plus readout/audit scripts. No runs or production/report edits
by this initial setup audit. Native output and MPI checks are recorded below.

## Confirmed parent benchmark parameters

Parent selected the original native example's400MeV proton energy and total
real particle count1e14 (Q=1.602176634e-5C), rather than initial low-charge
proposal. FullL10m,a5mm,b20mm; equivalent frozenkicklength1m. Approximate
analytic scales: gamma1.42631557,beta.71305596,peaklambda3.204353268e-6C/m,
|lambda-prime|6.408706536e-7C/m2. On-axisEzplateau10681.20V/m, uniform-disk
average9265.57V/m, nativefullwidthconstant13671.85V/m. PeakedgeEr11.5197MV/m;
E+v-cross-B transverse-equivalentfield5.6625MV/m. Native Physics.h mass and
epsilon0 are .93827208816GeV and8.8541878128e-12F/m; using scipyCODATA
differences is immaterial topercenttests butrecordconstantsforreplay.

H5PartWrapperForPT.cpp explicitly writes Ex/Ey/EzUnit=V/m. E-ref attributes
separately haveMV/m, so their scale must not be applied toself-fielddatasets.
NativeFFTgather returns labE, includingEz withgamma^-2, and sets
Bx=-beta*Ey/c,By=beta*Ex/c. Therefore comparison of transverse momentum kicks
must include magnetic cancellation E+v-cross-B=E/gamma^2.

## Completed native-output audit

Read parent main/probe pairs m64,m128,m256 and wide256. Parent primary runs
setPIPESIZE=.020m so the current longitudinal coefficient uses effective
pipe radius20mm; the transverse computationaldomain isthen20mmfullwidth.
wide256 sets.040m and has matched physical dx/dz to m128. This explicit
parameter-convention control is essential; it is not a conducting transverse
boundary solve. Our audit infers width from archivedinput, not physicalcfg.

check_native.py independently verified all8H5snapshots: returncodes,
input/binary/distribution/pathhashes, exactStep#0, V/mElectricunits, time,
totalcharge andperparticlemacrocharge, completeIDs, finitesource/probefields,
and reconstructedglobalprobegeometry. Same62onaxisacceptancepoints use
1<=abs(s)<=4m for allmeshes. The primarynativecoefficient is3.44258872224.
Native-modelmaxerrors are .0050834%,.0676406%,.5586563% for64/128/256;
this nonmonotonic small source/gridnoise motivates a source-resolutioncontrol
beforeanylongitudinalmeshconvergenceclaim. Physicalonaxismaxerrors are
8.75182%,8.80903%,9.25710%; medianinferredg m128=3.44260485649.
wide256native-modelerror .0676406%, physicalonaxiserror28.05716%,
medianinferredg4.82890571471 matchesexpected4.82888308336. No coefficientfit.
DetailedCSV/JSON and independentfieldextracts are beside thisstatefile.

NativeMPI2guard was tested using a copiedm64-probeinput under rank2-guard.
DefaultMPIlaunchfailedbeforeexecution onallocation/mapping; those failures
arearchived. Successfulcommandrequires --oversubscribe --map-by slot
--bind-to none --host localhost:2 -np2. OPALX thenlaunchedtwo ranks and
rejectedtheinput inbuildSpaceChargeConfig with explicitmessage
"FFT2D5 supports only one MPI rank." Nonzeroexit156 isexpectedPASS of
thesupportguard, notdistributednumericalvalidation. Theearliersolver-level
guardisthereforeunreached. Logs, command, binary/inputhashes and resultJSON
areinrank2-guard. No production edits or unrelatedprocessactions.

## Follow-up independent consolidation audit

source16384pair also passes all checks, making10snapshots/5pairs. Its
native-formulamaxerror .16078715%, physicalonaxismax8.87456766%, median
inferredg3.44279948. This is a source-resolutioncontrol, not proof of an
asymptotic convergence rate. Nativecode/model discrepancy persists.

check_consolidation.py independently compares all915 OPALXprobeEs values
against rootanalysis/fields.csv: maximumdifference exactly0V/m. Its physical
andnativeformulaerror maxima matchrootmetrics within7.11e-15percentagepoints.
PyORBIT archivechecks include actualNPZ/probeinput/harnesssnapshot hashes,
commonphysicalparameters, completeprobeIDs andpointgeometry, finite fields
andenergykicks, exactGeV-toV/m conversion, androunduniformanalyticradialfactor.
Exactold/newharnesssnapshots areinpyorbit/harness-snapshots withhashfilenames;
the newversiononlyaddsactualnativeweight/countallreducechecks. Those added
checksareverifiedwhenmanifestfieldspresent. Allcompletedcasespass.

MPI1vs2PyORBIT512x512x128comparison over all183probes givesmaximumEsdifference
1.5279511e-10V/m =1.4387042e-14ofcharacteristicfield. Actualsourcechargeand
countauditedrepeatalsomatchesbaseline. Rootconsolidation formula/acceptance
reviewfoundnomaterialerror. NewrunCSVcoverage isrecordedperevidencecase;
reruncheck_consolidation.pyafterrootrefreshesfields.csvandbeforearchiving.

Scientificreportreviewnotes senttoparent: callthislongitudinalpartofORBIT's
triangularbenchmark(no tune-shiftor1mdrifttrackingvalidation); labelaxis-local
versusradialcharacteristic-scalepercentage normalizations; distinguishmesh,
sourcequadratureandboundaryfitcontrols; nofullyasymptoticconvergenceclaim.
