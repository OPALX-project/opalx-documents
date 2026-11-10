# FODO MultipoleT regression investigation

Goal: explain the two FodoCell-multipoleT-fromfile CI mismatches without weakening tolerances, changing inputs, or silently replacing references. This is manual regression analysis; no native-unit-test Python/data/executable dependency is added.

## Repository and run state

- OPALX source HEAD: `23f04f6c8e57f497e6f1a722038f9e1cef010803`; tracked tree clean when inspected.
- Fresh local executable SHA256: `26ae4cdec13aa24bcacea47942ad8a0a86b3cddb9a65f8dc37f3847ba76f04a8` (built immediately before the publish commit; identical validated source state).
- Regression checkout HEAD: `a8bd50c4`, tracked tree clean. Another agent fetched current origin/master `737547e6ae38cf3001d6bc45cf38dd1a47d78402`; FODO directory diff between these revisions is empty.
- Historical reference `.out` identifies OPALX revision `72dd3803bfc066c1d4bf568dcad02ea8484c6b2b`, generated July 17, 2026. That historical OPALX object is unavailable locally.
- `head-23f04f6`: unchanged maintained input and particles, one MPI rank, OMP_NUM_THREADS=1, exit 0, fresh directory with executable/input hashes and complete log.
- `body-clipped-diagnostic`: separate one-rank negative control adding BBLENGTH=0.5 to each magnet. This deliberately changes physical support and is not a proposed input/reference fix. Maintained files remain untouched.

## Reproduced failure and comparison definition

The unchanged run produces 2001 matching timestamps and reproduces the old CI's two failures to printed precision:

| Observable | NightlyBuildX avg metric | Existing epsilon |
|---|---:|---:|
| rms_x | 1.30617242785e-5 m | 1e-5 m |
| emit_y | 1.31842859182e-5 m | 1e-5 m |

NightlyBuildX `avg` means `sqrt(sum((new-reference)^2))/N`, an absolute quantity in the observable's units, rather than a relative percentage or conventional RMS. Source: `scripts/OpalRegressionTests/stattest.py`, GitHub main blob `48d713a50129dbb5297568dddeca03a34bdc646d` (https://github.com/OPALX-project/NightlyBuildX/blob/main/scripts/OpalRegressionTests/stattest.py). The old architecture traces are excerpted in `ci-fodo-excerpts.txt`.

Final unchanged-run/reference values:

- rms_x: 0.013606 m versus 0.014366 m.
- emit_y: 0.002867 m versus 0.003505 m.
- Number of particles: 1000 versus 999. The reference loses one particle after row 1708; current tracking retains all particles.
- Energy remains 1000 MeV; maximum new/reference energy difference is 7.6e-11 MeV.
- The historical reference transverse momentum remains frozen at (-0.0067704,+0.0063600) mc through all 60 m. The current reference momentum evolves from the first magnet, as expected for an off-axis reference.

## Concrete historical behavior change

OPALX commit `fc719154c934ba1c4da5df323ce2e7ed177f3cb3` (September 4, after reference generation) intentionally:

1. Expanded `MultipoleT::getFieldExtent()` from body-only [0,L] to [-6*LFRINGE,L+6*RFRINGE]. For this fixture, L=0.5 m and fringe lengths=0.05 m, so support is now [-0.3,0.8] m.
2. Added `MultipoleT::applyToReferenceParticle()`, applying the same field to the reference instead of leaving it un-kicked.
3. Added spatial field-support/aperture handling for this element.

These changes already exist in origin/master. PR #637 does not change MultipoleT source; its new RF/probe paths are inactive for this no-RF FODO input. Source history and the frozen historical reference provide strong evidence that this is an obsolete baseline for changed field/reference behavior, rather than accelerator-backend precision or RF event handling.

The body-clipped negative control does not reproduce the old reference: rms_x metric becomes 7.77e-5 m and emit_y 1.83e-4 m, both substantially worse. It should not be used to force a pass. It also does not perfectly reconstruct historical selection, which operated at bunch/candidate level rather than clipping each particle independently.

## Proposed minimal resolution and remaining validation

Keep input physics, particle data and epsilon=1e-5 unchanged. Before updating references, validate current tanh-fringe field support and reference/particle field parity with independent analytic/native checks, and preferably verify a named current-master baseline executable produces the same trajectory. If those pass, regenerate only this fixture's references through the regression repository's standard `bin/makeReference.sh`, recording the source and executable hashes and this intentional pre-existing behavior change.

No source, reference, or tolerance edits have been made. A named origin/master executable has not yet been built/run, and no reference regeneration is authorized or performed at this stage. Source-history attribution is strong evidence but not a complete historical binary bisection.

