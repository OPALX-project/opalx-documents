# Compact OPALX and paper comparison

`xxx-short.pdf` is the six-slide presentation, updated26November2026. The matching editable source is `xxx-short.tex`. The full presentation and other PR records are unchanged.

1. Benchmark machine/mesh parameters.
2. Adopted inputs and actual production settings.
3. Maximum central-bunch tune depression for50/70/90pi mm mrad, paper PIC comparison and runtime per turn.
4–6. New OPALX KV slice profiles and footprints with approximate paper Figure6 hulls.

Only OPALX and the paper are compared. No previous-build or zero-current comparison is displayed. The older median/turn-window table is not included. Earlier user-edited source, PDF and README are preserved in `drafts/before-production-f8ac63538915/`.

## Results and estimator

LUMI source f8ac635389152f906f0df022978e6a834e671ba0; production jobs24039424/24039425/24039426 and analysis24039716 all completed exit0. All182825steps (ten nominal turns) and131072particles retained; finite particle/probe diagnostics passed. Two MPI ranks/two GPUs per run.

`data/production-f8ac63538915/comparison-summary.json` supplies the table. Maximum depression means the minimum accepted particle tune within |initial s|<0.15m, minus the bare tune. The per-particle fits use64probe samples (eight turns) after discarding16samples (two turns). Acceptance uses the established coherence and phase-winding cuts. This is our analysis choice; the paper's PIC core extraction statistic is unspecified. A maximum is sensitive to particle count and accepted extreme fits. The vertical coordinate y here corresponds to paper z; the paper text does not supply a numerical vertical PIC core tune.

Runtime is OPALX timing.dat mainTimer wall maximum divided by ten nominal turns, including startup/warmup. The files round all total times to11620s: approximately1162s/turn (19.37min/turn). Slurm allocation elapsed times differ slightly and include launch/teardown.

## Input verification

The copied shared `lattice.in` has `REAL MAXYPOWER=5` and all80magnets use `MAX_Y_POWER=MAXYPOWER`. Its SHA256 af0edd9b76e407a4db9a896fe85602e0661193b76c89dd3781d3e954d1440b6e matches the production preflight checksums. The header comment claiming2 is stale. The deck reports5. A copied50case production input and verification metadata are in the same data folder. Red annotations proposing200turns/beam-following mesh were preserved in the backup; the deck describes these completed ten-turn runs and the input mesh parameters.

Limitations remain: longitudinal self-fields disabled; zero-current-optics KV launch, not SC matched; full-ring763cells provide127.9945cells across the initial bunch, rather than a bunch-local128cubed grid. One mesh and timestep do not establish numerical convergence.

## Footprints

`figures/opalx-production-f8-{50,70,90}.pdf` are exact copies of the new LUMI analysis PDFs. Left panels show the lowest accepted horizontal tune per0.25m initial slice, not medians. Dashed theory profiles use the paper's theoretical peak and our Gaussian longitudinal profile; they are not digitized curves. Right panels show OPALX particle density, an open blue bare-tune circle, and the previously digitized approximate visible-color convex hulls of paper Figure6. There is no fitting or rescaling. They are image-derived outlines, not probability contours or exact particle boundaries. Original provenance: `data/zhou-fig6-hull-provenance.json` and `data/zhou-fig6-digitized-hulls.csv` (CC BY4.0).

LUMI result root: `/flash/project_465002453/2d5-PRAB-PAPER/analysis/results/production-f8ac63538915/`. Analysis source is `analysis/analyze_production_f8.py`; that script regenerates tune CSVs, slice minima and plots from raw particle histories. No tune fit or tracking was rerun for this presentation update.

## Regenerate and compile

From this directory:
```sh
~/.venv-h6/bin/python scripts/update_short_production.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/pr693-short-build xxx-short.tex
cp /tmp/pr693-short-build/xxx-short.pdf xxx-short.pdf
~/.venv-h6/bin/python scripts/catalog_production_short.py
```

The historical `make_short.py` and `plot_short_hulls.py` operate on archived data and are not used by the updated deck. QA: `data/short-presentation-qa.json`. Asset hashes: `data/production-f8ac63538915/sha256sums.txt` and repository manifest.
