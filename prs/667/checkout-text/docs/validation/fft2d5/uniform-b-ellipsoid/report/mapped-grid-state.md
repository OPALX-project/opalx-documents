# Mapped-grid explanation, 2026-11-03

Historical task record: the later Dubin/SACR illustration update expands the
full report to 38 pages and moves Section 15 to pages 29--34. The separate
six-page technical note and the mapped-grid LaTeX/TikZ content are unchanged.

Goal: add a detailed, code-consistent LaTeX explanation with native TikZ
graphics, compile the full validation report and a focused technical note.

Scope: documentation and figures only; preserve all numerical evidence,
production sources and unrelated dirty FFA changes. No simulations,
numerical tolerance changes, commit or push. The PDF skill edit marker ran
once for this task, with two expected PDF outputs; do not run it again.

Design: IPPL remains UniformCartesian. OPALX maps physical particle positions
to logical (u,y,s), deposits coordinate density, evaluates custom approximate
curved-source G/H/F convolutions with IPPL FFTs, applies the metric gradient,
then interpolates and rotates fields back. Physical images of coordinate
cells must not be described as native curved IPPL mesh cells. This OPEN
backend is a genuine nonlocal 3D calculation specialized to thin beams;
the retained pipe/PyORBIT comparison is a separate local model.

Ownership: root authors mapped-grid.tex, focused wrapper and report/build
integration; mapped_grid_tikz agent owns only two new figures/*.tikz;
mapped_grid_science_audit reviews physics/code correspondence; bundle agent
checks packaging.

Current status: complete. Full report 36 pages, new Section 15 pages 27--32;
focused note six pages. Both compiled cleanly and received scientific and
visual review. All 1045 evidence hashes verify; 1057 data files and 46 older
figures are unchanged. All six note pages plus changed report pages inspected;
actual running-header pixels are present and consistent. Source ZIP contains
1165 files, CRC clean. Independent extracted-source builds produce exact
36/6-page text matches with the delivered PDFs. Final metadata-only updates
to this file, HANDOFF.md and QA.md are rebundled; tested content is unchanged.

Outputs under /Users/adelmann/git/opalx/output/pdf/:
- fft2d5-mapped-grid-explanation.pdf
- fft2d5-uniform-field-validation.pdf
- fft2d5-uniform-field-validation-source.zip
- fft2d5-uniform-field-validation-artifacts.json

No additional physics work or simulation is required for this request.
