# Committed branch658 build — complete

User requested committed branch658 fixes, with uncommitted work kept separately
and existing executable preserved. Clean local clone at
/Users/adelmann/git/opalx-658-committed, detached at committed HEADfd6ba8dc5.
Original /Users/adelmann/git/opalx workingtree unchanged, including tracked
patch and untracked-path status. Existing build-omp/src/opalx unchanged and
backed up here with SHA256. Existingbinary embedsfd6ba8dc5, not60a001fcdc;
its dirty build state is unknown. Archived e85 executable used in prior
tracking reports60a001fcdc. These three binaries must remain distinguished.

New build: /Users/adelmann/git/opalx-658-committed/build-omp/src/opalx.
Clean committed source verified againstHEAD; embedded revision verified;
new SHA256 and archivedbinary recorded in provenance.json. All currentcode
changes (curvature/free-space/pipe/FFA/etc) excluded from this clean source.
Build uses separate copies of cached clean dependency sources, pinnedIPPL
revision, same Clang21/OpenMP Release settings and old MacOSX26.2 SDK.
configure-command.json/dependencies.json and all logs are recorded here.

Initialautomatic SDK27.2 caused heFFte NAN/INFINITY compile failures;
pinning oldSDK26.2 fixed them, no source change. InitialCTestlaunches all
failed before tests due MPI slots; --oversubscribe --bind-to none fixes local
launch, flags in buildcache/record. Full131 CTestentries pass OMP_NUM_THREADS1;
FFT2D5Algorithm,FFT2D5Numerics,SpaceChargeConfig (3entries) pass OMP4.
Extra2rank algorithm-fixture probe is rejected by fixedsingle-domain
FieldLayout before reaching solver, so is not a solverguard verification.
No multi-rank support claimed. No production source changed or toleranceedited.

Executable backups and checksums in provenance.json. No commits/pushes,
no original checkout edits or stashes, no tracking reruns requested/performed.
Next: deliver cleanbinary path and passing test/preservation results.
