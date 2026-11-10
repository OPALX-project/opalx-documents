# Probe CUDA runtime diagnosis — 25 October 2026

Update: the approved source fix is now implemented and passes OpenMP plus shared CUDA A100 one-/two-rank validation. See [storage-fix/VALIDATION.md](storage-fix/VALIDATION.md). It remains uncommitted and unpushed. The reproduction and diagnostic notes below are historical.

The cause of the original probe failure is confirmed. In the shared CUDA build, probe-history template implementations emitted in the test executable interpose on implementations in `libopalx`. The selected executable State-copy CUDA stub was never registered. The same boundary problem is exercised through virtual serialization during MPI migration. No permanent fix has been applied; no commits or pushes were made.

## Reproduction and controlled evidence

Source: branch `615-probe-command-does-not-work`, exact commit `61c90499b3f5638f2e26612561e149839774666d`. Remote clone: `/data/user/adelmann/opalx-dev/opalx-probe-615`. Shared Release, CUDA+SERIAL, A100/sm80, GCC14.3, NVCC13.2.78, OpenMPI5.0.10. This reproduces the GH200/CUDA13.1 runtime diagnostic, but is not a new GH200 validation.

| Configuration | One MPI rank | Two MPI ranks |
| --- | --- | --- |
| Unchanged baseline | 5/9 pass; 4 CUDA failures | 5/9 pass; same 4 CUDA failures |
| Overlay library with `-Bsymbolic-functions` | 9/9 pass | Migration throws same CUDA error, then timeout |

Job354760 created the overlay by relinking the exact baseline object files to a separate output. Baseline executables and library checksums are unchanged before/after. The overlay is a diagnostic, not an accepted linker fix. Job354763 captured the MPI first exception. Both diagnostic jobs completed; their exit0 records successful orchestration, not a passing two-rank test. Job354762 did not execute the test because its GDB script filename was initially incorrect; corrected in354763.

The baseline GDB trace records3044 CUDA kernel registrations. The failing `cudaFuncGetAttributes` query uses executable address `0x52b060` for a State ViewCopy kernel, absent from those registrations. Static disassembly shows the executable's corresponding dummy stubs and confirms their absence from executable registration code; real registered State-copy kernels exist in `libopalx`. Shared libcudart imports are used; duplicate static CUDA runtimes are not established.

Call path: `CyclotronProbeRecorder::initialize` in libopalx -> `ParticleContainer::probeHistory` -> executable Kokkos preserving resize/ViewCopy -> unregistered executable kernel stub -> `cudaErrorInvalidResourceHandle`.

With function-local binding in the overlay, all traced kernel queries are registered and all nine one-rank cases pass. Both binary modules still export the `ParticleAttrib<cyclotron_probe::State>` vtable. The library references its vtable through a preemptible `R_X86_64_GLOB_DAT` relocation; function-only binding does not localize this data symbol.

The MPI first-throw stack identifies `ParticleAttrib<State>::serialize` in the executable -> `SerializeHashFunctor<State>` -> `cudaFuncGetAttributes` -> the same invalid resource-handle exception. This is reached from `ParticleSpatialLayout::update` / `sendToRank`. Attached hang traces show rank0 unwinding into `LossDataSink::~LossDataSink`'s barrier while rank1 waits in migration `MPI_Waitall`. The timeout masks the rank-local CUDA failure; it is not evidence of missing probe input/output files.

## Recommended solution for discussion

Keep the probe-history storage lifecycle in libopalx rather than duplicating its template storage implementation in executable consumers. In `ParticleContainer.hpp`, retain the public `probeHistory()` signature and the real IPPL attribute registration. Replace the default-deleting unique_ptr with an out-of-line custom deleter; move allocation plus preserving resize/reset behind non-template out-of-line helpers defined in an existing implementation file such as `PartBunch.cpp`. Construction, initialization and deletion must move together: moving only resize or only the factory can leave executable vtable instantiation. No new source module is required.

Preserve State data layout, particle IDs, sorting, deletion, MPI serialization and capacity-growth behavior. Retain the preserving resize operation. No changed physical assumptions, units, discretization, boundaries, arithmetic, tolerances or intended device-data transfers are required. This is a proposed design, not a tested source fix.

Validate with the original shared CUDA configuration and no overlay: all nine cases on one and two ranks; check that executable definitions of the State attribute vtable, virtual migration methods and resize helpers disappear. Add a preserving-growth case that arms an existing particle's history, forces capacity growth with new IDs, and immediately crosses the probe: the original history must retain its interpolated crossing and new IDs must initialize without false hits. Retain actual ownership-changing migration, frame, HDF5 and repeated-flush checks. Then validate GH200.

Address collective error handling separately: a destructor barrier can deadlock during rank-local exception unwinding. Explicit collective close in the normal path and a coordinated failure policy are preferable; simply deleting the barrier would still leave the other rank waiting for migration data. Blanket hidden visibility was already rejected because it separates IPPL inline globals, and blanket binding of data would carry the same risk. A global ELF-only linker change is broader than the focused source containment.

## Evidence

`cause/` contains original job logs, runtime registration JSON, MPI first-throw log, attached-rank traces, exact relink command, source revision/status, accounting, and before/after checksums. `cause/elf-inspection.txt` and `cause/state-vtable.txt` contain independent static inspection. The downloaded archive SHA256 is `4e361ba2dc8361d551f60e2bdb789e7cb939b9b9ff2a58386fbc7c755e0c39c9`.
