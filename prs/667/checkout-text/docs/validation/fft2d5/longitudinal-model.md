# FFT2D5 longitudinal models

For a circular path, `PIPEMODE="OPEN"` uses the transverse slice backend with
the [thin-tube radial correction](curved-slice-radial.md): two 2D Poisson
solves per occupied slice and a one-dimensional circular line integral.
The longitudinal field still uses the original local closure
`E_s=-6.36*lambda'/(4*pi*epsilon_0*gamma^2)`. Correcting the transverse
curvature field does not supply the missing finite-source longitudinal field.
The pipe/NONE modes retain their existing separate slice/local models.

Straight OPEN retains the separate finite-source 3D FFT backend described
below. The curved version of that backend remains an experimental component
with its own tests; it is not selected by the circular OPEN path.

## Separate finite free-space 3D FFT model

For signed constant curvature `kappa`, transverse displacement `x=u-u'`,
vertical coordinates `y,y'`, and arc separation `tau`, define
`xi=2 sin(kappa*tau/2)/kappa`, `D=x*x+(y-y')^2+xi*xi`,
`G=D^(-1/2)`, `H=xi*xi*D^(-3/2)`, and `F=x*H`.
The first-order circular Coulomb potential is

\[
 \Phi=\frac{G*\rho_c-\kappa u(H*\rho_c)
                     +\kappa(F*\rho_c)/2}{4\pi\epsilon_0},
 \quad (E_u,E_y,E_s)=
 (-\partial_u\Phi,-\partial_y\Phi,-\partial_s\Phi/(1+\kappa u)).
\]

`rho_c=dq/(du dy ds)` is the deposited coordinate density, so the charge
already includes the physical Frenet Jacobian. Do not multiply by it again.
The full angular chord is retained; only transverse size/R is expanded.
The three convolutions reuse the same source spectrum. Singular cell kernels
are integrated analytically with a smooth curved-minus-flat correction;
physical-cell derivatives are fourth order.

This uses 3D FFTs on a uniform `(u,y,s)` array representing the thin tube.
No native curved IPPL mesh or general mapped Poisson solver is constructed.
The array avoids a global Cartesian box covering the orbit, but retains
genuine 3D FFT memory and computation costs exceeding the slice models.
The path must
be straight or a horizontal circular arc shorter than one turn; unsupported
paths and closed rings are rejected. Smooth geometry is used consistently
for deposition and gathering. Mesh plus field halo must satisfy
`abs(kappa*u)<=0.01`; every source needs a half-cell CIC margin.

Straight beams use a common mean-gamma rest-frame stretch and field boost.
Curved beams use instantaneous electrostatics and currently reject beta>0.1;
this cutoff is not a per-component error bound. The requested frozen test uses
beta=.001. The local magnetic-field approximation is not a nonlocal
Biot-Savart solve. Relativistic curved-bunch tracking remains unvalidated.

## Pointwise uniform-round-beam model

Use `PIPEMODE="CIRCULAR_UNIFORM"` for a beam with a uniform circular
cross-section of fixed radius `BEAMR=a`, centred on the reference path, inside
a coaxial grounded circular pipe of physical radius `PIPERADIUS=b`. Both radii
are in metres and must satisfy `b >= a > 0`.

For laboratory line charge `lambda(s)` and mean longitudinal Lorentz factor
`gamma`, the model is

