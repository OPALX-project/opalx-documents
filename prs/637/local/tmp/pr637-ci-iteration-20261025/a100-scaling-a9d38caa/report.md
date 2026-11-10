# Exact a9 A100 validation: passed

Existing job354773 completed successfully on Gwendolen/merlin-g-100: Slurm `COMPLETED`, exit `0:0`, elapsed14:06. No job was submitted, restarted or duplicated by this monitor. Prior setup-failure354771 and test-only354772 are separate attempts and are not counted as validation results here.

## Actual GPU execution

The job configured and built the requested library, six native test executables and OPALX executable, then ran six verbose CTest targets on one MPI rank with OpenMP1. JUnit records six passed targets, zero failures, zero disabled and zero skipped. Verbose GoogleTest output independently records64/64 native cases:

| Native target | Executed/passed cases |
|---|---:|
|TestMultipoleT|7|
|TestMultipoleTBase|3|
|TestMultipoleTStraight|15|
|TestScalingFFAMagnet|18|
|TestTrackReferenceStep|11|
|TestDeviceExternalField|10|

The new analytic fringe/reference/device test and the new Scaling field-superposition test explicitly appear as RUN and OK in `remote-logs/tests.log`. The separate actual `mpiexec -n 2` run executes and passes the new Scaling test on both ranks; this is not only a CTest dry-run or a successful compile. All changed native tests use self-contained C++ data, without external Python/data or an OPALX simulation launch.

## Source, backend and executable provenance

Source is exact committed `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`, with no tracked source changes before or after. All1015 hashed tracked source/config/test files match an independently generated local archive of that commit; all1015 post-run checks pass. Untracked task outputs/slurm logs were present and do not change the source. Configure/build used fully/updating-disconnected FetchContent.

Toolchain: GCC14.3.0, CUDA13.2.1 (NVCC13.2.78), OpenMPI5.0.10_slurm, CMake4.4.0; shared Release build, CUDA;SERIAL backend, AMPERE80/sm_80, default CTest rank count1. The allocation contained two NVIDIA A100-SXM4-40GB GPUs, driver595.91.07. Actual GPU inventory and toolchain output are in `remote-logs/job.log`; CMake backend/cache metadata and all executable hashes are in `terminal-metadata.txt`.

Dependency commits are unchanged before/after and their post-run working trees are clean:

|Dependency|Commit|
|---|---|
|IPPL|704932fdaa390f883524cf53588c92386294add4|
|Kokkos|8e15454876298832f013ebcaf08d53825b5bda40|
|heFFTe|6e16996e5a3eb65c60fd62fd4d93c4b2df833033|
|GoogleTest|6910c9d9165801d8827d628cb72eb7ea9dd538c5|

Main executable SHA256: `892ff495ede45e475ee503bfe91e6ffea78c4fed4d8985b3c7a41eaf52c9d015`.

Shared libopalx SHA256: `f4ce20f795a2a7f4aafcbc814a2d8fae2b3a5c0e149b3b6585e2ee80a0066c27`.

Full hashes for all six test executables, OPALX and libopalx are preserved in `terminal-metadata.txt`; the job's own selected hash manifest is `remote-logs/binaries.sha256`. Reproducible read-only log audit: `verify_gpu_logs.py`; complete combined audit: `verification.json`.

## Scope and user decision

This establishes actual CUDA compilation and native kernel execution for the six listed targets plus the dedicated two-rank field-superposition case. It does not establish a full CSCS pipeline pass or a full GPU end-to-end regression result. Separately, the complete local OpenMP suite passed401/401 comparisons across39 simulations using locally corrected references; that report is under `../full-local-regression-a9d38caa/`.

The user explicitly chose to keep reference updates local. No external reference push/PR, unpublished CI branch selection or OPALX reference overlay is authorized. Local candidate commitb8e4f8a6605b7e41e57fa31d2f7b51424fd82157 remains isolated. Parent published **a9 source only** at20:56UTC and independently confirmed the exact remote SHA. The three CI configs still select regression master; the external reference branch remains unpublished. The five existing external-reference CI mismatches remain a separate, intentional limitation until the user chooses to publish the references.
