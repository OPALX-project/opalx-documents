# FFA PROBE task state

Status: committed and pushed to PR #637 on 9 November 2026; automatic CI queued.

Branch: codex/ffa-probes-school-parity, base ec4319ac (published PR637 head). Published commit b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93 to 615-probe-command-does-not-work (PR #637). Original school files, original Merlin checkout and unrelated work preserved. Intended change set: nine tracked modified files plus three new guide/adapter files, all listed with hashes in intended-files.json. No new C++ source files or performance optimization.

Implemented shared native RING/cyclotron passive recorder; FFA phase-space-only output; COF passivity; general native-output coordinate-frame adapter; API/usage documentation; one focused self-contained C++16station/migration case. Unit tests have no external scripts, input fixtures or launched OPALX.

Validation complete:
- Final Release/OpenMP build and137/137native tests, zero failures/skips,40.99s.
-50standalone general-adapter checks (original 21-check utility retained as historical evidence), existing cyclotron OFF/ON20/1crossing checks and negative contracts.
- COF OFF/ON byte-identical; combinedCOF/INITIALORBIT/TRACK gives128accepted hits (8particles at16stations), no trial hits.
- Nine accepted old runs and18corrected native school cases:16-cell57/57,55-degreeD-off61/61,fourfold15/15crossings, no unmatched hits or losses. Coarse/half/quarter refinement and six plot sets ready.
- Fresh shared CUDA A100 build/native tests pass in355069:2/2CTest targets,12cases per process,36caseexecutions, zero skips.
- GPU school355070 completes1/2rank runs on explicitly distinct GPUs:57hits/all16stations, IDs/charge/labels preserved. Probe positions agree withCPU within6.93e-13m; finalcoordinate differences within7.39e-12m. GPU/CPU boundarysubstep counts differ (36256/36245), no bitwise cross-hardware claim.

Important limits: source-derived magnetic placement reflection/spiral reversal was required in copied comparison inputs; original school templates remain unchanged. LegacyRFturnlabels/initialduplicates are documented, not forced to native labels. One retained fourfold2rank subdivision outlier differs by at most8.57pm in particleposition and repeats exactly match controls; pointer-ordered scalar field sums are a plausible pre-existing sensitivity, not a proven cause. No numerical tolerances or regression references changed.

Durable evidence: REPORT.md, SCHOOL_COMPARISON.md, comparison-summary.json, native-final-tests.xml/log, adapter/, cof/, plots/, a100/REPORT.md and gpu-school-audit.json. Terminal archive SHA064ed62706d7c26b1093eacc63fd972d50673c259d46faa4375f01865e5e2695 independently verified. Changed C++ files match tested A100 snapshot790abac19643; later C++ changes are Doxygen only; the standalone Python adapter was generalized and revalidated on 9 November. Final local executable58bd5db2.

No active task jobs/monitors. User authorized publication on 9 November; all 12 intended files were committed and pushed. Performance optimization, restart/continuation, FFA radial summaries and issue672 remain deferred.

General adapter correction (user request, 9 November): production utility is now
tools/probe_frame_adapter.py with general origin/basis conversion, preserving
IDs/turns/bunch/time; no fixed radius, school dependency or turn relabelling.
README, probe guide and Doxygen use general terminology. Old utility/docs are
archived under adapter-school-original/ for provenance, excluded from commit.
50 general API/CLI/real-data checks pass. Revalidation reproduces 1087 archived
frame conversions exactly for identical decoded inputs. A corrected decimal
reader changes four ASCII values by rounding error; new values match independent
correct decimal parsing. HDF5 is unchanged. Relevant reports are
adapter/validation-general.json and adapter/existing-comparisons-general.json.
No compiled tracking behavior changed, so no CPU/GPU simulation was repeated.
Intended 12-file manifest refreshed and subsequently published with explicit authorization. Performance remains deferred.

Publication: b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93, exact reviewed 12-file contents and user-approved message. SSH non-force push succeeded; PR head and remote ref independently verified. Tracked working tree clean; local notes/tmp excluded. PR remains OPEN. Six automatic CI jobs were queued at verification. See PUBLISH.json. No monitoring was scheduled.

Audit, 9 November2026: full published PR b1551b9c3 reviewed for complexity, duplication and performance. No source changes. Eight prioritized findings and evidence at ../pr637-audit-20261109/AUDIT.md and STATE.json. Recommend diagnostic scratch cleanup, shared support predicate and RF validation cleanup; larger probe batching/history work remains follow-up. No runtime speed claims; no GitHub review posted.
