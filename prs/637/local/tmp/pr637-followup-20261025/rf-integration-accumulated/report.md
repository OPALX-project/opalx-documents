# Manual RF review integration — accumulated frame arithmetic

All six manual checks pass their intended outcomes with the accumulated-frame terminal convention. These are separate OPALX simulation runs, not CTest/native unit tests. The native unit tests remain self-contained C++; they neither run these scripts nor consume these copied inputs/maps. The maintained regression fixtures and reference files were not modified.

## Provenance

- Executable: `/Users/adelmann/git/opalx-master/build_openmp/src/opalx`.
- SHA256: `26ae4cdec13aa24bcacea47942ad8a0a86b3cddb9a65f8dc37f3847ba76f04a8`, unchanged across all six runs.
- Base revision: `61c90499b3f5638f2e26612561e149839774666d`, with current uncommitted source fixes. Source hashes/diff and input hashes accompany the runs.
- OpenMP threads: 1. MPI ranks: as shown below. No self fields (`FIELDSOLVER TYPE=NONE`).
- Input copied from `regression-tests-x/RegressionTests/Cyclotron-RF-Stop`; `EKINSTOP=0.073 GeV` retained. `PSDUMPFREQ=100` enables forced final HDF5 output. Two-particle inputs contain two identical physical protons and double the bunch charge.
- Commands, timestamps, exit codes, full logs and full-precision final HDF5 dumps are preserved per case.

## P1: all particles receive the complete terminal kick

| Physical protons | MPI ranks | Exit | Particle energy [MeV] | Reference energy [MeV] |
|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 73.27309842485165 | 73.27309842467186 |
| 1 | 2 | 0 | 73.27309842485249 | 73.27309842467186 |
| 2 identical | 1 | 0 | 73.27309842485249 each | 73.27309842467186 |
| 2 identical | 2 | 0 | 73.27309842485249 each | 73.27309842467186 |

All cases finish at `6.037904845375861e-8 s` and share exactly the same reference position/momentum in the extracted output. The terminal particle energy gain of approximately `0.47253857956 MeV` restores the full RF4 kick missed by the first endpoint candidate. Counts are exactly 1/2 as requested; the two-proton states are identical within each run.

Maximum differences across rank/particle variants:

- Particle energy: `8.384404281969182e-13 MeV`.
- Bunch-frame momentum components: below `2.90e-15 mc`.
- Bunch-frame position components: below `2.09e-14 m`.
- Reference position/momentum and final time: zero at full extracted precision.

The final particle position arrays are unchanged from the first candidate's missed-kick runs: the correction assigns a complete endpoint impulse without changing the common duration, adding drift or projecting positions. Physical-particle/reference energy differences remain about `1.8e-10 MeV` due to their independently accumulated arithmetic.

Final HDF5 `MASS` is total bunch macro-mass (`H5PartWrapperForPT.cpp` uses `getTotalMass()`), so analysis divides by the known number of identical one-proton macroparticles to recover proton rest mass. The resulting energies also match the final SDDS mean energy.

## P2: accepted hits persist before a failed reference trial

The two failure cases place a laboratory probe at x=-746.695032 mm, z=[1400,2400] mm and deliberately set RF1=-500 MV. Both one- and two-rank runs produce expected exit 156 and `ParallelTracker::terminalEvent: Unsupported or unphysical SINGLEGAP kick`.

Both preserve exactly one `.loss` row and histogram sum 1. At ASCII output precision the crossing records agree: x=-0.746695 m, z=1.89356 m, time `4.86509e-10 s`. This precedes RF1 (~1.025 ns) and the normal 100-step periodic flush (~4.11 ns), so the saved hit confirms the new collective trial-failure flush. The failed trial itself creates no extra hit.

## Numerical scope and limitations

The first candidate used a one-step `64*epsilon*L` endpoint classification allowance (~`2.69e-14 m`) and still missed an actual signed RF4 residual of ~`-1.5e-13 m` after 1468 accepted frame updates. Its results are retained in `../rf-integration`.

The corrected terminal-only allowance is `64*N*epsilon*L`, with `N=max(1,acceptedGlobalStep+1)` and `L=max(1 m,absolute start/end laboratory components)`. It budgets repeated frame arithmetic rather than fitting a larger fixed constant to this fixture. At N≈1468 it is approximately `3.95e-11 m` (39.5 pm), conservatively exceeding the measured 0.15 pm residual.

This is a first-order arithmetic classification resolution under `64*N*epsilon << 1`; it is not an ODE, field-discretization or PIC accuracy bound. Arrivals inside this allowance are unresolved and receive the complete terminal kick by convention, potentially including a physically later particle within that interval. Crossings beyond the allowance are excluded. Ordinary steps retain strict crossing signs. A clearly upstream start is required; arbitrarily small timesteps whose entire motion fits within the allowance are not covered by this convention. Nonfinite or >=1 accumulation factors are rejected.

These short NONE-solver checks validate the review's terminal-kick and failure-flush cases. They do not establish convergence or long-run accelerating PIC accuracy, and do not replace A100/GH200 validation.

## Reproduction and raw evidence

- `run-manual.sh`: six case commands and provenance capture.
- `analyse-manual.sh`, `extract-final.awk`: shell/HDF5/awk analysis, no Python.
- `final-particles.csv`: all final particle states and computed energies.
- `integration-checks.tsv`: counts, energies and failure-flush checks.
- `rank-and-particle-differences.tsv`: full-precision maximum differences.
- Per-case `run.log`, `command.txt`, `final-state.h5dump`, `final-stat-row.txt`, `input.sha256`.
