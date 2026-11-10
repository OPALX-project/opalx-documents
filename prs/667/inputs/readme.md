# OPALX and PyORBIT inputs for PR #667

## Published 10 m bend comparison

- [OPALX, 10 pC, 100 steps](bend-10pc-100steps/opalx-10pc-100steps.in).
- [OPALX, ZeroSC, 100 steps](bend-10pc-100steps/opalx-zerosc-100steps.in).
- [PyORBIT, 100 steps](bend-10pc-100steps/pyorbit-10pc-100steps.py); use `--zero-sc` for ZeroSC.
- [PyORBIT command](bend-10pc-100steps/pyorbit-command.json), [kinematics helper](bend-10pc-100steps/check_bend_kinematics.py), [shared source metadata](bend-10pc-100steps/source.json), and [original run notes](bend-10pc-100steps/readme.md).

This is the 5 m uniform round bunch, 10 mm transverse RMS, 10 pC, beta=0.001, R=2 m, tracked over 10 m with 100 steps and the 512³ charged mesh. These are exact run records. The OPALX ZeroSC deck is the later current-build repeat, clearly labelled separately from the original charged record.

## DBA timing pilot

- [OPALX pilot](dba-100steps/opalx-100steps.in): 100,000 particles, 5.602212334 nC, 64×64×512, dt=3 ps; run with `--2D5BatchSize 64` and the recorded restart checkpoint.
- [PyORBIT pilot](dba-100steps/pyorbit-100steps.py): `--nz 256` or `--nz 512`. This timing driver disables longitudinal SC; the final OPALX OPEN pilot enables it. These files represent different validation stages, not a claim of matched longitudinal physics or tune validation.

## Dependencies and rerunning

The archived files retain their original absolute paths. Adapt those paths before rerunning. OPALX and native PyORBIT must be installed. Large particle distributions, NPZ files and restart snapshots are deliberately excluded under the archive's text-only policy; the source metadata records their identities. The original source-generation code and its quiet-source helpers are under `source-generation`, preserving their directory relationships. The bend reference path and uniform-field map are included where they fit the small-text policy. These generators create large files only when explicitly run; none were generated during archiving.

The DBA PyORBIT driver additionally needs `dba-lattice/model/machine.json` and the original matched-KV source metadata/NPZ; the OPALX pilot needs its restart checkpoint and lattice assets. Native merlin6 run locations remain recorded in the validation reports. `provenance.json` records exact copied-file hashes. No new simulation was run for this archive repair.
