# Unified-version validation — active 2026-11-04

LATEST USER OVERRIDES ALL EARLIER EXECUTABLE SELECTION: only build~/git/opalx andonlyrun~/git/opalx/build-omp/src/opalx. Neverexecute archivedbinariesagain. Keepcurrentbranchcodex/fft2d5-explicit-original-model(HEADccfdc1055) andnon-srcdirtychanges.

Orderedgoal:redoOPALXPR667benchmarks(100stepZeroSC+10pCbend,original1,048,576particles/512³,configunitOMP1/4);redoDBAbaretunesandoptimizetimestep(~1%tunechangeacceptable),showbestdt/tunes/shifts;onlythenstart5.602212/12.268262nCDBAfullcoastingKVSC64x64x512/100k.

build.pyconfigures/buildsexclusivelybuild-omp;oldexebackupinsidebuild-omp/previousneverexecuted. SupplementaldeferredCMakeconfigtesttargetusesHEADcommittedtestsourceintmpbecausepreservednon-srctestsreferenceexcludedexperimentalAPIs. Nooverwritinglocaltests.

Knownissuesfrompreviouswork:currentPRsrc lackscommittedfd6frame/workspacefixes(solverparticlesmovingframe vsfixedlabpath;currentchargedbendfailsafter~4m). Needtest/fixnecessarycurrentbranchissuesbeforePRacceptance,recordanynumericalsourcechangesandrerunallunderonefinalbuild. Do NOT restoreexperimental3D/curvatureoperators wholesale.
FullcoastingDBAarchivedpilot(noncurrent,nowobsolete) initializedreferenceatcentroid(-4.2,0,0),P~0;existingrestartschemafixedinitialreferencebutspuriousapertureloss34144/100kfirststep. CurrentcodehasexplicitfileBEAMmomentumdirectionoverridebutreferencepositionstillmean;fullringtestneedsproperindependentrefandnearest-elementaperturehandling. No sourceeditsyet.
PriorPyORBITq5.60216turnrunendedAssertionErrorphasejump>.4;DO NOTpublishasvalidtunes. run_pyorbit.py/sources/logsunderdba-lattice/comparison-20261104/charged-kv. SecondPycasenotstarted. Noactiveoldnativeprocesses. Preservefiles,historicalrundata;doNOT resumeoutdatedSCrunsbeforeunifiedpreflight.

Artifacts belong opalx-documents/examples/2026/2d5-1 and/or dba-lattice,notopalx/docs. No pushrequested. Maintain source/exe/inputhashes forEVERYnewrun.

## Build frozen andPR repeats active
- BaselineHEADccfdsource frame tests(fromcommittedfd6) failedbothLabPathFieldsSurviveReferenceFrameChanges andActiveContainersShareLabPathAcrossReferencePoses.
- Restored8src/SpaceCharge/FFT2D5files fromfd6committedfixes only:framepathconsistency,cell-integratedGreen/halo,shared2DFFTworkspace+empty-sliceoptimization. NoexperimentalFiniteSource/3D/curvature. Originalsbackupbefore-frame-restoration;sourcepatchsaved.
- BuiltONLY~/git/opalx/build-omp. FinalbinarySHA4fd718db8dea11088409158506cd61761eb35f7a0e6a15638fba235c433ba0eb;sourcepatchSHA885e59c8a4fe5c3751b0077db53051f7467667af1a4d0fee77b799b68ef6764a;validated-build.json.
- TestsOMP1and4:17config,8frame,66numerics passed;oneexpectedmultiple-ranktestskippedonsinglerank. Explicitmpiexec2 Configuration_MultipleRanksRejected passed onbothranks.
- FoundexistingDELETEONTRANSVERSEEXIT=FALSE input attribute:aperturelossdisabledWITHOUTchangingfieldapertures,consistentunboundedanalyticKV;avoidsneedforaperturecodefixinbenchmark. Nativefullringreferencecanbeinitializedthroughcheckpointwithcorrectdesignpose;mustregenerateseedwithCURRENTbinary,noarchivedexe/checkpointreuse.
- PRredo script ~/git/dba-lattice/comparison-20261104/unified-current/run_pr_bend.py usesONLYcurrentbinary andexactoriginalPRinputs/sources. SequentialZeroSCand10pC100steps1,048,576particles,charged512³. Toolsession97738active. Everycaseassertsexehashbeforestart;manifestprovenance. Do NOTrebuildoverwritebinarywhilerunning.
- AfterPRrepeats:DBAZEROSCfixed-step scanonordinaryrestartpathmatchingFFT2D5SCpath,notthezeroSC-onlyboundarycontroller125pscap. ProposedDT125,250,500,1000,2000,4000,8000ps,16turns,69localizedKV/probes. SelectlargestDTwith≤1%analyticandfinersteptunechanges andfirst/secondhalfdriftbounded;showtable. Fullcoasting100kZeroSCpreflightatselectedDT(withDELETEONTRANSVERSEEXITFALSE)mustpassbeforetwoSCchargesstart.
- OlderPyORBITcoastingtrialendedphaseunwrapassertion after16turns;invalidtunes,noproductionsummary. Stopoldworkflowuntilunifiedpreflightcomplete. Nootheroldnativeprocesses.

