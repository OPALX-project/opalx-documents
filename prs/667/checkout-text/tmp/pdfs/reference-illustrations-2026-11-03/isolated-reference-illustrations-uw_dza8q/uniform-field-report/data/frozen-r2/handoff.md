# Direct FFT2D5 / SACR frozen-field comparison

Goal: compare all three local electric-field components for a constant-section
uniform-physical-density 5 m tube, R=2 m, radial semiaxis 5 mm. Vertical
semiaxis 0.5 mm and beta=0.001 are controlled benchmark choices, not confirmed
operating parameters. Charge is 10 pC; electrostatic fields scale linearly.
No tracking-accuracy or real-beam energy claim. No production changes or push.

Reference owner: sacr_uniform_tube, `reference/`. Root owns native OPALX input,
source generation and runs. Read-only solver/frame audit by fft_frozen_audit.
Use the current pinned build-omp/src/opalx, source hashes checked against the
completed 10 pC study; no rebuild. Only one MPI rank is supported by FFT2D5.

Plan: converged independent boundary Coulomb reference at 43 targets; native
one-step OPALX fields with tiny dt and H5 ID/frame reconstruction; transverse
mesh refinement at fixed NZ and separate longitudinal refinement. Control
particle sampling and path geometry before assigning persistent differences
to the solver model. Uniform tube ends are sharp, so separate bulk and ends.
Use fixed characteristic scales, retain zero fields, report absolute V/m.

Numerical design: equal-charge product source, midpoint longitudinal stations
and equal-area polar cross samples with the exact physical Jacobian inverse
angular transform. Source spacing commensurate with longitudinal grids.
Reference path extends to +/-4 m. Add probe-centred straight segments so the
local polyline tangents at probes equal exact circle tangents. Path refinement
is an independent control. Probe-only companion runs permit subtraction of
the small diagnostic-particle charge contribution by field linearity.

## Progress

Independent constant-tube reference complete in `reference/`: 43 points,
boundary levels through phi4096/nrad128, largest final normalized change
6.78e-12. Endpoint, PDE, symmetry, straight-cylinder and independent volume
checks pass. Use current acceptance.json (four PDE targets, including an end).

Current binary e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf
and all 12 pinned solver/build source hashes match the earlier completed
study. No rebuild. A distant inactive drift gives zero external E/B and fast
reference setup; the prescribed charge geometry/reference path supplies the
curvature for this frozen solve. Two earlier active-element pilots were
stopped by PID before any physical step because OrbitThreader would traverse
the active element with dt=1e-17. Their logs/manifests are archived as
pilot-uniform-b-stopped and pilot-drift-stopped. One under-specified drift
placement was corrected before running the successful cases.

Native pilot and exploratory mesh pairs all complete: xy64/128/256-z512,
xy128-z1024/z2048, with Ns2560/Ncross1024. Extra Ncross4096 and Ncross16384
fine-XY cases also complete. All H5 charge/count/ID/time/finite checks pass;
probe motion about 2.9e-12 m. H5 coordinates and E are in the tracker frame;
analysis reconstructs global coordinates and exact-circle local components.
Probe-only Es is corrected for the small mean-gamma difference before
subtraction. Actual source charge excludes the subtracted 43 probe charges.

Exploratory results reveal transverse source-quadrature error, so final
transverse sequence uses a matched dense cross-section source:
Ns640 x Ncross16384, NX/NY=64/32,128/64,256/128,512/256 at NZ512.
`run_transverse.py` is running this sequence (root owns it).

Independent audit/longitudinal_sampling.py shows Ns2560 aliases at NZ4096.
Final longitudinal sequence uses Ns5120 x Ncross1024, NX128/NY64,
NZ512/1024/2048/4096, plus Ns10240 at NZ4096 and path-step .01 m control.
fft_frozen_audit owns these native runs; root must not duplicate them.
Its reproducible 1D audit predicts fixed-probe spurious Es below .001% of
the SACR tangential scale for either denser longitudinal source.

frozen_analysis owns `analysis/`: validated compare script, all-case CSV/JSON,
separate matched T/L plot selectors, publication field/mesh/end figures and
explicit centre radial field. Early centre Er shows why characteristic-field
agreement alone cannot validate the much weaker curvature-only hoop field.

Next: finish matched sequences and independent source/path controls; check
all-axis convergence (not assumed), review final plots and report conclusions.
No production changes, commit or push. Keep all inputs/logs/manifests.

## Further controls / current active work

