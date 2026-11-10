# Selecting the FFT2D5 OPEN model

`FIELDSOLVER, TYPE=FFT2D5, PIPEMODE=OPEN, FFT2D5MODEL="ORIGINAL"` selects
independent transverse 2D Poisson slices and the local longitudinal closure
with g=6.36. It uses the reference-path projection and existing slice workspace;
it does not invoke the curvature source correction or the 3D FFT operator.
Current frame, interpolation and other local numerical fixes remain active.
It selects the original physical model, not an older executable byte-for-byte.

`FFT2D5MODEL="FINITE_SOURCE"` preserves the previous local-build default for OPEN:
straight geometry uses the finite-source 3D operator; circular geometry uses
the curvature-corrected slice operator with its existing validity limits.
The longitudinal closure of the circular implementation is still local.
Neither model selector changes PIPEMODE's other longitudinal models.

The original model can be used for controlled comparisons without disabling
validity checks in the curvature operator. Selecting ORIGINAL does not establish
its accuracy for a long curved bunch. The two models must be identified in
tracking reports. The selected value is printed in the solver input summary.

Example (retain the desired source, reference path and mesh settings):

```
FS: FIELDSOLVER, TYPE=FFT2D5, PIPEMODE=OPEN, FFT2D5MODEL="ORIGINAL",
    NX=512, NY=512, NZ=512,
    PARFFTX=FALSE, PARFFTY=FALSE, PARFFTZ=FALSE,
    REFPATHFNAME="circle-R2.dat", CLOSEDRING=TRUE,
    PIPESIZEX=.256, PIPESIZEY=.320, BEAMR=.02,
    SCATTERLONGITUDINALLY=TRUE;
```

`FFT2D5MODEL="ORIGINAL"` is rejected for other FIELDSOLVER types.