## Latest user steering: show EXACT PR plots before further simulations
- User: "show me the very same plots that are on the PR. If something is missing you do not yet repeat the simulation".
- QueriedPR667body;bothpublishedplotURLspointopalx-documents commit691d1480bcb27275b8d6b913dd77851f498cb47b examples/2026/2d5-1/{rms,emittance}.png. Verifiedlocalfilesbyteidenticalvia gitshow691d148: RMS SHAea9453b69b833c990d2236af099bdc5810b7556851f9174c6589fd5b0164c24e;emittanceSHAc07b9d9568fc7b73273d2c87438f8ad6f1362d0020dbb318d8f36ea143b8310d. Bothpresent,norecreationneeded.
- Tolduser nofurthernew simulationswillstart. Existingcurrent-buildPR100step10pCrepeat(session97738)alreadyrunning,step56whenchecked. Do NOTlaunchDBAtimesteporSCcaseswhileuserreviewspublishedplots. Noexplicitrequesttokillcurrentrepeat;itcontinuesandwritesmanifestoncompletionautomatically.
- PRZeroSCrepeatcompletedbefore10pCstarted. Unit/config/frame/numerics alreadypassunderfrozen4fd... currentbuild. Atchargedstep41,millionIDsand10pCpresent;RMS radial/verticalmatchedpublished to~1e-9relative(prog-auditJSON).
- New scripts under~/git/dba-lattice/comparison-20261104/unified-current:run_pr_bend.py(active),analyze_pr_bend.py(ready),run_dba_timestep_scan.py(preparedbutNOTstarted),analyze_dba_timesteps.py(preparedbutNOTstarted). Scanplanned69KV/probes,16turns,ordinaryfixedrestartpath;DT125..8000ps;selectlargest≤1%errorsandhalf-drift. Needuserreviewgatebeforelaunching.
- Pendinguser-scopedobjective afterreview:finishPRredoanalysis,DBAtimestepoptimization/table,fullcoastingZeroSCpreflight(deleteapertureFALSE,inputcheckpointcurrentbuild),thenSTART(notnecessarilyfinish)twochargedfullringruns. AllnewOPALXexecutionONLY~/git/opalx/build-omp/src/opalx,neverarchivedexecutables.

