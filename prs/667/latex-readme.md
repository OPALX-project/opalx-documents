# LaTeX archive and compilation

All 151 LaTeX source files found in the checkout are indexed in `latex-inventory.json`, including tables, historical report variants and the interpolation note. TikZ sources, bibliography sections, scripts, small inputs and result records are retained under `checkout-text`. Original paths and hashes are preserved in the chunked inventory.

**All 14 standalone documents compile with latexmk/pdflatex**, with no undefined references/citations reported. Included fragments are compiled through their parent documents. The one backup document under `.build` is compiled from its parent report directory, matching its original relative figure paths. No scientific wording, model or result was changed.

The main documents are:

- [FFT2D5 field-validation report (38 pages)](../../reports/2026/pr667/fft2d5-uniform-field-validation.pdf).
- [Mapped-grid technical note (6 pages)](../../reports/2026/pr667/fft2d5-mapped-grid-note.pdf).
- [Model-comparison paper (10 pages)](../../reports/2026/pr667/fft2d5-model-comparison.pdf).
- [Interpolation note (3 pages)](../../reports/2026/pr667/interpolation-polynomial-smoothing.pdf).

These are historical research reports. SACR, the experimental 3D free-space operator and curvature extensions described there are **not** the supported model merged by PR #667. Preserve that distinction when citing the results.

## Rebuild

From this directory:

```sh
~/.venv-h6/bin/python tools/build_latex.py --output /tmp/pr667-latex
```

The builder verifies and stages the archived source files and required figures, then compiles each standalone document. Four historical manual-diagram files contain absolute input paths; those paths are relocated only in the disposable staging copy. Recorder checks confirmed that compilation does not read the original OPALX checkout. Required compact figure PDFs are stored outside this text-only archive in `examples/2026/2d5-1/latex-assets`. Compiled reports live outside it in `reports/2026/pr667`.

`latex-validation/compile-results.json` records the original checks; `latex-validation/compact-rebuild.json` records a fresh successful rebuild of all 14 standalone documents after compaction. Bulk text logs were removed. Build products and PDF renderings are not stored in `prs/667`. Large field/particle snapshots are excluded; regenerating historical numerical datasets or all figures may require the separately recorded original run assets. The LaTeX rebuild itself uses the preserved figure assets and needs no simulation.

Historical report JSON/CSV duplicates are represented by inventory aliases; the builder reconstructs their original locations before compiling. All LaTeX/TikZ sources and required figure assets remain available.
