# Manual RF terminal-event integration check

These are manual OPALX simulation runs, separate from CTest and native unit tests.
They copy the maintained Cyclotron-RF-Stop fixture without changing its files or references.
EKINSTOP remains 0.073 GeV (73 MeV), field solver remains NONE, and all protons are identical.
The two-particle variants set NALLOC/NPARTDIST=2 and double the bunch charge, preserving one proton's physical charge.
PSDUMPFREQ=100 enables a forced final phase-space dump; STATDUMPFREQ retains the forced final statistics row.

Cases: one proton on one/two ranks, and two identical protons on one/two ranks.
Input copies and their hashes make the manual checks reproducible without adding fixture/data dependencies to unit tests.

Do not execute until the updated `opalx_exe` target has finished building.
Run with `./run-manual.sh /absolute/path/to/updated/opalx --execute`.
The runner records the executable hash, source manifest, arguments, timestamps, exit code and full log.
Expected checks: successful reference target, final particle count, final reference/particle energies >=73 MeV,
complete terminal kick, final momentum/time parity across rank count, and identical two-particle states.

The two `failure-*` cases add a probe at laboratory x=-50 mm, z in [-500,500] mm,
and set RF1 to -500 MV. The proton reaches this probe around 0.5 ns and RF1 around
1.025 ns, before the normal 100-step flush cadence (~4.11 ns). The deliberately
unphysical kick must produce a nonzero exit while preserving exactly one accepted
probe crossing in `accepted-before-failure.loss` and one count in its histogram.
Both one- and two-rank runs must preserve the same crossing/time and diagnostic.

Correction after inspecting the actual launch: RING already translates the launch to
(-0.696695032,0,1.91415387) m. The valid failure cases are
`failure-probe-verified-{one-rank,two-ranks}`, whose probe is x=-746.695032 mm,
z=[1400,2400] mm. The original failure cases are preserved as staging diagnostics.
`REPORT.md` records the current unresolved terminal-kick result and verified failure flush.
