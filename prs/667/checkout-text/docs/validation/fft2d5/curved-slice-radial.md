# Circular FFT2D5 transverse field

The original flat slices predict an inward centre radial field for the
5 m physical-density tube at R=2 m. A physical volume element has Jacobian
J=1+kappa*u. Depositing its charge per du dy ds into a flat transverse
Poisson solve biases the source toward the outside. The finite circular arc
also generates an outward field that independent flat slices omit.

Positive u is along b=n cross t, with dt/ds=-kappa*b and J=1+kappa*u.
The circular OPEN path now corrects the transverse field while retaining
2D FFTs. It uses no SACR reference, beam-shape fit, pipe radius or softening.
This is an expansion in transverse size/R, retaining the full arc angle;
it also assumes slow longitudinal variation on the transverse size scale.

## Matched local and distant field

Let k=1/(4*pi*epsilon_0), rho=rho_grid/J, lambda(s)=integral rho dA,
and r=|r_perp-r'_perp|. Use the same logarithmic reference length r0=1 m
as the native 2D kernel. Two existing transverse Poisson solves supply

\[
 \Phi_0=-2k\int\rho\log(r/r_0)\,dA',\qquad
 \Phi_u=-2k\int u'\rho\log(r/r_0)\,dA'.
\]

The near-source expansion of the original Cartesian Coulomb integral gives
a transverse potential correction. Its logarithmic far part matches the
exact circular centreline radial kernel

\[
 K_\kappa(\delta)=\frac{\kappa|\kappa|}
 {4|\sin(\kappa\delta/2)|},\qquad
 C(s)=k\lim_{h\to0}\left[\int_{|\delta|>h}
 \lambda(s+\delta)K_\kappa(\delta)\,d\delta
 +\kappa\lambda(s)\log(2h/r_0)\right].
\]

On a closed circular reference, integrate one turn, with wrapped source
separation and the actual charged profile including its vacuum gap. On an
open arc, charge is zero beyond its endpoints. This is a one-dimensional
line integral, not a three-dimensional convolution. The matching scale h
cancels analytically; there is no numerical cutoff.

The corrected potential and transverse fields are

\[
 \Phi_\perp=\Phi_0+
 \frac{\kappa}{2}(\Phi_u-u\Phi_0)+k\kappa\lambda u-uC,
 \qquad (E_u,E_y)=-\nabla_\perp\Phi_\perp.
\]

In particular,

\[
 E_u=E_{u0}+\frac{\kappa}{2}
 (\Phi_0+E_u[u'\rho]-uE_{u0})-k\kappa\lambda+C.
\]

The arbitrary reference length cancels between the slice potential and C.
Implementation differentiates the combined scalar potential with its valid
convolved halo. It retains the deposited coordinate charge unchanged;
only the two slice sources use physical density.

## Finite-volume line integration

For piecewise constant line density on cells of width ds, the self weight is

\[
 w_0=\kappa\log\!\left[
 \frac{8\tan(|\kappa|\,ds/8)}{|\kappa|r_0}\right].
\]

A source cell centred at separation d>ds/2 has the exact integrated weight

\[
 w(d)=\frac{\kappa}{2}\log\!\left[
 \frac{\tan(|\kappa|(d+ds/2)/4)}
 {\tan(|\kappa|(d-ds/2)/4)}\right],\qquad C_i=k\sum_j w_{ij}\lambda_j.
\]

The current 1D summation costs O(Ns²), with only O(Ns) coefficient storage.
Transverse FFT work remains two solves per occupied slice; a vacuum slice
retains its distant radial field without an FFT. This adds no 3D FFT buffers.

## Scope and checks

The circular geometry may be an open arc or an explicitly closed full circle.
The coordinate and field mesh use the same smooth circle and physical period.
The thin-tube restriction |kappa*u|<=0.01 applies to active source/gather
particles, not empty numerical padding. Occupied grid cells allow the one
CIC-spacing offset from their particle positions; the numerical mesh and
halo must retain a positive metric. This allows a valid beam to reach the
physical limit while its CIC buffer extends outside it. The physical limit
and slow-beam guard beta<=0.1 remain unchanged; neither is an accuracy guarantee. The longitudinal field
retains g=6.36 and still misses the finite-end and curved-source response.

The independent sign checks integrate both the Cartesian Coulomb vector and
the scalar potential without SACR code. At the 5 m/R2 m centre they confirm
outward fields +0.0550920222 V/m (uniform) and +0.0918388656 V/m (triangular)
for Q=10 pC and ellipse semiaxes 5/0.5 mm. The thin-tube continuum prediction
is +0.0550920405 and +0.0918079025 V/m respectively. These are analytical
model checks; native mesh results must be assessed separately.

`TestFFT2D5Curvature` checks the independent Cartesian line kernel,
finite-arc/full-ring identities, gauge cancellation, weak-field sign and
amplitude on a real density grid, unchanged charge and empty-source reset.
`TestFFT2D5Geometry` checks the explicit full-circle mapping in both senses.
Tracking and a general finite-source longitudinal correction remain separate
validation tasks.
