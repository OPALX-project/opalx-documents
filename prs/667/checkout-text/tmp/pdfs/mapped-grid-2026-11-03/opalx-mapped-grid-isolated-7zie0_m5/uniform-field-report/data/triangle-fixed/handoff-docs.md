# Longitudinal model documentation

Goal: document explicit pointwise uniform-round FFT2D5 longitudinal physics,
physical pipe radius independent of numerical transverse widths, retained
legacy closures and PyORBIT model differences. Parent owns code/build/tests
and the benchmark/LaTeX report. No report edits in this documentation task.

Files changed:

- /Users/adelmann/git/opalx/docs/validation/fft2d5/longitudinal-model.md
- /Users/adelmann/git/opalx-manual/user-guide/field-solver/index.qmd
- /Users/adelmann/git/opalx-manual/physics/field-solver/index.qmd
- /Users/adelmann/git/opalx-manual/REMEMBER.md

The user-given separate manual paths are absent; the actual unified manual
checkout is /Users/adelmann/git/opalx-manual. Its AGENTS.md and REMEMBER.md
were read. Existing unrelated HANDOFF.md modifications were preserved.

Documented contract, checked against current API and kernel:

- PIPEMODE="CIRCULAR_UNIFORM", required positive PIPERADIUS=b>=BEAMR=a.
- Fixed uniform circular section centred on reference path; r<=a uses
  1+2ln(b/a)-r²/a², annulus a<r<=b uses2ln(b/r), wallEs=0.
- Active particles outsidephysicalpipe cause coverageerror; no transverse
  conducting-wall solve or material-loss handling is supplied.
- PIPESIZEX/Y are full numerical widths, independent of b in newmode.
- Legacy CIRCULAR retains.67momentclosure, optionalradiusdecouplesitsg;
  absent radius retains historicalminwidth. OPEN/PLATES/NONE rejectradius.
- LabEs contains gamma^-2 and onlylocal/longbeam approximation; no arbitrary
  profile, nonlocalend or fullcurved-source claim. No Qiang correction.
- PyORBITslices differentiate sameconducting-boundary potential; OPALX's
  longitudinal formula is separate from open numerical transverse potential.
  PyRB shares localroundformula but projects transversely and infersradius.

Checks passed:

- env DOCUMENTS_CHECKOUT=../opalx-documents ruby scripts/validate_manual.rb
  (56chapters / text-only asset policy).
- quarto render user-guide/field-solver/index.qmd --profile opalx --to html
- quarto render physics/field-solver/index.qmd --profile opalx --to html
- ruby scripts/validate_rendered_html.rb (63renderedpages, internalanchors).
- git diff --check in both OPALX/manual scopes; scientific/source diff review.

Quarto initial sandbox failures: standard macOSSassDenoKVcache could not open.
XDG/DENOenvredirects do not alter macOScache; routine escalated renders were
auto-approved and succeeded. No runtime/application modification was made.
Render logs: /tmp/opalx-longitudinal-user-render.log and physics-render.log.
Generated HTML onlyunder existingmanual _site; no generatedfilescommitted.

No changes to manual last-reviewedmetadata because fullchapters not reaudited.
No commits, pushes, report edits or physics acceptance claims. Parent can
review/link docs and report completed benchmark results separately.
