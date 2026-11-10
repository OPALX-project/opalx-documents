# Round-beam reference status — complete

Goal: independent finite straight-cylinder and exact R=2 m curved-tube
references for the new concise paper. User-confirmed parameters are Q=10 pC,
L=5 m, uniform round transverse disk radius20mm (nominal sigma_x/y10mm),
with uniform and triangular longitudinal profiles. No production/native
source was changed and no solver job was launched by this reference task.

All four field CSVs and both geometry point CSVs are ready. The 51 original
target IDs/longitudinal coordinates are retained; u scales by4 and y by40
relative to the earlier 5/0.5mm ellipse. Native source/PyORBIT agents were
notified when points and references became available.

`acceptance.json` passes: exact straight-axis formulas; independent original
3D volume checks; potential gradient, Poisson/divergence and curl checks;
all-target quadrature refinements; independently integrated curved centre.
`symmetry-checks.json` and `curved-pde-checks.json` also pass. All methods,
equations, sources, output hashes and meaningful bounds are in `MODEL.md`.

One convergence failure was resolved without relaxing its threshold: the
uniform curved .1mm end probes needed160 cap-radial nodes; the previous
64→96 change was2.79e-8V/m, and the final96→160 change is3.37e-11V/m.
Straight and triangular quadrature sequences already passed.

New exact curved centre Eu: uniform+.040935976012, triangle+.063687106181
V/m. New curvature expansion continuum errors: +.000750% and−.29946%.
Curved physical-J source mean_u=50µm; centred sigma_u9.999875mm versus the
nominal10mm (sigma_y remains10mm). This tiny coordinate-density distinction
is explicit, rather than silently recentering/reweighting the source.

Remaining root work: join native OPALX/PyORBIT exports to these independently
computed references, plot, write/compile/review the new paper. Straight
original2D5 equals the mathematical corrected slice model at kappa0; do not
mislabel the separate current straight OPEN3D backend as that model's test.
The local-g longitudinal model already differs from the full straight finite
cylinder (triangle Es at s1.25m ~.091457 versus exact~.137446V/m).
