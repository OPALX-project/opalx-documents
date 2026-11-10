# Native PyORBIT tracking completed

All four authorized cases pass: straight and R=2 m bend, each with ZeroSC
and 10 pC space charge. Each main run has exactly ten full steps over a
nominal one-metre central-reference advance and eleven endpoint rows.
The root's shared 1,048,576-particle D4 sources, IDs and hashes are unchanged.
ZeroSC retains the same nominal charge and disables the SC kicks.

Files: `track_straight.py`, `track_bend.py`, `check_bend_kinematics.py`,
`audit_tracking.py`; payloads under `runs/{geometry}-{mode}-10steps/`.
Each payload has `moments.csv`, `final-particles.npz`, `manifest.json`
and a native guard-only zero-gradient check. Run `audit_tracking.py` with
`/Users/adelmann/.venv-h6/bin/python` to regenerate `completion.json`.

Native package is the existing compiled PyORBIT package at
`/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe/pyorbit/native-package`.
Set PYTHONPATH to that path. Driver/source/library hashes are recorded.
No native solver edits, builds, commits or pushes occurred.

Straight transport uses native exact relativistic linac half drifts around
the native slice and gradient-LS kicks. Bend transport uses the existing
TEAPOT body composition with no fringe or custom field tracker, again with
SC at the central split. Both retain the native transverse-work omission in
dE; it is explicitly recorded and not patched.

The physical g=6.36 is encoded for each kick by
g_native=g*ds/period, because the native LS map integrates over its period.
This is exact step scaling, not a field fit. All six zero-weight mesh guards
are at the LAB domain ends, including transverse extent guards. Native
Grid1D deposition/gradient verifies their contribution is identically zero
throughout LAB s in [-3,4] m. Their coordinates are reset around field solves.
Weighted native statistics exclude them. Fixed LAB mesh bounds are checked
at all ten charged kicks. Bend uses the OPALX Cpoly period; native exact
Frenet coordinates are retained rather than intrusive polyline projection.
The path's maximum chord sagitta is recorded in the bend manifests.

Straight charged final rms x=y=10.473157169931 mm,
sigma_z=1.443396669859 m. OPALX/PyORBIT total transverse rms differs by at
most 0.007626% across the eleven rows; expansion increments differ by about
0.169%. ZeroSC shape is unchanged.

Bend charged final local rms u=9.243733119906 mm,
y=10.477991322046 mm, s=1.443404252111 m. Maximum OPALX/PyORBIT local-rms
differences are 0.013381% (u), 0.007703% (y), 0.000011374% (s). Bend ZeroSC
maximum radial-rms difference is 0.005728%, consistent with the native
TEAPOT/Boris map approximations. The separate native linear bend control
verifies u=u0*cos(phi), xp=-u0*sin(phi)/R and delta_s=-u0*sin(phi) to floating
precision; the nonlinear body map's correction is retained explicitly.

Coordinate convention: bend `mean_frenet_s_m` and `native_mean_4` are relative
to the design reference phase. `mean_absolute_s_m` is the absolute physical
arc centroid, and `reference_phase_rad=advance/R`. Global positions use
theta=(native_z+advance)/R. Covariances and rms are unaffected by this origin.
Root analysis uses `mean_absolute_s_m` and converts OPALX's centroid-based
origin separately. No reported native trajectory was altered.

Limits: this demonstrates matched reduced-model tracking and numerical
transport agreement. It does not establish complete curved-source Coulomb
accuracy, asymptotic mesh convergence or energy-conservation accuracy.

No native run or tool process remains pending. Root owns final combined
analysis, figures and the LaTeX report. The separately assigned SACR radius
sweep is also complete under `reference-extension/radius-sweep/`.