## CURRENT USER TASK COMPLETE — HOLD DBA
- Userauthorizedfinishcurrent-buildrepeatandshowmatchingPRplotsoverlaid;explicitDO NOT START DBA.
- ExistingPRrepeat(session97738)finished0:ZeroSC7.8927395s;10pC1268.0236102s(21min8s). BothONLYcurrent~/git/opalx/build-omp/src/opalx,SHA4fd718db...,branchccfdc1055+sourcepatch885e59c...;filehashverifiedafterruns.
- analyze_pr_bend.py checkedall200nativeframes:1,048,576persistentIDs,10pCnominalQ,time100fixedsteps,finiteR/P. Generatedcurrent/nativeCSV/audit.
- plot_pr_overlay.py reproducesthePR's2×3RMS/emittancelayout andall3publishedcurvesplusanalyticcommon-time/stationreferences;newcurrentblackdiamonds. OnlyZeroSClongitudinalemittancetoprightlog. PublishedrootPNGfilesunchangedbyteidentical691d148.
- LargestRMSdifferencevspublishedlocalOPALX1.597965e-7percent;largestchargedemittancedifference5.974464e-7percent(<1e-8relative). ZeroSCs–Eemittancecurrent2.153459e-12m eVvspublished1.799438e-12m eV,roundoffonly.
- Curatedresults/scripts/inputs/manifests/sourcepatch/tests metadata/PNG/PDFin ~/git/opalx-documents/examples/2026/2d5-1/current-build-repeat-2026-11-04. Table current-vs-published.csv;summary.json. BothportableoverlayPNG replaysbyte-identicalin/tmp;visualinspectionpassed;exeSHA/sourceanddocdiffchecks pass. Docvalidatoronlypreexistinguncatalogedmovieerror afterremovingtaskgeneratedrootpycache.
- No newDBAtimestep/fullring/chargedrunsstarted;preparedDBAscriptsremainunexecuted. No nativeprocessesfromcurrenttaskremain. NOcommit/pushrequested/performed. WaitforuserbeforeresumingearlierDBAgoal.


## Completed DBA ZeroSC timestep study
See DBA-TIMESTEP-STATE.md for complete results. Largest tested full-record ~1% step4ps; stricter half-record stability selects3ps. Final scans OMP1 using unchanged build-omp SHA4fd718db8dea. Fullring96particle4ps check passes full-record analytic tune band. Artifacts in opalx-documents/examples/2026/2d5-1/dba-zerosc-timesteps-2026-11-04. All jobs finished; NO SC runs, commits or pushes.


## Completed bounded DBA space-charge feasibility pilot
User authorizedpilot afterZeroSCstudy.100steps at3ps,100k,64x64x512,5.602nC,ORIGINAL transverseSC, currentbuildSHA4fd718db8dea. OMP4=.736s/step →~54days/16turns (40days at4ps);notpractical. OMP1=1.66s/step. ZeroSCcontrol=.031s/step. AllIDs/charge/finite/endtimeaudited;nonzeroSCconfirmed. No16turncampaign started. SeeDBA-SC-PILOT-STATE.md andopalx-documents/examples/2026/2d5-1/dba-sc-feasibility-2026-11-04. No sourcechanges/builds/commits/pushes.


## Completed FFT2D5 profiling
Unchanged build-ompSHA4fd718db8dea, exact100step4OMPpilot. Referenceprojection~46%steadytime;stockFFTmath~34%;otherPoisson/FFTinterface~13%;rest~7%. Kokkosblockingwall:scatter16.59s,gather16.48s,packing6.61s/100steps;totalcallbackrun73.8s vs75.4sbaseline. Profiledendpointsagreebaselinewithin1.2e-12beta-gamma. NoOPALXsource/exechanges,onlyread-onlyprofilercompiledbuild-omp/profiling/fft2d5. FullresultsDBA-FFT2D5-PROFILE-STATE.md andopalx-documents/examples/2026/2d5-1/dba-fft2d5-profile-2026-11-04. NO16turnruns. Optimizationproposalsnotimplemented.


## Published core fixes — current branch HEAD
Userauthorizedcommit/push. Commit40856f1a28246fb8d137864ca7541f2aede71a7b pushed toc odex/fft2d5-explicit-original-model (branchspelling: codex/fft2d5-explicit-original-model). PR667updatedscope/title/body andverifiedremotehead. Eightvalidatedsrcfilesplusmatchingnormalunittests+README committed;src/SpaceChargetestsclean. Experimentaltestspreservedtmp/2026-11-04-fft2d5-pr-fixes/preserved-experimental-tests;unrelatedlocalsuntouched. NormalCTests config/algorithm/numerics passOMP1/4;MPI2rejectionpass. Build-ompbenchmarkexeUNCHANGEDSHA4fd718db8dea. PublicCI CSCSjobs pending; noGPUclaim. NoSCcampaign/optimization. SeeTASK-STATE.md inpr-fixesfolderforcompletepublicationprovenance.


