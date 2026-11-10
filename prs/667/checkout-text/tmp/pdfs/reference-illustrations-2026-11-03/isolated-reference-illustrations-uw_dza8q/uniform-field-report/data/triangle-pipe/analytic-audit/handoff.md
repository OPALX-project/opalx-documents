# Analytic audit complete

Goal: independently define the triangular fixed-radius round-pipe reference,
audit native OPALX CIRCULAR mapping and provide reusable no-fit functions.

Files: analytic.py, analytic-reference.json/.csv, AUDIT.md. Constants follow
OPALX Physics.h; default mass0.93827208816GeV,energy0.4GeV,N1e14,L10m,
a5mm,b20mm,one equivalent frozen length1m. Exact metadata is machine-readable.

Key: OPALX g=.67+2ln(min(fullNumericalWidth)/BEAMR), transverse slices open.
Input20mm matches effective longitudinal b20mm on numerical span+-10mm.
Input40mm gives g for effectiveb40mm. This is overloaded parameter semantics;
do not require an open numerical grid to reach the physical conducting wall.
.67 additionally differs from pointwise uniformdisk1 and diskaverage.5.
Matched-effective-b expectednativeerror -8.7473%axis,+5.19466%diskmean.
No production edit or coefficient fit proposed/made.

Analytic breakpointNaNs intentional; fixed1<=|s|<=4m bulk window excludes
cusp/ends. Native-model default is primary fullnumericalW20mm=effectiveb.
The intended exact1m/4m boundary IDs are included with1e-12m coordinate
comparison tolerance; all codes must use the same common target IDs. This
changes neither the physicalwindow nor any fieldaccuracythreshold.
PassW40mm explicitly for widerdomaincontrol at matchedtransversespacing.
All observables SI, PyORBITdEGeV→E[V/m] multiplying1e9/ell, no extra beta.
Independentverify.py checks chargeintegral,diskgaverage,andGauss-law
potentialquadrature derivative: allPASS,maxgradientrelativeerror2.01e-13.
No native simulations run by this agent; root owns runtime/report.
