# DBA ring benchmark discovery

Goal: locate PR #553's full DBA lattice and related KV charge-dependent tune model.

PR #553 inspected via gh; merged 2026-10-02. No production files modified.

Located under /Users/adelmann/git/old-opal/opalx/sandbox:
- Regression-Tests/dba-ring-cof-1/cof.in: complete six-cell electron lattice, K1=+2.84.
- Regression-Tests/dba-ring-cof-1/analysis/generate_analytic.py: independent exact hard-edge optics.
- dba-cof-1/: separately packaged self-contained version, reference data and runner.
- Regression-Tests/tune-shift-ring/config.json: 2.5 MeV proton KV model, geometric rms emittances 3e-6 m rad.
- Regression-Tests/tune-shift-ring/analysis/kv_model.py: analytic KV forces, numerical periodic envelope matching and phase integration.
- Regression-Tests/tune-shift-ring/analysis/run_model.py: current scan and tune targets.
- Regression-Tests/tune-shift-ring/bare-cof.in: complete proton deck, K1=-2.84.
- Regression-Tests/tune-shift-ring/analysis/prepare_kv.py and kv_distribution.py: matched source generation.
- Regression-Tests/tune-shift-ring/matched-kv.json and kv-section.txt: saved matched source metadata and transverse section.

The two models share geometry/normalized focusing but use different particles/energies. Full positive KV zero-current tunes 0.770107569 / 1.689536397 correspond to PR principal eigenphases 0.229892431 / 0.310463603.

Archived analytic results live under output/regression-cleanup-20260909/removed/tune-shift-ring/results in the older checkout; the sandbox tune-shift-ring/results directory is empty.

Validation: read inputs, code, documentation, PR body and directory inventories. No simulations or tests run; discovery only. Historical tracking limitations are not a statement of current-source behavior. Next step, if requested: reproduce the analytic current/charge scan and validate against the current OPALX tracker.