Both matched initial sequences now complete. L all43-target maximum Es error
for NZ512/1024/2048/4096 is 34.51/73.32/53.55/100.00% of the fixed tangential
scale; the finest sampled miss survives Ns5120->10240 (<.001% change).
All12 longitudinal controlled snapshots pass independent integrity checks.
Native all-station end profiles are in audit/ and being plotted by analysis.

Dense polar T source is still NOT independently converged: at Nx512/Ny256,
Ncross16k->65k (fixed Ns320) changes radial/vertical fields by 1.59/.82% of
their scales. Ns320 vs640 affects near-end CIC profiles strongly. Those
exploratory data must not be sold as a converged physical discrepancy.
All high-polar controls complete; no root process from them remains.

Root therefore added optional --cross-layout cartesian to run_study.py;
default polar behavior is unchanged. The new equal-area clipped Cartesian
midpoint cloud uses the exact conditional-u Jacobian inverse, preserving
uniform physical density. Source Ns640/Nrad512/Nphi512-cartesian has 32180
cross points (20,595,200 source particles), mean u=3.124029um versus exact
3.125um. The small ellipse boundary quadrature is explicit. This quiet grid
should avoid annular structure on the fine CIC mesh. Pilot
xy512-z512-cart uses mesh512x256x512 and pathstep .005; root launched it in
exec session44334, currently running. If clean, run matched Nx128/256/512
with that source and seek a source-resolution control. Do not silently claim
convergence if the particle or path controls still fail.

fft_frozen_audit is running dense-polar T path controls .01 and .005 at
Nx512/Ny256/Nz512, Ns640/Ncross16k. Root must not duplicate those names.
sacr_report_figures is preparing a concise 3-page report extension READ-ONLY,
waiting for final numerical data. It owns report/ and will run the PDF edit
marker exactly once before authoring, then compile/render/check/sourceZIP.
Root has not run a marker for this new PDF edit. Frozen_analysis owns all
analysis files/figures; it knows the new Cartesian design and must select
independent matched T and L series. Existing final16-page PDF remains intact
until final data are ready. Do not deliver provisional plots.

## Final numerical study complete

All 21 main/probe pairs (42 native runs) completed. The final matched
Cartesian T cases are xy128/256/512-z512-cart with the same Ns640 x 32180
source and .005 m path. All six Cartesian snapshots pass independent checks;
all 12 controlled L snapshots also pass. No native run remains active.
Two dense-polar T path cases mentioned above were never started (messages to
an idle agent had not triggered work); they are not results or pending tests.
The final quiet Cartesian source/path supersedes that proposed control.

Last T refinement 256x128 ->512x256 at fixed NZ512 changes fields by
0.00468794% radial and 0.0488219% vertical of the transverse scale. Fine
interior errors (end distance >=50mm, inclusive roundoff tolerance1e-12m)
are 0.55628% radial and 0.04136% vertical. Fine all-point T-case errors are
4.2403% radial/2.6475% vertical; their end-region longitudinal resolution is
not established by a T-only scan. The L-study finest max Es error is100.00%
at the fixed near-end probes, stable under doubled Ns/path controls.

The midpoint on the reference path (u=y=s=0) has native Er=-0.0176291V/m
at512 vs-0.0176243V/m at256 (exact10pC normalization differs by ppm). SACR
gives +0.055092V/m. The ideal flat-slice model with rho_slice=rho*(1+u/R)
independently predicts -0.0163410V/m, from
integral_A u^2/(u^2+y^2)dA=pi*a^2*c/(a+c). Root verified the integral to
3.4e-16relative. Thus boundary-scale agreement masks the wrong curvature
response. This is a model diagnosis, not a newly applied solver correction.

Auxiliary `source-controls/` performs independent 2D CIC/log-kernel source
quadrature refinement, NOT another native or curved-path test. 32180 ->
128708 ->514748 cross points gives sampled r/y changes .05859/.00882%,
then .00815/.01041% of transverse scale. Analysis read-only reviewed it.
This does not bound full3D/path error; its scope is documented explicitly.

frozen_analysis is writing final all-case CSV/JSON and publication plots with
the three Cartesian levels plus four matched L levels; report agent has
written the three-page extension and will snapshot final evidence/compile.
PDF edit marker already succeeded ONCE for this extension; DO NOT repeat.
Root updated NEXT-STEPS and new frozen README. Python compile and
git diff --check pass. Next: inspect final plots/PDF, freeze QA/sourceZIP,
write completion/provenance and give final self-contained result to user.
