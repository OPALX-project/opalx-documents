# Native PyORBIT triangular conducting-pipe benchmark

The unmodified PyORBIT3 source at revision
`28df66018aebe4e2b780b9747f4a2d7b8430a5c0` was compiled with MPI support.
The frozen direct kick reproduces the longitudinal local-model benchmark:
uniform transverse disk radius5mm, triangular full length10m, conducting
pipe radius20mm,1e14protons at400MeV, equivalent kick length1m.

The numerical result comes directly from native `trackBunch`, using zero
macrosize probe particles. No field expression in the solver was modified.
The analytical comparison is the round-pipe long-bunch expression

\[
E_s(r,s)=-\frac{\lambda'(s)}{4\pi\epsilon_0\gamma^2}
\left(1+2\log(b/a)-r^2/a^2\right),\quad r\le a.
\]

`run_native.py` accepts the shared compact NPZ source and probe CSV, native
model (`slice` or `rb`), mesh sizes and output directory. Each native run
archives its command, input/harness hashes, constants and per-rank probe CSV.
Source and probe coordinates remain fixed during each kick. The new audited
cases additionally verify actual native Bunch weights and counts, including
MPI reductions. Both exact harness versions are in `harness-snapshots/`.

Example replay, after building the package as recorded in `build-provenance.json`:

```sh
PYTHONPATH=/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe/pyorbit/native-package \
  /Users/adelmann/.venv-h6/bin/python run_native.py \
  --source ../common/triangle-ns8192-nr16-np32.npz \
  --probes ../common/probes.csv --out replay-slice512 \
  --nx 512 --nz 128 --model slice
```

The MPI launcher needed explicit slot mapping on this machine:

```sh
mpirun --oversubscribe --map-by slot --bind-to none --host localhost:2 -np 2 ...
```

Fine slice fields agree with the continuum model within0.57% for the main
Nr16 source and0.287% after doubling radial and azimuthal source sampling.
The native rb model agrees within0.0067%. The unresolved fine longitudinal
source cases are retained: nearest-slice binning needs source resolution to
grow with the longitudinal grid. Explicit Ns65536 controls resolve them.
Numerical boundary refinement is negligible; MPI1/2 agrees to roundoff.

`HANDOFF.md` records the exact completed case set and metrics. Root's
independent consolidated analysis is in `../analysis/`. These are frozen
longitudinal-kick comparisons; ring tune shifts and evolving-bunch tracking
were not tested.
