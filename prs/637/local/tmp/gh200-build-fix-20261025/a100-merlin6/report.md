# A100 probe unit-test reproduction

Update: the approved source fix is now implemented and passes OpenMP plus shared CUDA A100 one-/two-rank validation. See [storage-fix/VALIDATION.md](storage-fix/VALIDATION.md). It remains uncommitted and unpushed. The reproduction and diagnostic notes below are historical.

## Result

Update: the runtime cause is now confirmed; see [PROBE_CUDA_DIAGNOSIS.md](PROBE_CUDA_DIAGNOSIS.md) for controlled linking, registration tracing, MPI first-throw evidence and the recommended source solution. Baseline binaries and source remain unchanged. The earlier unresolved-hypothesis wording below records the preceding reproduction stage.

Compilation succeeded. The original failure is reproduced on Gwendolen with both one and two MPI ranks: five of nine GoogleTest cases pass, and the same four recorder cases fail with `cudaErrorInvalidResourceHandle` at `cudaFuncGetAttributes` in Kokkos_Cuda_KernelLaunch.hpp:152. No validated fix or source change remains. No commits or pushes were made; the user explicitly requested no commit at the end of this work.

Remote clone: `~/opalx-dev/opalx-probe-615` (`/data/user/adelmann/opalx-dev/opalx-probe-615`). Parent `~/opalx-dev` already contained unrelated studies and was preserved. Branch `615-probe-command-does-not-work`, commit `61c90499b3f5638f2e26612561e149839774666d`.

## Baseline environment and execution

- Slurm job354754, cluster gmerlin6, partition/account gwendolen, host merlin-g-100. Two A100-SXM4-40GB GPUs; allocation16CPUs/96GiB, build parallelism8.
- GCC14.3.0, OpenMPI5.0.10_slurm, NVCC13.2.78 (cuda/13.2.1), CMake4.4.0, NVIDIA driver595.91.07.
- Shared Release build, CUDA+SERIAL, AMPERE80/sm80, Kokkos bounds checkingOFF, original tolerances unchanged.
- IPPL704932fdaa390f883524cf53588c92386294add4; Kokkos5.2.2 commit8e15454876298832f013ebcaf08d53825b5bda40; heffte6e16996e5a3eb65c60fd62fd4d93c4b2df833033; gtest6910c9d9165801d8827d628cb72eb7ea9dd538c5.
- Built TestCyclotronProbe and TestCyclotronProbeMPI. CTest launched the former with1rank and the latter with2ranks, sequentially. Both fail with5/9cases passing. CTest10.64s, exit8; overall build/job38m55s. Only these two registered targets were built/run; no whole-suite claim.
- First failing ASCII case also fails in isolation on1and2ranks.

## Backtrace and interpretation

`cudaFuncGetAttributes` -> Kokkos CUDA ViewCopy<State> helper in the executable -> view_copy / impl_resize -> `ParticleContainer::probeHistory` in libopalx -> `CyclotronProbeRecorder::initialize` in libopalx.

The failure occurs while resizing probe-history device storage, before probe output is written. It is not a missing input file. A100/CUDA13.2 reproducing the GH200/CUDA13.1 error shows the problem is not confined to GH200 hardware. CUDA/shared-library template binding is a leading hypothesis, not a completed root-cause fix. Symbol inspection shows registration/query calls in both the executable and libopalx resolve to shared libcudart.so.13; no evidence of duplicate static CUDART instances was found.

## Rejected diagnostics

- Job354752: setup-only failure12s. OpenMPI auto-loaded CUDA13.2.1, which conflicted with requested12.9.1 and prevented CMake loading. Corrected before baseline compilation.
- Job354756: test-only CXX_VISIBILITY_PRESET=hidden plus VISIBILITY_INLINES_HIDDEN=ON, shared Release unchanged otherwise. Builds, then segfaults in suite setup. IPPL inline Comm disappears from the executable dynamic symbol table; out-of-line IPPL initialization and test-side globals no longer agree. Rejected and reverted.
- Job354758: inline-only hidden visibility, build one MPI executable and run its full suite on1rank plus CTest on2ranks. One rank still fails5/9 with the original error; the2rank run stalls in the first ASCII case. Cancelled this task's job after the one-rank failure and observed stall; no completed2rank verdict for this diagnostic. Rejected and reverted.

No upstream dependencies, physics kernels, public APIs, numerical tolerances, or permanent build configuration were changed. Tracked remote source is clean. Baseline executables were restored from preserved copies; restored MPI executable SHA256 is `0cd53fe4ee4db2aaec70f6f7e3971f11692b87db1726c06b466223db16112117`. Generated test object/build-rule files may still reflect the last trial until the next normal CMake regeneration/build; the restored executable files match the baseline exactly. All task Slurm jobs are terminal and no allocation remains. No further checks are scheduled.

## Evidence

Original baseline logs/backtrace: `baseline/cuda132/`.
All runs, scripts, rejected patches, and accounting: `all-runs/tmp/a100-probe-20261025-61c90499/`.
Checksummed archive: `a100-probe-615-evidence.tgz`, SHA256 `7c116d8d9d54dfe800e593b9fd4b683d26b2071aa5c4814550d9f67a739692fe`.

Possible next diagnostic, not performed: bind only libopalx function references locally using GNU ld -Bsymbolic-functions, leaving data globals shared, to test function interposition. This is ELF-specific and changes production function override behavior, so it must remain a diagnostic until an appropriate final fix and tests are agreed. The user's latest instruction prohibits committing or pushing without renewed authorization.
