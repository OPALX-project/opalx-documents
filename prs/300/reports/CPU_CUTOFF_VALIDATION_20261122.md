# Longitudinal witness-field cutoff — 22 November 2026

Relocated to PR #300 documentation. This is the completed CPU validation
record; later [Lumi validation](../campaigns/lumi-experiment4-cutoff-20261122/STATUS.md)
and [the current index](../README.md) supersede historical “no GPU validation”
and “uncommitted” statements below. Code commit `4231c717f` is now pushed.
All commands run from `/Users/adelmann/git/opalx-beambeam`; sibling run paths
below mean `sandbox/experiment-4/results/cutoff-20261122-n1` and `-n2` there,
not siblings of this document. Raw data and generated per-run reports stay put.

The local revision sets the physical-plus-mirrored primary contribution to
witness E/B to zero strictly outside the fixed IP ±10 mm longitudinal window.
Endpoints retain ordinary CIC sampling. Witnesses remain in their containers
and may re-enter; only primary charge is deposited. Primary kicks, the field
solve, the primary-exit lifecycle, and physical apertures are unchanged.

The mixed inside/outside gather fills both field halos collectively and uses
IPPL's CIC weights on the default Kokkos execution space. Outside particles
branch before grid access. All-inside gathers retain the original IPPL path.
There are no particle-array host copies, temporary particle selections, or
upstream dependency changes. An invalid in-window stencil or any nonfinite
coordinate still triggers the collective guard.

## Full Experiment 4

These are the existing legacy simultaneous-injection cases, not the exact
timed production distribution. Each uses 10,000 evolving Gaussian primary
particles, a 16³ mesh, 1,297 witnesses per species, the 32 cm element and 15 cm
radius, and 550 + 25,001 + 1,025 steps with 1 ps / 1 fs / 1 ps timesteps.
Both runs finish at 1.600001 ns with 26,576 integration steps. The previous
revision stopped at step 25,566 before any loss.

| Check | One rank | Two ranks |
|---|---:|---:|
| Final electron witnesses | 643 | 643 |
| Final positron witnesses | 731 | 731 |
| Removed electrons / positrons | 654 / 566 | 654 / 566 |
| H5 intervals with losses, per species | 49 | 49 |
| Duplicate / replacement / reappearing IDs | 0 / 0 / 0 | 0 / 0 / 0 |
| Nonfinite phase-space components | 0 | 0 |
| Displacements exceeding c Δt + 1 pm | 0 | 0 |
| Maximum survivor Δp at ballistic loss intervals [mc] | 0 | 0 |
| Maximum ballistic position residual at losses [m] | 1.35e-15 | 1.26e-15 |
| Maximum Δp in same-side outside-window intervals [mc] | 0 | 0 |
| Repeated positron oscillations near overlap | absent | absent |

The audit joins only immutable IDs, never nearest-neighbour trajectories.
For outside-window intervals it requires both endpoint samples to be outside
on the same longitudinal side. For loss-interval ballistic checks it excludes
the lifecycle-transition interval by two coarse steps. Momentum is constant
and position follows the relativistic drift velocity. No tolerance was relaxed.

No ID renumbering or post-deletion trajectory jump is reproduced in these runs.
Repeated positron oscillations remain absent. At nominal overlap the two-rank
primary has RMS widths 435.5 µm and 444.2 µm, versus the entrance parameter
1.944 µm. The witnesses are injected simultaneously 16.747 ps before nominal
overlap. These conditions differ substantially from rigid, exact-timed Track-12.
Identical final counts alone do not establish decomposition independence of
all trajectories: the Gaussian source realization and reductions can depend
on MPI size, and initial witness IDs need not agree between rank counts.

## Other checks

- Boundary, nextafter-outside, all-outside, re-entry, migration/ID, collective
  guard and Gaussian field checks pass on 1 and 2 ranks. The field-service suite
  also passes on 4 ranks, including its non-slab field-mirroring case.
- The existing witness-deletion/H5 regression passes on 1 and 2 ranks.
- Experiment 2: all 1,501 coarse Track-12 steps complete, with the same 13,012
  reference-grid samples as the matched pre-cutoff control. All 13,008 actual
  H5 witness records have exactly equal IDs, clocks and x/y/z/px/py/pz values.
  The other four samples are reconstructed birth states, not stored records.
