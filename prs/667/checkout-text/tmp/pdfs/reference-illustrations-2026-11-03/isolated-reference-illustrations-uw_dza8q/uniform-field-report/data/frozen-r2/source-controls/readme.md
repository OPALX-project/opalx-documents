# Auxiliary transverse source-quadrature check

Run `~/.venv-h6/bin/python check_transverse_quadrature.py` here.

This isolates equal-charge cross-section sampling through a separate Python
implementation of CIC deposition, the cell-averaged 2D logarithmic Green
function, centred gradients and CIC gather. It is not an additional native
OPALX run, curved Coulomb reference, or full reference-path/deposition check.
The native OPALX transverse/longitudinal mesh sequences remain primary.

At a fixed 512x256 transverse Poisson grid, the Cartesian ellipse source is
refined from 32180 to 128708 to 514748 points, retaining the exact conditional
Jacobian mapping. All unique transverse coordinates from the 43 prescribed
targets are checked. Changes, as percentages of E_trans*, are:

| Source grid change | Radial | Vertical |
|---|---:|---:|
| 512^2 to 1024^2 | 0.0585865% | 0.00881992% |
| 1024^2 to 2048^2 | 0.00815297% | 0.0104054% |

These sampled source-resolution differences do not establish a uniform
three-dimensional field-error bound. In particular they do not certify the
longitudinal sampling or the polyline path.

The ideal flat-slice centre field can be obtained independently. Physical
uniform density maps to rho_slice=rho*(1+u/R). For a 2D free-space slice,

    Er(0) = -rho/(2*pi*epsilon0*R) integral_A u^2/(u^2+y^2) du dy
          = -rho*a^2*c/[2*epsilon0*R*(a+c)]
          = -E_trans* a/(2R).

The ellipse integral is pi*a^2*c/(a+c), independently checked by angular
quadrature to 3.4e-16 relative. At exactly 10 pC the analytic field is
-0.0163410032 V/m. The fine reconstructed result is -0.0163383665 V/m.
This is the flat-slice model prediction, not the SACR curved-tube field
(+0.055092 V/m). The native fine Cartesian snapshot gives -0.017629 V/m.
The opposite signs remain visible even though both fields are small compared
with the characteristic transverse field of approximately 13.07 V/m.

CSV values use F=E/(k*rho), in metres, and F_trans*=4*pi*a*c/(a+c).
`summary.json` records numerical settings and the script hash.
