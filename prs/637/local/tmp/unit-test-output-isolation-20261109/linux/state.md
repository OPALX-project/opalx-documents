# Linux unit-test output isolation validation

Complete, 9 November 2026. No task jobs remain active. No commit or push. Root owns the broader source change; this worker implemented seven Fields fixtures and performed Linux validation.

Before: task-owned reused CPU build at /data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490, frozen old source3320 plus prior C5LossDataSink fix. All1072 source hashes, prior archive3260..., old production library and FM2D binaries verified before new changes. Job355094 completed0:0: two original FM2D targets passed in isolation, but their first concurrent pair failed10native cases, including `cannot remove: Directory not empty [/tmp/opalx_fm2d_test]`. Raw before logs/metadata are preserved.

Final source update:30unit-test files (29CPP plus TemporaryDirectory.h), portable atomic filesystem helper SHAafda956bd571dcf600751c3cca4550dee97ea3bf16842a1d0aee5ab2c5ef9ed9. No production or CMake source changes. Root's seven previous audit/loss file hashes unchanged. Staging used write_bytes+freshmtime; compute job touched intended sources before build. All1073 expected sources match the current local checkout.

After job355096 completed0:0 in13m37. All29affected targets rebuilt/relinked, every object/binarymtime follows the pinned source, every ELFhash differs from baseline, and all29 compile records are present. Production library remains byte-identical (b8c48c6930df7121b0bd0e39dba18239808f64dc50146652d5b5f10cad3bc859). All29selected targets passed. Twenty concurrent FM2Dpairs passed:40CTest target runs,840native cases,0skips.

Manual MPI checks all pass with actual execution and no skips: CheckpointFile2ranks(4caseinstances), MultiContainer diagnosticH5rewind2ranks(2), ORBupdater2ranks(2), ORBload-balancing4ranks(8), FFT2D5multiple-rank rejection2ranks(2). Total18native instances. This exercises default one-rank cases that otherwise skip their multi-rank paths.

Full Linux suite:136/137 pass. Only the unchanged GaussianTest.largeCutoffDisablesTruncation fails, maximum5.5717775960503042 versus5.5. No source/seed/tolerance changes or additional Gaussian reruns were made for this task. The full-suite exit8 is retained explicitly; job completion0 means the planned validation completed with this recorded known limitation.

Environment: compute hostmerlin-g-100, Linux kernel5.14el9_8, GCC14.3/OpenMPI5/CMake4.4, Debug/OpenMP,4OpenMPthreads. SSHlogin reports RHEL8.10; this is not used to infer compute-node userland. Kokkos5.2.2 differs from GitHubCI5.2.0; no exact Ubuntuimage parity claim.

Task-wrapper history: old mkdtemp helper package was superseded locally before upload or source changes when local compilation exposed feature-macro portability; it never ran on Linux. A redundant dependency on already-completed355094 was rejected before after-job creation; after completed accounting was verified,355096 was submitted once without that dependency and without reapplying sources. A monitor later had one transient DNS error; hostname resolved to its existing known-host IP, and subsequent read-only retrieval used per-command HostName with originalHostKeyAlias/StrictHostKeyChecking=yes. No SSHconfiguration/keys were changed; no tests were restarted.

Evidence: validation-evidence.tgz SHAe06d7b6d09d549b42d24260608b88633f14c1284a71fb609816c5582e0cf575f (327445bytes), remote-evidence/ rawlogs/JUnit/source/bin/accounting, audit.json, reproducibleaudit_linux.py. All source/library/binary/oldarchive hashes were verified at completion and canonical audit compares1073files with current checkout. No further tests are needed. Next root final review/report.
