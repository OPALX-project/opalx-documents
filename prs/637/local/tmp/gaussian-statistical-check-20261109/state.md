# Gaussian statistical check

Complete, 9 November 2026. The remaining Gaussian failure is fixed. Relevant checks and both full suites pass. All task jobs are terminal; no further tests are needed. Nothing is staged, committed or pushed.

Checkout: /Users/adelmann/git/opalx-master, branch codex/ffa-probes-school-parity, HEAD b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93. This task changes only unit_tests/Distribution/TestGaussian.cpp. All37earlier modified/new source files are byte-identical to prior-files.json. Fullcurrent1073sourcehashes verified. NewcppSHA6569cabdd647bd40dcbbeb280819aca92ea724b5f06b30972975b5bf830fa4ce.

Fix: replace arbitrary5.5sigma maximum and max>3 proxy with MPI-global exceedance counts and a sample-size-derived normal maximum. Five uncutunitnormalaxes have P(|Z|>3)=erfc(3/sqrt2). Split newtail-familyalpha1e-6 equally: Bernsteincount envelope L=log(4m/alpha), margin=L/3+sqrt(2vL+L²/9); normalunionmaximum=sqrt(2(L+logN)). N100000 yields counts170..370 andmaximum7.5265089. Assertactualglobalcount equalsoriginalrequest, all6values finite andstrictzcut preserved. Sampler, seed,N100000, RMS4SEblock andallothertestcases unchanged. No externaldata/Python/unitdependencies ornewtestcases.

Math: independent reviewers approve both formulas/budget and collective safety. Statistical-audit.py/.json/.md reproduces bounds, exactbinomial/normaltail numericalunionupper4.22e-8<=1e-6, clipping3/count0 rejection and40sigma outliermaxrejection. Those are analyticalcounterfactuals, notnativefaultinjection. Alphaappliesonlynewtail/maxchecks, excludingexistingRMS; IIDnormalmodeldoesnotcertifyPRNG. MITBernsteinprimarynoteslinked inREPORT.

Tests: localGaussian8/8 pass andfullOpenMP137/137 pass. LinuxDebug/OpenMP Gaussian rank1/2×thread1/4 variants48nativecaseexecutions0skips;7/7distributiontargets;full137/137targets0fail. Finaljob355097COMPLETED0:0 (4m44), no failedattempts/native retries. ELFobject/relink hashes verified fresh; productionlibrary andtwoearlier frozenarchives unchanged. Formatting, diffcheck andindependentcode/MPI/math reviewpass.

Evidence: REPORT.md, RESULTS.json, ROOT_VERIFICATION.json, LOCAL_RESULTS.json, statistical-audit.* andlinux/remote-evidence rawlogs/JUnit/source/binary/accounting. Archive linux/validation-evidence.tgz SHA f21f064d3def3d9429038c4321512aacd6ef5c6cd7c3dc7f4baf3eaded171063. Linuxcanonicalaudit linux/audit_linux.py. Sourcepatchfix.patch;single-file metadataintended-file.json.

Limits: CPU LinuxDebug/OpenMP onMerlin6 isnotexactUbuntuCIimage; noCUDA runtimeclaim. Default1rankORBcasescaninternallyskip, buttheirmanual2/4rankcoverageis preservedinpreviousownershipevidence. TheformerlyreportedGaussianfailureisnowresolvedwithoutproductionorRMS/seed/samplecount changes.

Next: user review. Do not commit or push without newexplicitinstruction. Largerprobeperformanceworkremainsdeferred.

## Authorized publication

User explicitly authorized committing/pushing all38source/testfiles with the proposed message. Commit648ce4ea55b56b0b542f17fa9010c3e1fca8e363 pushed non-force viaSSH to origin/615-probe-command-does-not-work forPR637. Exactly38validatedfiles committed; investigationnotes/tmpartifacts excluded and retainedlocally.
