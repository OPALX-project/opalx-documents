# One-turn DBA: rms sizes and emittances versus matched KV

The completed A100 run uses 100,000 particles, 5.602212333965894 nC, a 64×64×512 mesh, 3 ps steps, batch64 and the ORIGINAL FFT2D5 model. PIPEMODE=NONE matches the uniform coasting-beam longitudinal approximation. It covers one reference circumference (25.7663986 m after 393,240 steps), not an independently localized particle return. All particles and charge are retained. The executable/source/dependency identities are in manifest.json; no tracking was repeated for this analysis.

## Analytic model

The existing hard-edge KV script was rerun with the recorded current, emittances and lattice. For edge radii a,b and geometric edge emittances e_x,e_y,

    a'' + k_x(s) a - e_x²/a³ - 2K/(a+b) = 0,
    b'' + k_y(s) b - e_y²/b³ - 2K/(a+b) = 0,
    K = 2 I / [I_A (beta gamma)³],   I = Q beta c/C.

The match is periodic over one of the six identical cells. I=4.74876955018864 mA, K=7.78527376215725e-7, e_x=e_y=12e-6 m rad. Thus sigma_x=a/2, sigma_y=b/2 and geometric rms emittances are e_x/4=e_y/4=3e-6 m rad (3 mm mrad). Normalized rms emittance is 0.2191447 mm mrad at 2.5 MeV. The independent periodic matching residual is 1.29e-13. Frozen source/model files are retained under model/.

The model assumes uncoupled paraxial linear optics, uniform coasting density, linear free-space transverse self-fields, no dispersion and no longitudinal force. It is a conditional KV envelope prediction, not proof of a stationary finite-emittance distribution in the full tracking equations.

## Coordinates and moments

The beam occupies the whole ring at each time. Native Cartesian .stat moments combine metre-scale ring geometry; even local transverse moments pooled across different Twiss phases do not equal single-section emittance. Each saved native snapshot is transformed back to the laboratory using its reference position and direction. Each particle is then projected onto the exact hard-edge design path, independently of OPALX's solver polyline. This projection reproduces the frozen source coordinates within 2.62e-15 m and slopes within 1.05e-15.

The top rms panels show direct local physical rms sizes in 96 spatial bins at the initial and final snapshots, with the continuous analytic envelope. For profile error metrics the model variance is averaged over the same particles' lattice positions, avoiding a point-versus-bin comparison.

For evolution over time, fixed analytic Twiss functions remove the known variation around the ring:

    xi = x/a(s),    pi = [a(s) x' - a'(s) x]/e_x,
    x_eq = a(0) xi,    x'_eq = a'(0) xi + e_x pi/a(0).

The same map is used vertically. The composite map has determinant one and is not fitted to tracking. It maps the matched prediction to the cell-entrance covariance, allowing all 100k particles to contribute without Twiss-phase mixing. Reported geometric emittances use slopes p_x/p_s and p_y/p_s and centred population covariances. Residual differences between slice centroids remain included. These are section-equivalent pooled moments, not direct single-section measurements.

## Results

| Quantity | Matched KV | One turn | Final difference |
|---|---:|---:|---:|
| Section-equivalent sigma_x (mm) | 5.334873 | 5.325865 | -0.16885% |
| Section-equivalent sigma_y (mm) | 2.385514 | 2.384056 | -0.06112% |
| Geometric epsilon_x (mm mrad) | 3.000000 | 3.009350 | +0.31165% |
| Geometric epsilon_y (mm mrad) | 3.000000 | 3.002214 | +0.07379% |

Across the initial state and 40 saved tracking snapshots, the largest absolute deviations are 0.19673%/0.08520% for horizontal/vertical section-equivalent rms size and 0.31165%/0.11520% for emittance. The physical envelope around the ring follows the model; the maximum final 96-bin rms differences from bin-averaged KV are 1.583% horizontally and 1.441% vertically. These finite-bin results do not establish sub-percent agreement at every lattice position. No tolerance was changed to obtain agreement.

![Rms comparison](rms-vs-matched-kv.png)

![Emittance comparison](emittance-vs-matched-kv.png)

All 40 snapshots pass ID, count, charge, time and finite-coordinate/momentum checks. This is a one-turn moment comparison, not mesh/timestep convergence, a particle tune measurement or evidence for the 12.268 nC case.

## Reproduction

Run analyze.py and plot.py with ~/.venv-h6. The native HDF5 file is not copied into this documents directory; set OPALX_DBA_H5 to its path. It is currently downloaded at /Users/adelmann/git/opalx/tmp/2026-11-06-dba-one-turn-analysis/case.h5 and remains remotely at /psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/one-turn-and-bend/dba-one-turn/case.h5. All other required model/source inputs are frozen here. source-manifest.json records hashes and software versions. Output CSV/JSON, input, native stat file and PDF/PNG figures are retained. No code commit, push or new run was made for this analysis.