- The pre-cutoff control uses the exact HEAD CartesianPIC3DAlgorithm.cpp in
  an isolated executable linked against the same current static dependencies;
  working sources were not reverted. Build commands and hashes are retained
  in tmp/cutoff-validation-20261122/reference_build.json.
- Experiment 3: the 160-step run preserves all 1,297 exact births of each
  species. Stored witness phase space is bitwise equal to the former
  local-20261120-221523-66s1bzsm run. Primary z differs by at most 3.47e-18 m;
  the comparison is against that earlier executable, not an identical build.
- Experiment 1: all four 3/2/1/0-sigma manufactured-field smoke comparisons
  complete with finite metrics and zero uncovered probes. The 1,000-particle
  8×8×16 mesh is deliberately coarse; its large errors are not an accuracy gate.
- Five synthetic audit tests pass, including injected renumbering, an
  impossible position jump and a nonzero kick outside the field window.
- clang-format and git diff --check pass; the updated LaTeX note compiles.

## Reproduction and outputs

Build with the existing GCC15.2/Kokkos SERIAL build (AppleClang build_openmp
has an unrelated LossDataSink comparator compile error):

```sh
cmake --build build_gcc --target opalx_exe TestBeamBeamFieldServices \
  TestMultiContainerPartBunch TestWitnessDeletionMPI2 -j4
ctest --test-dir build_gcc \
  -R '^Test(BeamBeamFieldServices(MPI2)?|MultiContainerPartBunch|WitnessDeletionMPI2)$' \
  --output-on-failure
mpiexec --oversubscribe --bind-to none -n 4 \
  build_gcc/unit_tests/SpaceCharge/TestBeamBeamFieldServices
```

Some local default MPI launches transiently failed in process mapping before
tests started. The identical binaries pass with --oversubscribe --bind-to none,
and the final ordinary CTest rerun passes all four entries. This is separate
from test assertions; no production mapping policy or CMake setting changed.

Full runs are in sibling directories cutoff-20261122-n1 and cutoff-20261122-n2.
Their inputs, H5 output, opalx.log, timing.dat, manifests, and loss-audit/ plots,
per-ID CSVs and summary.json are retained. Run-local primary H5 frequencies
were set to 0 and 100, respectively, matching the diagnostic policies of the
previous failed runs. No physical input parameter changed.

For a fresh directory, prepare with sandbox/scripts/run_experiment.py
--experiment 4 --full --prepare-only --opalx build_gcc/src/opalx --threads 1
--output-dir NEW_DIR. From NEW_DIR run the absolute OPALX path with
mpiexec --oversubscribe --bind-to none -n N, the generated staged input and
--info 4. Then run the normal launcher with --analyze-only NEW_DIR.
Regenerate the loss audit with:

```sh
OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/opalx-cutoff-mpl \
  ~/.venv-h6/bin/python sandbox/experiment-4/scripts/audit_loss_trajectories.py \
  RUN_DIR --ranks N --track12-reference \
  sandbox/lumi-validation-20261120/track12/results/track12_pointwise_comparison.csv
PYTHONDONTWRITEBYTECODE=1 ~/.venv-h6/bin/python -m unittest discover \
  -s sandbox/experiment-4/scripts -p 'test_audit_loss_trajectories.py'
```

Source base: 9102c9cd1 plus the uncommitted cutoff diff. Executable SHA256:
65a9eb7cc7b947b81d0dff36c6517fc41cb5c0a8bd73465e9edc74278788eb8a.
Track-12 runs and exact before/after CSVs are under experiment-2/results/
cutoff-20261122-reference and cutoff-20261122-n1. Experiments 1 and 3 use
results/cutoff-20261122-smoke and results/cutoff-20261122-n1, respectively.

## Limits

This is a hard, discontinuous force truncation, not a physical wall. Successful
tracking and stable IDs do not bound the omitted impulse. Window size,
edge-crossing timestep, mesh and source-model convergence remain necessary.
No GPU validation or new mesh-convergence acceptance is claimed. The local
LaTeX/Doxygen descriptions are updated; the configured physics-manual checkout
is unavailable and still needs synchronization. Nothing was committed or pushed.
