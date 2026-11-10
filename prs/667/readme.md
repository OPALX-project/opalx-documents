# PR #667: FFT2D5 supporting records

[PR #667](https://github.com/OPALX-project/OPALX/pull/667) merged on 2026-11-07 as `b34cc5b6501744c08812a7602c13f65328064165`.

This archive contains small UTF-8 text files only (at most 1 MiB per file): notes, analysis scripts, input decks, LaTeX sources, patches and compact validation summaries. No particle snapshots, traces, images, PDFs or executables are stored here. Original filenames are recorded in `inventory.json`; archive paths are lowercase.

## Start here

- [OPALX and PyORBIT input files](inputs/readme.md).
- [LaTeX sources, compiled reports and rebuild instructions](latex-readme.md).

- [Final cleanup and CPU/GPU validation report](../../examples/2026/2d5-1/cleanup-2026-11-07/readme.md), including the published timing plots.
- [Earlier reports and comparisons](../../examples/2026/2d5-1/).
- [Development handoff](local/handoff-fft2d5.md).
- [Final local test/build state](local/tmp/2026-11-07-fft2d5-cleanup/task-state.md).
- [Merlin6 build and validation state](local/tmp/2026-11-07-fft2d5-cleanup/remote-state.md).
- [PR description and commit metadata](pr.json).
- [File inventory and hashes](inventory.json).

The historical scripts and notes retain their original paths and commands. Paths into the removed temporary/build directories must be adapted before rerunning them. Archived refactoring scripts are historical evidence, not scripts to apply to current master.

## Local cleanup, 2026-11-10

After verifying the retained text files, removed `~/git/opalx/build`, `build-omp`, the PR-specific dated temporary directories, the ZeroSC audit cache and the original FFT2D5 handoff/DBA discovery note. About **6.16 GB** of local files were removed. Large snapshots, traces, saved executables and the temporary external artifact store were deleted as requested. Their original paths, sizes and available hashes remain in the inventory; their bytes cannot be recovered from this archive.

Published example reports/plots and remote merlin6 run directories were left in place. Unrelated FFA, manual, announcement and working-tree changes were preserved. `tmp/pdfs` contains mixed report/announcement renderings and was left untouched. No build or simulation processes were active during cleanup.

`task-state.json` and `compaction.json` record the completed cleanup. No commit or push is included in this archive operation.

## Archive rename incident

A case-only filename-normalization error deleted 388 archived text copies after the original cleanup. **129 files were recovered byte-for-byte**, verified against the pre-cleanup SHA-256 inventory, from other local copies, Git objects and literal content in the tool journal. All development notes and analysis scripts were recovered. The remaining **259 generated files** were not recovered: 64 generated element-position plotting scripts, 62 geometry display files, 124 element-position tables, eight CMake caches and one generated build README. They contain no analysis scripts or input decks. Their paths and original hashes are explicitly listed in `recovery-unrecovered.json`; the main inventory marks them `not-recovered-generated-file` rather than claiming they were archived. Published validation reports, actual run inputs and numerical result records remain available.

Archive checks verify all retained original hashes, catalog digests and the small-text policy. The full repository validator still reports seven unrelated uncataloged files (Finder metadata, a Python cache and a movie); see `task-state.json`. No unrelated assets were changed.

## Compact archive

At the user's request, removed bulk logs/statistics, generated orbit/element-position displays, font caches and high-resolution raw tables. All 151 LaTeX files, TikZ fragments, the directly named OPALX/PyORBIT input package, non-generated analysis code and compact validation summaries remain. Byte-identical JSON/CSV copies in historical report bundles share canonical files through inventory aliases. The build tool restores their original paths in its disposable checkout. All 14 standalone documents were rebuilt successfully after compaction; see `latex-validation/compact-rebuild.json`.

Archived `.gitignore` files are now named `original-gitignore.txt` so their historical rules cannot silently exclude archived sources. The original paths and hashes remain in the inventories. Removed records are explicitly marked, rather than claimed as retained. `compaction.json` records the size reduction. Source checkouts, PR #637, published PDFs and external figure assets were not changed by this compaction.
