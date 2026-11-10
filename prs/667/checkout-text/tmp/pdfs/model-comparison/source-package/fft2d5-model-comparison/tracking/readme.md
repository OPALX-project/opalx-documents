# First native tracking comparison

User-authorized scope: exactly ten steps for a straight bunch; if its
consistency checks pass, repeat on an R = 2 m bend with exactly ten steps.
No extra step-refinement campaign is requested. The initial source is cold,
uniform in a radius-20-mm disk and over 5 m, with 10 pC of protons at beta
0.001. The nominal transverse RMS is 10 mm. Each geometry shares identical
particle bytes/IDs between codes (1,048,576 quiet equal-charge particles).

The ten steps cover a nominal reference flight distance of 1 m. OPALX uses
its immutable original e85 2D5 slice executable with explicit MIDPOINT
field updates. PyORBIT uses native drift/bend maps, its native free transverse
slice solver and the matched local longitudinal model g = 6.36. A fixed
48 mm transverse box and numerical longitudinal vacuum gap are used. The
current experimental straight 3D OPEN implementation is excluded.

Each geometry has a ZeroSC control using the same nominal charge/mass and
initial source with self-field kicks disabled. This is not a literal
zero-macroparticle-charge test. Source population, total physical charge,
finite coordinates and matching initial moments must pass. Compare all
three RMS sizes, centroids and charged-minus-ZeroSC changes, rather than
using total RMS alone to judge space-charge response. An approximate 1%
code-to-code RMS criterion is a screening check, not a field or tracking
accuracy certificate. Native differences and the absence of step convergence
with only ten steps must remain explicit.

`prepare_shared.py` reuses audited D4 and curved physical-J source generators.
Files in `sources/` record physical local coordinates, Cartesian positions,
normalized momenta, IDs, source/driver/helper hashes and FROMFILE inputs.
Straight material coordinates equal Cartesian coordinates at t = 0. Bend
momenta are tangent with the same beta*gamma for every particle. The bent
physical cross-section includes J = 1 + u/R, so its mean u is 50 micrometres.
No fit or RMS rescaling is applied.

Ownership: OPALX cases and transport audit in `opalx/`; native PyORBIT in
`pyorbit/`; root owns shared sources, combined analysis and report. Detailed
native conventions and limits are in each code's design/manifest records.

Completed 4 November 2026: all eight primary cases and independent source/frame
audits pass. The combined records are in `analysis/comparison.csv` and
`analysis/final-comparison.csv`; the updated paper documents results and
measured limits. No further native runs are pending.
