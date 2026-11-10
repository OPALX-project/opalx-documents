# Native PyORBIT triangular-pipe benchmark

Goal: reproduce original triangular conducting-pipe local-model singlekick
benchmark in native PyORBIT3 and export independent probe kicks for OPALX
comparison. Root owns OPALX and common source; this agent owns pyorbit/.

Common case confirmed: fullL10m, beam radius5mm, pipe radius20mm,
protons at kineticenergy0.4GeV, Nreal1e14, Q1.602176634e-5C,
equivalent kicklength1m. Frozen source; no drift profile evolution.

Source: /Users/adelmann/git/PyORBIT3 pinned detached revision
28df66018aebe4e2b780b9747f4a2d7b8430a5c0. No production modifications.
Native MPI-enabled build completed successfully in task-local native-package/.
Build dependencies installed into task-local build-python/ using venvPython,
so shared ~/.venv-h6 site-packages remain unchanged. build.log records build.
Wheel version3.2.dev59+g28df66018; wheel SHA256
63336f027353cfe36caebce56b5e12e91dca33857f8b28f96ba741d23c5f9845.

Native import/zero macrosize probe smoke passed. Native constants:
mass0.938272013GeV, classicalRadius1.534698e-18m,
gamma1.4263156040656624,beta0.7130559804349318 at0.4GeV.
Native deltaE[GeV]*1e9/kicklength[m] yields longitudinal E[V/m].

## Completed

Sixteen native case configurations completed (18 rank manifests), plus the
unmodified upstream random-source triangular drift example. Every native
case exited0. No solver, source-package or coefficient changes were made.
No active task processes remain. No report edits, commit or push by this agent.

run_native.py reads the shared compact tensor NPZ and183 diagnostic points;
zero per-particle macrosize probes give genuine test-particle readout. Six
zero-charge guards enforce exact extrema. Native direct trackBunch gives the
single frozen kick, with coordinates asserted unchanged. DeltaE/L yields
lab longitudinal field. Analytic columns use both SI and native constants;
the tiny constant discrepancy is <3e-7 relative. Source is equal-charge.

Main matched quiet cloud: Ns8192 x Nr16 x Nphi32 =4,194,304 sources.
Physical geometry and intensity equal the original example. Grid series:

- At fixedNz128, Nx=Ny64/128/256/512 axis errors vs SI analytic are
  2.245889%,0.570452%,0.569751%,0.569894%; radial-scan maximum at fine512
  is0.569894%. Plateau metric is1<=abs(s)<=4m; radial scan is s=+-2.5m.
- FixedNx=Ny256,Nz64 and128 agree to roundoff. Nz256 at fixedNs8192
  aliases badly (up to100% plateau error); preserve this diagnostic case.
  Native nearest-longitudinal-slice binning makes source charge counts a
  staircase. IncreasingNs to65536 at256^3 restores agreement with the
  same128Z baseline to roundoff, axis error0.569751%.
- Cross-source refinement Nr32,Nphi64,Ns8192 at512x512x128 gives
  0.2860456% axis and full radial-scan maximum error. This demonstrates the
  approximately0.57% residual of Nr16 is radial source quadrature dominated.
- The Nr32 fine case with boundary points128->256 and free-space modes32->64
  changes maxEs by6.7866313e-7V/m (6.354e-11 of analytic axis scale).
- Native Baartman rb128x128x128 axis maximum error0.0066606%; Nz256 at
  fixedNs8192 aliases to1.2521%, resolved by Ns65536 to0.0065983%. This is
  a separate longitudinal local model with native radius inference.
- Native MPI1/2 main512x512x128 maxEs difference1.5188562e-10V/m,
  1.42199e-14 of analytic axis scale. Audited repeat cases are named
  slice-512x512x128-nativeaudit-r1/r2. Actual native Bunch macrosize sums
  checked and MPI-reduced to exactly1e14 real protons, source count4,194,304,
  total count4,194,493 including183 zero probes and6 zero guards.

The original random-source upstream example (64x64x20,1e6MP,seed10)
prints31 selected near-axis samples around10.3--10.8keV vs10.7keV theory.
It includes a drift, while our controlled study reads the frozen direct kick.
No ring tune shifts or full tracking envelopes were calculated here; this
reproduces the local longitudinal-kick part of the benchmark only.

Reproducibility: build-provenance.json records all relevant pinned source
hashes, clean git state, native library/extension hashes, compiler/MPI/FFTW,
build dependency versions/command and build log. provenance/ holds upstream
MIT license and wheel metadata; no native binaries are needed in the report.
Each case manifest records exact argv, input hashes and harness hash. Both
exact harness revisions are archived in harness-snapshots/ because native
weight assertions were added after the first run batch; no numerical path
changed. Source-resolution control NPZs are compact and reproducibly generated.

Next: root consolidates OPALX/PyORBIT/analytic comparisons and report. All
PyORBIT requested runs and requested boundary/source/MPI controls are complete.
