# Linux Gaussian statistical-check validation

The Gaussian test-only fix passes the complete Linux Debug/OpenMP unit suite. Job **355097 completed 0:0**, with no failed attempts or retry-until-pass loops.

| Check | Result |
| --- | --- |
| Gaussian, one rank / one thread | 8/8 native cases pass |
| Gaussian, one rank / four threads | 8/8 native cases pass |
| Gaussian, two ranks / one thread | 16/16 native case executions pass |
| Gaussian, two ranks / four threads | 16/16 native case executions pass |
| Related distribution targets | 7/7 pass |
| Full unit suite | 137/137 targets pass |

The Gaussian variants have zero skips and explicitly set both KOKKOS_NUM_THREADS and OMP_NUM_THREADS. They use the unchanged default seed and particle count. Full-suite target success does not imply every rank-dependent GTest case runs in a single-rank invocation; the existing ORB cases were explicitly covered in the prior frozen ownership task.

Only unit_tests/Distribution/TestGaussian.cpp changed, to approved SHA256 **6569cabdd647bd40dcbbeb280819aca92ea724b5f06b30972975b5bf830fa4ce**. All 1,073 current source hashes verify against the checkout. The 37 earlier pending files remain unchanged. Object/link timestamps and the new ELF fingerprint prove the changed test was rebuilt. The production library remains byte-identical. Both previous frozen validation archives are unchanged. The old Gaussian source, binary and previous failing full-suite output were preserved before staging.

Toolchain: Linux on merlin-g-100, GCC 14.3, OpenMPI 5.0.10, CMake 4.4 and Kokkos 5.2.2 in CPU Debug/OpenMP. This is not an exact reproduction of the GitHub Ubuntu image or a CUDA runtime check. Two pre-existing dangling-else compiler warnings in untouched collapsed-axis assertions remain; the new statistical checks compile successfully.

Raw bundle: validation-evidence.tgz, SHA256 **f21f064d3def3d9429038c4321512aacd6ef5c6cd7c3dc7f4baf3eaded171063**. It contains stage/source expectations, before/failure records, four variant logs, group/full JUnit, binary proof and terminal Slurm accounting. The old ELF is preserved remotely rather than included in the small archive; its hash is recorded. Canonical results are in audit.json and raw files in remote-evidence/.

Reproduce the local evidence audit from /Users/adelmann/git/opalx-master:

```sh
/Users/adelmann/.venv-h6/bin/python tmp/gaussian-statistical-check-20261109/linux/audit_linux.py --evidence tmp/gaussian-statistical-check-20261109/linux/remote-evidence --checkout /Users/adelmann/git/opalx-master --output /tmp/gaussian-linux-audit.json
```

All task jobs are terminal. No staging in Git, commit, push, production changes, seed changes or further test runs were performed by this worker.
