Adds `FFT2D5MODEL="ORIGINAL"`, prints the selected model, and rejects its use with other solver types. ORIGINAL remains the default and only supported mainline model. Field calculations are unchanged.

Validation: configuration unit tests pass with 1 and 4 OpenMP threads.

**Test case:** cold protons (β=0.001), a 5 m uniform round bunch with transverse RMS 10 mm, ZeroSC or 10 pC. A uniform vertical magnetic field gives R=2 m. Track 10 m in 10 steps; compare RMS sizes and emittances with committed 658, PyORBIT and the analytic ZeroSC radial reference.

**`FFT2D5MODEL` choices:**
- `"ORIGINAL"`: independent transverse 2D slices and a local longitudinal closure (`g=6.36` for `PIPEMODE=OPEN`). Default and only supported choice in this PR.
- `"FINITE_SOURCE"`: experimental local build only, outside this PR. Straight geometry uses a 3D finite-source solve; circular geometry uses curvature-corrected 2D slices plus a 1D arc integral. Its circular longitudinal closure remains local.

`PIPEMODE` is a separate longitudinal-model setting; it is not another `FFT2D5MODEL` choice.

| 10 pC endpoint | RMS radial (mm) | RMS vertical (mm) | Normalized radial emittance (mm mrad) | Normalized vertical emittance (mm mrad) |
|---|---:|---:|---:|---:|
| Local ORIGINAL | 7.163 | 53.888 | 0.006462 | 0.002630 |
| Committed 658 | 7.163 | 53.888 | 0.006462 | 0.002630 |
| PyORBIT | 7.322 | 53.523 | 0.011254 | 0.004485 |

Plots are reference data from the local benchmark build, not PR-head tracking. Ten-step tracking is not converged.

![RMS comparison](https://raw.githubusercontent.com/OPALX-project/OPALX/d47703aff69879de8e3a87f862a171926b288f69/docs/validation/fft2d5/original-model-selection/rms.png)

![Emittance comparison; dotted black is analytic ZeroSC radial reference](https://raw.githubusercontent.com/OPALX-project/OPALX/d47703aff69879de8e3a87f862a171926b288f69/docs/validation/fft2d5/original-model-selection/emittance.png)

Refs #658.
