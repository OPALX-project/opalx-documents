# Python Script Inventory

Relocated to PR #300 on 22 November 2026. This historical inventory is not a
current launcher specification. Scripts remain in `/Users/adelmann/git/opalx-beambeam`;
use [Experiments.md](Experiments.md) and [README.md](README.md) for current tools.

> Historical inventory: the paths and "current" labels below predate the
> numbered-experiment cleanup. For the authoritative current tools and launchers,
> see [Experiments.md](Experiments.md). The legacy shared GUI and
> helpers were archived in `tmp/sandbox-cleanup-20261003/shared-legacy-scripts.tar.gz`;
> they are no longer active tools. Earlier deleted inputs/prototypes are described
> in the sandbox cleanup archives, not restored by this inventory.

This inventory focuses on Python files present in this checkout. The BeamBeam
workflow scripts in `sandbox/` are the active analysis tools for PR #300; the
large `pyOPALTools/` tree is a bundled OPAL analysis package.

## Active BeamBeam Sandbox Tools

| Path | Role | Inputs | Outputs | Notes |
| --- | --- | --- | --- | --- |
| `sandbox/beambeam_analysis.py` | Combined BeamBeam front-end. Dispatches to the collision-window viewer, manufactured analytic view, and OPALX-vs-analytic comparison. Provides a Tk GUI, with a local browser fallback. | RHO dumps, BeamBeam HDF5 diagnostics, optional OPALX input files. | PNG/GIF plots, GUI/browser views. | Current top-level UI for manual inspection. Subcommands: `gui`, `collwin`, `analytic`, `compare`. |
| `sandbox/checkCollWin.py` | Collision-window/RHO dump viewer. Parses scalar RHO debug dumps and overlays BeamBeam element geometry, collision-window bounds, IP, and bunch centers. | `*-RHO_scalar-collwin_vis-*.dat`; optionally the corresponding `.in` file or explicit geometry values. | Single PNG or GIF. | Current low-level viewer used by `beambeam_analysis.py collwin`. Defaults to grid-index view; `--physical` switches to physical coordinates. |
| `sandbox/read_beambeam_h5.py` | BeamBeam HDF5 diagnostics reader. Summarizes stored diagnostic states and plots density views. | `*-beambeam_diagnostics.h5`. | Console overview table, line-density plots, GIFs, x-z galleries. | Current tool for verifying HDF5 diagnostics. Actions: `--overview`, `--line-density-z`, `--gallery-xz`. |
| `sandbox/beam-beam-manufactured-solution.py` | Analytic manufactured-solution tool for a symmetric 3D Gaussian BeamBeam case. Can compare OPALX HDF5 fields against analytic `rho`, `phi`, and `E` fields. | Analytic parameters, or `--compare-h5` plus `--step`. | Console error metrics and diagnostic PNGs. | Current physics comparison tool used by `beambeam_analysis.py analytic/compare`. Assumes a symmetric Gaussian pair. |

## BeamBeam Inputs And Generated Artifacts

| Path | Role | Notes |
| --- | --- | --- |
| `sandbox/beambeam-1.in` | OPALX BeamBeam test input with longer BeamBeam element/window. | Current syntax uses `NALLOC` and `BCHARGE`. Produces `data/sandbox/beambeam-1-beambeam_diagnostics.h5`. |
| `sandbox/BeamBeam-2.in` | OPALX BeamBeam test input with shorter drift/BeamBeam/drift layout and finer timestep through the IP. | Current syntax uses `NALLOC` and `BCHARGE`. Produces `data/sandbox/BeamBeam-2-beambeam_diagnostics.h5`. |
| `sandbox/data/*_ElementPositions.py` and `data/sandbox/*_ElementPositions.py` | Generated geometry viewer/export scripts from OPALX element-position output. | Not hand-maintained analysis code. They contain embedded base64/zlib geometry and optional PyVista export/view helpers. |

## Legacy BeamBeam Sandbox Scripts

