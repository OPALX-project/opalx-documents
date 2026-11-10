# Frozen-field analysis

Own only this analysis directory. Root owns OPALX runs and reference agent owns
the independent SACR evaluator. Analyze completed native one-step cases only,
subtract their probe-only companion fields, and compare at the same 43 source
coordinates. H5 fields and positions require tracker-reference to global
rotation and translation; local comparison axes are radial, vertical, tangent.

Use fixed SACR characteristic component scales, not local relative errors.
Preserve symmetry zeros. Report absolute V/m, scaled errors, and mesh changes
separately; sample maxima do not establish a distribution-wide bound. Main
bulk charge is Q_total*Nsource/(Nsource+43). Probe-only Es must be adjusted
for its slightly different mean gamma before subtraction (transverse E does
not need a boost). This factor and reconstruction checks are recorded.

Completed 2026-11-01: strict final analysis covers all 21 complete native
main/probe pairs (42 runs), with no pending pairs. Stopped setup pilots are
excluded explicitly. Fields are compared at 43 exact targets in all three
directions (2709 component values across the complete cases).

Final primary scans, saved in plot_selection.json:
- Transverse: xy128/256/512-z512-cart, same quiet Cartesian source Ns640,
  Ncross32180, path step .005 m, grids128x64/256x128/512x256, NZ512.
- Longitudinal: xy128-z512/1024/2048/4096-ns5120, same source Ns5120,
  Ncross1024 and128x64 transverse mesh, path step .02 m.
- Direct all-component field plot: quiet Cart512 and longitudinal4096.

Final 256→512 transverse changes are .004688% radial, .048822% vertical
and roundoff tangential, of the fixed component scales. Fine transverse
errors at points at least50mm from either end are .55628% radial and
.04136% vertical; at5/10mm they are4.2403% and2.6475% with fixed NZ512.
This does not establish joint end-field convergence. The low-N polar source
was shown underresolved and remains as exploratory evidence, not the primary
mesh sequence. Root's independent2DCIC/log-kernel source-control reconstruction
supports the quiet Cartesian cross-section sampling only, with limited scope.

At the tube/reference-path midpoint u=y=s=0 (not the whole curved beam charge
centroid), fine FFT2D5 gives Er=-.017629 V/m while SACR gives +.055092 V/m.
The independent analytic limit of the flat transverse operator, including
deposited rho_slice=rho*(1+u/R), is -.016341 V/m at10pC. Thus a small boundary-
scale percentage can hide an incorrect curvature-only response.

Longitudinal maximum errors over all fixed targets are34.5104%,73.3249%,
53.5547%,100.0002% as NZ increases. At least50mm from the ends the fine
error is10.9006% of Es*, dominated by the50mm target. Use >=.05-1e-12
for this inclusive material-distance criterion; raw .04999999999999982m
floating values otherwise incorrectly exclude the50mm points.
The native all-station end profile shows a shrinking, growing model end kick
instead of SACR's finite spatial profile. Audit agent independently verified
the diagnostic-particle subtraction. The dense illustrative SACR profile is
projected into the same nearest-polyline direction as native Es, with checked
PCHIP/quad errors; the43accuracy metrics use direct quadrature.

Data integrity, charge, IDs, time, frame reconstruction and exact probe
tangents all pass. A5e-12m reconstruction allowance accounts for nearzero
H5 reference-momentum reduction roundoff at10–20million particles; actual
picometre residuals remain exported. No physics tolerance or fitted parameter
changed. OneMPIrank only, as required by the current solver.

Five publication-quality PDF/PNG sets are generated. The final centre figure
uses only the quiet transverse scan; all longitudinal centre values remain
in CSV. Portable --replot uses saved selectors and cached CSVs, requires no
OPALX/H5/helper paths, and does not mutate inputs. verify_offline_replot.py
checks identical PNGs and unchanged copied inputs. No production changes,
commits or pushes. Report agent owns the final LaTeX/PDF integration.
