# Reviewable FODO and ScalingFFA reference draft

This is an isolated manual integration/reference-generation artifact. Native unit tests remain self-contained C++; none calls these scripts, reads these fixture files, or launches OPALX. The maintained regression checkout is unchanged. Publication and GPU/CI acceptance remain parent-owned.

## Exact source and generation

- OPALX source: committed, tracked-clean `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a` (not the older published CI head23f04f6). Both generated `.out` headers independently report the exact a9 revision.
- Regression base: exact `737547e6ae38cf3001d6bc45cf38dd1a47d78402`, extracted with `git archive`, including its unchanged `bin/makeReference.sh` and both complete fixture directories.
- Executable: preserved `executable/opalx`, SHA256 `68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590`. LLVM21.1.8 static Release/OpenMP local build, CMake reconfigured with both `FETCHCONTENT_FULLY_DISCONNECTED=ON` and `FETCHCONTENT_UPDATES_DISCONNECTED=ON`, then `cmake --build build_openmp --target opalx_exe --parallel 8`. Configure/build logs are one directory above this draft.
- Each standard generation ran in its isolated fixture directory with `OMP_NUM_THREADS=1 OMP_PROC_BIND=false OPALX_EXE_PATH=<this-draft>/executable bash ../../bin/makeReference.sh --ranks 1`.
- Both launcher/generator completions returned0; nonempty final `.stat` counts and `.out` runtime revisions were checked, not inferred from the script status. The standard generator's pipeline can otherwise mask a failed launcher.
- All9 original non-reference files have identical pre/post SHA256, including inputs, particle data, `.rt` tolerances, `.local` launchers and existing manual plot script. The six generated MD5 checks all pass. `preserved-inputs-{before,after}.json` and `reference-sha256.json` retain the full manifests.

## Why each reference changes

FODO's old reference was generated at historical72dd3803 in July2026, before September's intentional MultipoleT support/reference changes in fc719154: retain six fringe lengths outside the body and apply the element field to the reference. The old reference had frozen transverse reference momentum and lost one particle; the current implementation evolves the reference and retains1000. Clean named pre-PR master8c1a862 reproduces the two old-reference failures exactly, so this mismatch predates PR637. Current MultipoleT sources equal that master. Native analytic C++ tests independently verify By=g*x*[tanh(z/lambda)-tanh((z-L)/lambda)]/2 in T, including fringe points outside the0.5m body and reference/scalar/device parity; the actual production source is unchanged by a9 except the separate ScalingFFA correction. Detailed source/history/analytic evidence is in `../fodo-multipolet/INVESTIGATION.md`.

ScalingFFA's maintained input requests1000 steps, while its old reference contains only the10-step/1ns result. A full run also exposed an actual field-superposition defect shared by pre-PR master: each element overwrote previous contributions, and an outside-support element could clear the field. Commita9 corrects element application to add its own contribution while preserving raw-getter overwrite semantics, formulas, support, units and public signatures. Native C++ tests first failed on the former implementation, then passed after correction, including real particle views, two overlapping fields, outside-support behavior, scalar/reference parity and two-rank execution. The full unchanged1000-step run now retains identical particles alongside the reference to arithmetic precision instead of1.222m separation. Detailed evidence is in `../SCALING_SUPERPOSITION_STATE.md` and `../scaling-superposition-final/REPORT.md`.

## Counts and physical sanity

| Case | Rows | Existing comparisons | Particles | Final time | Energy variation | Maximum charge error |
|---|---:|---:|---:|---:|---:|---:|
| FodoCell-multipoleT-fromfile |2001|7/7 pass|1000 throughout|200.1ns|1.59e-10MeV around1000MeV|7.89e-31C|
| ScalingFFABasicPlacements |10|3/3 pass|10 throughout|100ns|8.46e-13MeV around46.726MeV|7.89e-31C|

FODO comparisons use the independently built clean named-master8c1a862 run: maximum absolute emittance difference3.37e-14m, maximum energy difference1.02e-12MeV; all seven original eps=1e-5 comparisons pass. FODO is a finite-emittance input, so its0.503mm final centroid offset is not the identical-particle parity check used for ScalingFFA.

Scaling comparisons use the separately executed corrected1000-step run: all three centroid columns are numerically identical; original eps=1e-4m remains unchanged. Final mean particle/reference separation is7.931939441046071e-13m, maximum over ten sampled rows8.327145229187566e-13m, compared with named old-master1.2220141692200102m. Exact comparison definitions/results appear in `comparison-results.csv`; `validate_drafts.py` reproduces the full accounting. NightlyBuildX's avg metric remains its existing absolute `sqrt(sum(difference^2))/N`, without tolerance changes.

These local fixed-resolution runs establish reproducibility and the stated invariants; reference comparison alone does not establish physics accuracy. Independent analytic/native checks supply the field evidence. They do not replace GPU runtime validation or a general FFA convergence study. Status updated after the complete backend audit: the exact a9 source now passes A100 validation and all six CSCS builds and nine native unit configurations (137/137 each). The three CSCS regression jobs used the old published references and each reported 396/401, with exactly the two FODO numerical mismatches and three Scaling row-count mismatches described here. This local reference patch has not been selected in external CI. Its full 401/401 comparison validation is local CPU evidence; public GPU artifacts omit raw statistics, so an independent comparison against the corrected references cannot be recomputed from those artifacts. See `../FINAL_CI_AUDIT.md` and `../ci-checkout-provenance-a9d38caa/README.md`.

## Concrete patch

`combined-reference.patch` changes exactly12 generated reference files: `.stat`, `.out`, `timing.dat` and their existing `.md5` companions for each case. It changes no input, particle distribution, launcher, `.rt`, tolerance or source. SHA256: `05b649a08c40f351a048f9b4b051e832a2288032ab19a48d40a35cea9865ea4e`.

`git apply --check` passed against an isolated archive of exact regression737547e6, preserved in `patch-check-base/`. No patch was applied to the maintained regression checkout; `maintained-regression-status.txt` is empty. Review the generated files, this provenance and GPU results before parent publication.
