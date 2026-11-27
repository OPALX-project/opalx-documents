# Compact OPALX comparison

`xxx-short.pdf` is the six-slide compact copy. It contains benchmark parameters, adopted inputs, the OPALX 4/6/8-turn tune table, differences from the paper, and three KV footprint slides (50/70/90 pi mm mrad). Results use the completed PR693 build, displayed simply as OPALX. The previous-build comparison, runtime section, and shorter-window fit-quality checks are omitted. Absolute OPALX results appear only in the turn-window table. The original full deck is preserved.

Regenerate tables and compile from this directory:

```sh
~/.venv-h6/bin/python scripts/make_short.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/pr693-short-build xxx-short.tex
cp /tmp/pr693-short-build/xxx-short.pdf xxx-short.pdf
```

These tables reuse stored ten-turn tracking histories; no simulation is rerun. Fit windows use the same accepted core cohorts. Adopted beam parameters and the median-versus-endpoint limitation remain explicit. PDF QA is recorded in `data/short-presentation-qa.json`.

The footprints overlay the previously digitized approximate visible-color convex hulls from Zhou et al. Figure 6 (CC BY 4.0), without fitting or rescaling. These are image-derived outlines, not probability contours or exact particle boundaries. Digitization methods and limitations are preserved in `data/zhou-fig6-hull-provenance.json`.

To regenerate the footprint PDFs, copy the completed PR693 `space-charge-tunes.csv` and `space-charge-off-tunes.csv` files for each case from LUMI, preserving the root/`emittance-70`/`emittance-90` layout, then run:

```sh
~/.venv-h6/bin/python scripts/plot_short_hulls.py /path/to/case-csv-directory
```

`MAX_Y_POWER=2` was checked directly on LUMI in all six production input files on 25 November 2026: all 80 scaling FFA elements in each file use 2. This is an input verification, not an inference from the deck or the order-3 comparison runs.

Latest user-edited version comments out the turn-window slide. The comparison slide now explicitly identifies the median as an OPALX analysis choice and states that the paper does not specify its PIC core-tune extraction method. User changes to source and table labels were preserved.

Plot styling on pages4–6: zero-current reference omitted from left panels; bare tune marked by an open blue circle in right panels; all right-panel reference lines and grid removed.

2026-11-26: pages4–6 now show maximum tune depression, defined as the lowest accepted horizontal tune in each initial0.25m slice. Same eight-turn per-particle estimates and validity cuts; no tune refit or tracking rerun. Percentile bands removed; single extrema are sensitive to unusual fitted tunes and particle count. Reproducible slice minima/counts are in data/max-depression-slices-{50,70,90}.csv. Right panels retain the full particle footprints. Page3 still compares central-bunch medians and is labeled accordingly.
