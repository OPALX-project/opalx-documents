# Triangular bunch in a conducting circular pipe

This reproduces the longitudinal-force part of the ORBIT triangular-bunch
benchmark using native OPALX FFT2D5 and PyORBIT3. It does not reproduce tune
shifts, self-consistent drift tracking or finite curved-source fields.

The common prescribed source is a centred uniform transverse disk of radius
5mm with triangular line density, full length10m,1e14protons (16.02176634μC)
and400MeV kinetic energy. The physical grounded-pipe radius is20mm; fields
are converted to the equivalent energy kick over1m. Native kicks do not evolve
positions. OPALX samples fields after one1e-20s step.

Analytic equations and independent checks are in analytic-audit/analytic.py,
AUDIT.md and analytic-checks.json. The physical comparison uses62on-axis
targets1≤|s|≤4m and82radial-profile targets at s=±2.5m. Both sets exclude
the cusp and ends. Allplots includezero; no constant is fitted.

Run the common-source preparation and OPALX benchmark with:

```sh
/Users/adelmann/.venv-h6/bin/python prepare_common.py
/Users/adelmann/.venv-h6/bin/python opalx/run_opalx.py m128 --mesh 128 128 128 --source common/triangle-ns8192-nr16-np32.json
```

Use `prepare_common.py --ns 16384` for the denser longitudinal source and
`prepare_refinements.py` for compact PyORBIT controls. Distribution files and
HDF5 snapshots remain here; report builds use only archived CSV/JSON evidence.
Completed OPALX cases are integrity-checked and reused rather than overwritten.
PyORBIT run directories are write-once; reproduce into new output directories.

PyORBIT3 is pinned to28df66018aebe4e2b780b9747f4a2d7b8430a5c0 in
/Users/adelmann/git/PyORBIT3, built into pyorbit/native-package. Exactbuild
dependencies/commands and native-library hashes are in
pyorbit/build-provenance.json; examples and all runargv are archived in
pyorbit/runs/*/manifest-rank*.json. Set PYTHONPATH to that native-package before
running pyorbit/run_native.py. The harness accepts shared compact tensor NPZ
files and common/probes.csv. It applies the actual native solver to zero-weight
probes. Exactharnessversions are retained byhash in pyorbit/harness-snapshots.

For two MPI ranks the local launcher needs:
`--oversubscribe --map-by slot --bind-to none --host localhost:2 -np 2`.
PyORBITrank1/2agreement and actualnativeweight sums were checked. OPALXFFT2D5
intentionally rejects multiple ranks; that nativeguard was exercised.

After native runs, rebuild the result CSVs with:

```sh
/Users/adelmann/.venv-h6/bin/python analysis/analyze.py
/Users/adelmann/.venv-h6/bin/python opalx-audit/check_native.py
/Users/adelmann/.venv-h6/bin/python opalx-audit/check_consolidation.py
```

The current OPALX CIRCULAR mode retains open transverse solves and a separate
longitudinal coefficient0.67+2ln(W/a), with numericalfullwidthW also entering
the longitudinal model. PrimaryW20mm makes the effective logarithmic pipe
radius20mm; its numericaldomain±10mm need not reach the physical conductor
for the centred round local model. A separateW40mm control changes the
coefficient. This is documented parameter coupling, not a fitted correction.
The uniformround benchmark instead hasg(r)=1+2ln(b/a)−r²/a² inside thebeam,
and diskaverageg=.5+2ln(b/a). OPALX's .67 profile convention is different.

Raw exploratory256-slice PyORBIT runs with insufficient longitudinal sampling
are retained. Dense-source controls resolve their aliasing; do not use those
unresolved runs as physics conclusions. The final slice residual is explained
by independent radial-source quadrature; see analysis/source-quadrature.json.
No production solver code, numerical coefficients or tolerance was changed.
