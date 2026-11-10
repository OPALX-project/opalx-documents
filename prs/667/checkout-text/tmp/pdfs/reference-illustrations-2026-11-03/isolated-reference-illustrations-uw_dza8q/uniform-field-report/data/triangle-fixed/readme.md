# Pointwise longitudinal model: fixed triangular-pipe benchmark

This is the implemented follow-up to the conducting-pipe benchmark. All old
results remain in the parent study. No coefficient was fitted to native data.

The new input is:

```text
PIPEMODE="CIRCULAR_UNIFORM", PIPERADIUS=0.020, BEAMR=0.005
```

The physicalpipe radius is separate from PIPESIZEX/Y (full open numerical
widths). The round beam is centred on the reference path with fixed radius.
The model uses the pointwise longitudinal field from the uniform-disk
potential matched to a grounded circularpipe; it includes the vacuumannulus.
It does not change the transverse Poisson operator. The oldmomentclosure is
still available through CIRCULAR; OPEN/PLATESareunchanged.

Build the executable and checks with the existing OpenMP configuration:

```sh
cmake --build /Users/adelmann/git/opalx/build-omp --target opalx_exe TestFFT2D5Numerics TestFFT2D5Algorithm TestSpaceChargeConfig -j 4
```

The target `opalx` builds only the library; `opalx_exe` relinks the executable.
The initial native parse failure in this task exposed that stale-executable
distinction; it was resolved before collecting successful benchmark outputs.
The old executable is archived by SHA in binaries/ and binary-archives.json.

Rerun all six OPALX source/probe pairs and consolidate the native fields:

```sh
/Users/adelmann/.venv-h6/bin/python run_fixed.py
/Users/adelmann/.venv-h6/bin/python analyze_fixed.py
/Users/adelmann/.venv-h6/bin/python capture_checks.py
```

These commands use the parent study's deterministic sources and probes.
Completed cases are write-once/integrity checked. Each pair uses one1e-20s
native step; the matched probe-only field is subtracted at equal macrocharge.
PyORBIT native reruns are in pyorbit/runs; their manifests record exact argv,
source/harness hashes and native particle-weight checks. Reproduce into new
directories, with PYTHONPATH set to ../pyorbit/native-package.

The fixed matchedmesh series is64³/128³/256³ with the same8,388,608source
particles. A W20→40mm control holds physicalb20mm and transverse spacing
fixed. A physicalb20→10mm control holds source/mesh fixed. Legacy CIRCULAR is
also rerun and compared with archived old-binary fields.

Three independent Gauss-law/potential unit tests cover nonzero slopes,
radial fieldshape, both branches, relativistic scaling, annulus/wall,
independent numericalwidth/physicalradius and coverage rejection.
Seven new config/builder tests cover explicitradius and compatibility.
The native FFT2D5-TriangularPipe regression uses the existing regression
framework,65536source+10probe particles, and an independent HDF5 field
validator; it includes a legacy negative control and probe-only control.
Existing OPEN tracking smokes guard backwardcompatibility. See checks/gates.json.

Only accepted frozen longitudinal fields of the straight uniform-round pipe
model are qualified here. The finite-end/free-space/curved-source limitations
of the earlier report are not repaired by this local pipe closure. Newmode
self-consistent tracking and GPU execution have not been validated.
No commit or push is performed by these scripts.
