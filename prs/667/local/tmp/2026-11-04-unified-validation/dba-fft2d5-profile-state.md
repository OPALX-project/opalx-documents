# FFT2D5 profiling — completed, 2026-11-04

Goal: profile the same bounded DBA space-charge pilot in ~/git/opalx/build-omp; no16turnruns.

Frozen executable /Users/adelmann/git/opalx/build-omp/src/opalx, SHA4fd718db8dea11088409158506cd61761eb35f7a0e6a15638fba235c433ba0eb. Source patch SHA885e59c8a4fe5c3751b0077db53051f7467667af1a4d0fee77b799b68ef6764a verified unchanged. No OPALX source/buildconfig/executable changes. Only read-only Kokkos Tools profiling plugin compiled at build-omp/profiling/fft2d5/kernel_timer.cpp ->libkernel_timer.dylib usingcurrentKokkosCinterface. No addedfences orarraymutations.

Setup EXACT input copy from unified-current/dba-sc-feasibility/omp4-100steps/case.in, SHA f6692da8991aadf01282f7811183427c78e649ac5266c3b11bb5ecf813185f38; sameinitialcheckpointSHA4d6adf38da35d9168f9cdb10847786eb1ea64d27e13e521211173901037e19f5.100steps,100kfull-ringmatchedKV5.602nC,64x64x512,3ps,OMP4,MPI1,ORIGINALtransverseSC,PIPEMODE NONE,MIDPOINT. No16turnrun.

Measurements:
- Callbackpilot100steps73.7917s (native main73.4608); baseline75.4243s. SeparateCPU-sampled100steppilot75.7119s. ~2%spread means no resolvedoverhead; doNOTclaimnegativeprofiler overhead.
- Callback plugin reports0errors,0pending; synchronousOpenMP blockingwalltimes, nestedcallbackexclusive accounting.
- Deposition includingprojection100calls16.59296s;gather100calls16.48251s. Combined33.07547s (~45%wholeprocess/~46%steadystate).
- FFTpacking/unpacking409612calls combined6.61334s (~9%wall). FFT_toTemp andFFT_fromTemp204806callseach.
- Othercallbacks8.07266s; outsidecallbacks25.69934s (includeshostFFTmath ANDstartup/host; cannotlabelallFFT).
- 20s macOSsample,requested1msinterval,16467main-thread samples; nonoverlappingtree-leaf classification: referenceprojection46.3837%;heFFTestockmath/reshapes33.8131%;otherPoisson/FFTinterface12.8560%;remaining6.9472%. ThetwoPoissonparts sum46.6691%, comparableprojection. Sampleexcludesstartup; doNOTaddpercentages tocallbacktimes.
-3OpenMPworkers: projection46.36%;runtime/wait/unclassified52.89%;no stockFFTmathsamples. MainthreadexecutesstockFFTs; slice loopserial withreusedworkspace.

Code findings:
1. FFT2D5Algorithm.hpp:384 convertToFrenetSerret scansall2606reference segments atline396;prefixarclengthloopline421. Calledperparticlebothscatter/gather: ~521millionnearestsegmentchecks perstep plusprefixsums. Samplingdoesnotseparatethe2internal loops.
2. hpp:564 loops512occupiedslices serially;51200coupling/copycalls100steps. GreenFunctiongenerationonce: workspace/planreuse alreadyworks.16turnsat3pswouldrequire~3.2billion2D slice solves.
3. FFT2D5Poisson.cpp:123 forward/backwardtransforms useheFFTestockbackend,confirmedruntimefunctionsstock_fft_executor_r2c,plan_stock_fft,pow2_FFT_helper. Heffte_ENABLE_FFTW/MKL OFF inCMake/generatedheader; Traits.h selectsstockfallback. Packing~4096smallkernels/step.

Recommendedfutureoptimizations (NOTimplemented): precompute segmentgeometry/inverse-length/cumulative-s;reuseparticleprojection betweenscatter/gatherWITHINoneforcecall(R/Punchanged);exactacceleratednearestlookupwithglobalfallback/periodicseam/tiepreservation;benchmarkoptimizedCPUFFTbackend/batchedindependent2Dslices/reducepacking. EliminatingprojectionentirelycapsAmdahlspeedup~1.9x,soadditionalworkneededforlaptopfeasibility. Anyfieldcadence/timestepchange requiresseparateconvergencetests. No numericaltolerancechanged.

Validation:
Bothprofiledpilots nativeexit0,100steps,all100000IDs/count,correctcharge,finitearrays,final300ps/globalstep99. Labendpointdifferences vsunprofiledbaseline:kernelmaxR3.54e-13m,maxP1.141e-12betagamma;samplemaxR3.48e-13m,maxP7.79e-13. BothfarbelowQA1e-9m/1e-10momentum andphysicsgoal. Input/checkpoint/binaryhashesmatch. Allstudyprocessesfinished.
Macsample initiallysandboxdeniedinspection; approvedread-onlytool escalationattachedONLYtaskPID35946 for20s. No unrelatedprocessinspected/stopped.

Raw /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-fft2d5-profile; runner/analyzer/plot/archive scripts inparent. kernel/kernel-timings.csv, sample/cpu-sample.txt,main-thread-sample-summary.csv,openmp-worker-sample-summary.csv,summary.json,endpoint-audit.json.
Curated /Users/adelmann/git/opalx-documents/examples/2026/2d5-1/dba-fft2d5-profile-2026-11-04:21catalogedassets inclPNG/PDF,rawprofile,CSV/JSON,logs,input/manifests,pluginCPP,compilecommand,backendflags,scripts/readme. All21hashesandPythonparsechecked,plotvisuallyinspected,manifestdiffwhitespaceclean. Repo-widevalidatorfailsONLY preexistinguncatalogedmovie movies/2026-10-30-mue4_analytical-trails.mp4;untouched.

No16turncampaign,solveroptimization,commit,pushorPRupdate. Next:reportprofileandawaituserdirection.
