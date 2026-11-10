# Full local regression validation

**PASS: 401/401 comparisons across 39/39 enabled simulations.**

- Exact OPALX source/runtime revision: `a9d38caa4f88433a5de1508b3d5c7d01bdfea95a`.
- Executable SHA256: `68fad17728ccb7ed11f51e906bd739d6c59fe1ab646749ef9a54737292242590`.
- Exact regression base: `737547e6ae38cf3001d6bc45cf38dd1a47d78402`.
- Applied only reviewed 12-file generated-reference patch
  `05b649a08c40f351a048f9b4b051e832a2288032ab19a48d40a35cea9865ea4e` for FODO and ScalingFFA.
- Standard unmodified NightlyBuildX driver revision:
  `5539fa31b56d4952d923e6641557d6683c68725a`.
- Local static Release/OpenMP, LLVM21.1.8; one MPI rank and one OpenMP thread
  per simulation. Fresh isolated output tree; simulations ran sequentially.
- Runner exit0; summary401/401. Every simulation's actual log contains the
  expected a9d38caa revision and completed End-of-input marker. Runtime
  172.8s. No launch failures, tracebacks or new
  numerical mismatches. Full comparisons.csv has401 independently parsed rows.
- All 451 original source files,
  including every proposed/unmodified reference, match their expected hashes
  after the run. All 212
  non-reference files (inputs/data/.local/.rt/eps) and the executable are
  unchanged. Maintained regression checkout remains clean.
- No reference regeneration, source edits, website publication, upload, commit
  or external notification was performed by this run. The standard driver was
  called directly without publish/web flags and REGTEST_WWW was unset.

## Evidence

- manifest.json: exact versions/hashes/command/counters/timestamps.
- runner.log: unabridged standard runner and OPALX output.
- comparisons.csv and case-summary.csv: all401 comparison metrics and39 case totals.
- simulation-completions.json: exact runtime revision/completion per simulation.
- before/after SHA256 manifests: complete fixture/reference and input preservation.
- run_full_local_regression.py: reproducible isolated orchestration; unit tests
  do not depend on this script or these external integration fixtures.

This validates the full local regression comparison scope at fixed resolution.
It is not a GPU/CSCS run or a general physics/convergence claim. GPU CI remains
with the parent task. Outputs remain at `/tmp/pr637-full-regression-a9d38caa-20261025`.