| Path | Role | Status |
| --- | --- | --- |
| `sandbox/oldpy/integrateCounterpropagatingGaussians.py` | Direct numerical Coulomb integration for two counter-propagating Gaussian bunches; scans fields along axes and can plot results. | Legacy/prototype. Superseded for normal workflow by `beam-beam-manufactured-solution.py`. |
| `sandbox/oldpy/makeAsciiMovie.py` | Renders stored ASCII collision frames into PNGs/GIFs using Pillow. | Legacy utility for older ASCII-frame diagnostics. |
| `sandbox/oldpy/makeRhoMovie.py` | Makes GIFs from OPALX RHO debug dumps using x-y projections and metadata overlays. | Legacy utility. `checkCollWin.py` is the current richer RHO/collision-window viewer. |
| `sandbox/oldpy/visRho.py` | Thin wrapper that re-execs `checkCollWin.py --no-geometry`. | Compatibility wrapper. Note: as written it looks for `checkCollWin.py` inside `sandbox/oldpy/`, while the current script is one directory above. |

## Other Local/Support Scripts

| Path | Role | Notes |
| --- | --- | --- |
| `sandbox/OPALX-IMPACT/plot_extracted_graph.py` | Replots digitized OPAL/ImpactT comparison data and can overlay OPALX `.stat` columns. | Uses pandas/matplotlib. Separate from BeamBeam. |
| `tools/Normalization2DMaps/normalization.py` | Computes a normalization ratio for 2D field maps by comparing global peak to on-axis peak. | Python 2 style print statements; likely legacy. |
| `opalx-manual/examples/gen_seed.py` | Generates `gen_seed.opal` containing a time-derived `REAL genseed = ...;`. | Manual/example helper. |
| `NightlyBuildX/scripts/run-reg-tests.py` | Scans and runs OPAL regression-test directories, then reports/publishes results. | Regression infrastructure. |
| `NightlyBuildX/scripts/OpalRegressionTests/*.py` | Regression-test package used by the NightlyBuildX runner. | Includes test execution, `.stat` comparison, and report generation. |

## Bundled `pyOPALTools`

`pyOPALTools/` is a separate OPAL Python analysis package, not BeamBeam-specific
code. It contains about 90 Python files, grouped as:

| Area | Role |
| --- | --- |
| `pyOPALTools/opal/datasets/` | Dataset wrappers for OPAL output files such as H5, SDDS/stat, timing, memory, loss, sampler, optimizer, field, grid, and solver data. |
| `pyOPALTools/opal/parser/` | Parsers for OPAL output formats: H5, SDDS, stat, timing, lattice, loss, optimizer, field, histogram, track-orbit, and related files. |
| `pyOPALTools/opal/analysis/` | Higher-level analysis classes for statistics, H5, field, optimizer, sampler, orbit, Pareto fronts, and standard OPAL output. |
| `pyOPALTools/opal/visualization/` | Plotting classes for the datasets and analyses, including stat, H5, timing, field, memory, optimizer, probe, and solver plots. |
| `pyOPALTools/optPilot/` | opt-pilot visualization tools, mostly legacy Python 2 era according to its README. |
| `pyOPALTools/amr/`, `db/`, `jobhandler/`, `pc/`, `surrogate/` | AMR helpers, database access, job submission, polynomial chaos, and surrogate-model support. |
| `pyOPALTools/tests/` and `doc/source/json-reader/` | Package tests and documentation examples. |

## Practical Recommendation

For the BeamBeam PR, treat these as the current scripts to keep maintained:

1. `sandbox/beambeam_analysis.py`
2. `sandbox/checkCollWin.py`
3. `sandbox/read_beambeam_h5.py`
4. `sandbox/beam-beam-manufactured-solution.py`
5. `sandbox/beambeam-1.in` and `sandbox/BeamBeam-2.in` as their paired runnable inputs

The `sandbox/oldpy/` scripts should either stay clearly marked as legacy or be
removed after confirming no workflow still depends on them.
