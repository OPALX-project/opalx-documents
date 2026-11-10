# Native original2D5 tracking

User locks exactly10steps per geometry, nominal designpath advance1m.
Uniform cold physical rounddisk radius20mm (rawRMS10mm),L5m,Q10pC,
protons beta.001. Root generated shared1,048,576D4 equal-charge particles:
../sources/{straight,bend}-uniform-n1048576.{json,npz,dist}. No probes.
Same source and assignedq for charged and ZeroSC controls; ZeroSC uses
TYPE=NONE, not literalzero macrocharge (old q0 deposition dividesdtby0).

Executable immutable archivede85, branch658 fd6ba8dc5 originalindependent
2D slices and localOPENg6.36. No currentstraightOPEN3D, no build/C++edit.
RUN explicitlySCFIELDUPDATE="MIDPOINT": driftΔt/2, solve, relativisticBoris
kick, driftΔt/2. Δt=3.3356409519815204e-7s, totalT=3.3356409519815204e-6s.
1MPI rank,4OMP; mesh128²z512,xybox48mm. Longitudinalmesh is fixedLAB,
so the bunch advances through itscells; peerPyORBIT must shift relativez
by referenceflightdistance before nativeSC deposition (or shift guards).

Straight path2nodes z=-6..+6m,12m numericalperiod/free transverse space.
H5every10 steps(finalonly), STATevery1. Sharedsourcephysicalhashes pinned;
driver snapshots are underprovenance/. Preparedinputs and initial+10endpoint
moments/final-particleNPZ live in runs/*, selected-straight.json authoritative.

## Straight completed

Root released afterSACR reportextension compiled. Bothnative10step runs
complete/allchecksPASS. ZeroSC2.11s; charge7.40s. ZeroSCeveryfinalparticle
equals initial+(0,0,1m) within1nm, momentumunchanged; RMSx/y10mm.
Charged final RMSx=y≈10.474mm, RMSz1.443397m(initial1.443376m), reference
z=1m. AllSTATcounts/q/times, savedH5IDs/q/finite/frame and11CSVrows pass.
Firstsetup rejectedunquotedSCFIELDUPDATE; rejectedinput/log/manifest are
archived besideZeroSC result; nophysicalstep ran underthatsetup.

## Bend completed after straight comparison

Preparedfullcirclefixedlabreferencepath reusedfromcurvednativebaseline,
chordperiod12.566367358402026m. Uniform+By chosen fromnativeprotonrestmass
and betaγ forsingle-particleR2. EnlargedCartesianfieldmap coversx[-3,.1]m,
y[-.05,.05]m,z[-2.2,2.2]m. H5every1authorizedforbend (10states) tocompute
alltrueexactcircle/Frenetmean/RMS/covariances; STATCartesianmoments alone
are dominatedbycurvature andcannotgive20mmcross-sectionwidths.

Important: native fresh reference starts atWHOLEBUNCHCartesianmean, not
centraldesignparticle: x≈-.481588m,pz≈.000759187. UnderuniformBythis
centroidorbitscentre(-2,0,0)atradius≈1.518m whileeachcoldparticlehasR2.
The10dt schedule corresponds1mcentraldesignadvance; STATreferencearclength
is≈.759m. Phaseatan2(RefRz,RefRx+2)andper-particleexactcircleprojection
providepropercomparisonwithPyORBITcentralreference. Exportglobaland
Frenetobservablesseparately. Straightlocal/globaltransversecoordinatesmatch.

IndependentZeroSCbendcheck usesexactDISCRETEdrift/Boris/driftgeometry:
perstepangle2atan(beta*c*dt/(2R)), orbitradiusR unchanged. Forinitial
theta=s0/R andu, position=(R e_r(theta+angle)+u e_r(theta))-R e_x;
momentum=betaGamma*t(theta+angle). Continuousrotationphase differs by
~1.04e-4rad over10steps. AnalyzerwillassertZeroSCagreementbeforechargedbend.

Root's straightgatepassed: maxRMSdifference.0076253%, transversegrowth
difference.16851%, longitudinalgrowthdifference.10892%. Rootauthorizedbend
ZeroSCfollowedbychargedcase. Bothnative10stepbendrunscomplete/allPASS;
ZeroSC2.16s, charged42.29s. IndependentdiscreteBorisidentitypassesatALL10
endpoints: maximumpositionresidual9.55e-15m,momentum2.82e-18betaGamma.
Chargedrunstartedonlyafterthiscontrolpassed.

FinaltrueFrenetRMS(u,y,s) is approximately(8.776,10.000,1443.384)mm for
ZeroSC and(9.245,10.479,1443.404)mm charged. Actualcentroidphase.499884rad;
the differencefromcentraldesignphase follows theexpectedreferencecentroid
convention. All11CSVrowsmean/RMS/fullFrenetcovariance andglobalmoments
arefinite. All10bendH5states and finalsorted-IDparticleNPZ preserved.
selected-bend.json isauthoritative. Parent/PyORBITagentnotified; no owned
nativeprocess remains. PyORBITcurvedcomparison andpaper belongtoroot.

audit_tracking.py aggregates all4nativecases tocampaign-completion.json
and native-tracking-summary.csv. RelevantPythonfilescompile. No builds,
newphysics, productionedits, steprefinements or extrapolations were made.
