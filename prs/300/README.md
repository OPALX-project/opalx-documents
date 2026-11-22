# PR #300 — BeamBeam interaction and validation

Updated: 22 November 2026. This directory is the maintained Markdown record for
[OPALX PR #300](https://github.com/OPALX-project/OPALX/pull/300).
Update these notes here; the former paths contain redirects rather than copies.

## Current state

Code: `/Users/adelmann/git/opalx-beambeam`, local branch
`codex/beambeam-recovery`, tracking `origin/271-implement-interation-point-element`.
Commit `4231c717f`, `fix(beambeam): cut off witness fields outside the longitudinal solve window`,
has been pushed. Code, inputs, scripts, raw data, figures and the LaTeX manuscript
remain in the source checkout. This relocation changes documentation only.

Only primary container 0 deposits charge. Passive electron/positron witnesses
sample the physical-plus-mirrored primary field. The IP is the element midpoint.
The longitudinal field window is IP ±10 mm; the transverse mesh follows the
combined primary/witness envelope without shrinking. Finite witnesses outside
the longitudinal window receive zero BeamBeam E/B without deletion, reflection,
wrapping or ID changes, and resume sampling on re-entry. The solve stops after
the complete primary exits the downstream field window, without retiring
primary container 0. `RETIRE_TIME` is removed.

This hard cutoff neglects a physical far-field impulse. Passing implementation
tests does not establish window-size, timestep or mesh convergence.

## Latest evidence

| Case | Configuration | Result |
| --- | --- | --- |
| CPU regressions | Field services on 1/2/4 ranks; deletion/H5 on 1/2 ranks | Boundary, re-entry, collective guard, persistent survivor IDs and phase space pass |
| Lumi GPU regressions | Field services on 1/2 ranks | Applicable tests pass |
| Figure 6(b), new Track-12 | One MI250, 400,000 fixed primaries, 256×256×128, 1,501 steps | 472.25 s; manufactured relative L2 errors: x 0.853738%, longitudinal 0.117302% |
| Track-12 repeatability | Same inputs; saved old executable repeated | Original→cutoff max position difference 0.302 nm; original→old repeat 0.982 nm. Consistent with run-to-run variation, not a statistical characterization |
| Full Lumi Experiment 4 | One MI250, 10,000 evolving primaries, 16³, 1,297 witnesses/species, 26,576 steps | Completes at 1.600001 ns in 477.98 s; 643 electrons/731 positrons survive, with no ID replacement or post-loss trajectory jump |
| Matched old Lumi Experiment 4 | Identical inputs, pre-cutoff binary | Reproduces window-exit gather abort; common old/new histories agree within 1.25×10⁻¹⁵ m |

Track-12 stays within 1.65 mm of the IP: it tests preservation inside the window,
not force truncation accuracy. Experiment 4 tests losses and ballistic motion.
Its CPU/GPU final counts agree, but long-tail positions differ by up to 0.454 mm
and two intermediate snapshots differ in loss timing. This is not bitwise
cross-architecture agreement.

## Experiment 4 versus Track-12: physics interpretation

Track-12 has a nearly nondivergent, narrow primary with `BBRIGID=TRUE`, and
six artificial witness pairs born from −3.002 to +1.999 ps relative to nominal
overlap, with zero transverse momentum. Birth positions are correlated with
birth times; they are not all exactly at the IP.

Experiment 4 is a legacy production-geometry/loss test, not yet the validated
production physics model. It starts with a 1.944 µm entrance spot and 2.674 mrad
divergence, without focusing or position–momentum correlations to create a
waist at the IP. Unforced drift over 17 cm predicts 455 µm; stored CPU diagnostics
give 436×444 µm near overlap, versus about 1.92 µm for the Track-12 fixed input.
`BBRIGID` suppresses collective kicks, not ordinary drift; the flag alone
would not keep the divergent Experiment 4 source narrow.

Experiment 4 injects all witnesses 16.747 ps before nominal overlap. By overlap
the new Lumi positrons have median radius 2.47 mm; their initial transverse
speeds predict 2.50 mm of free-flight travel. Repeated positron oscillations
are absent in both old and new Experiment 4; one positron turns once. Source,
timing and witness phase space strongly explain the contrast, but their
individual contributions have not been isolated. Mesh resolution also differs.

The source measurements use earlier two-rank CPU snapshots because primary
H5 output was disabled in the new GPU run. Witness envelopes use the new GPU
data. Track-12 source constancy is a free-drift prediction from its fixed input,
not a measured GPU primary history.

Next: define the intended primary waist/correlations at the IP; separately
control source preparation and witness birth timing; then establish mesh,
timestep and force-window convergence with the full timed CAIN population.

## Document inventory and former paths

| Former path in the source checkout | Maintained note |
| --- | --- |
| `sandbox/BEAMBEAM_PHYSICS_AND_VALIDATION.md` | [Physics and validation](BEAMBEAM_PHYSICS_AND_VALIDATION.md) |
| `sandbox/Experiments.md` | [Experiment guide](Experiments.md) |
| `BEAMBEAM_REDESIGN_STATE.md` | [Redesign history](BEAMBEAM_REDESIGN_STATE.md) |
| `HANDOFF.md` | [Chronological handoff](HANDOFF.md) |
| `PYTHON_SCRIPTS.md` | [Historical Python inventory](PYTHON_SCRIPTS.md) |
| `sandbox/experiment-3/FIRST_WITNESS_DIAGNOSIS.md` | [First-witness diagnosis](diagnostics/FIRST_WITNESS_DIAGNOSIS.md) |
| `sandbox/lumi-validation-20261120/STATUS.md` | [Initial Lumi validation](campaigns/lumi-validation-20261120/STATUS.md) |
| `sandbox/lumi-cutoff-20261122/STATUS.md` | [Lumi Track-12 cutoff](campaigns/lumi-cutoff-20261122/STATUS.md) |
| `sandbox/lumi-experiment4-cutoff-20261122/STATUS.md` | [Lumi Experiment 4 and model diagnosis](campaigns/lumi-experiment4-cutoff-20261122/STATUS.md) |
| `sandbox/experiment-4/results/cutoff-20261122-study/REPORT.md` | [CPU cutoff study](reports/CPU_CUTOFF_VALIDATION_20261122.md) |

Dated logs retain their execution-time state. This index supersedes historical
“not committed”, “not implemented” and “running” statements. Repository
instructions (`AGENTS.md`), project/build READMEs and `VENV.md` remain with code.
Generated per-run reports remain beside their data, except the authored CPU
cutoff study moved above. Unrelated Lumi master experiments remain out of scope.

## Reproduction and data

Commands and `sandbox/...` paths in these notes refer to the source checkout:

```sh
cd /Users/adelmann/git/opalx-beambeam
```

Use `~/.venv-h6` for local analysis. See [Experiments.md](Experiments.md) for
commands. Lumi source: `/flash/project_465002453/opalx-beambeam-recovery-20261120`.
The remote campaign roots, with case-local Slurm scripts and logs, are:

- `/flash/project_465002453/bb-validation-e24dc9218-20261120`.
- `/flash/project_465002453/bb-cutoff-track12-20261122`.
- `/flash/project_465002453/bb-experiment4-cutoff-20261122`.

Local raw data, metrics and figures remain in the corresponding `sandbox/lumi-*`
directories. Recent figures and manuscript (sibling-checkout links work locally):

- [New Figure 6(b)-style comparison](../../../opalx-beambeam/sandbox/lumi-cutoff-20261122/track12/results/track12_cain_vs_opalx.png).
- [Experiment 4 trajectories](../../../opalx-beambeam/sandbox/lumi-experiment4-cutoff-20261122/comparison/all_trajectories.png).
- [Fixed-ID positron histories](../../../opalx-beambeam/sandbox/lumi-experiment4-cutoff-20261122/comparison/positron_oscillations.png).
- [Source evolution and birth timeline](../../../opalx-beambeam/sandbox/lumi-experiment4-cutoff-20261122/model-comparison/primary_evolution_and_births.png).
- [LaTeX manuscript](../../../opalx-beambeam/sandbox/note/bb-note.tex), unchanged in location with its figure assets.

Generated figures are not published by this move. No commit or push is
authorized for this documentation relocation.
