# Native/old school PROBE integration validation

The first implementation uses native OPALX laboratory output and the school adapter. All original school files remain unchanged. Source-derived geometry reflection and spiral reversal are applied only to copied comparison inputs. See the driver and old-school field-transform audit.

## Raw crossing comparison

| Native case | Physical hits | Unmatched old/native | Maximum coordinate difference [m] |
|---|---:|---:|---:|
| native-16-cell-matched-hdf5-r1 | 57 | 0/0 | 1.04852e-05 |
| native-16-cell-matched-refined-hdf5-r1 | 57 | 0/0 | 1.08188e-05 |
| native-16-cell-matched-quarter-hdf5-r1 | 57 | 0/0 | 6.16112e-06 |
| native-16-cell-matched-vertical-hdf5-r1 | 57 | 0/0 | 1.08453e-05 |
| native-fourfold-matched-hdf5-r1 | 15 | 0/0 | 5.27722e-06 |
| native-fourfold-matched-refined-hdf5-r1 | 15 | 0/0 | 5.27722e-06 |
| native-55deg-d-off-matched-hdf5-r1 | 61 | 0/0 | 9.20399e-06 |
| native-55deg-d-off-matched-refined-hdf5-r1 | 61 | 0/0 | 7.78465e-06 |

All cases use one particle with no losses; two initial old t=0 records are excluded explicitly. Time, particle IDs and chronological station passage define the join, while both native and old turn labels remain available.

## Passivity, output and MPI

- The listed one-rank OFF/ASCII/HDF5 controls are bitwise identical in final particle state, charge, reference state, time, path length and accepted-step count.
- Sixteen-station one/two-rank outputs are identical. The repeated fourfold two-rank ON run is also identical to its OFF control and to the one-rank case.
- Native ASCII and HDF5 format consistency is checked against six-significant-digit ASCII rounding; exact detail is in comparison-summary.json.
- FFA output has no misleading lab-origin .hist/.peaks products.

## Retained two-rank outlier

The first fourfold HDF5 two-rank run used 63,158 accepted subdivisions; OFF and repeated ON runs used 63,143. The repeated ON is exactly identical to OFF. Initial input bytes, particle bytes and binary hash are identical across the two ON runs. The driver fixes OMP/IPPL thread counts to one and disables binding, but the complete inherited environment was not captured. The first run overlapped independent jobs; this is context, not an established cause.
The outlier has identical final time, ID and charge. Maximum local position difference is 8.56757e-12 m; reference-position difference is 1.22569e-13 m. Cause remains unresolved; no blanket bitwise MPI or general baseline-nondeterminism claim is made.

## Reference labels

In the fourfold diagnostic, radial PROBE1 returns occur 132.05, 18.84 and 98.80 ps after returns through the initial reference plane. Their native labels are 1,1,3, whereas launch-plane probe labels are 0,1,2. The second pair shares one accepted interval, so its station record retains the previous step-start count. This is the documented counter/observation ordering, not a new particle or station turn definition.

## Numerical limits

Old OPAL uses RK4 and extrapolated event positions with current-step momentum; native tracking uses its existing boundary-controlled particle transport and coherent endpoint interpolation. Old raw ASCII has six significant digits. Nominal timestep refinement is reported without claiming uniform accepted-step refinement. No tolerances or physics references were changed.

Plots and standalone CSV/JSON are in plots/. The validation is a few-turn detector comparison, not space-charge, convergence, long-term stability or fresh GPU validation.

## Geometry and provenance

Legacy RingDefinition LAT_PHIINIT is clockwise from old +Y. The existing native school template had treated the accumulated angle as counterclockwise from +X. Copied physical magnet placements are corrected by theta_entrance = PI/2 - phi_template - L/R0, TAN_DELTA is negated, and the existing axial B0 sign conversion is retained. Native AsymmetricEnge already reverses the old scalar coordinate with the same start/end names; no additional endpoint swap is applied. Zero-field geometry arcs are retained. No original school template or production field calculation was changed.
The independent source-derived field transformation check covers 450 points, off-plane fields, and symmetric/asymmetric fringe profiles, with maximum error 8.05e-15 T: [script](old-school/check_field_transform.py), [results](old-school/check_field_transform.json).
Native executable hashes are b13e9e5354a4434826ebf9844b05ebed6c3e6534a2b48fcc867dd6329cd80ef5 (frozen first implementation) and 58bd5db212d2dc3e62c8fdf62a51fb2dca456580eabf9452c595ea448777f9d5 (final linked source). Old executable hash, exact revision, input/distribution/template hashes, full initial states and corrected physical masses/timesteps are retained for each run in comparison-summary.json and each manifest.json. Both binaries are preserved under bin/.

