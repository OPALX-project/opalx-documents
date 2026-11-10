# Gaussian tail-check fix

The fixed Gaussian maximum of 5.5 sigma was not a guaranteed property of an untruncated normal sample. A legitimate sample maximum of 5.5717775960503042 repeatedly failed it. The revised native test uses statistically derived tail checks and preserves the sampler, seed, particle count, other test cases and existing RMS checks. Only unit_tests/Distribution/TestGaussian.cpp changed in this task; the 37 earlier source files remain unchanged. Nothing is staged, committed or pushed.

## Statistical contract

With fixMeanR=false and unit widths, rejecting only |z|>3 leaves five untruncated unit-normal coordinates. For each, count K values beyond |Z|>3. Under that null model, p=erfc(3/sqrt(2)), mu=Np and v=Np(1-p). The test verifies the actual MPI-global particle count equals the original request before using N.

Set the new tail-check family budget alpha=1e-6 and m=5. Split it equally between two check families. With L=log(4m/alpha), inverted two-sided Bernstein gives count radius L/3+sqrt(2vL+L²/9). Union-bounding across coordinates spends at most alpha/2. The source of the underlying bound and its quadratic inversion is [MIT's Bernstein lecture notes](https://ocw.mit.edu/courses/18-465-topics-in-statistics-statistical-learning-theory-spring-2007/797e43db787d6e1666d75693e76a30dc_l6.pdf).

For a standard normal, its moment-generating function and Markov's inequality give P(|Z|>u)<=2exp(-u²/2). Union-bounding over mN values spends the other alpha/2 at u=sqrt(2(L+log N)). This retains an extreme-outlier guard without asserting that an unbounded distribution has a fixed maximum. No independence across coordinates or between these two check families is needed for the union bounds; binomial counts assume independent normal samples within each coordinate.

For N=100000, these formulas accept 170–370 exceedances per coordinate around the expected 269.98, and a maximum of 7.5265089 sigma. The old 5.5718 sigma sample is valid under these checks. Complete truncation at 3 sigma produces zero exceedances and fails; a 40 sigma outlier fails the maximum guard. The audit computes a conservative numerical family probability bound of 4.22e-8, below the analytic 1e-6 budget. These are analytical counterfactual/power checks, not native sampler mutations.

The source explicitly scopes this budget to the new tail checks. The pre-existing four-standard-error RMS checks retain their separate probability behavior and unchanged thresholds. All six components must be finite, and z retains its strict configured cutoff. Pseudorandom output is modeled as IID Gaussian; the test does not certify the RNG or every possible distribution defect.

## Validation

Local Release/OpenMP: all eight Gaussian cases pass with four Kokkos/OpenMP threads, then the full parallel suite passes 137/137 targets. LLVM21 formatting, git diff --check and independent mathematical/MPI/source review pass. The statistical audit verifies the sampling setup and RMS block are unchanged.

Linux Debug/OpenMP job 355097 completed 0:0 in 4m44. Four one-/two-rank by one-/four-thread Gaussian variants pass, totaling 48 native case executions with zero skips. All seven related distribution targets pass, and the full parallel suite passes 137/137 targets with zero failures. There were no failed native attempts or retry-until-pass runs in this task.

All 1,073 current source hashes match the expected snapshot. The only new source change is TestGaussian.cpp; the 37 prior files are unchanged. The test object and executable were rebuilt from the frozen source (SHA6569cabdd647bd40dcbbeb280819aca92ea724b5f06b30972975b5bf830fa4ce), and its binary differs from the failing baseline. The production library and both earlier frozen validation archives remain byte-identical. All task jobs are terminal.

Reproduce the independent numerical audit using statistical-audit.py and the user's ~/.venv-h6 environment. It uses installed SciPy only for offline verification; the native test uses C++/MPI and has no Python, SciPy or external-data dependency. Exact calculations and derivation are statistical-audit.json/.md. Source hashes and diff: intended-file.json, prior-files.json and fix.patch. Local raw results: local-gaussian.log/xml and local-full-suite.log/xml.

## Evidence and limits

Raw Linux archive: linux/validation-evidence.tgz, SHA256 f21f064d3def3d9429038c4321512aacd6ef5c6cd7c3dc7f4baf3eaded171063. Raw JUnit, four Gaussian logs, source manifests, binary proof and accounting are under linux/remote-evidence. The canonical replay audit is linux/audit_linux.py; independent root verification is ROOT_VERIFICATION.json. Final structured results are RESULTS.json.

The Linux build uses GCC14.3/OpenMPI5/CMake4.4 with Debug/OpenMP on Merlin6; it is not the exact Ubuntu GitHub image. Default one-rank ORB cases can internally skip in the full suite; their explicit multi-rank coverage was verified in the preserved prior ownership task. No CUDA runtime result is claimed here. The new tail-check budget excludes unchanged RMS checks and does not certify every distribution defect or the pseudorandom generator.

No production code, CMake settings, sample count or seed changed. All existing pending work is preserved. No files are staged, committed or pushed; the next step is user review.
