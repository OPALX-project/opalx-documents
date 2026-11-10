# Completed SACR constant-section frozen reference

Goal: independent all-component Coulomb fields for direct FFT2D5 comparison
on the physical-uniform-density 5 m tube, R=2 m, radial/vertical semiaxes
5/0.5 mm. The vertical size remains a benchmark assumption.

Owned files are this reference directory only. `tube_reference.py` evaluates
the exact side-plus-two-cap boundary integral and independent tangential
filament endpoint identity. `build_reference.py` fixes 43 exact targets,
performs six quadrature levels, writes converged fields and independent checks.
`README.md` documents equations, normalization, SI conversion and use.

Run with `~/.venv-h6/bin/python build_reference.py`; final run ~4.7 s and all
acceptance checks pass. Max last-refinement r/y/s changes are
5.31e-16 / 6.78e-12 / 2.19e-16 of the declared scales. An initial
128/256/512/1024 run failed the tighter 1e-6 criterion at vertical-axis y=.9c;
2048/4096 levels resolved that known angular quadrature difficulty.

Independent checks: tangent endpoint 3.89e-16 of tangential scale;
symmetry 1.12e-14 of component scale; straight-cylinder limit 4.41e-13;
exterior volume/surface integral 3.73e-14 relative. Cartesian PDE residuals
at four interior targets (including 10 mm from a cap) are max divergence
3.89e-10 and max curl 2.24e-10 after normalization by 4*pi. These finite
difference values include truncation, not a uniform accuracy bound.

Physical volume is 3.926990816987242e-5 m^3, rho=Q/V. Source sampling must
include J=1+u/R to represent constant physical density. F=E/(k*rho) has units
metre and local order r/y/s. Shared transverse scale is .005711986642890534 m;
fixed tangential scale .0014202325784798471 m. Bulk/end groups must also be
examined separately because the near-end tangential signal is much larger
than bulk tangential fields.

No OPALX field, fitted g, softening, simulation, tracking, production code or
old tapered reference was changed or used. Source hashes are in acceptance.json.
Next: root generates matched particle/tracer source, runs meshes and compares
tracer fields in the same local frame. This static source cannot represent a
subsequently deformed self-consistent beam.
