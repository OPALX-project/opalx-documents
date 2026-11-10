# FFA PROBE implementation and validation

Status: implementation and validation complete. CPU tests, old-OPAL school comparisons, fresh A100 native tests and one-/two-GPU school runs pass. Published to PR #637 as b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93 on 9 November 2026.

## Implementation

Branch `codex/ffa-probes-school-parity`, based on published PR637 head `ec4319acb1d3cf676f2581f4c86c3e691ce2e22d`. PR637 remains separate and unmerged. No external regression reference data were changed or published.

The existing passive recorder now accepts native RING particle tracking. It remains outside magnetic placement and field selection, with the same accepted-endpoint crossing kernel, stable-ID migratable histories, compact hit transfer and collective periodic flushing. No new C++ source file, tracking hierarchy, CUDA state owner or performance optimization was introduced. The historical CyclotronProbeRecorder name is documented as shared planar machinery.

FFA output is native laboratory X-Z horizontal/Y vertical, in standard ASCII/HDF5 phase-space records. Its lab-origin radial summaries are disabled because an FFA ring centre may be translated. Cyclotron .hist/.peaks behavior is unchanged. Geometry and positive STEP are checked during parsing; optional histogram allocation is checked only after transport selection. Native output is canonical; tools/probe_frame_adapter.py converts records into a caller-defined Cartesian frame with an explicit origin and orthonormal basis. It is independent of any example or lattice.

COF ignores PROBE as passive and produces no detector records during trial tracking. Restart, continuation and spectral-tune trial tracking with probes remain unsupported. Performance optimization, FFA radial summaries and issue672 remain deferred.

## Local validation

- Final complete Release/OpenMP build and **137/137 native CTest targets pass**, zero failures (40.99 s). Native unit tests remain self-contained C++, with no external scripts, input data or launched OPALX. The existing probe target and its two-rank twin include a translated sixteen-station circle with actual IPPL migration, stable IDs, native coordinates and duplicate-free flushing.
- All **50 standalone general-adapter checks pass**, including arbitrary rotations/translations, inverse conversion, handedness, exact large integer IDs and metadata, ASCII/HDF5 batches, CLI behavior and malformed data. The original school-specific utility and its 21-check evidence are retained only as local historical artifacts. This Python utility is not a native unit-test dependency.
- Existing cyclotron coasting/RF integration checks pass. Probe OFF/ASCII/HDF5 physical states, reference, time and steps agree exactly; crossing counts 20/1 and all four negative contracts are preserved.
- COF probe OFF/ON results are byte-identical and create no probe files. A combined COF -> INITIALORBIT -> one-turn TRACK run succeeds with 8 particles, exactly 8 hits at each of 16 stations and no trial/initial-time contamination.
- The final linked executable SHA256 is `58bd5db212d2dc3e62c8fdf62a51fb2dca456580eabf9452c595ea448777f9d5`. A full matched 16-cell run with the final source accepts a tiny positive FFA STEP without allocating unused histograms, records 57 hits and has exactly the same final physical state as the frozen first implementation. The earlier frozen executable is retained with its own hash; numerical comparison manifests identify which was used.

Evidence: native-final-tests.xml/log, build-final-all.log, adapter/validation-general.json, adapter/existing-comparisons-general.json, cyclotron-integration/report.json, cof/verified-report.json, cof/cof-then-track/report.json, final-source-comparison.json, intended-files.json.

## Old OPAL school comparison

See [SCHOOL_COMPARISON.md](SCHOOL_COMPARISON.md), [comparison-summary.json](comparison-summary.json) and [old-school/REPORT.md](old-school/REPORT.md) for exact inputs, actual masses/timesteps, binary revisions/hashes, fields and retained excluded attempts. Nine accepted old runs and 18 corrected native cases cover the original 16-cell, 55-degree D-off and fourfold examples, with vertical excitation and nominal timestep refinement. The old executable's relevant probe/field sources were pinned at its actual revision and checked against OPAL 2022.1.

All positive-time crossings match by station, stable particle ID and chronological passage: **57/57, 61/61 and 15/15**, respectively, with no unmatched records or particle losses. The quarter-step16-cell radial difference is at most 8.71 micrometres; the fourfold radial difference is at most 5.28 micrometres. The D-off radial momentum difference decreases from 1.48e-4 to 7.30e-5 p/(mc) when the nominal old/native timestep is halved. Different event sampling and old six-significant-digit ASCII limit comparison precision; these few-turn tests do not establish a general integrator convergence order or long-term stability.

An existing school migration error initially obscured parity: old RingDefinition angles are clockwise from +oldY. Source-derived copied-input correction reflects physical magnet placements and reverses spiral handedness while retaining the axial B0 sign conversion. Original school files and production field algorithms are untouched. An independent 450-point scalar/matrix check, including asymmetric fringes and off-plane fields, confirms the transformation to 8.05e-15 T; actual native/old runs provide executable validation.

Old school turn labels count RF step budgets, not orbital revolutions; old PROBE also emits two duplicate initial t=0 records. Native output retains its reference launch-plane return count at step start and suppresses initial-plane hits. The adapter does not fabricate legacy turn equivalence. A launch-plane diagnostic explains the fourfold station labels when two planes are crossed inside one accepted interval.

## Parallel numerical limit retained