## PARFFTZ/four-rank probe
UserrequestedinputflagTRUEand4MPIsmallpilot. Tried4MPIx1OMP and1MPIx4OMP onunchanged4fdexe. BothrejectedBEFOREtracking:singleMPIrankonly /PARFFTflagsmustFALSE.0steps,noH5,no newdecomposition/resultcomparison. Source/layoutchecksconfirmserialimplementation; no guardbypassorMPIfeatureimplemented. EvidenceDBA-PARALLEL-Z-PROBE-STATE.md andopalx-documents/examples/2026/2d5-1/dba-parallel-z-probe-2026-11-04. No16turnruns.


## Local geometry/projection cache implemented and benchmarked
Userrequestedonepreparationfunction/no newsolverclasses/files. Algorithm.h/.hpp/.cpp+existingunitfile/README modifiedlocally onHEAD40856f1a2;uncommitted. Originalexe4fdpreservedbuild-omp/previous/opalx-4fd718db8dea; currentbuild-omp/src/opalx optimizedSHAa38391aa99db. Geometry48B/segment+projection32B/particle preparedonceperforcesolve;defaultstandalonediagnosticsuncached. DetailedDoxygen0warnings. NormalCTestsOMP1/4+MPI2rejectionpass. Identical100steppilotbaseline73.65s,optimized54.85/50.78s (~25-31%less). EndpointsmaxR4.9e-13m,maxP1.81e-12betagamma;RMS/emitrel<1.75e-14. Profilehotpath33.08->11.49s. No16turnruns/commit/push. Fullstate tmp/2026-11-04-fft2d5-projection-cache/TASK-STATE.md;curatedreportopalx-documents/examples/2026/2d5-1/dba-projection-cache-2026-11-04.

2026-11-04 FFTW follow-up complete: FFTW3.3.11 installed~/git/fftw;build-ompReleaseHeffte_ENABLE_FFTW=ON;currentexeSHA9b4a00eae1cd121dbcb00dfed6cdd46c1f34f7131f597e72973a56686f77a2c2;stocka383preservedbuild-omp/previous/opalx-a38391aa99db-stock.4CTestsOMP1/4+MPI2rejection+FFTWmakecheckpass.100steppilot32.711s vs51.096sstock,numericalQApass. No source edits/push/16turnruns. See tmp/2026-11-04-fftw-release/TASK-STATE.md and documents dba-fftw-release-2026-11-04.

FFTWprofilecomplete:kernel32.13s;projection10.86s (34%),FFTcopies6.50s (20%),otherkernels8.04s,hostresidual6.50s. CPUFFTarithmetic14%,projection37%. QApass. See tmp/2026-11-04-fftw-profile/TASK-STATE.md anddocumentsdba-fftw-profile-2026-11-04. No source/rebuild/push/16turnruns.

Exactnearestsegmenthierarchycomplete,uncommitted4files. Currentbuild-ompReleaseFFTWexed2c0add433c40f47557d354323093f1d3949835defff5945bcb7337e7223f4d1;old9b4preservedprevious/opalx-9b4a00eae1cd-exhaustive. 100steppilot21.27–21.81s vs32.71s,projection27.4xfaster;exactsearchoracle43540entriespass,trackingroundoffQApass. CTestOMP1/4,MPI2reject,Doxygenpass. See tmp/2026-11-04-fft2d5-exact-search/TASK-STATE.md anddocumentsdba-exact-search-2026-11-04. No16turnruns/push.

Optimizationpublicationcomplete:OPALX a1ad007c8 (+priorcache01bb) pushedPR667;documentsce71b01pushedbenchmarkarchive. PRdescription+newplotsupdatedverified. Evidencepublished examples/2026/2d5-1/dba-solver-performance-2026-11-04. Unrelatedworkpreserved. Next assessbatchingFFT;userexplicitlyNOIPPLchangesyet. No16turnruns.