\[
 E_s(r,s)=-\frac{\lambda'(s)}{4\pi\epsilon_0\gamma^2}g(r),\qquad
 g(r)=\begin{cases}
  1+2\ln(b/a)-r^2/a^2,&0\le r\le a,\\
  2\ln(b/r),&a<r\le b.
 \end{cases}
\]

Here `r` is the distance from the reference path in its transverse plane.
The annular expression joins continuously at `r=a`; the longitudinal field
vanishes at the grounded wall `r=b`. A particle beyond that physical radius
causes an error. This check does not implement a transverse wall or particle
loss at the conductor.

The result follows by integrating the round beam's Gauss-law radial field to
the grounded wall and differentiating the resulting potential longitudinally.
The on-axis geometry factor is `1+2 ln(b/a)`. Its charge-weighted uniform-disk
average is `0.5+2 ln(b/a)`. These are distinct observables.

`PIPESIZEX` and `PIPESIZEY` remain full numerical transverse mesh widths.
They set the mesh origins and spacings and do not set `b` in this mode.
Changing the numerical width at fixed `PIPERADIUS` therefore leaves the
physical longitudinal model unchanged. For example:

```opal
FS: FIELDSOLVER, TYPE="FFT2D5",
    NX=128, NY=128, NZ=128,
    PARFFTX=FALSE, PARFFTY=FALSE, PARFFTZ=FALSE,
    PIPEMODE="CIRCULAR_UNIFORM", BEAMR=0.005, PIPERADIUS=0.020,
    PIPESIZEX=0.040, PIPESIZEY=0.040,
    REFPATHFNAME="straight-reference.dat",
    CLOSEDRING=FALSE, SCATTERLONGITUDINALLY=TRUE;
```

The mode requires `PIPERADIUS`; it does not infer the beam radius or profile
from the particles. It is a local long-beam approximation for a fixed uniform
round section. For a triangular line density, the analytic comparison applies
on the linear branches away from the cusp and ends. It does not reproduce
nonlocal finite-end fields, arbitrary transverse distributions or the full
field of a finite curved source.

## Retained scalar models

`CIRCULAR` retains the equivalent parabolic/ellipsoidal moment-model
coefficient `0.67+2 ln(b/a)` and gives the same longitudinal field to all
particles at a given `s`. An explicit `PIPERADIUS` separates its physical
length from the numerical mesh. If that attribute is absent, the historical
calculation uses `min(PIPESIZEX,PIPESIZEY)` in place of `b`.

The value `0.67` is not the uniform-disk on-axis constant `1`, nor its
transverse-average constant `0.5`. Replacing that constant alone cannot
recover the pointwise radial field variation. Existing `CIRCULAR` inputs
without `PIPERADIUS` retain their previous behavior.

`PLATES` retains its scalar model and numerical-width convention. `OPEN` uses
the finite-source potential above. Neither accepts `PIPERADIUS`;
`NONE` disables the longitudinal field and also rejects that attribute.

## Comparison with PyORBIT

| Model | Transverse calculation | Longitudinal calculation |
|---|---|---|
| PyORBIT slice-by-slice | A transverse Poisson solve for each longitudinal slice, with a supplied conducting boundary | The longitudinal gradient of the same sliced potential, when enabled; the current implementation disables this kick without a boundary |
| OPALX `CIRCULAR_UNIFORM` | Open transverse Poisson solves for the deposited slice distributions | An independent local formula for a centred, fixed-radius uniform round beam and an explicit circular-pipe radius |
| PyORBIT Baartman variant | One projected transverse distribution, with kicks weighted by line density | A separate local line-density derivative with radial dependence; its equivalent beam radius is estimated from transverse second moments |

Thus the new OPALX mode shares the round-beam longitudinal formula with the
Baartman variant, while retaining OPALX's separate transverse slice solves.
It does not turn FFT2D5 into PyORBIT's sliced-potential model or a full 3D
Poisson solver. For a general evolving transverse profile, the OPALX
longitudinal formula is not derived from its numerical transverse potential.

The native triangular-bunch comparison and its numerical controls are
recorded in the uniform-field validation report. They concern frozen
longitudinal fields; they do not establish tune shifts, evolving-bunch
tracking or curved-source accuracy. FFT2D5 still requires one MPI rank,
`BINS=NONE`, open `BCFFT*` values and no Cartesian-domain or cathode-plane
correction.

Primary references:

- [Baartman, *Form Factor g in Longitudinal Space Charge Impedance*](https://arxiv.org/abs/1508.00153).
- [Oeftiger and Hegglin, *Space Charge Modules for PyHEADTAIL*, HB2016](https://proceedings.jacow.org/hb2016/papers/mopr025.pdf).
- [PyORBIT3 slice-by-slice implementation](https://github.com/PyORBIT-Collaboration/PyORBIT3/blob/28df66018aebe4e2b780b9747f4a2d7b8430a5c0/src/spacecharge/SpaceChargeCalcSliceBySlice2D.cc).
- [PyORBIT3 Baartman implementation](https://github.com/PyORBIT-Collaboration/PyORBIT3/blob/28df66018aebe4e2b780b9747f4a2d7b8430a5c0/src/spacecharge/SpaceChargeCalc2p5Drb.cc).


## Frozen-field validation and charge audit

The finite curved-tube study uses the specified uniform and triangular
physical densities at L=5 m, R=2 m, radial/vertical semiaxes of 5/0.5 mm and
10 pC. SACR evaluates the exact finite-source Coulomb field independently
of the production convolution. The reproducible source, mesh and reference
checks are archived with the LaTeX report in `uniform-b-ellipsoid/report`.

For quiet weighted sources, the benchmark uses the existing native checkpoint
and Q/M attributes, with mass proportional to charge. A tracker fix skips the
emission initialization when no emitting sampler exists; otherwise it would
replace all restored Q/M values with the first particle's values. Every input
and output charge/mass is checked by particle ID before a field is accepted.
The known weighted-source H5 `CHARGE` header uses a representative particle
charge rather than `sum(q_i)`; use the actual q datasets for this audit.
No output-header value or fitted field scale enters the SACR comparison.

These are frozen electric-field tests. Close to a sharp end, the longitudinal
mesh and field interpolation must resolve the requested distance to the end;
agreement at points 5 mm inside does not qualify points 0.1 mm inside. The report
keeps the closer probes visible and states their remaining numerical error.
The tests do not qualify the local magnetic-field approximation, evolving
bunch tracking or relativistic curved-beam dynamics.
