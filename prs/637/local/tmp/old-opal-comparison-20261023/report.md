# OPAL 2022.1 vs OPALX: coarse accelerating radial profiles

Both runs use the PSI Ring maps/RF configuration with trim-coil strength zero,
72 MeV launch, 2 mA at50.65MHz (39.486673pC/bunch),8^3 grid,
4096launched particles and nominal timestep164.527805ps (720steps/turn).
OPEN/STANDARD Green functions and BBOXINCR=2 were selected in each interface.
Old OPAL uses native cyclotron LF2/FFT; OPALX uses Boris, one GAMMAZ bin and
its MIDPOINT frozen-self-field split. The operator sequences are not identical.
Each simulation uses one MPI rank; oldOPAL one thread, OPALX four threads.

## Checks and matching

- OPAL2022.1 binary SHA2563e20fe1e8b040e10dcbb958b2d1a92d5020f5397361b230a615c0e41ca0b5ecd.
  Old full run returned0 in181.99s for bounded140000steps. Data after the first
  580MeV reference crossing are excluded from the analysis; old code was not
  modified to add an energy-stop interface.
- Legacy first580MeV reference crossing: step133932,t=22.0355380059us,
  K=580.467800755MeV. OPALX localized stop:t=22.0354053688us,
  K=580.470767685MeV. Terminal-clock difference is132.64ps, below one nominal step.
- Legacy FROMFILE uses radial/tangent/vertical offsets atPHIINIT110degrees.
  Conversion from OPALX Cartesian samples was verified in the initial global
  HDF5 snapshot:4095common nonreference particles match within1.46nm position
  and3.80e-10 normalized momentum. Old OPAL forces particle0 to its reference
  and excludes it from phase-space moment output. ID0 is excluded from BOTH
  probe curves. Its different charge placement remains a small collective-model
  difference, not removed merely by excluding it from the plotted records.
- Bare oldLF2 reference control versus OPALX reference at133matched-time snapshots:
  maximum positiondifference0.32747mm, momentumdifference1.7574e-4,
  energydifference3.6281keV. This bounds an external-transport discrepancy of
  this coarse setup; it is not an asymptotic convergence statement.
- Native legacy probe turns are one-based; subtract1. Common selected passages
  are178..185. Every selected record has a unique(ID,turn). Same0.1mm physical
  bins and physical macrocharge are used, with no area normalization.
- Legacy probe plane residual is up to2.27um over the580MeV window; OPALX
  residual is below1e-11m. Observation algorithms differ slightly.

## Results

Maximum absolute per-turn mean-radius difference:1.0583mm.
Old/new rms-width ratio spans0.8311..1.1125 (up to16.9% narrower or11.2% wider).
Summed-profile binwise L1 difference / mean total charge:0.2920.
This last metric includes finite-sample/bin noise and is not a numerical-error bound.

Old OPAL retains4096particles, versus4049for OPALX at its580MeV threshold.
After excludingID0, plotted per-turn counts are4095for old OPAL and
4051(first two turns)/4048(remaining six) for OPALX. The OPALX losses are from
its10sigma boundary. Legacy deletion criteria/cadence have not been matched;
loss differences must not be assigned uniquely to the space-charge solver.

The overall peak structure agrees qualitatively; individual peaks and tails
show resolved differences. The run is much too coarse to claim quantitative
machine validation. Both transport only one bunch; neighbouring-turn self fields,
septum losses and a matched accelerating Vlasov equilibrium are not modeled.
The earlier16^3 failure near584MeV is not diagnosed by this different8^3 case.

## Reproduction and artifacts

`stage.py` prepares fresh smoke/full inputs; `run_old.py` executes installed old
OPAL with its environment profile; `run_bare.py` makes the external reference
control. `check_initial_and_bare.py` verifies coordinate matching and reference
transport. `compare.py` reads completed native probe outputs and makes:

- comparison.png/pdf: summed final8profiles and per-turn mean±rms.
- per-turn-comparison.png/pdf: eight individual paired profiles.
- turn-comparison.csv, differences.csv, summed-line-densities.csv.
- summary.json: complete settings, launch, metrics and limitations.

All source inputs, original output files, hashes and logs are retained.
No production C++ source or numerical reference/tolerance was changed for this
comparison. No commits/pushes.
