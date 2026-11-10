# Precomputed FFT2D5 geometry/projection reuse — completed locally

User requested one preparation call if possible, no new solver classes/files, detailed Doxygen, preservation of current executable, build ONLY ~/git/opalx/build-omp, same100step pilot results/runtime comparison, NO16turns. No new commit/push authorized or performed.

Base HEAD40856f1a28246fb8d137864ca7541f2aede71a7b. Local implementation changes ONLY3existing solverfiles FFT2D5Algorithm.h/.hpp/.cpp, existingTestFFT2D5Algorithm.cpp andunit_tests/SpaceCharge/README.md. UnrelatedFFA/workflow/rootREADME/.gitignore/tools changes hash-verified unchanged. No new untracked solver/testsourcefiles. Diff whitespace reviewed/clean; changedlines clang-format21 applied.

Implementation:
- Private methodpreparePathGeometryAndProjections(context) atAlgorithm.cpp104, headerDoxygen~565/declaration622; calledonce fromdoRunSolver.
- One small sequential geometry kernel followed by one projection kernel peractivecontainer. For2606segments: direction3doubles,lengthSquared,length,prefixS =48bytes/segment. Keepolddivisionratherthanmultiplyinverse; sameglobalnearestscanorder,strictfirsttie,clamp,degeneratezeroskip,basisn=(0,1,0). PrefixSpre-sum changesfloatingassociation documented.
- Per-container projectedlocalcoordinates3doubles +nearestsegment size_t =32bytes/particle. Geometry+100kcachepayload3325088bytes~3.17MiB. Sharedread-onlyviews, reusedallocations, allactiveentriesrecomputed EVERYcompleteforcesolve; resizeifNchanges. Inactivecontainersretained. No N*Mmatrix.
- Coverage/scatter/gather usepreparedviews throughEXISTINGfunctors and converter. Standalone internal diagnostic stages defaultuncached; explicitper-callbool in fullpipeline avoidsstaleglobalactiveflag afterexceptions. Momentum notcached; diagnosticsprojectcurrentP. Productionframes/restorationunchanged. No field model, timestep,SCcadence,grid,domain/MPIpolicy change.

Executables:
- Original4fd718db8dea11088409158506cd61761eb35f7a0e6a15638fba235c433ba0eb preservedbyte-for-byte build-omp/previous/opalx-4fd718db8dea, notexecutedfromarchive. FreshbaselinewasrunBEFORErebuild throughbuild-omp/src/opalx.
- Currentoptimized build-omp/src/opalx SHAa38391aa99db0cf5e6813ca96bd03dac68246e6ad1b4c204857df314edc261a3.
- Current3sourcefilediffSHA7d07d871ddfa6b6745e42b2e8a4e936208d962cee3c10af8304532af2cc685bc. build-final.json recordsidentities. NoSRCeditsafterbenchmarkstart; onlyunitREADMEwordingclarified.

Validation:
- Normal configuration/algorithm/numerics CTesttargetspassOMP1 andOMP4 (tests-final.json,ctest-final-omp*.log).
- ExistingMPI2unsupported-rankrejectiontestpassesbothranks (mpi2-rejection.log;approvedtoolMPIlaunchoutsidesandboxCPUtopologyrestriction). DistributedFFT2D5stillunsupported.
- NewtestPreparedProjectionsMatchUncachedStagesAfterSourceChanges inexistingalgorithmtest: cachedcompletepipelinevsuncachedoriginalstages, independentnonaliasmirrors,fullrho+allE/Bcomponents. Nonuniformclosedgeometricpath,zerolengthsegment,corner,seamprobes,bothboundarymodes,invalidparticle,N8->12->16->20,reordering,momentumchanges. Tight1e-12scaledfield/densitycomparisons;notolerancerelaxed. Existingframe/inactive/exceptionchecksalsopass.
- Doxygen generatedXMLforprivatefunction,detailed3456characters,0warnings. Doxyfile/output/logintaskfolder;documentedframes/formulas/lifetime/complexity/rounding. GPU executionnotchecked.

Identical100steppilot inputSHAf6692da8991aadf01282f7811183427c78e649ac5266c3b11bb5ecf813185f38;checkpointSHA4d6adf38da35d9168f9cdb10847786eb1ea64d27e13e521211173901037e19f5. 100kmatchedKV,5.602212nCfullDBAring,64x64x512,3ps,OMP4,MPI1,ORIGINALtransverseSC/longitudinalNONE/MIDPOINT. PARFFT flagsFALSE.
- Freshoriginalbaseline73.6520418s.
- Optimizedunprofiled1=54.8504818s(1.3428x,25.53%less),2=50.7792873s(1.4504x,31.06%less). Mean52.8148846s(~28.29%less).
- Separateoptimizedkernelprofile52.425112s, sameexistingread-onlyprofilerlibrarySHAasoldprofile,0callbackerrors/0pending.
- Max overall labendpointdifferenceR4.892e-13m,P1.801e-12beta-gamma;maxPdifference0.003347%ofreferenceSCimpulsescale. All100kIDs/count/charge/finitearrays/final300ps/globalstep99audited. All10statRMS/emitrowsmaxrelativedifference1.744e-14.
- Exactprofile100callsgeometry0.001266s,100callsprojections11.298414s,scatter0.114111s,gather0.072407s. Combined11.4862s vsoldscatter+gather33.07547s =>~65.27%lesshotpathcost.512slicePoissonsolvesperstepunchanged. RemainingFFTcoststilldominant; no16turnfeasibilityclaim(stillweeks).

Raw /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-projection-cache; run_dba_projection_cache_pilot.py,analyze_dba_projection_cache.py,plot_dba_projection_cache.py,archive_dba_projection_cache.py inparent. Allbaseline/optimized-1/optimized-2/optimized-profile100stepprocessesfinished (sequentialrunner session24622 completed). No furthernativejobrunning.

Curated /Users/adelmann/git/opalx-documents/examples/2026/2d5-1/dba-projection-cache-2026-11-04:29catalogedassets,source/testpatch,build/test/Doxygenrecords,manifests/logs,input,CSV/JSON,reproscripts,PNG/PDF. All29hashes+Pythonparsechecked,plotvisuallyinspected,manifestwhitespaceclean. Repo-widevalidatorfailsONLYpreexistinguncatalogedmovie movies/2026-10-30-mue4_analytical-trails.mp4; untouched.

Next: report implementedlocaloptimization, detailedDoxygenlink, runtime25-31%reduction, preservedresults, originalexe location/newSHA. No commit/push/PRupdate or16turnrun inthis task.

## Retiming follow-up
Optimization committed locally as 01bb3835a; no remote push. User requested fresh profiling of same100step pilot, no source changes or16turnruns. Running unprofiled and kernel-profile repeats in dba-projection-cache-retiming with current build-omp executable.

Retiming completed: unprofiled51.0958s,kernel52.3190s,sampled54.5327s. Main-thread samplesFFT48.63%+interface18.79%,projection22.77%;workerwait76.19%. Exactkernelprojection11.214s,FFTpack6.503s. Endpointauditspass100kID/charge/time/finite withmaxdeltaR3.91e-13m/P7.82e-13. Report+scripts at /Users/adelmann/git/opalx-documents/examples/2026/2d5-1/dba-projection-cache-retiming-2026-11-04. No source edits/rebuild/push or16turnrun. Next recommended benchmarkoptimizedCPUFFTbackend,thenexactspatialprojectionsearch.
