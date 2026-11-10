# Direct frozen FFT2D5 / SACR comparison

Purpose: measure the field accuracy of the existing FFT2D5 solver for a long
beam on a curved path, separating mesh/sampling effects from its physical
approximation. These are frozen electric fields, not a tracking benchmark.

## Prescribed source and measurement

- Uniform physical volume density in a constant elliptical cross-section.
- Full arclength 5 m; bending radius 2 m; radial semiaxis 5 mm.
- Vertical semiaxis 0.5 mm, charge 10 pC and beta 0.001 are benchmark choices.
- Sharp ends at s=+/-2.5 m. Physical volume is pi*a*c*L.
- 43 fixed targets include symmetry zeros, off-axis bulk and 5/10 mm end probes.
- A one-step readout with dt=1e-17 s and zero external fields freezes the
  prescribed curved geometry. Probe motion is a few picometres.

Native input files and output logs are under `runs/`; generation and paired
probe subtraction are reproducible with `run_study.py`. Particle sampling
includes the physical volume Jacobian 1+u/R. A probe-only companion removes
the small diagnostic-particle charge contribution. The analysis restores the
HDF5 tracker frame to global coordinates, then projects into each target's
outward radial, vertical and tangential directions.

`reference/` contains the independent SACR boundary integral for the constant
tube, including both end caps. It is independently checked by endpoint,
symmetry, straight-cylinder, Cartesian Poisson/curl and volume integrals.
This is a different source from the tapered family used in the Dubin limit.

## Matched numerical studies

The transverse sequence uses NX/NY=128/64,256/128,512/256 at NZ=512,
with one common Cartesian quiet source (640 longitudinal stations x 32180
cross points) and a 5 mm reference-polyline step. The final refinement changes
the sampled radial/vertical fields by 0.00469%/0.04882% of the transverse
characteristic field.

The independent longitudinal sequence uses NX/NY=128/64 and NZ=512,1024,
2048,4096 with one common 5120x1024 source. Doubling the longitudinal source
sampling at the finest mesh and halving its path step check the end-field
conclusion. Exploratory polar sources and their sampling controls are retained
and distinguished from the final Cartesian transverse series.

Cross-section sampling has a separate auxiliary check in `source-controls/`:
an independent CIC/2D-convolution reconstruction refines the quiet cloud to
128708 and 514748 cross points. The largest sampled change is below 0.059%
of the transverse field scale. This isolates transverse source quadrature;
it is not a full native curved-path or longitudinal error bound.

FFT2D5 explicitly supports one MPI rank here. The pinned executable SHA256 is
e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf;
all 12 prior solver/build source hashes still match. No production code,
g-factor or numerical acceptance tolerance was changed.

## Findings and limits

For targets at least 50 mm from either end, the fine Cartesian radial and
vertical maximum differences from SACR are 0.5563% and 0.04136% of their
characteristic field. These component scales retain zero-field points and
are not the local field value. At 10 pC the transverse scale is 13.0728 V/m.

The weak radial curvature field is not reproduced: at the beam centre,
SACR gives +0.055092 V/m (outward), while the refined native field is
-0.017629 V/m (inward). The current ideal flat-slice model predicts
-0.016341 V/m because its deposited density is rho*(1+u/R). Thus a small
error relative to the large transverse field does not certify the curvature
response. `source-controls/README.md` gives the independent analytic limit.

The longitudinal field also fails the finite-source reference. At 5 mm inside
an end, SACR gives about 3.25 V/m while the finest FFT2D5 field is essentially
zero. Refinement narrows and raises the mesh-localized gradient force rather
than producing SACR's extended finite-end field. Native source-particle end
profiles make this distinction visible independently of the 43 probes.

The transverse scan holds NZ=512, so end-region transverse differences
(about 4.24% radial and 2.65% vertical) are not combined transverse/longitudinal
convergence results. No distribution-wide error bound, complete 1% curved-beam
qualification, or self-consistent tracking validation follows from this study.

## Reproduction and outputs

Use `/Users/adelmann/.venv-h6/bin/python`. For example:

```sh
python run_study.py xy512-z512-cart --mesh 512 256 512 --ns 640 \
  --nrad 512 --nphi 512 --cross-layout cartesian --path-step .005 --run
python run_study.py xy128-z4096-ns5120 --mesh 128 64 4096 --ns 5120 --run
python analysis/analyze_fields.py --require-all
```

Completed results are preserved, rather than overwritten. `analysis/` contains
all-component fields/errors, mesh/control changes, integrity checks and
publication figures. `audit/` contains independent source/frame/native-profile
checks. The LaTeX report copies small scripts, evidence and figures; large
native source/HDF5 files remain here. No commit or push is performed.
