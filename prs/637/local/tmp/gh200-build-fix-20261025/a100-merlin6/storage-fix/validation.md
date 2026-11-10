# Probe storage fix validation

Status: implemented and validated on OpenMP and shared CUDA A100. Job354765 completed successfully (exit0,21m45s). Source is uncommitted on top of61c90499b3f5638f2e26612561e149839774666d; no push authorized. Patch SHA256553eb6c9eea830354187fc1c75c327fc4122d124fd6c189c1a1140501bbe5603.

## Changes

- ParticleContainer stores the same real IPPL State attribute through a stateless custom deleter. Non-template factory, initialization and deletion live in existing PartBunch.cpp. The helper preserves registration before getView(), preserving resize and device reset. Public probeHistory signature and State layout are unchanged.
- LossDataSink removes the redundant idle destructor barrier. Normal save still explicitly closes/synchronizes. The still-open parallel HDF5 fallback close remains collective and active-save failures need coordinated handling; this is not a complete generic MPI exception-recovery mechanism.
- New growth regression arms the original stable ID, forces capacity growth by creating new particles, then crosses without resetting history. Exactly one original-ID hit at1ns is required, with the existing1e-24s tolerance. New IDs must not generate hits; empty MPI ranks participate.
- New cleanup regressions create unopened ASCII/HDF5-configured sinks on rank0 alone. Rank1 waits for a completion token during ordinary destruction and exception unwinding. They would deadlock with the old destructor barrier. The dedicated MPI target selects only these two cases because the older statistics tests assume one rank.

## Execution and numerical impact

No physical formulas, units, boundary conditions, discretization, State data layout, crossing arithmetic or tolerances change. No additional data transfer or hot tracking kernel is introduced. The existing CUDA attribute virtual methods and preserving storage kernels are emitted/owned in libopalx rather than interposed from an executable. MPI attribute migration/sorting/deletion and normal save ordering are preserved. Idle destruction deliberately no longer performs a communicator barrier.

## Completed checks

- Independent read-only review: no concrete issues found in the7file diff.
- clang-format21.1.8 applied to changed C++ lines; git diff --check passed.
- Local Release OpenMP build: TestCyclotronProbe, TestCyclotronProbeMPI, TestLossDataSink, TestLossDataSinkMPI, TestParticleContainer, TestCoordinateSystemTrafo and opalx_exe all compile/link.
- OMP_NUM_THREADS=2;6CTesttargets pass3.79s. Actual one-/two-rank launch commands recorded. Probe10cases on1rank and10perrank on2ranks; LossDataSink15cases on1rank and2cleanupcasesperrank on2ranks; ParticleContainer21cases and CoordinateSystemTrafo8cases pass.

## A100 result

Shared Release CUDA13.2.78, GCC14.3, OpenMPI5.0.10, two A100-SXM4-40GB GPUs, original cache/toolchain with dependency updates disconnected. No diagnostic overlay, global visibility change or symbolic linker binding was used. All7targets compile/link, including opalx_exe. All6CTesttargets pass in25.49s. Probe10cases pass on1rank and10casesperrank on2ranks; cleanup2casesperrank pass on2ranks. LossDataSink15, ParticleContainer21 and CoordinateSystemTrafo8cases also pass on1rank. OMP_NUM_THREADS=1 for the CUDA allocation.

Full symbol inspection finds no State ParticleAttrib definitions in the MPI executable (including local symbols). Its vtable and serialization/migration implementations exist in libopalx. Export-table-only listings are empty for those library symbols too; full symbols establish ownership. No assumption of exported library vtables is needed. Source patch before/after is identical and matches the local patch SHA256.

Evidence is in cuda/ and probe-storage-fix-20261025-evidence.tgz, archiveSHA2564b7acf74bb644d31fe0c5a5bca78f573ab4bbe94c80c1edf839631d7f6d577ed. The older login-node ldd inspection reports GLIBC mismatches; this is explicitly marked as login-only evidence, not a compute-node failure. All reported runtime results are from the allocated A100 job.

## Remaining limits

GH200 runtime validation requires later CI on a published revision and is not claimed by A100 results. Active parallel HDF5 save failure recovery remains collective and requires coordinated handling. No source change, test repeat or additional job is required for the completed A100 validation. No commit or push was made.


## Source documentation follow-up

After runtime validation, comments were expanded in ParticleContainer.hpp, PartBunch.cpp, CyclotronProbe.h and LossDataSink.cpp. They explain why the stateless HistoryDeleter structure is required, why a factory alone leaves consumer-side default deletion, the CUDA kernel/vtable module boundary, the real registered State attribute, registration-before-getView and initial live-range reset, and the cleanup deadlock/fallback-close limitation. Independent review found the descriptions accurate. The before/after diff contains comments only; clang-format and git diff --check pass. No rebuild or runtime-test repeat was needed for this documentation-only step.

The hashes above identify the exact runtime-tested patch. The current complete uncommitted patch with comments is source-with-comments.patch, SHA2567f3517b0629539d4feaf945239ba9324455db2d88b458e00cf9552e703935790; source-comments.patch isolates this follow-up. No commits or pushes.
