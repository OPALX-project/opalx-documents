# Independent methods/physics review of the new paper

The source and model equations in
`docs/validation/fft2d5/model-comparison-paper/paper.tex` are physically
consistent. No blocking sign, charge-Jacobian, coefficient or attribution
error was found. This review is read-only; the root owns paper edits.

Verified points:

- The physical density and Q-normalization are correct for both profiles.
  Curved coordinate density is J*rho, with J=1+u/R. The auxiliary u'*rho
  is a source moment, not added physical charge.
- The transverse first-order expansion retains exact circular longitudinal
  separation. Its matched potential, finite-part line kernel, coefficient,
  sign and logarithmic gauge cancellation agree with the independently
  derived Coulomb expansion. Slow longitudinal variation is correctly stated.
- SACR is the finite physical-volume Coulomb reference, with no fitted g,
  conductor, softening or curvature truncation. Its new20mm axis/volume,
  symmetry, differential and scalar-potential checks pass.
- The native PyORBIT modules/free transverse condition and prescribed
  g=6.36 are stated correctly. Constructor-ratio use is not a physical wall.
- The mathematical kappa0 corrected-slice identity with original2D5 is
  correct. Explicitly excluding the separate straight3D FFT branch prevents
  a false native validation claim for that identity.
- The source/operations TikZ diagrams have consistent radius, arc angle,
  local outward/tangent directions and auxiliary-source meaning.
- Qiang is cited as related prior work; the paper does not attribute the
  independently constructed finite-part model to Qiang or claim a Qiang
  implementation. No unsupported novelty claim is made.

Concise clarifications recommended to the root:

1. Use Phi_c for the original rho_c Poisson potential, since Phi0 is later
   defined anew using physical rho. This avoids overloading the same symbol.
2. Explicitly state that each native longitudinal gamma^-2 factor is removed
   in reported electrostatic fields; the displayed original equation retains
   its native convention.
3. State the numerical longitudinal periods and one bunch/vacuum gap, with no
   periodic Coulomb images. Curved PyORBIT matches original OPALX's polyline
   period12.5663673584m; corrected OPALX uses the exact circle12.5663706144m.
   The same physical Cartesian source is conserved, but these numerical
   coordinate conventions should not be called exactly identical.
4. Show the short exact finite-cylinder on-axis equation as the analytic
   reference anchor; use L/2 directly, since h already denotes the matching
   cutoff. A disk-electrostatics reference is appropriate here.
5. Use 'nominal' for10mm in the geometry caption, consistently with the
   stated curved physical section and its12.5ppm centroid-width distinction.

Primary reference verification:

- Oeftiger and Hegglin, HB2016 MOPR025, pp124–129, explicitly give the
  line-density-derivative model and discuss the geometry factor:
  https://proceedings.jacow.org/hb2016/papers/mopr025.pdf
- Qiang's author-submitted preprint verifies the title,2025PRAB28,114602,
  DOI10.1103/npx1-nclt, and circular extension. Its2026version is identified
  as minor improvements over the published version:
  https://arxiv.org/abs/2606.26484v1
- Shishlo et al., PyORBIT, Procedia Computer Science51,1272–1281(2015),
  DOI10.1016/j.procs.2015.05.312, agrees with the publisher and ORNL record:
  https://www.sciencedirect.com/science/article/pii/S1877050915011205
  https://www.ornl.gov/publication/particle-accelerator-simulation-code-pyorbit
- Bochko/Silagadze, EJP41,045201(2020), DOI10.1088/1361-6404/ab87aa,
  is an appropriate primary disk-electrostatics citation for the independent
  cylinder axis construction: https://arxiv.org/abs/2004.04540

Corrected native audit and the new20mm scalar-potential sign check are
recorded separately in `corrected-native-audit.json` and
`curved-potential-sign.json`. The strong slice field and weak curvature field
must retain separate error scales; neither two-grid agreement nor a passing
centre field establishes all-target/end/longitudinal/tracking accuracy.

## Expanded SACR and final results review

The root incorporated the notation, electrostatic gamma convention,
period/geometry, nominal RMS and exact-axis clarifications. The expanded
SACR text and `sacr.tikz` caption pass a further technical review. The
integration-by-parts source-gradient sign is correct. Uniform density leaves
side and end caps; triangular density vanishes on those caps and retains
the volume density-gradient term. Its continuous central cusp requires no
extra internal surface. The illustrated symmetric centreline charges have
outward radial contributions and cancelling tangent contributions, exactly
as the caption states. The finite-cylinder interior-axis formula is correct.

`audit_paper_data.py` independently checked all3,060 field values in20
selected native cases, using OPALX HDF5 probe fields/reference frames/gamma
and native PyORBIT exports with their own bases. Maximum native comparison
error is1.78e-15V/m; all reference copies are exact and all signed residuals
agree to the same precision. Evidence is in `paper-data-audit.json`.

Reported maxima are reproduced: corrected-centre.174006681%, sampled even
field.674333325%. The straight triangular axis result at s1.25m is
.0914573402 versus exact.1374463796V/m,33.4596223% low. Source/grid/
profile labels and the mathematical original=corrected kappa0 identity
are consistent with the actual selected cases. No fake corrected native
straight dataset or hidden straight3D run is reported.

Only optional bound-language precision was noted: rounded.17%/.67% can
be written approximately, or as strict ceilings.18%/.68%. No technical
blocker remains. PDF layout inspection is separate and follows root render.
