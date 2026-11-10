# Native PyORBIT tracking contract (pre-run)

Latest scope: exactly ten steps over one metre, matching OPALX initial
particles and its ZeroSC control (same nominal charge, kicks disabled).
The shared source has 1,048,576 particles (Ns64, Nr64, Nphi256).
Radius20mm, length5m, Q10pC,
protons beta=.001, free transverse box48mm, common longitudinal domain12m,
mesh128×128×512. No native solver changes. Root locks final shared source.

## Native maps and common time

Use native `linac_tracking.drift`, rather than the paraxial TEAPOT drift.
Its source `src/linac/tracking/linac_tracking.cc` advances all particles for
`dt=ds/(beta_sync*c)` using their exact relativistic beta_x,beta_y,beta_z.
Its z is displacement from the synchronous particle: `z += (beta_z-beta_sync)c dt`.
Initial cold input maps to `(x,xp,y,yp,z,dE)=(x,0,y,0,s,0)`, where
xp=p_x/p_sync and yp=p_y/p_sync, while the OPALX input is
`(x,0,y,0,s,beta*gamma)` in normalized momentum units.

For each of the ten steps, propose native half drift, native slice SC kick,
native local longitudinal kick, native half drift, matching OPALX's explicit
`SCFIELDUPDATE=MIDPOINT` drift/kick/drift order. The transverse native map
already accepts the physical kick length ds; no amplitude fit is needed.

OPALX deposits on its fixed LAB reference path even though storage follows
the reference particle. Before each native field solve, temporarily map
relative z to `z_lab=z_relative+s_reference(midpoint)` and restore afterward.
Pin the native mesh to the same fixed LAB endpoint/centre coordinates with
zero-weight guards. Keep guards fixed in lab and exclude them from physical
statistics. Native LS bins unit counts. All tracking guards are placed at
the LAB domain ends; the native compact gradient has identically zero
guard contribution throughout the physical bunch. This is explicitly
verified, so no tracking companion is needed.

## Longitudinal step normalization

Native `LSpaceChargeCalc` has no kick-length argument. In its gradient branch,
the kick factor is `period*g_native*r_classical*mass/gamma_sync^2`.
For a physical step ds with prescribed g=6.36, use the exact algebraic
encoding `g_native=6.36*ds/period` and constructor ratio
`exp[(g_native-1)/2]`. Then `period*g_native=ds*6.36`; the period still
sets the common mesh, not a physical pipe. This is step integration, not a
fitted coefficient. Record physical g and encoded per-step g separately.

## Native approximation to retain

The free transverse slice map updates xp/yp without adding transverse work
to dE. Native drift therefore conserves each particle's existing total energy
between longitudinal kicks, while OPALX Boris updates Cartesian momentum.
This differs at second order in the deflection angle. Preserve and report
this approximation in the first native comparison; do not silently add an
energy-consistency patch. Root decides whether any explicit wrapper is needed.

## Feasible source and diagnostics

The root selected a shared D4/octet quiet source with 1,048,576 particles
for ten kicks using one persistent Bunch and solver. Native weighted statistics exclude
zero-weight guards and retain exact physical charge. Export initial plus ten
endpoint rows (reference distance/time, transverse/longitudinal rms, momentum
and energy moments), final particle data, actual mesh metadata and source/
library hashes. The zero-charge run should preserve the cold shape exactly.
No additional step refinement is authorized unless a failure warrants it.

## R=2m continuation

If straight tracking passes, native TEAPOT bend maps can represent a sector
bend of angle0.5rad over1m at R=2m, retaining local slice and scalar-g forces.
They are paraxial maps, whereas OPALX Boris can track the full Cartesian
uniform-field orbit. For a long bunch, material z must remain a phase label
on the curved reference and must be embedded/rotated consistently when
comparing Cartesian moments. The existing frozen shared curved source gives
the required local positions/bases; it does not by itself validate the bend
transport map. Before a charged comparison, require the same ten-step
zero-current orbit/kinematic control and document map approximation.
An exact native RK4 magnetic-field tracker is another existing PyORBIT
option, but its common-time/local-slice interface needs separate inspection;
do not substitute it silently for native bend tracking.

Status: the independent SACR radius sweep and all four native tracking runs
are complete and audited. See HANDOFF.md and completion.json for final
results, conventions and limits. No native physics correction was applied.
