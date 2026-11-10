# PSI Ring probe demonstration — complete

Date: 2026-10-23. Workspace: /Users/adelmann/git/opalx-master, branch 615-probe-command-does-not-work.
No production source, tests, numerical tolerances, or public manuals changed for this demonstration.
No commits or pushes performed.

## Inputs and provenance

- Found old PSI Ring inputs in /Users/adelmann/git/opalx/sandbox/cyclotron/opal/cyclotron1.in and cyclotron2.in.
  Copies are in legacy/. These old inputs do not contain probes.
- Used existing OPALX ports under /Users/adelmann/git/opalx/sandbox/Regression-Tests/
  ring-cyclotron-coasting-1 and ring-cyclotron-accelera-1; did not rederive the transport model.
- Added radial probes at 0 and 90 degrees, r=1900–4700 mm, STEP=1 mm.
- Added the exact old manual PROBE example:
  (4166.16,-1226.85)→(4250,-1241.3) mm in old horizontal x/y, now laboratory X/Z.
- Coasting duration extended from one to ten turns, MAXSTEPS from 2000 to 20000;
  reduced output cadence and selected HDF5 probe output.
- Acceleration launch, fields, RF parameters, zero trim-coil strength, timestep
  (2880 steps per nominal turn) and 590 MeV target were retained from the existing port.
  This is not a new calibration or an assertion of exact legacy-deck equivalence.
- One proton, no space charge, one MPI rank, one OpenMP thread throughout.
- manifest.json records input/map/executable hashes, source revision and local diff,
  launch commands, elapsed times and zero exit codes for all four runs.

## Successful accelerating Ring run

Input: acceleration-590MeV/acceleration.in.
Final energy: 590.326824538 MeV after a complete RF4 gap kick.
189 completed reference turns; 545799 accepted integration steps.
Final time: 22.449771273 µs; path length: 4254.864206 m.
Final particle/reference separation: 3.27497e-10 m.

- radial0: 189 crossings, radii 2146.257–4393.964 mm.
- radial90: 189 crossings, radii 2143.140–4402.262 mm.
- extraction: 3 crossings, zero-based reference turns 186, 187, 188;
  radii 4345.043–4359.587 mm and kinetic energies 581.472, 584.425, 587.380 MeV.
- All probe histogram totals equal HDF5 hit counts. .peaks matches the per-turn
  arithmetic mean radius. Times increase strictly; hits satisfy segment bounds.
  Extraction-plane residual is at most 1.01e-16 m.

The probe-off control completed normally. All 546 saved particle phase-space records,
reference coordinates/momenta, times, path lengths and global step counts are
exactly identical. Every numerical statistics row is also identical.

## Coasting anomaly retained for follow-up

The ten-turn coasting run and its control completed normally with constant 72 MeV
kinetic energy. However, the particle separates strongly from the reference:
final separation 22.998475 m. radial0 records 8 hits and radial90 9,
instead of the ten that a confined once-per-turn orbit would give; extraction
correctly has no hits. Probe-off reproduces every saved state and statistics row
exactly, so this excursion is not caused by PROBE. Its cause has not been diagnosed.
Do not present the ten-turn coasting run as a successful closed-orbit validation.
See coasting-anomaly.png and coasting-10turns/statistics.csv.

## Results and reproduction

- ring-probes.png / ring-probes.pdf: visually reviewed four-panel accelerating-ring figure.
- summary.json: numeric run/probe summaries and exact control-comparison results.
- acceleration-590MeV/*-hits.csv: crossing phase space, time, energy and radius.
- Both run directories retain input/maps, logs, statistics, phase space, and
  .h5/.hist/.peaks outputs (no phase-space probe file for a no-hit detector).
- stage_and_run.py and run_controls.py reproduce runs in a new directory after
  copying the scripts there and adjusting repository/source roots if necessary;
  existing run folders and probe outputs are deliberately not overwritten.
- ~/.venv-h6/bin/python analyze.py revalidates the retained results and regenerates figures.

Next step if requested: diagnose the magnetic-only ten-turn particle/reference
separation independently of probe development. FFA/RingElement support is still deferred.
