# PR667 serial/OpenMP builds — COMPLETE

User requested ~/git/opalx source at PR667, preserve local non-src changes,
build serial inbuild/ and OpenMP inbuild-omp/, use thischeckout goingforward.
CurrentHEADd47703aff69879de8e3a87f862a171926b288f69,
branchcodex/fft2d5-explicit-original-model. Tracked src exactlyPRhead;
non-src local tests/docs/workflow modifications retainedbyte-for-byte atcheckout.
Old sourcepatch+589untrackedfiles backedup inopalx-checkout-667-record.
Both old658branchreferencesdeleted perexplicituserauthorization; commitsretained
locally,codex/fft2d5-local-work atfd6,remotea351backupinPRclone.

Serial: /Users/adelmann/git/opalx/build/src/opalx
SHAde6f5d7c4736a9a51494d7c6263e70bafac1bafadb3c57fcbd7a69431cba15c6.
OpenMP(defaultfuture): /Users/adelmann/git/opalx/build-omp/src/opalx
SHAf10675a9374993f1b3bc7d623e981e0a0060df8fbb24c5d0876d8b5ec183d5c2.
BothReleaseClang21SDK26.2,PRd477revision andcorrectbackendverifiedinruntime.
Both2step1particleZeroSCuniformBsmoke runs passfiniteparticle/H5/time checks.
Existinga2exe backuphere,alla0a/ab1/e85archivesretained.

Executable-onlybuilds unitOFFbecauseuserkept experimentalnon-src tests
inplace whileallowingSRCoverwrite. These testsneedreconciliationbeforefull
build/testing; priorisolatedPRconfigurationtestpassedOMP1/4. No sourceedits
or physicschangesduringbuild. FirstOMPconfigurehitnestedLAPACKcachedsource
path mismatch, fixedkeepingexistingdependency sourcepaths; no sourcepatch.
Serialinitialtargetbuiltstaticopalxlib,thenexplicitopalx_exe linked; both
actualexecutablesverified. Commands/logs/provenance/smokeJSON retainedhere.

TheONGOING100step localORIGINAL experiment startedwitharchiveda2c872...
andMUSTfinishunchanged; userexplicitlyaskedfinishit. Native session42273,
postanalysis/audit session33632,roottracking/bend-10m-100steps-local-original.
Current~90/100chargedsteps;ZeroSCpassandaudit/cachecomplete. NeithernewPR
executableusedinthatdataset. Subsequentworkandnewrunsuse~/git/opalx andits
OpenMPbuild. Nextfinish100analysis/plots/metrics/replayanddeliverresultsplus
source/build/branch/PRdescriptionsteeringcompletion. No furtherbuildworkneeded.