Most listed matched OFF/ON/format/rank controls agree exactly. One first fourfold two-rank ON run had 63,158 accepted subdivisions, compared with 63,143 for controls and repeat ON, with identical final time, ID and charge. Maximum local position difference was 8.57e-12 m and reference difference 1.23e-13 m. Identical input, particle and binary hashes were verified; the full inherited environment was not captured. This remains an unreproduced outlier and is not hidden behind a loosened tolerance.

A read-only source audit finds pre-existing pointer-ordered overlapping field sums in TrackReferenceStep, ExternalFieldRayTracker and OpalBeamline scalar paths. Boundary splitting uses scalar reference trials and sharp support tests, so tiny addition-order changes are a plausible sensitivity, not a proven explanation of this run. No general bitwise cross-rank guarantee is claimed, and no unrelated field-ordering change is included.

## A100 validation

Fresh Gwendolen shared-Release CUDA build and both native probe CTest targets pass in job 355069 (COMPLETED 0:0,27m45s). CTest 2/2 passes in 11.05 s. The single-rank process runs 12 cases; each of the two-rank processes runs 12 cases, for 36 successful case executions with zero skips. The new sixteen-station FFA/migration case runs and passes on all three processes. All 1072 snapshot source files were verified after testing.

The unchanged matched 16-cell input then completes successfully in job 355070 (COMPLETED 0:0,10m40s), once on one GPU and once on two explicitly distinct A100s. Both runs record 57/57 crossings across 16 stations, preserve one particle and charge, and match CPU particle IDs, bunch numbers and native reference-return labels. Maximum GPU/CPU probe-position component difference is 6.9234e-13 m, momentum difference 1.0897e-13 p/(mc), and time difference 1.512e-19 s. Final TIME and charge agree exactly; maximum final local-coordinate difference is 7.3815e-12 m. GPU accepted subdivisions are 36,256 versus 36,245 on CPU, so no bitwise cross-hardware schedule/state claim is made. This one-particle correctness run is not a performance benchmark.

Source snapshot 790abac19643 matches every changed C++ file in the final local tree; subsequent C++ changes are Doxygen wording only. The standalone adapter was generalized and separately validated on 9 November 2026. GPU uses the declared release-testing Kokkos 5.2.2 versus local CPU 5.2.0, and both use IPPL 3.4.0. Original remote checkout/build remain untouched. Setup-only attempts 355067/355068 are retained separately and do not represent source/test failures. No current task jobs or monitors remain active.

Evidence: [A100 report](a100/REPORT.md), [native tests](a100/remote/tests.log), [GPU school audit](a100/gpu-school-audit.json), [complete terminal evidence](a100/remote-final/). The retrieved archive checksum was independently verified: 064ed62706d7c26b1093eacc63fd972d50673c259d46faa4375f01865e5e2695.

## Plots and use

Six overlay sets (PNG/PDF, CSV and metrics JSON) are in plots/. They were visually inspected. Main examples: [16-cell radial](plots/16-cell-radial.png) and [fourfold vertical](plots/fourfold-vertical.png). Native probe geometry/output is documented in docs/probes.md, with adapter CLI in tools/probe_frame_adapter.md.

```sh
~/.venv-h6/bin/python tools/probe_frame_adapter.py PROBE1.h5 analysis/PROBE1.loss \
    --origin-m -4.42 0 0 --basis 1 0 0 0 0 1 0 1 0
```

Native files are preserved and converted outputs are created exclusively. Performance work is explicitly deferred until this correctness milestone is reviewed. The reviewed 12 files were committed and pushed to PR #637 on 9 November 2026; local artifacts remain excluded.

## General adapter correction, 9 November 2026

The user requires a general utility, with no school-specific production feature.
The former fixed-R0 Y/Z permutation has been replaced by `transform_frame` with
`r_target=B(r_lab-o)` and `p_target=B p_lab`. Origin is arbitrary; the basis is
orthonormal with either handedness. IDs, turn labels, bunch and time are
preserved; the turn-offset option was removed. Production source/docs contain
no school-specific references or magnetic-migration recipe. School inputs remain
only comparison benchmarks in local task evidence. No executable C++ changed.

The validator found `pandas.to_numeric` could lose one ULP when rereading a
17-digit decimal. Direct float64 conversion fixes this, including exact time
round trips. For identical decoded inputs, the general transform reproduces all
1087 archived converted records across 25 datasets exactly. The reader correction
changes four ASCII-decoded values; they independently match correctly rounded
decimal parsing. HDF5 data are unchanged. Archived outputs have not been rewritten.
This adapter correction required no simulation rerun or physics tolerance change; publication followed explicit user authorization.

Reproducible checks: `adapter/validate_adapter.py` and
`adapter/revalidate_existing_comparisons.py`; reports alongside. The 1e-12
orthonormality acceptance is an input-geometry check, not a tracking tolerance.

## Publication, 9 November 2026

Commit b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93 uses the approved message and contains exactly the 12 reviewed files. Non-force SSH push to 615-probe-command-does-not-work succeeded; GitHub PR #637 and the remote branch independently report that commit. Tracked tree is clean. CPU OpenMP, CPU Serial, clang-format, CUDA, HIP and SYCL checks were queued automatically. No new PR or merge was performed. See PUBLISH.json.
