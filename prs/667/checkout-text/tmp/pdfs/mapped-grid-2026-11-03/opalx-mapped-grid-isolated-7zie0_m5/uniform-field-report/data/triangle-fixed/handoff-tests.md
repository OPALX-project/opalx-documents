# Independent uniform-round pipe physics tests

Owner: /root/longitudinal_physics_tests. Production scope restricted to
unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp. Root owns solver and builds;
API agent supplies CIRCULAR_UNIFORM/PIPERADIUS plumbing. No native build or
test executable was launched by this agent to avoid concurrent build races.

Three tests added:

- UniformRoundPipeLongitudinalFieldMatchesGaussLawPotential: normalized
  uniform-disk grid cells have exact triangular line charge; longitudinal
  scatter/gather is checked against a real-space Gauss-law potential integral,
  followed by an independent finite-s derivative. Tests r=0,a/2,a,(a+b)/2,b;
  both transverse axes and signs; both triangle branches; CIC and NGP;
  ps=0,.4,1,-.4 and therefore gamma^-2. No transverse FFT is required because
  this isolates the new longitudinal model and deposition integral.
- UniformRoundPipePhysicalRadiusIsIndependentOfMeshWidth: W4→6 at fixed b
  does not change E_s, while physical b1→1.5 changes it by the additional
  vacuum-annulus potential. Both geometries match independent potential.
- UniformRoundPipeRejectsParticlesOutsidePhysicalWall: new mode throws on
  an active r>b target in scatter and gather, while an invalid-masked outside
  particle is ignored. The grounded wall itself is included in first test.

Independent reference integrates E_r/linecharge inside/outside the beam via
split1024-panel Simpson quadrature. check_test_reference.py compares against
the separately integrated analytic potential over80points and gamma cases.
Worst relative field-reference error1.058e-11; new unit tolerance2e-8 has
ample numerical margin and remains far below1% physical acceptance.
unit-reference-check.json records the numerical tolerance justification.

git diff --check for the edited test source passes. Root still needs to build
and run the new tests after API and algorithm implementations are ready.
