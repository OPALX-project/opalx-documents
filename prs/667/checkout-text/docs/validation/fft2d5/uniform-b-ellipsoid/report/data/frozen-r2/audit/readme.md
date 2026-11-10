# Independent frozen-source audit

`longitudinal_sampling.py` evaluates the same prescribed equal-charge
cross-section and longitudinal stations as the native OPALX source. It
projects them onto the actual circular polyline, deposits only longitudinal
CIC weights, central-differences the line density and interpolates the
result at the fixed 43 diagnostic targets. No OPALX field output enters
this calculation.

The noise baseline is exact CIC deposition of continuous flat line charge
between affinely compressed endpoints. The actual 8 m design polyline has
length 7.99996724802 m. Uniform compression itself gives no interior
gradient; local geometry and station/grid phase cause the residual.

Normalization is `F=E/(k*rho)`, with `k=1/(4*pi*epsilon0)` and
`F_s=-g*pi*a*c*d(lambda/lambda0)/ds`. The existing reference scales are
0.005711986642890534 m transverse and 0.0014202325784798471 m tangential.
The gamma correction is below 1e-6 relative at beta=.001 and is omitted.
Bulk summaries exclude 50 mm at either end; fixed-probe summaries retain
all targets and subtract the continuous-CIC finite-end baseline.

At NZ=4096 the maximum bulk / fixed-probe sampling fields, as percentages
of the tangential reference scale, are:

| Ns | Bulk max [%] | Fixed-probe max [%] |
|---:|---:|---:|
| 2560 | 3.707 | 0.2428 |
| 5120 | 0.0430 | 0.00080 |
| 10240 | 0.1998 | 0.0011 |

The nonmonotonic bulk values reflect station/grid phase and polyline
projection. Ns=5120 is sufficient to make this contribution small at the
selected targets; a denser-source comparison should still accompany a
claim of native-solver mesh convergence. These are diagnostic sampled
checks, not a bound throughout the beam.

Additional read-only checks of the native generator and first completed
`xy64-z512` case:

- Inverting `phi+a*r/R*sin(phi)` gives the correct physical Jacobian with
  equal charges. Sample mean u=3.125e-6 m agrees with a^2/(4R).
- All 43 probes are interior (normalized transverse radius at most 0.9),
  and occupy IDs Nsource through Nsource+42.
- Probe-centred path segments match exact-circle tangents within 6.1e-14.
- Native HDF5 contains all 2,621,483 particles at TIME=1e-17 s and total
  charge 1e-11 C. Probe displacements are at most 2.91e-12 m.
- HDF5 positions/fields require the reference-to-global rotation; the
  reference centroid is not on the 2 m circle for this extended beam.
- The probe-only run uses the same per-particle charge and should be
  subtracted at matched probe IDs. The remaining physical source charge is
  Q*Nsource/(Nsource+43), as recorded in the manifest.
- The original active uniform field map made the orbit threader integrate
  indefinitely at the tiny frozen-field step. The completed input uses a
  distant drift, giving no applied field in the bunch region.

The three-adjoining-chord projection used by the independent audit agrees
with a full all-segment Cartesian search within floating-point precision
at all 43 probes and 128 independently selected source positions.

Reproduce with:

```sh
/Users/adelmann/.venv-h6/bin/python longitudinal_sampling.py
```

CSV results and provenance hashes are saved beside the script.

## Completed native longitudinal controls

`run_longitudinal_sweep.py` executed NZ512/1024/2048/4096 at 128x64 and
Ns5120, plus Ns10240 and path-step .01 controls at NZ4096. All six main/probe
pairs completed exit0 with the same pinned binary. Per-run commands,
manifest hashes and timings are in `longitudinal_native_runs.json`.

`verify_longitudinal_runs.py` checked all 12 snapshots independently:
N/IDs/Q, finite particle coordinates/momenta/fields, tube geometry,
input/binary/path hashes and probe displacement all pass. Maximum probe
displacement is 3.593e-12 m at DT1e-17 s. See
`longitudinal_snapshot_acceptance.json` and
`longitudinal_snapshot_checks.csv`.

`extract_longitudinal_profiles.py` extracts all 5120 stations at one fixed
cross-section point (index47, u=-42.9804 micrometres, y=-88.2838 micrometres)
for each of the four controlled meshes. It rotates native fields into
global coordinates and projects them onto each station's nearest-polyline
tangent. The 43 diagnostic particles' contribution is removed using an
independent 1D CIC calculation with the actual full-run gamma. That
calculation agrees with all 172 companion probe-only field values within
1.866e-11 V/m. The profile CSV uses both V/m and F=E/(k*rho) units, with the
actual physical source charge after diagnostic particle subtraction.
Reproduce from the completed snapshots:

```sh
/Users/adelmann/.venv-h6/bin/python extract_longitudinal_profiles.py
```

This profile extraction and probe correction do not supply the independent
SACR physics reference; they isolate the native 2D5 field of the physical source.

## Matched Cartesian transverse meshes

Root's `xy512-z512-cart` and this agent's matched `xy256-z512-cart` and
`xy128-z512-cart` all use the same Ns640, Ncross32180 Cartesian source and
5 mm reference-path segmentation. Main runs took 111.76, 105.27 and 105.59 s,
respectively. All main/probe pairs completed exit0. Run metadata is in
`cartesian_native_runs.json`.

`verify_cartesian_runs.py` reuses the independent snapshot checks for all
six files. All pass, with maximum probe displacement 2.999e-12 m; see
`cartesian_snapshot_acceptance.json` and `cartesian_snapshot_checks.csv`.

The Cartesian source starts with midpoint cells clipped to the ellipse.
At fixed y and half-width w, the inverse map
`u=sqrt(R^2+2R*u0+w^2)-R` maps endpoints correctly and satisfies
`du/du0=R/(R+u)`. Equal-charge samples therefore include the physical
`1+u/R` Jacobian. The clipped-cloud area excess is 0.0313685%, mean-u
relative error is -0.0310719%, and second-moment errors are about 0.03%.
These are geometry diagnostics rather than uniform field-error bounds.

At the centre, the continuum flat-slice physical-Jacobian prediction is
`Er=-Etransverse_scale*a/(2R)=-0.0163409691V/m`. Native Cartesian256/512
give -0.0176242599/-0.0176291015 V/m after probe subtraction. Their centre
change is 4.84 microV/m, while SACR gives +0.0550920 V/m. The centre's
curvature signal and its sign must be interpreted separately from the
much larger characteristic transverse field scale.

Use an inclusive tolerance for intended 50 mm regional boundaries in CSV
analysis. Nominal 50 mm target distances store as 0.04999999999999982 m;
`>=0.05-1e-12` retains them. Raw `>=0.05` silently excludes these targets.
