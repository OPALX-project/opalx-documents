# Reference-model illustrations, 2026-11-03

User request: add illustrations of Dubin and SACR to the field-validation
report, in the established native TikZ style.

Scope: two model schematics and their explanatory captions integrated into
the existing report. Preserve all numerical evidence, old figures,
production code and unrelated user changes. The separate six-page
mapped-grid note remains unchanged. No simulations, commit or push.

The PDF edit marker ran once for this task (one expected PDF output).
Root owns report integration/build/packaging. Agents own two new TikZ
sources and independent scientific/layout review. Status: complete.
User's follow-ups established that the present map is orthogonal, not
conformal, without ruling out other mapped formulations. This explanation
is included on the SACR illustration page.

Full report: 38 pages. Dubin Figure 2 on page 3; SACR Figure 11 on page 13.
Both new figures/captions and integrated pages 3/4/13/14 received scientific
and visual review. Eleven new/transition pages rendered. LaTeX has zero
warnings, undefined references and box issues. All 1045 evidence hashes pass;
1057 data files and 48 preexisting figure files are byte-identical to the
previous source ZIP. No numerical result or solver source changed.

The 1168-file source ZIP passes CRC and byte matching. Independent extracted
compilation produces exact text matches on all 38 report pages. The separate
six-page mapped-grid-note PDF is unchanged. Final metadata-only edits to this
file, HANDOFF.md and QA.md are rebundled; tested sources/data stay identical.
The output PDF, ZIP and updated artifacts JSON are in output/pdf/.