## Coordinate observables and refinement

| Native run | Max radial difference (µm) | Max radial momentum difference p/(mc) | Max vertical difference (µm) | Max vertical momentum difference p/(mc) |
|---|---:|---:|---:|---:|
| native-16-cell-matched-hdf5-r1 | 13.549 | 9.6636e-06 | 0 | 0 |
| native-16-cell-matched-quarter-hdf5-r1 | 8.7131 | 2.2886e-06 | 0 | 0 |
| native-16-cell-matched-refined-hdf5-r1 | 13.58 | 3.4362e-06 | 0 | 0 |
| native-16-cell-matched-vertical-hdf5-r1 | 13.921 | 8.8146e-06 | 1.2814 | 1.9892e-07 |
| native-55deg-d-off-matched-hdf5-r1 | 9.204 | 0.00014784 | 3.6692 | 1.8774e-06 |
| native-55deg-d-off-matched-refined-hdf5-r1 | 7.0579 | 7.3028e-05 | 3.6573 | 1.0766e-06 |
| native-fourfold-matched-hdf5-r1 | 5.2772 | 7.031e-08 | 0.62371 | 3.9501e-08 |
| native-fourfold-matched-refined-hdf5-r1 | 5.2772 | 7.031e-08 | 0.62671 | 3.9701e-08 |

The 16-cell radial momentum difference decreases from 9.66e-6 to 3.44e-6 to 2.29e-6 p/(mc) across nominal coarse/half/quarter budgets. Quarter-step radial-position maximum decreases from about13.6 to8.71µm. The 55-degree D-off radial momentum difference approximately halves from1.48e-4 to7.30e-5 p/(mc). These observations support the expected legacy event/momentum sampling difference; they do not establish a uniform integrator convergence order because native boundary subdivision and old ASCII rounding both intervene.

## Artifacts and reproduction

- [Matched native preparation/run/comparison driver](check_school_probes.py)
- [Summary reproduction script](summarize_validation.py)
- [Plot reproduction script](plot_school_probe_comparison.py)
- [Old run provenance and accepted cases](old-school/REPORT.md)
- [Structured complete comparison summary](comparison-summary.json)
- 16-cell-radial: [PNG](plots/16-cell-radial.png), [PDF](plots/16-cell-radial.pdf), [CSV](plots/16-cell-radial.csv), [metrics JSON](plots/16-cell-radial.json)
- 16-cell-vertical: [PNG](plots/16-cell-vertical.png), [PDF](plots/16-cell-vertical.pdf), [CSV](plots/16-cell-vertical.csv), [metrics JSON](plots/16-cell-vertical.json)
- fourfold-radial: [PNG](plots/fourfold-radial.png), [PDF](plots/fourfold-radial.pdf), [CSV](plots/fourfold-radial.csv), [metrics JSON](plots/fourfold-radial.json)
- fourfold-vertical: [PNG](plots/fourfold-vertical.png), [PDF](plots/fourfold-vertical.pdf), [CSV](plots/fourfold-vertical.csv), [metrics JSON](plots/fourfold-vertical.json)
- 55deg-d-off-radial: [PNG](plots/55deg-d-off-radial.png), [PDF](plots/55deg-d-off-radial.pdf), [CSV](plots/55deg-d-off-radial.csv), [metrics JSON](plots/55deg-d-off-radial.json)
- 55deg-d-off-vertical: [PNG](plots/55deg-d-off-vertical.png), [PDF](plots/55deg-d-off-vertical.pdf), [CSV](plots/55deg-d-off-vertical.csv), [metrics JSON](plots/55deg-d-off-vertical.json)