Artifacts: `comparison-summary.csv`, `full-row-comparison.csv`, `body-clipped-comparison-summary.csv`, `analysis.log`, `fodo-comparison.png/.pdf`, reproducible manual `analyse_fodo.py`, per-case inputs and logs.

## Authorized validation and reference draft (completed)

The root authorized a focused native C++ regression and a temporary standard-generated reference draft, while keeping the maintained regression checkout unchanged.

`unit_tests/AbsBeamline/TestMultipoleTStraight.cpp` now adds `AnalyticFringeFieldsAgreeForParticlesAndReferenceOutsideTheBody`. It uses only in-memory C++ data: L=0.5 m, lambda=0.05 m, gradient=1.8046482322261885 T/m, x=0.01 m, y=0, and z={-0.2,0,0.25,0.5,0.7} m. The independent analytic result is Bx=Bz=0 and By=g*x*[tanh(z/lambda)-tanh((z-L)/lambda)]/2. It verifies absolute normalization of production particle-view kernel fields, scalar fields and reference fields to 1e-14 T, with explicit host/device transfers. Two outside points (-0.31,0.81 m) verify excluded reference support. Existing assertions/tolerances are unchanged; no Python, data file or OPALX launch is used by this native test.

Fresh one-rank OpenMP validation with OMP_NUM_THREADS=2 passes 25/25 cases across TestMultipoleT (7), TestMultipoleTBase (3), and TestMultipoleTStraight (15). Existing independent coverage includes transverse polynomial multipole fields, exact tanh derivative coefficients and values, finite-difference Maxwell divergence/curl checks, and asymmetric six-fringe support. The old reference API smoke cases only checked return flags; the added case supplies the missing nonzero-field parity assertions.

All MultipoleT implementation/configuration/placement files are identical between candidate 23f04f6 and origin/master 8c1a86236. In ParallelTracker, FODO's LINE has ringPeriod=0, no RF gaps and no probes, so new cyclotron-specific eligibility, ordering and transport branches are inactive. The generic reference `advanceInBeamline` implementation is unchanged. A separately built named-master baseline comparison remains with the root.

The fresh OPALX executable was relinked after the native build. SHA256 is `e4e8b35004a178b0f8fc2d3cd3bd644874d1043ffcce537e64275f37f9a0a9cc`, and its generated output correctly reports source revision `23f04f6c8e57f497e6f1a722038f9e1cef010803`.

`draft-standard-generated/reference/` was generated using the unmodified regression repository `bin/makeReference.sh --ranks 1`, in a task-only draft directory, OMP_NUM_THREADS=1. Input, particle data and `.rt` checksums are unchanged before/after generation. All three generated MD5 checks pass. The draft's 2001 rows pass all 7 existing epsilon=1e-5 comparisons against the held-out unchanged-input run (see `draft-held-out-comparison.csv`); this repeat comparison supports reproducibility but is not independent physics proof. Independent physics evidence comes from the analytic native test and documented intended field-support change.

The maintained regression checkout remains clean, and no references or tolerances there have been changed. The only tracked OPALX change is the added native test. Baseline comparison and cross-repository publication remain root-owned decisions.

## Clean named-master baseline (completed)

The exact clean origin/master `8c1a86236` executable (SHA256 `de8fd16697d9dcaeae8af96fdeac25c936e1a9ff2ddf7729806c2b1ea19d9d17`) completed the unchanged fixture on one MPI rank, OMP_NUM_THREADS=1, exit 0. The 2001 rows reproduce both historical-reference failures: rms_x avg=1.30617242785e-5 m and emit_y avg=1.31842859182e-5 m. It retains all 1000 particles. Against the fresh candidate draft, the largest absolute discrepancies among the seven comparison observables are 3.37e-14 m for emittances and 1.02e-12 MeV for energy. See `master-baseline-comparison.csv` and `baseline-master-8c1a862/` for exact input/executable hashes and logs. This independently confirms the FODO mismatch already exists on pre-PR master; it is not introduced by the new probe/RF work.

## Exact committeda9 reference draft

Following parent commit a9d38caa4f88433a5de1508b3d5c7d01bdfea95a, a fresh disconnected rebuild embeds the exact committed revision. Standard generation from exact regression737547e6 is preserved jointly with correctedScaling under `../reference-drafts-a9d38caa/`. Runtime revision, binarySHA68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590, preserved input/data/tolerance checksums,2001rows/all1000particles and7/7 unchanged comparisons against independent cleanmaster8c1a862 are verified. Combined generated-only patch and provenance are ready for parent review; maintained regression checkout remains unchanged and actualGPUvalidation is pending.
