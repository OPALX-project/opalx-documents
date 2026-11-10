# Quick analysis of the original failure near 584 MeV

Analyzed the original 16³ mesh / 32,768-particle run, not the later 8³ case. No simulation, build, source change or new unit test was performed. Reproduce the saved numerical accounting with `~/.venv-h6/bin/python quick_analysis.py`.

## What failed

The old run stopped after the reference's RF3 event at 584.1575 MeV, before its 590 MeV target. Its exception was `SINGLEGAP particle left field support or received an unphysical kick.` The old device transport returned a single boolean for unsupported magnetic trial midpoints and rejected RF impulses. Five gaps and the fixed positive timestep exclude the negative-timestep and gap-count structural guards.

Magnetic support was radial 1.9–4.7 m, vertical ±50 mm, with half-open angular sectors. A nonfinite trial position can also fail those support comparisons. RF rejection includes nonfinite/nonforward momentum or an unphysical outgoing longitudinal momentum. Merely missing a gap's radial profile support skips that crossing; it does not itself trigger this fatal error.

The largest saved vertical extent was 44.36 mm at mean energy 581.88 MeV, approaching the 50 mm map limit. Vertical halo escape is therefore a plausible cause. It is not proven: saved moments do not identify the failing particle, and an RF rejection, angular-support issue or nonfinite state remains possible. The final HDF5 file has metadata only, with no particle checkpoints. Exact retrospective classification is impossible from the saved outputs. This was not the later terminal-EKINSTOP endpoint problem.

## Was shutdown graceful?

No, in the orderly-cleanup sense. The program reported an OpalException and deliberately called MPI_Abort(-100); the launcher returned 156. There is no evidence here of a segmentation fault. Current Main.cpp:488–501 still logs the exception and aborts, bypassing normal field cleanup and ippl::finalize at lines572–579.

Current code does preserve accepted probe hits before a collective SINGLEGAP/reference-trial error. Existing one-/two-rank deliberate RF-failure cases saved exactly one accepted hit and returned156 promptly. This is output preservation, not normal finalization or a restart checkpoint. The particle kernel is not whole-bunch transactional: successful particles may have committed an attempted step when another particle fails. The failed live bunch must not be labelled a consistent checkpoint. Other current GPU fatal-error logs show secondary cudaErrorCudartUnloading teardown errors.

## Concrete diagnostic defect

ParallelTracker.cpp:1386–1393 emits first-failed-particle cause/ID/state through gmsg, but Main.cpp:184 constructs that logger with its default rank-zero-only output. IPPL Inform's constructor defaults to node0 and outputMessage suppresses other ranks. Consequently a failure confined to a nonzero rank can lose its detailed cause/ID/state even though the generic error is collective. This did not cause the original one-rank run's missing details: that old binary lacked them entirely.

## Appropriate follow-up

Use the original 16³ / 32,768-particle input, charge, timestep and 590 MeV target. Capture the failing particle and the exact rejected support/kick condition, with all-rank diagnostics. Since no late particle checkpoint exists, an exact replay needs the original trajectory from the start. Treat an orderly collective failure exit and last-accepted-state persistence as explicit requirements; retaining MPI_Abort for unsafe/uncoordinated failures may still be necessary. No support expansion, silent particle dropping or numerical-tolerance change is justified by this audit.
