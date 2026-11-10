# Frozen-field audit and longitudinal sweep

Parent-authorized task: run the native OPALX controlled longitudinal sweep
at fixed transverse mesh 128x64, Ns5120 and the same 1024 cross-section
points; then Ns10240 and path-step .01 controls at NZ4096. No production
or root generator edits.

`run_longitudinal_sweep.py` owns only these new case names and records
commands, manifest hashes, return codes and timings in
`longitudinal_native_runs.json` after each main/probe pair.

Controller session 53543 completed all six main/probe pairs with exit0:
- xy128-z512-ns5120: main13.63s, probes0.109s.
- xy128-z1024-ns5120: main14.20s, probes0.137s.
- xy128-z2048-ns5120: main16.16s, probes0.277s.
- xy128-z4096-ns5120: main18.22s, probes0.463s.
- xy128-z4096-ns10240: main32.91s, probes0.397s.
- xy128-z4096-ns5120-path01: main23.91s, probes0.609s.

`verify_longitudinal_runs.py` independently checked all twelve snapshots:
PASS for return codes, input/binary/path hashes, N/IDs/Q, finite coordinates,
momenta and fields, tube geometry and probe motion. Largest probe
displacement is 3.593e-12 m. Acceptance JSON and per-case CSV are saved here.

Optional native end profiles requested by frozen_analysis are complete:
`native_longitudinal_profiles.csv` has all 5120 longitudinal stations for
four Ns5120 cases at fixed cross index 47, u=-42.9804 micrometres,
y=-88.2838 micrometres. Fields rotate to global and project onto the actual
nearest-polyline tangent. `extract_longitudinal_profiles.py` removes
diagnostic charge using independent 1D CIC deposition/gradient/gather;
the formula matches all 172 companion probe values within 1.866e-11 V/m.
CSV, provenance and formula-check tables are saved here. Analysis notified.

Read-only generator/first-case audit and independent longitudinal-CIC
sampling audit are documented in README.md and CSV files. Parent and
frozen_analysis agent receive completion notifications. No source files
or other runs may be overwritten; no commit/push is authorized.

Python compile check passes for all four audit scripts. Root and analysis
were notified of all completed controls and profiles. No running process
remains from this agent, and no numerical or production source change was made.

Next: parent/analysis assess actual field convergence and SACR differences.

## Resumed: matched Cartesian transverse meshes

Parent requested actual matched runs using the prepared Cartesian source
(Ns640, Ncross32180, Nrad/Nphi512, path step .005). Root completed the
512x256x512 case. This agent owns only `xy256-z512-cart` and
`xy128-z512-cart`, sequentially in that order. No additional polar path
or longitudinal run is requested.

Completed both requested native pairs:
- `xy256-z512-cart`: main 105.271 s, probes 0.274 s, both exit0.
- `xy128-z512-cart`: main 105.587 s, probes 0.117 s, both exit0.

`cartesian_native_runs.json` archives all three matched levels, including
root's 512x256x512 case. `verify_cartesian_runs.py` independently checked all
six snapshots; N/Q/IDs, input/binary/path hashes, all finite fields/momenta/
coordinates, tube geometry and probe displacement pass. Maximum probe
motion is 2.999e-12 m. No native process from this agent remains running.

Cartesian Jacobian inverse is correct. Boundary-area quadrature excess is
0.0313685%, mean-u error -0.0310719%, second-moment errors about0.03%.
These are geometry diagnostics rather than a uniform field-error bound.
Independent cart512 HDF5 centre Er=-0.0176291015V/m, compared with the
analytic flat-slice physical-density value -0.0163409691V/m. The remaining
flat-slice difference is -0.00985% of the transverse component scale.

Independent 256-to512 field extraction gives maximum changes 0.004688%
radial and 0.048822% vertical of the fixed component scales; centre Er changes
only 4.84 microV/m. Use the final analysis tables for regional SACR errors:
the intended inclusive 50 mm boundary must use a small floating tolerance,
because the nominal 50 mm points store as 0.04999999999999982 m. A raw >=.05
mask would incorrectly omit them and understate longitudinal error.

Source-quadrature uncertainty remains distinct from mesh convergence.
The Cartesian geometry area/moment checks do not supply a uniform bound
on all fields. No production code, physics parameter or tolerance changed.
