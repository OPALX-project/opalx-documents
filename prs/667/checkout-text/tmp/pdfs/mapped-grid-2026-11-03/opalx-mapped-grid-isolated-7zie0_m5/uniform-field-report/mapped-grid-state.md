# Mapped-grid explanation, 2026-11-03

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
advises packaging. Current status: drafting. Next: scientific review,
compile both documents, inspect rendered new/changed pages, verify evidence,
update source ZIP and artifact metadata, and deliver PDFs plus editable source.
