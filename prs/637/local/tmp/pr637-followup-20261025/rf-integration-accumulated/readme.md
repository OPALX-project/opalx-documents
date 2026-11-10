# Manual RF integration — accumulated-frame endpoint resolution

Separate manual OPALX runs, not CTest/native unit tests. Inputs retain EKINSTOP=0.073 GeV,
TYPE=NONE, one/two identical physical protons and one/two MPI ranks. Native unit tests
remain self-contained C++ and do not consume these files or scripts.

These cases repeat the first candidate's four normal cases and the two verified
probe-before-unphysical-RF cases, using fresh output directories and a newly rebuilt binary.
The terminal classification allowance now uses 64*N*epsilon*L, where N counts accepted
reference-frame updates including the terminal step. At ~1468 steps, it is about
3.95e-11 m, conservatively exceeding the observed ~1.5e-13 m roundoff-short plane residual.
This is accumulated arithmetic classification uncertainty, not a discretization or ODE
accuracy bound; physically later particles inside this unresolved interval receive the
full terminal impulse by convention. Ordinary crossings remain strict.

The original candidate's logs/results remain under ../rf-integration.
Do not execute until root confirms the updated opalx_exe is ready:
`./run-manual.sh /absolute/path/to/updated/opalx --execute`, then `./analyse-manual.sh`.
