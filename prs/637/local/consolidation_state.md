# Cyclotron consolidation: completed 2026-10-25

## Goal and scope

Implement the approved consolidation in `/Users/adelmann/git/opalx-master`, branch `615-probe-command-does-not-work`, preserving the existing cyclotron probe, coasting correction and accelerating-PIC behavior. No public input/API, physical support, field formula, numerical tolerance or PIC splitting changes. FFA RingElement probes remain a later step. No commit or push requested/performed.

## Changed files and design

- `src/Algorithms/DeviceExternalField.h/.cpp`: existing field infrastructure now owns the unchanged conservative cyclotron AABB/wedge candidate selection. Native kernels retain exact radial/vertical/angular support; analytic `Builder::supports` eligibility is unchanged. Also owns explicit mapped-sector/gap descriptors, the unchanged device magnetic primitive, RF device policy and transactional particle wrappers. Documented laboratory SI units, borrowed immutable map storage and existing positive-proton restriction.
- `src/Algorithms/TrackReferenceStep.h`: shared internal `rf_event::advance`, diagnostics and guarded host callback bridge. Preserves 40 bisections, negative-to-nonnegative crossing, inclusive profile support, later-index equal-root tie, one visit per gap, and stopping only after a complete RF impulse. Trials have no accepted-event/report side effects.
- `src/Algorithms/ParallelTracker.h/.cpp`: host reference/single-particle and device bunch paths use the common event algorithm. Host visited storage stays unrestricted; device retains its 64-gap mask. Host/device magnetic arithmetic, frame/misalignment conventions and sector iteration order remain separate and unchanged. PIC prediction, solve/gather, accepted duration, energy-target localization and MPI failure handling stay in the tracker.
- Removed redundant `CyclotronSectorCandidates.h` and `CyclotronBunchStepper.h` and their Algorithms CMake entries.
- `unit_tests/Algorithms/TestRFEventStep.cpp` and CMake: eight tests exercise actual Kokkos execution and host callback parity, chronological/tied/endpoint crossings, duplicate suppression, finite profiles, complete-kick stopping, bisection and later-kick failures. Sector tests migrated to the consolidated capability. Unit tests do not launch OPALX.
- `/Users/adelmann/git/opalx-manual/physics/overview/index.qmd`: clarified the pre-existing cyclotron spatial-selection exception to the blanket OrbitThreader description; linked the existing cyclotron chapter.

No extra particle copies to host or MPI collectives were added. Device wrappers retain per-particle rollback; a whole bunch is still not transactional on error. Host callbacks add std::function dispatch; no controlled performance benchmark was performed. No intended changes to floating-point/reduction order, conservation, stability or accuracy.

## Validation

- Full OpenMP build succeeded. Final rebuilt focused CTest: **10/10 targets passed**, including CyclotronSectorMPI and CyclotronProbeMPI (3.59 s). New RF event target contains eight host/device tests. Log: `/tmp/opalx-consolidation-final-tests.log`.
- Probe integrations passed: ten-turn coasting, full RF stopping, HDF5/ASCII, passive ON/OFF equality and rejection guards. Accelerating-bunch integrations passed near-zero-charge equivalence and dedicated one/two-rank checks; maximum MPI coordinate difference 8.45e-15 m, momentum 2.78e-15 p/(mc), resolved collective impulse 1.0235e-4 p/(mc).
- Ten old/new short integration cases are exactly equal: 604 HDF5 datasets, 1,370 physical attributes, 14,740 compared values. Matching undefined NaNs require identical dtype, locations and payload bytes; no physical fields omitted. `short-parity-report.json` retains results.
- Full identical-input **8^3 grid / 4,096 particles / 580 MeV** run returned 0 after 516.39 s, one MPI rank/four threads. Same 134 snapshots, reference final energy 580.470767685 MeV, final time 22.035405368802868 us, 4,049 survivors, 47 lost IDs, 759,907 probe hits and all per-turn counts. Every saved reference R/P/time/path/step attribute is exactly equal.
- Strict full-run numerical equality **failed** and is honestly retained in `parity-report.json`. Probe serialization order differs; after joining by unique (turn,id), maximum probe position difference is 1.64e-9 m and arrival difference 7.98e-18 s. Maximum saved particle-coordinate difference is 2.39e-9 m; RMS-size difference 4.14e-11 m and mean-energy difference 1.71e-10 MeV. No acceptance tolerance was introduced/widened.
- Derived position means differ by at most 1.2744e-10 m. The pre-existing HDF5 `centroid` attribute contains raw moment sums rather than a physical position mean; the diagnostic report annotates it and derives means directly from particle coordinates. Strict attribute comparisons remain unchanged.
- Entire `radial.hist` is byte-identical. All final-eight-turn (178..185) 0.1 mm physical-charge density bins are exactly equal. Analysis: `physical-differences.json` / `physical_differences.py`.
- Repeatability controls: the frozen baseline itself differs between four-thread repeats by up to 2.59e-13 m after 2,000 steps. **Old/new final binaries on one thread are exactly equal** for positions, momenta, IDs, reference states and times at both 1,000/2,000-step snapshots. Thus long-run differences are consistent with existing multithread PIC roundoff, rather than evidence for changed RF physics. Report: `repeatability/report.json`; runner `check_repeatability.py`. First bounded decks retained EKINSTOP and hit its expected MAXSTEPS guard; logs preserved under `repeatability-target-guard/`. Corrected controls omit EKINSTOP and return 0.
- Manual source validator passed 58 chapters; edited-page Quarto HTML render passed; rendered-site validator passed 64 existing pages and relative cyclotron link resolves. Only edited page rendered, no full-book/PDF build. Commands: `DOCUMENTS_CHECKOUT=../opalx-documents ruby scripts/validate_manual.rb`; `quarto render physics/overview/index.qmd --profile opalx --to html`; `QUARTO_PROFILE=opalx ruby scripts/validate_rendered_html.rb`.
- Independent source/diff review found no blocking issue. `git diff --check` passed.

