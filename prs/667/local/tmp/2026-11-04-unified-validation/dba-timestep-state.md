# DBA ZeroSC timestep study — completed, 2026-11-04

Goal: compare tunes and timestep changes using ONLY ~/git/opalx/build-omp/src/opalx. No space-charge runs.

Frozen executable SHA-256: 4fd718db8dea11088409158506cd61761eb35f7a0e6a15638fba235c433ba0eb.
Branch codex/fft2d5-explicit-original-model, HEAD ccfdc1055b2721d2308761d45a3030b29ef70e11 plus eight previously restored FFT2D5 source files. Source patch SHA 885e59c8a4fe5c3751b0077db53051f7467667af1a4d0fee77b799b68ef6764a verified unchanged. No code changes/rebuilds in this task.

Results:
- Largest tested step meeting requested full-record ~1% criterion: 4 ps. Conservative choice with additional half-record stability: 3 ps.
- Reference 2 ps. Analytic Qx=.7701075691328534, Qy=1.689536397020211.
- 4 ps median Qx=.770050, Qy=1.689527. Radial 95th-percentile paired change vs2ps=.795840%; analytic error=.761975%. At8ps these are1.382514% and1.366811%, so reject8ps.
- 4ps radial first8turn/last8turn 95th-percentile difference2.083364%; 3ps=.892328%. 2ps=1.272777%, illustrating weak-signal finite-record noise; do not claim universal1% individual-particle accuracy.
- Final scan: 2,3,4,8,16,31,62,125,250,500,600,700,800,900,915ps; ALL final results OMP1/MPI1. 69particles:64matchedKV + central + four10/50um probes. Acceptance uses64KV only.16turns.
- Native checkpoint initialization selects ordinary fixed Boris/PIC path matching FFT2D5. FreshZeroSC boundary subdivision is intentionally disabled, so nominal fresh-run DT is not comparable to this fixed-step study. FSNONE, no SC solver.
- 1000ps rejected before tracking by unchanged ten-step/0.2m-quadrupole guard (~916ps cap). Coarse ring trajectories are not converged.
- Full-ring source-position check:96particles over48longitudinal strata, antipodal matchedKV-shell pairs,8turns,4ps,OMP1. All96records valid. MedianQx=.769779190844,Qy=1.689529961732;95th-percentile analytic errors .611151% and .006531%. Radial half-record diagnostic2.143%; max relative momentum-magnitude change3.2e-8. Not a100kSCproduction test.
- Timings: section4ps238.9s,3ps308.0s,2ps459.1s; fullring4ps482.3s. Concurrent diagnostic jobs; not isolated performance benchmarks.

Artifacts:
- Curated /Users/adelmann/git/opalx-documents/examples/2026/2d5-1/dba-zerosc-timesteps-2026-11-04 (14cataloged assets): full/fine publication PNG/PDF, summary and particle CSVs, selection/buildJSON, readme, replay/analysis/input ZIP. No opalx/docs changes.
- Raw /Users/adelmann/git/dba-lattice/comparison-20261104/unified-current/dba-timesteps and dba-fullring-zerosc; scripts in parent. Use audited-* CSVs and selection.json. Old timestep-comparison.csv/selected-timestep.json were moved into preliminary-phase-estimator/; they are NOT final results.
- Prior coarseOMP4 attempts preserved under dba-timesteps/omp4-comparison. Interrupted31psOMP4 and384particle fullring attempts retained under interrupted dirs with reasons. Only this task's identified processes were stopped. CoarseOMP1/4 trajectories diverge due hard-edge sensitivity; no fine-thread reproducibility claim.

Validation:
- Exact linear-lattice synthetic trajectories recover both analytic tunes within2e-8 (phase much better).
- All final particle IDs/counts, finite coordinates/momenta, time coverage and absence of boundary controller audited; own-station crossings avoid common-time bias and integer-tune aliasing.
- Portable ZIP analysis replayed existing2/4ps snapshots (no new OPALX runs): maximum frequency difference1.84e-12; phase3.3e-16; half-record percent difference2.25e-9. Initial1e-12 frequency assertion was overspecified and failed marginally; accepted QA limits1e-10 tune and1e-8 percentagepoints are far below1% physics criterion. No physics tolerance changed.
- ZIP integrity/Python syntax checked, publication plot inspected, all14manifest hashes verified, manifest diff whitespace clean. Repository-wide document validator reports ONLY pre-existing uncataloged movies/2026-10-30-mue4_analytical-trails.mp4; untouched.

No DBA SC runs started. No commit, push or PR update. All study simulations finished. Await next user instruction.
