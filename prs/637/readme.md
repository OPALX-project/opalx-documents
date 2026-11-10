# PR #637: PROBE supporting records

[PR #637](https://github.com/OPALX-project/OPALX/pull/637), **Implement cyclotron PROBE and accelerating space-charge tracking**, merged on 2026-11-10 as `4ade4a0c062daf5c420d2305c3525d56ee001c98`.

Archived from `/Users/adelmann/git/opalx-master`. That checkout is on `codex/ffa-probes-school-parity` at `89e300eeb`, including later visualization work; it is not labelled as the exact PR merge checkout. Tracked source files, commits and branch selection were left unchanged.

This folder contains small UTF-8 text files only, up to 1 MiB each: development notes, Python/batch scripts, exact run inputs, source patches and compact JSON/CSV validation summaries. No large snapshots, traces, images or executables are retained. Original paths, sizes and hashes are recorded in the chunked `inventory.json`.

## Start here

- [Input decks](inputs-index.md): direct links to 268 archived OPALX/legacy comparison inputs.
- [PROBE plan](local/probe_plan.md).
- [Accelerating space-charge notes](local/accelerating_sc_state.md).
- [Coasting fix](local/coasting_fix_state.md).
- [Consolidation and original publication](local/consolidation_state.md).
- [GH200 build work](local/gh200_build_state.md).
- [FFA probe implementation and CPU/A100 validation](local/tmp/ffa-probes-implementation-20261107/state.md).
- [Final PR audit fixes](local/tmp/pr637-audit-fixes-20261109/report.md).
- [Terminal RF endpoint fix](local/tmp/terminal-rf-roundoff-20261110/state.md).
- [PR description and merge metadata](pr.json).

Historical scripts and inputs retain original paths; adapt these and supply separately recorded external assets before rerunning. The archive does not claim every historical run is a self-contained example. Native merlin6 results remain at their recorded locations. No new simulation was run during archiving.

## LaTeX

The checkout's only project LaTeX document is the general interpolation note, not a PROBE validation paper. It compiles successfully with latexmk/pdflatex and has no undefined-reference warning. The [editable source](local/src/fields/interpolation/polynomial_solve_with_smoothing.tex), `latex-validation.json` records the check; its [compiled PDF](../../reports/2026/pr637/interpolation-polynomial-smoothing.pdf) is stored outside this text-only folder.

## Cleanup

After verifying all retained hashes, removed the PR-related local temporary directories, five archived root state/plan files and `build_openmp`. Large raw data and saved executables were deleted as requested. No tracked source files, remote runs, unrelated checkouts or Git history were removed. No commit or push was performed. See `task-state.json` for exact scope and sizes.

## Compact archive

Compacted at the user’s request: removed generated orbit/element-position tables and plotting exports, raw run statistics, bulk build/test/CI logs and other transient output. Development notes, non-generated Python scripts, all 268 input decks, small directly referenced data/map inputs, source patches and compact JSON/CSV validation summaries remain. Original paths/hashes of removed files stay in the inventory, marked `removed-generated-output-during-compaction`; they are no longer claimed as retained evidence. Historical notes may reference these discarded detailed outputs. `compaction.json` records the reduction.
