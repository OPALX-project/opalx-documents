# FFT2D5 z parallelism — completed, 2026-11-06

User requested OPEN-based z MPI, no IPPL changes, preserved executables, 100-step pilot CPU1/2/4 and GPU1/2/4. User later explicitly deferred4GPU dueavailability; onlyGPU1/2run. No16-turnruns started. No commit/pushauthorized orperformed.

## Source and binaries
Repo /Users/adelmann/git/opalx, branch codex/fft2d5-explicit-original-model, base8cf0239d0f7b0c65465ccf6fd66272189e46aeca. Changes remainuncommitted. Preserve unrelated FFA/workflow/rootREADME/toolschanges.
CPU build onlybuild-omp; final executable SHA135d999a84df3676913ebb2716d6de06bc0e9cc0a15f8dcc357ba8119feac5aa. Frozenstudycopyopalx.cpu-z-validated. Originalbuild-omp/src/opalx.pre-mpi-z-20261106 SHAd75ea9dda8e438e63182dfa9aec7d0eb0db3fb0ba440f9fb3988aacfee5d8e73.
GPU /psi/home/adelmann/opalx-dev/dba/build/gwendolen-cuda/src/opalx SHAb181efbc6bba421f8e1c8907c0f141080e5fdc84f1c5e78f110390f862536abf. Original .pre-mpi-z-20261106 SHA6bd5c3a499e54c8201ac788e6c036e56d6add6c77b76967e2ce156e937f21d65. Immutableone-turnreferenceunchangedatvalidation-a100-20261105/one-turn-and-bend/opalx.
RemoteSHAofeverychangedsourcefilematcheslocal. IPPLd6216553e39dcf4405849c027517cc3401fefee5 unchanged; Kokkos/heffteclean too. Sourceproofgpu-identity.json. No further code changes afterfinalvalidation.

## Implementation
- PermitPARFFTZonly; requireitforMPI>1; ranks<=Nz.
- 3D field layout ownszslabs; wholetransverseplanes solved using existingheFFTe batchingonMPI_COMM_SELF; no3D/longitudinalFFT orIPPLmodification. MPIdefaultbatch1 ifnoCLIbatch.
- ReuseOPENpc.update migration with boundedtemporary(u,v,s)R. LazyregisteredCartesianRattribute migratesallattributes/IDs exactly; restoreR beforephysics. Disable/restoreparticleBCsduringlogicalmigration topreventIPPLperiodicrulemovingexact0->L. Wrapclosed-endcachedSconsistentwithownership.
- Refreshparticleprojectionsaftermigration,reusepathhierarchy. Existingfieldaccumulate/fillhalos connectslabs/seam; cleartransverseghosts foropen2Dphysics.
- Reduceonlysmallglobal1Dlineprofile fromunaccumulateddeposits beforehalo/xyclearing toretainoriginalCICspillconvention. MPIpotentialdiagnosticcallbackspreserved. MPIprivateGreencached. Backendcountsreducedglobally. Validationreductionsproperexplicitin-placeAPI.
Files:src/PartBunch/ParticleContainer.hpp;src/SpaceCharge/FFT2D5/{FFT2D5Algorithm.cpp,h,hpp,FFT2D5FieldStorage.cpp,h,FFT2D5Poisson.cpp,h};SpaceChargeConfig.cpp,SpaceChargeConfigBuilder.cpp;unit_tests/SpaceCharge/CMakeLists.txt,README.md,TestFFT2D5Numerics.cpp,newTestFFT2D5Parallel.cpp.

