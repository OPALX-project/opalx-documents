# Independent API/core review

Reviewer: longitudinal_api, 2026-11-02. Read-only review while root owns the
build. No material defect found in the reviewed diff.

## Physics and numerical path

- The uniform-round interior coefficient equals the potential obtained by
  integrating the uniform-disk Gauss-law field to the grounded circular wall.
  The annulus expression is the corresponding vacuum logarithm. The
  longitudinal field retains the required lab-frame gamma^-2 factor.
- The physical radius is drawn from the validated optional configuration,
  independently of numerical widths in the new mode. Legacy CIRCULAR uses
  the old numerical-width fallback only when radius is absent.
- The wall guard is checked before charge-scaled per-particle time steps can
  be mutated. It ignores invalid particles and outer loops skip inactive
  containers. The solve wrapper restores particle frames on exceptions.
- The Kokkos coverage reduction reads only device views and returns a host
  count. No optional access occurs in device code. The wall clamp is limited
  to the guard's 32-machine-epsilon boundary allowance.
- The legacy gather branch is unchanged apart from explicit-radius opt-in;
  OPEN/PLATES/NONE cannot silently consume a PIPERADIUS because validation
  rejects those combinations.

## Independent tests

The new physics tests integrate the Gauss-law radial field with Simpson
quadrature and differentiate its scalar potential, instead of reproducing
the production g(r) expression. They test a nonzero triangular slope on both
branches, both scatter modes, positive/negative longitudinal momenta,
several transverse radii on both axes, the beam surface, vacuum annulus and
grounded wall. Separate tests vary physical radius and numerical width, and
exercise outside-wall rejection and ignored-invalid-particle behavior.

The new public configuration tests distinguish absent radius from an
explicit zero, reject nonfinite/negative/smaller-than-beam radii, reject
irrelevant mode/solver combinations, preserve legacy absence and verify
physical-radius independence of numerical widths.

## Limits retained

This is a pointwise analytic longitudinal closure for a centred, fixed-radius
uniform round source. It is not a general arbitrary-transverse-density
slice-potential solver, a full transverse conducting-wall solver or a
curvature correction. Existing source/profile and frozen-field limits still
need to remain explicit in the documentation and report.

Root owns compile/test execution and native benchmark validation; no binary
or simulation was launched by this reviewer.