## Provenance and limits

Artifacts/scripts live in `tmp/consolidation-20261025/`; `source-snapshot/` contains the final relevant sources. Baseline frozen executable `tmp/ring-space-charge-profiles-20261023/opalx-pre-consolidation`: SHA256 `0c4f905d4aec6b0766a29e8619296b52cff337b6ef75a952718d5cc1477734fd`. Numerical full/short integrations use consolidated SHA256 `ff839a2b4891fdc6c18f6f41ebde16fa43a7e7403fba89bece938df61656f207`. After comment/format-only changes, final source build SHA256 is `2b507a2075301764b81a8f2a94347c9e60a3b5a3817b591b544b529e79af785f`; final unit tests and one-thread repeatability control use this build.

CUDA compilation/execution is unverified. These are refactor checks, not mesh/timestep convergence or physics validation. Existing host/device support/misalignment differences and the unreconstructed 16^3 failure near 584 MeV are not resolved by this consolidation. No simulation remains running.

Next: no required work remains for the approved consolidation; retain reports for review.

## Published at user's request, 2026-10-25

- Explicit push/PR authorization received. Applied clang-format 21.1.8 to the three remaining formatting failures only; affected targets rebuilt and all 10 focused CTest targets passed again (2.25 s).
- Commit `8b38e4c5b9945973771c6c7b65b8cde65d66edc9` (25 source/test/tool files) pushed successfully to origin/615-probe-command-does-not-work. Generated tmp outputs and task notes remain local.
- PR https://github.com/OPALX-project/OPALX/pull/637 created against master and attached to this chat. Description covers behavior, coasting/PIC integration, all validations, multithread differences, deferred FFA probes, CUDA and old 584 MeV failure limitations, and separate manual checkout.
- GitHub connector PR-create returned integration permission 403; gh was unavailable; completed PR creation through the user's authenticated Chrome session. PR creation verified visually and title/description/head/base confirmed. Screenshot /tmp/opalx-pr-637-created.png.
- Read-only merge-tree check against current origin/master completed without conflicts. Branch is behind master, review required, compile CI label-gated; no branch update, reviewer request, merge or CI-label change performed. Manual repository edits remain local and were not pushed by this source-branch request.

## PR comparison figures added, 2026-10-25

At user's request, updated PR #637 description with the existing OPAL 2022.1 LF2/FFT versus OPALX Boris/MIDPOINT PIC comparison for the last eight complete passages (zero-based178..185), plus expandable individual-turn profiles. Uploaded original comparison.png and per-turn-comparison.png to GitHub attachments; no production code/source commit or new run needed. Caption gives8^3 mesh,4096 launched,2mA,580MeV window, common0.1mm physical-charge bins, ID0 exclusion/no area normalization, loss counts, and distinct integrator/self-field/removal rules. Kept existing PR text unchanged around the inserted section.

GitHub assets:
- https://github.com/user-attachments/assets/e88843b0-98ef-4384-b585-3e34febb449d
- https://github.com/user-attachments/assets/667f7c57-6c0b-428a-bd12-047c1b2f2bac

Verified both rendered figures load with original dimensions2200x1760 and2420x2420. Proof screenshot: /tmp/opalx-pr-637-comparison.png. Upload API required the extension file-URL permission; completed through direct image clipboard paste without changing that permission. Browser tab retained as deliverable.
