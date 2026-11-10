# Triangular bunch conducting-pipe benchmark

User authorized native OPALX and PyORBIT reproduction, analytic comparison,
and integration in the existing LaTeX report. No push requested.

Common case follows PyORBIT example: full length10m, circular beam radius5mm,
pipe radius20mm,400MeV protons,Nreal1e14,1m equivalent frozen kick.
Shared deterministic equal-charge tensor source and target probes are generated
by prepare_common.py. OPALX uses one1e-20s field readout and source/probe
companion subtraction; PyORBIT native direct kicks use zero-weight probes.
No self-consistent tracking claim and no production solver edits planned.

Owners: root common source/OPALX/analysis; triangle_pyorbit native build/runs;
triangle_model_audit independent equations; triangle_opalx_audit evidencecheck.

Critical predicted discrepancy: OPALX CIRCULAR uses full numerical meshwidth
as radius inside logarithm and .67 profile coefficient. There is no native
transverse wall. Primary width20mm gives effectiveb20mm,g3.442589 vs rounduniform
onaxis3.772589, expected-8.7473%; diskaverage3.272589,+5.1948%.
The open numerical grid need not reach the physical wall for this centred
roundsource (image transverseforcezero inlocalmodel). A secondary width40mm
case givesg4.828883,+28.00%axis; labelthisextent/gcoupling explicitly rather
thanasserta proveddiameterbug. No coefficient or parameter fitting.

## Native work completed

Six nativeOPALX main/probe pairs (12snapshots),16PyORBIT configurations and
the unchanged upstreamexample allcompleted. No production solver edits.
Independentnativeandconsolidationaudits passed. OPALXbinarye85bc091...e70bf
unchanged; PyORBITsourceclean at28df66018 withlibrary/build/sourcehashes.
MPI1/2Pyfields agree<1.6e-10V/m; OPALXrank2 intentionalguard exercised.

Finalanalysis files: fields.csv,summary.csv,controls.csv,integrity.json,
selection.json,source-quadrature.json. Rootanalysis includesall22caseIDs.
Acceptancefixed62axispoints1<=|s|<=4m and82radialpointsats=+/-2.5m.
IndependentanalyticGauss/potential/charge checks passed to2.1e-13relative.

SelectedfineOPALXsource16384: maxphysicalaxis8.874568%,radial24.200713%,
butmaxnativeformulaerror.160787%; exactnativeaxisbias-8.747309%.
Matched128->256 dense-sourcemeshchange.125280%ofEaxis.
SelectedPySlice512²128ZwithNr32/Nphi64: maxphysicalaxis/radial.286050%.
Lasttransmeshchange.338352%,crosssourcechange.283849%ofEaxis.
Independentquiet-ringquadpredicts-.286004%(Nr32),-.569851%(Nr16),matching
thefieldoffset. DenseNs65536 resolveslongitudinalNGPsourcealias; exploratory
100%fine-gridfieldpointdeficits withNs8192are retained,notphysicsclaims.
SelectedPyBaartman128²256Z/Ns65536: maxphysicalaxis/radial.006603%.
Boundaryresolutionchange<6.8e-7V/m; nativeweights/N/probezeros checked.

Reportownertriangle_model_audit ranNEWPDFeditmarkerEXACTLYONCE beforefirst
authoring; doNOTrepeatmarkerforthisoperation. Itownstwo-pageSection13,
offlineCSV/JSON/sourcearchive,figures,compilation,visualQAandupdatedsourceZIP.
Rootmustscientificallyreviewlatesttext/figures andverifyfinalPDF/ZIP.
Existing unrelated worktreechangespreserved. No commit or push authorized.
