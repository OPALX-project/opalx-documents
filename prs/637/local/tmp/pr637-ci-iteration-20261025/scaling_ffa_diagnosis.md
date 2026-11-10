# ScalingFFABasicPlacements regression diagnosis

Read-only investigation; no fixture/reference or manual edits.

## Provenance and direct evidence

- OPALX current source: `23f04f6c8e57f497e6f1a722038f9e1cef010803`.
- Local regression repo: clean `a8bd50c40d66ecb2ce4a75d5c15b6ecb86ae5615`
  (2026-10-23 merge of PR #70).
- Regression commit `e902bfd6bd6aa5ce39111edb1a0f637b8252b298`,
  2026-10-22 18:23:47 +0100, introduced the `.rt` and reference while changing
  `MAXSTEPS=10` to `MAXSTEPS=1000`. It also changed the line composition/order,
  removed enabled field dumps and renamed SOLine to FFALine.
- Committed reference `.out` was produced earlier that day at 17:33:56 using
  OPALX `6c65ec878f1b953aa7b71e548155db82c29524cc`. It explicitly says
  `Max integration steps = 10` and logs only steps 0..9 to t=1 ns and s=0.091239 m.
  Its OrbitThreader map contains one section, versus nine sections in current CI.
- Committed reference `.stat` has one numeric row at t=1 ns, checksum matches.
- Current committed input uses DT=1e-10 s, MAXSTEPS=1000, STATDUMPFREQ=100,
  ten identical deterministic protons, TYPE=NONE, ZSTOP=60 m. Its stale comment
  says every 10 steps despite configured cadence 100.
- `/tmp/pr637-cscs-openmp-old.trace` lines 30962..32130: successful actual launch
  of OPALX a27c1b392a178a67e4f0df8c10c7fe48acb111f3; steps 0..999, t=100 ns,
  s=9.124 m, no simulation error. Comparison lines 40876..40892 reject all
  mean_x/mean_y/mean_s only because reference length1 versus simulation length10.
- Cadence code at current ParallelTracker.cpp:965..968 and :1075..1079
  writes at completed steps100,200,...1000; no duplicate final row. The source
  from original reference revision6c65ec878 uses the same cadence and final-dump
  logic. A ten-step run at cadence100 writes only its final row, explaining
  the exact mismatch without any STATDUMPFREQ behavioral change.

## Conclusion and proposed repair

This is an internally inconsistent input/reference committed before the PROBE
change, not an accelerator-specific failure. The reference was generated with
shortened/earlier input and committed alongside a longer input.

Keep the intended 1000-step fixture, deterministic distribution, physical
settings and accepted 1e-4 m thresholds. Generate fresh references in a clean
temporary copy using standard bin/makeReference.sh and a named, hashed current
executable. First retain and inspect all ten timestamps, particle counts, energy
and reference trajectory; compare a separate ten-step diagnostic against the
old single-row reference to distinguish input duration from changed numerics.
Do not hand-edit values, discard nine rows, change avg to last merely to pass,
relax tolerances or reduce MAXSTEPS to10 (which would lose intended downstream
magnet coverage). Source changes are not indicated by the evidence.

The three current mean_* checks use bunch coordinates relative to the moving
reference. The initial 1 ns snapshot is near zero, but the intended 1000-step
run has mean_x=1.219384512687868 m and mean_s=-0.08012515205253731 m at 100 ns.
This large particle/reference separation is a material limitation. The draft
reference must not be accepted as independent physics validation. The isolated
named original/master comparison below now proves that the separation predates
PR637, while root is separately investigating/fixing FFA field superposition.

## File hashes (SHA-256)

- input:4c6ba2c4bbfb44f6d556ef334582771e6b36d692c9346402db0cd92ea113a59a
- particle file:3b1201ebe57a5d38a46cc6ccabe95beff5904a6e8b358fbdae7d1334ec4f1d52
- old reference.stat:39f74bd61fb66d8c1a75788ea5227204452bcfe8d6300ab171ca431da684e245
- existing local build_openmp/src/opalx:26ae4cdec13aa24bcacea47942ad8a0a86b3cddb9a65f8dc37f3847ba76f04a8
  (not yet used for this investigation; runtime provenance requires checking).

## Follow-up evidence and concrete draft (not yet accepted)

- Current remote regression master is `737547e6ae38cf3001d6bc45cf38dd1a47d78402`
  (2026-10-23 21:50:46 +0200). Fetched refs only; local checkout stays unchanged.
  ScalingFFABasicPlacements subtree Git tree is exactly
  `7df021d2ef6a0d1a10ebeded5f6494fa27627328` at both local a8bd50c4 and remote
  737547e6. CI trace does not print the regression checkout SHA. Its fresh
  master clone has 451 files and includes IdealRFCavity, consistent with
  current737547e6 (451 tracked files; older local a8bd50c4 has437). This is
  strong corroboration, not an invented exact recorded CI SHA.
- Fresh experiment `/tmp/pr637-scalingffa-20261025` uses a standalone executable
  snapshot SHA25626ae4cdec13aa24bcacea47942ad8a0a86b3cddb9a65f8dc37f3847ba76f04a8.
  Its embedded revision reports61c90499 because it was built before review-fix
  commits; do not call it a freshly compiled23f04f6 executable.
- Standard bin/makeReference.sh from remote737547e6 was used, unchanged, in a
  clean temporary full-input directory; generator SHA256
  82278a4d2ef6edc4541f3435866d3c2b32ed6277d5305d4219290f87e518e2ce.
  Both short and full OPALX launches completed (End of input, exit0).
- Short-run10-step diagnostic preserves every current input setting except its
  diagnostic duration. At the old1ns time, reference coordinates match within
  4.2e-17m, momenta1.1e-17 p/(mc), energy1.4e-14MeV. This independently
  reproduces the stale reference and directly establishes the duration mismatch.
- Full draft has exactly10 rows at10,20,...100ns; count10 and charge preserved.
  Particle energy46.72604383544756MeV follows normalized momentum0.3195 and
  proton rest energy938.27208816MeV to1.1e-12MeV; energy range8.2e-13MeV.
  This verifies magnetic energy preservation, not trajectory correctness.
- Seven recorded magnet entry poses match the independent circular formula
  (x,y,z)=[R0*(cos(ELEMEDGE/R0)-1),0,R0*sin(ELEMEDGE/R0)], including both
  negative-R0 magnets, within2.1e-10m (ten-significant-digit output precision).
  Existing native ScalingFFAMagnetTest.PlacementTest also passes on one rank.
- `scaling-ffa/proposed-reference.patch` is a concrete six-file generated-only
  proposal: .stat/.stat.md5, .out/.out.md5 and timing.dat/.md5. It retains the
  full1000-step input, all fields/distribution and existing .rt avg1e-4m checks.
  Every generated MD5 was checked. No fixture/reference checkout files changed.
- `scaling-ffa/analysis.json`, CSVs, placement JSON, logs, executable hashes and
  reproducible analysis script preserve the evidence. The large late particle/
  reference separation is explicitly reported, not silently accepted.

## Exact named-master comparison completed

- Newly attached managed worktree:
  `/Users/adelmann/.codex/worktrees/pr637-master-baseline/opalx`.
  Exact clean source revision8c1a862369fb05034bb27aa1111d63a7b1e16c02.
- Configured a separate build_openmp using LLVM/Clang21.1.8, gfortran, static
  Release and OPENMP, test/unit/example targetsOFF; six compile workers.
  Both configure and executable-target build exited0. Fully/updating
  disconnected FetchContent source overrides point to existing main dependency
  sources; all Git sources stayed clean at the same commits and HDF5/LAPACK
  full source-tree SHA256 values stayed unchanged before/after.
- Preserved baseline executable
  `master-baseline/opalx-master-8c1a862`, SHA256
  de8fd16697d9dcaeae8af96fdeac25c936e1a9ff2ddf7729806c2b1ea19d9d17.
  Runtime header independently reports the exact baseline source revision.
  Configure/build commands, cache, logs, dependency manifest, orchestration and
  comparison scripts are saved in master-baseline/.
- Regenerated current candidate draft with newly relinked23f04f6 executable
  e4e8b35004a178b0f8fc2d3cd3bd644874d1043ffcce537e64275f37f9a0a9cc.
  Its header verifies23f04f6. Previous26ae snapshot evidence is retained.
  `scaling-ffa/current-candidate/proposed-reference.patch` passes git apply--check;
  generated MD5s match. Its47-column numeric results equal the earlier snapshot.
- Most decisively, named master8c1a862 and candidate23f04f6 produce IDENTICAL
  DataFrames across all47 numeric columns and all10 full-run rows (including
  matching nonfinite values). Both have mean_x=1.219384512687868m and
  mean_s=-0.08012515205253731m at100ns. The deviation definitively predatesPR637.
  Existing3 avg1e-4m comparisons would also pass the stricter maximum absolute
  difference check against this matching full-duration baseline.
- Saved proof: master-baseline/scaling-comparison.json,
  scaling-master-candidate-differences.csv, scaling-baseline.stat andscaling-run.log.
  This proves unchanged behavior, not correct FFA transport. Keep the generated
  full-run draft provisional while root handles the independently identified
  FFA superposition issue. Do not publish a reference that silently accepts the
  large particle/reference separation.
- Baseline executable path/hash sent to root and FODO agentrf_review_fix for its
  independent FODO comparison; do not archive the managed worktree until all
  baseline consumers finish. No source/dependency/manual edits by this agent,
  no commits and no publication.

Next: root/FFA agent's field-superposition fix and fresh full-duration output;
regenerate a physically justified reference only after that validation.