OPALX-onlybatchingcompleteduncommitted11files,CLI--2D5BatchSizepositiveinteger/defaultserial. Currentbuild-ompReleaseFFTWexe4d627521ac4f...;priorseriald2c0addpreservedprevious/opalx-d2c0add433c4-serial-slices. Same100steppilotserial21.38s,B1~12.92s,B8/B32~11.02s,B64~11.43s. Recommend8memorylower,allQApass1e-14stat. ExistingIPPLunchanged,hostonly1MPI,CLI/testsOMP1/4/MPIreject/Doxygenpass. See tmp/2026-11-04-fft2d5-batching/TASK-STATE.md anddocumentsdba-fftw-batching-2026-11-04. No16turnruns/commit/push.

Batchingpublicationdone:OPALXa28af0417/documentsf2f0cbc pushedandPR667updatedlatestplots.16OMPpilot~12.38svs4OMP11.02s,keep4. One-turnestimate10–12h(3ps,batch8). FFTWthreadcapabilityconfirmedbutproductionplansdefault1;noactivationyet,canbeOPALX-onlyfuturechange. No16turnruns. Currentexe4d627521...unchanged;unrelatedworkpreserved. See batchingTASK-STATE.

FINAL: All user-requested phases complete sequentially, no native run remains. Frozen Release91a50ddc25ed... exe unchanged; previous4d627... preserved. FFTW CLI implemented OPALXonly, testsOMP1/4+17CLI+MPI2rejectionpassed (final targetTestFFT2D5Numerics; initialwrongtargetlaunched0tests, correctedandverifiedactual1/rank). Doxygen0warnings/diffclean/unrelatedhashesunchanged. Threadmeans1/4/16=10.92386/12.97784/22.59820s B8OMP4;15FFTworkerssampleverified.
PRphysicalretention:200snapshotschecked, chargedcurvepeakrel<=1.946e-9; serial/B1/8/32/64pilotpublishedretention<=1.35e-14relative. MainZeroSC7.758s/charged314.609s. NZ2568.378s vs51210.924s, tiny RMS/emitsbutSCmomentum7.1044%RMSdifference,26.59%peak-scaledmax;no1%meshconvergenceclaim.
PyORBIT100stepfullringphasepilot4casescomplete:mean51233.3911s/25632.5163s; nativeSC2.4997/1.3585s,Pythonphasegroup/copy30.319/30.583s,nativebody.0896s. Samephysicalsourceandflight; nativeNGP/TSCvsOPCIC andcommon-svscommontime. Do notinferintrinsiccode-speedratio or tuneaccuracy from driver-heavyshortpilot. Endpointrmsdifference<=4.3e-6%,emit<=1.4e-4%.
Archive134assets ~/git/opalx-documents/examples/2026/2d5-1/fftw-validation-nz256-pyorbit-2026-11-04; datedreadme,PRoverlayplots,threadplot,nz/pyplots/tables,scripts/manifests/logs/sourcepatch; rootmanifestappendedscopedentries,all134SHA/date/lowercase/PDFLFSchecks passed. Fullrepositoryvalidationretainspreexistinguncatalogedfiles/movieissues; checkdocuments-validation.log. No commits,push,PRmutation,IPPL/PyORBITnativeedit or16turnrun. Finaluseransweroutstanding; recommendFFT1B8OMP4, reportNZ256kickdifferenceandPyOrbitdrivercostclearly; linksreadme/PRplots/timingplot.

Follow-up archive final: fftw-validation-nz256-pyorbit-2026-11-04 has134validatedassets, source snapshotsunderanalysis/. Fullcatalogvalidator96preexistingerrorsand0newarchiveerrors. Allrunsfinished; no commit/pushor16turnrun. RecommendB8/FFT1/OMP4, NZ256notestablished1%converged(SCmomentumdiff7.1%RMS).
