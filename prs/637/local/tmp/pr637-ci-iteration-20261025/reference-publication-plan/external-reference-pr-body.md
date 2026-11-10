These references follow the intended MultipoleT fringe/reference behavior and the ScalingFFA field-superposition correction in [OPALX PR #637](https://github.com/OPALX-project/OPALX/pull/637). FODO’s July reference predates the MultipoleT changes already present on clean master. ScalingFFA’s old reference stops at 1 ns although its maintained input requests 1000 steps; the complete corrected run now retains particle/reference agreement to arithmetic precision.

Generated with committed OPALX `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`, using the unchanged `bin/makeReference.sh --ranks 1`, `OMP_NUM_THREADS=1`, and regression base `737547e6ae38cf3001d6bc45cf38dd1a47d78402`. This changes only the 12 generated reference and checksum files. Inputs, particle distributions, launchers, all 401 comparison definitions, and tolerances stay unchanged. Native unit tests remain self-contained C++.

Validation:

- Independent native analytic tests verify MultipoleT fringe amplitude and particle/scalar/reference field parity; the clean pre-PR master reproduces the obsolete FODO mismatch and matches the regenerated trajectory.
- ScalingFFA’s new native regression fails before the source correction and passes afterwards, including seeded/overlapping/outside-support fields and two-rank execution. The unchanged 1000-step run reduces final separation from 1.222 m to 7.93e-13 m, retaining all ten particles, charge and energy.
- Both standard-generated outputs report the exact source revision. FODO has 2001 rows/1000 particles; ScalingFFA has 10 rows/10 particles. All six generated MD5 checks and ten existing comparisons against independently executed outputs pass.
- Full standard NightlyBuildX suite: **401/401 comparisons pass across 39/39 simulations**, exit 0, using runner `5539fa31`, the exact committed executable and unchanged one-rank/OpenMP1 inputs. All launches report the expected source revision and normal completion.
- A100/CSCS build/runtime checks: **pending** in the linked OPALX task.

This external reference PR must stay unmerged until the compatible ScalingFFA source is available on OPALX master. PR #637 can select this feature branch in all three architecture configs for paired validation. After the source and these references are merged, restore those configs to regression `master` before deleting the feature branch.
