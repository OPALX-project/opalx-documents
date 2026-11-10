# Terminal outcome: A100 validation passed

355069build/native tests and355070one/two-rank school integrations completed0:0. All12native cases passed on each1/2rank process, skipped0. All16schoolstations match57hits; GPU/CPU probe position differences<=6.924e-13m, momentum<=1.090e-13p/(mc), time<=1.512e-19s. Charge/IDs/turn labels retained. Explicit schoolrank0/1GPUUUIDs recorded. AcceptedsubstepsGPU36,256vsCPU36,245; no bitwiseCPUclaim. RawarchiveverifiedSHA064ed62706d7c26b1093eacc63fd972d50673c259d46faa4375f01865e5e2695. No activejobs/monitor, no commits/pushes. Full REPORT.md, native-log-audit.json, gpu-school-audit.json, gpu-rank-equivalence.json, remote-final/ andvalidation-evidence.tgz are authoritative.

---

# FFA probe A100 validation

User authorized implementation/testing; parent authorized isolated remote validation. Adapter docs updated for RF-budget legacy turn labels. Read-only core review found early unused-histogram cap issue; root fixed via geometry-only helper before snapshot. No further blocking issue found.

Initial job355067 failed setup after12s: wrapper used SLURM_SUBMIT_DIR while only --chdir was set, yielding cd /psi/home/adelmann/src. No configure/build/tests ran. Failed logs preserved in remote evidence/attempt1. Corrected submissioncwd, same source and jobscript. Replacementjob355068 on gmerlin6/gwendolen submitted once after355067confirmedFAILED.2A100,2MPI,32CPU,192GB,2h. Status pending first poll; do not duplicate.

Remote root: /data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643. Original /data/user/adelmann/opalx-dev/opalx-probe-615 checkout remains at a9d38caa tracked-clean; SSH origin. No user jobs existed before submission.

Archive source-790abac19643.tar.gz SHA25679fecb6412362da127d7a9e42bb1a18a7699e267d0c85e8bcd44a0d9bcce2624, source_id790abac196432fcfca893ad73d0e045de4efca21768a32fa6cfc33a53ba47afa,1072filesverified before extraction/build. Base ec4319ac; uncommittedfeaturetree, not a committed revision. Generated untracked OPALXrevision.h identifies snapshot.

Fresh IPPL3.4.0 d6216553e39dcf4405849c027517cc3401fefee5; isolated clones of cleanmatching preset dependencies Kokkos5.2.2 8e15454876298832f013ebcaf08d53825b5bda40, heFFTe6e16996e5a3eb65c60fd62fd4d93c4b2df833033,GTest6910c9d9165801d8827d628cb72eb7ea9dd538c5,H5hutb5c74f760bc9919d409f46b5472e9eedf9a764d5. Allbinarydirs isolated. LocalCPUcache uses Kokkos5.2.0; GPU uses project's release-testing preset5.2.2, deliberatetoolchain difference, no dependency code changes.

Build targets opalx_exe/TestCyclotronProbe/TestCyclotronProbeMPI; CTest native self-contained1/2ranktests. ShortschoolGPUintegration pending matchedfixture; root diagnoses old/new inputconversion mismatch.

Remote evidence: evidence/{submission.json,source-manifest.json,dependency-sources.json,status.tsv,job.log,configure.log,build.log,test-commands.log,tests.log,junit.xml,source-verification.json,binaries.sha256}. Localrun.sbatch andprepare_remote.py reproduce setup. JobscriptSHA3e218245fbe9a8d744ff708c92895813230e0744d7b6ef8d599eba6d87da7c1c.

Modules GCC14.3.0,CUDA13.2.1,OpenMPI5.0.10_slurm,CMake4.4.0; OMP1. No relevant remote AGENTS/merlin6 skill files found in inspected remotehome/data ancestors, no skill availablelocally. PartitionUP/mixed8A100node; normalQOS accountgwendolen. No commits/pushes made.

