# Manual RF review integration checks — first endpoint candidate

These are manual OPALX runs, separate from CTest/native unit tests. No regression fixtures or references were modified. No Python was used. The maintained Cyclotron-RF-Stop input/maps were copied to private case directories; EKINSTOP=0.073 GeV and TYPE=NONE were retained. The two-particle cases contain two identical protons with doubled bunch charge. PSDUMPFREQ=100 enables final HDF5 inspection.

Binary: `/Users/adelmann/git/opalx-master/build_openmp/src/opalx`.
SHA256: `93b28c43a17fddc01a13f765c874ee595c89a0be38b8c57c5c94c4ec41309970`.
Base HEAD: `61c90499b3f5638f2e26612561e149839774666d`, with the current uncommitted ownership, collective output and RF review fixes. Exact source/input hashes, diff, commands, timestamps, exit codes and logs accompany the cases.

## P1: terminal RF endpoint remains unresolved

| Protons | MPI ranks | Exit | Particle energy [MeV] | Reference energy [MeV] |
|---:|---:|---:|---:|---:|
| 1 | 1 | 0 | 72.8005598452900 | 73.2730984246719 |
| 1 | 2 | 0 | 72.8005598452909 | 73.2730984246719 |
| 2 identical | 1 | 0 | 72.8005598452909 each | 73.2730984246719 |
| 2 identical | 2 | 0 | 72.8005598452909 each | 73.2730984246719 |

The first 64-epsilon terminal-endpoint candidate still misses the final full kick in the actual fixture. All cases share final time `6.037904845375861e-8 s` and identical reference state. Particle energy differences across cases are only `8.38e-13 MeV`; parity alone does not establish the correct terminal impulse. Final bunch-frame particle/reference position offsets are approximately `(2.24e-12,0,3.4e-13) m`. Investigate the actual signed final RF-plane residual and accumulated transform/event arithmetic before selecting any wider endpoint bound.

HDF5 `MASS` is total bunch macro-mass (`H5PartWrapperForPT.cpp` uses `getTotalMass()`), so the analysis divides by the number of identical one-proton macroparticles to recover the physical proton mass. The reported particle energies also match the final SDDS mean energy. The initial analysis briefly treated total mass as per-particle mass and was corrected; those doubled two-particle energies are not physical results.

## P2: accepted probe hits survive reference-trial failure

The `failure-probe-verified-*` cases use a laboratory probe at x=-746.695032 mm, z=[1400,2400] mm and deliberately set RF1=-500 MV. Both one- and two-rank runs terminate with expected exit 156 and `ParallelTracker::terminalEvent: Unsupported or unphysical SINGLEGAP kick`.

Both cases preserve exactly one accepted `.loss` row and histogram sum 1. The accepted crossing is identical at output precision: x=-0.746695 m, z=1.89356 m, time `4.86509e-10 s`. This precedes the first RF1 crossing (~1.025 ns) and the normal 100-step probe flush (~4.11 ns), so persistence tests the new failure flush rather than a periodic save.

The earlier `failure-one-rank`/`failure-two-ranks` cases used a probe around the origin, overlooking the RING launch translation. They correctly failed at the RF kick but recorded no crossing; they are retained as staging diagnostics and are not the successful P2 check.

Reproduction/analysis: `run-manual.sh`, `analyse-manual.sh`, `extract-final.awk`; raw full-precision output: `final-particles.csv`, `integration-checks.tsv`, `rank-and-particle-differences.tsv`.

### Terminal-plane residual derived from full-precision output

For RF4, composing the input origin with the RING translation gives
`o=(0.35592778157577948-0.69669503200000005, 0, -2.1527616675220353+1.91415387) m`.
Its positive crossing normal is `(0.8191520442889918,0,0.5735764363510461)`.
Using the final reference momentum to rotate the bunch-frame displacement into
laboratory coordinates gives the particle/reference offset
`(1.1748685718828622e-12,0,-1.9436133357517368e-12) m` for the one-rank host case.
The derived reference plane distance is `+1.8874e-15 m`; the particle/reference
plane offset is `-1.52415e-13 m`, leaving particle plane distance approximately
`-1.50527e-13 m`. The initial 64-epsilon bound is only `2.68997e-14 m`.
These values support accumulated frame/event arithmetic error rather than merely
a single final transform. A fixed 512-epsilon replacement would cover this case
but would not by itself justify behavior for longer accelerating trajectories.