## Validation / timings
Same100kmatchedKVDBApilot64x64x512,Q5.602212333965894e-9C,DT3e-12,100steps,ORIGINAL,PIPEMODENONE,CLOSEDRING,batch64, samecheckpointSHA4d6adf38da35d9168f9cdb10847786eb1ea64d27e13e521211173901037e19f5; onlyPARFFTZTRUEinputchange.
CPU1/2/4 meanmain-minusOrbThreader16.231960/9.174905/5.421395s (two repeats). GPU1/2 means8.585350/6.622500s(two repeats), speedup1.296391. GPUendtoend51.229952/50.131853s becauseOrbitThreader~39s. CPUwall18.350419/11.111425/7.883636s.
Allacceptedruns100kuniquepersistentIDs/fullQ/finite/time3e-10/step99pass. MaxRMS/emittance relativeerror1.047651957e-12 vs preservedCPU; maxparticleRdiff4.86755e-12m. GPUnativevsGPUoriginalstaterror<=8.26235e-13.
IndependentMPIunit comparesdirectdiscretelog-Greenconvolution,all3particleE/B,gradlambda;open/closed,bothzshapes,seam/slabinterfaces,exact0/L,emptyranks,repeatedmigration,restoration. PASSCPU1/2/4ranks andGPU1/2 actualranks. ExistingAlgorithm11/Numerics67/Config17tests passGPU1andCPUOMP1/4. No tolerancechanges. Diffreviewedandgitdiff--checkpasses.

## GPU launcher / jobs (important)
SlurmdefaultMPI=pmi2; noPMIxplugin. Default srun withOpenMPI5 launchedindependentsingletons at2GPUs; invalidmeasurementsdiscarded. No solverfixwasbasedonthatfailure. Oldinvalid2GPUrunsremote discarded-singleton-launch. ProperOpenMPI mpirun -npN --map-byslot --bind-tonone withgpu_rank.sh oneCUDAvisibledeviceperOMPIlocalrank. mpi_gpu_probe independentlyassertsworld=N,onevisibleGPUperrank,distinctphysicalUUIDs beforetests. OPALXlogalsoassertsTimings{0}> forN>1. Currenthelper scripts inprovenance.
ValidGPUjobs3550282GPU and3550291GPU bothCOMPLETED0:0; actualUUID/worldverifiedlogs. PreservedGPUbaseline3550211GPUvalid (singletonsarecorrectforN1). FourGPUjobs355023/355027canceledatuserrequest; noneactive. Manyearlierownbuildjobsoldversionscanceled/staleobjectlinkfixedbytouchrecompileafterarchivecopy; finalsourcesverifiedhashes. Currentcorecodeunchangedsincereviewedbuild.

## Artifacts / final response
Localstudy /Users/adelmann/git/opalx/tmp/2026-11-06-fft2d5-mpi-z. FinalCPUdirsfinal-cpu-ranks-N-repeat-R; GPUdirsgpu-ranks-N-repeat-R,gpu-preserved. Earlierdevelopment/pre-portabilitydirsnotfinal. Finalanalysislogfinal-analysis.log. analyze.pyreproducible (~/.venv-h6),comparebyIDsandSDDSstats.
Report/artifacts /Users/adelmann/git/opalx-documents/examples/2026/2d5-1/fft2d5-mpi-z-2026-11-06:README.md,timing.png/pdf,rms-emittance.png/pdf,differences.png/pdf,summary/timings/series/comparison/particle-audit/gpu-vs-preserved.csv,provenanceinputs/logs/identities/sourcepatch/newtest/helpers. Zeroaxesinrmsplots; normalizeddifferencesseparate. Figures visuallyQA'd. They useglobalCartesianringstats, notlocalKVcross-section. GPU4deferred,128rankscaling/longtrackingnotclaimed. PipelinepilotPIPEMODENONE; longitudinalenabledtestedinstaticsunit.
RawGPUoutputsremain /psi/home/adelmann/opalx-dev/dba/validation-mpi-z-20261106; collectedgpu-results.tgzlocalandremote. RemoteinteractiveSSH execsession98597 ready cwdroot; closeviaexitwhenfinished.
Remaining: finalsmallartifactQA(ifneeded),ensureallcurrentjobsfinished,finaluserreplyconcisewithtimingtable+timingplot+RMSlink,agreement/noIPPLchange/executablespreserved/no16turnruns. No furtherimplementationworknecessary.