## Setup correction and current job

355068 failed during CMake configuration after43s: Kokkos reported Invalid compiler forCUDA (compiler IDGNU). IPPL3.4 hardcodes launchers at build/_deps/ippl-build/_deps/kokkos-src/bin even when FETCHCONTENT_SOURCE_DIR_KOKKOS points elsewhere. Added expectedcachepath symlink to isolatedcleanKokkos source; no dependency code edit. Preserved attempt2configure/job/status logs.

Currentjob355069 submitted once after355068terminalFAILED. Script run-attempt3.sbatch uses explicituniquejobroot and cmake--fresh. SHA256bc02c0dcc422214e44473fcb5a18ffde4e5241eb3b9dba60fe7eca1d066ff7d2. Source remains790abac19643; monitor355069, do notduplicate. No build/test success claimed yet.

355069 passed freshconfigure with NVIDIA13.2.78 detected correctly and is compiling OPALX after dependencybuild (6m44s atlastobservedpoll), no compilererrors. Monitor_remote.py now follows job every60s, and only after nativebuild/testsuccess submits one shortschoolGPUintegration using run-school.sbatch. Submissionguard evidence/submission-school.json preventsduplicate. Schoolfixture is unchanged native-16-cell-linked-final-hdf5-r1 (school.in SHA31fee815416edc19edc318000be8a6dee28f1c2bc5df57f230cd189ede3729ea; particles SHA65ca902e9907a3a48563ec34729429e71ea68433a6055ceef92b6caa60fa16d7). It will run1/2MPI ranks, no rebuild. Afterterminalresult monitor archives remote validation-evidence.tgz.

Active local SSHmonitor execsession73447; sourcecode and fullpaths recorded in monitor_remote.py. Do notstartsecondmonitor that couldsubmitduplicate; script guardchecks submissionmetadata.

At parentrequest, nativeCTest355069 GPUassignment will be qualified as2MPIranks in2A100allocation unless actualmapping becomesavailable. Alreadyplanned schoolfollowup updatedbefore submission: perrankwrapper logs inheritedCUDA mask, selectsoneallocatedtoken byOMPIlocalrank, resolvesphysicalGPUUUID/PCIbus, sets KOKKOS_DEVICE_ID0 withinthat singlevisibleGPU andexecs samebinary. RankPID/UUID records proveexplicitassignment forsuccessful1/2rankruns. No extra simulation/test sweep.

## Native GPU result and school follow-up

355069 COMPLETED0:0,27m45s. SharedRelease CUDA13.2 build passed. CTest2/2passed in11.05s: TestCyclotronProbe12/12cases ononeprocess; TestCyclotronProbeMPI12/12cases on eachoftwoMPIprocesses(24executions), skipped0each. New FfaStationsPreserveNativeFrameAndHistoryWithoutRadialSummaries RUN/OK appearsoncefor1rank andtwicefor2ranks(105ms/198ms). Perprocessaudit native-log-audit.json; rawlogs remote/tests.log andremote/junit.xml. All1072sourcefiles verifiedaftertests, remote/source-verification.json.

Planned followupjob355070 submittedonceafter355069success. It is running unchanged linked-final16schoolinput on1then2MPIranks with explicitCUDAmask/GPUUUIDlogging. Source/jobbinaryunchanged, no rebuild. Inputhas10,000nominalsteps but CPU36,245acceptedboundarysubsteps, soGPUrun takeslongerthan10kstepestimate. One-rankprogress observed17,627acceptedsteps/~halfcase, noerror. QuantitativeGPU/CPUaudit must report adaptiveacceptedstepcounts ratherthanassume bitwise schedules. CurrentnativeCTest GPUmappingnotcaptured; qualify as2MPIprocessesinA100allocation. Schoolmappingisexplicit.

Source code remainsuncommitted/unpushed. Onlyplanned1/2rank schoolruns remainbeforeterminalarchive/audit; noadditionalvalidation planned.
