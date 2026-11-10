# A100 audit-fix validation — complete

The final uncommitted six-file audit fixes were validated in isolated source snapshot `3320cf6fc490a8be7dc2a33468b35cd99804cf179fd13d07f4d62d00e4bc2ae3`, based on published PR #637 head `b1551b9c3`. All 1,072 snapshot files were verified before and after native tests; all six intended file hashes still match the local working tree. No commit or push was made.

## Terminal jobs

- **355081: COMPLETED, exit 0:0, 32m21s.** Fresh shared Release CUDA build passed. All six native CTest targets passed in 29 seconds: sector, RF-event and probe tests on one and two MPI ranks. Logs contain 111 RUN and 111 OK case executions, with zero skipped or disabled tests. The new concurrent failure-capture case and extended sector boundary/nonfinite case each ran and passed on all three processes.
- **355082: FAILED, exit 1, 15s — launcher setup only.** The job-only Python metadata wrapper called nonexistent CUDA Runtime API symbol `cudaDeviceGetUuid`. Its traceback is preserved. No OPALX banner, HDF5 output or GPU mapping record exists; zero simulations started. The native build and tests remained valid. A separate evidence-download command initially used unsupported scp flag `-x`; retrieval was corrected to `-o ForwardX11=no`. That affected download only.
- **355083: COMPLETED, exit 0:0, 35s.** The reviewed correction compiled a small C++ metadata child probe against the installed CUDA headers, using `cudaGetDeviceProperties(...).uuid`. The probe and OPALX resolve to the same shared libcudart realpath. All four actual-tracker checks passed: valid 256-particle NONE-solver runs on one/two ranks, and expected particle field-support failures on one/two ranks. Failure cases exited 156 promptly with captured ID, cause and laboratory state, without a timeout or MPI hang. Existing fatal-abort semantics were retained.

## Output and device evidence

The valid GPU runs retain 256 particles, unique IDs, finite states and exact TIME, step, mass and zero charge relative to the CPU fixture. Maximum GPU–CPU position difference is `6.866740249328318e-15 m`; momentum difference is `3.219646771412954e-15 p/(mc)`. Reference position/momentum differences are at most `2.220446049250313e-16 m` and `1.6653345369377348e-16 p/(mc)`. Existing absolute `1e-10` bounds were unchanged. Physical state sets are matched using well-separated unique x coordinates because FROMFILE sample-to-ID association can differ by rank count; this does not prove identical sample-to-ID associations across ranks.

The actual-tracker launcher confirmed one visible device per rank using the CUDA Runtime and distinct UUIDs in the two-rank run:

- Rank 0: `GPU-dbbd7375-8fc1-093d-f86b-ae1f64b87448`.
- Rank 1: `GPU-ddaf526c-0266-266a-8606-0f82d8aa1f8d`.

Both metadata probe and OPALX use `/opt/psi/Programming/cuda/13.2.1/targets/x86_64-linux/lib/libcudart.so.13.2.75`, runtime/header version 13020. Native-test mapping selected distinct CUDA ordinal masks and recorded NVML UUIDs via nvidia-smi; it did not query the runtime UUID API. The stronger runtime UUID confirmation belongs specifically to job 355083.

These short NONE-solver runs exercise actual tracker/shared-library scalar storage and failure handling. Their macroparticle charge is zero; they do not establish nonzero charge conservation, GPU PIC-solver behavior, production throughput or mesh/long-term convergence. Native tests separately cover frozen self-field and RF algorithms.

## Provenance and preservation

GPU executable SHA256: `6cd248ee531a5e36318335a82949041c01fb3e50189e40a9683bec11174823de`. All four tracker cases used the identical native-tested executable and shared build, with binaries checked before/after. Unchanged CPU input/reference fixture archive SHA256: `559eb9abc34b6b3323be9ed1838759807e233b25937005b083b40678c7ef9943`.

- Native evidence archive: `99b376a4cc223d61bf29dc3411f3501f654c91e029564812e17d9a59ac16492c`.
- Failed launcher evidence archive: `ca09d14668deac811c9f2340536f31e28e60663e308e686e008453e277dd9dd6`.
- Successful tracker evidence archive: `0f50f331268b8a039dc48878f92c5532b6e2bcc8d4411fd1ac64587274920f6c`.

The superseded pre-submission snapshot `663f93a30bef` was uploaded only, never extracted or submitted; it was replaced after the enclosing-private-method NVCC concern was caught locally. Prior source/build snapshot `790abac19643`, the original remote checkout and dependency source code were untouched. New work used `/data/user/adelmann/opalx-dev/pr637-audit-fixes-20261109/3320cf6fc490` with isolated dependency clones/copies.

No task jobs or monitors remain active. No more testing is planned. Authoritative structured reports are `native-audit.json`, `tracker-gpu-audit.json` and `summary.json`; raw terminal evidence is under `remote-native/`, `remote-tracker-355082/` and `remote-tracker-final/`.

## Reproduce the retrieved tracker analysis

The successful job 355083 archive was extracted without renaming or normalizing paths under `remote-tracker-final/`; its run directory is `gpu-integration-final/`. The original successful analysis used `audit_tracker_gpu_final.py`. The canonical `audit_tracker_gpu.py` now accepts `--run-dir` and defaults to that final directory. The earlier unparameterized draft is retained as `audit_tracker_gpu_legacy_path.py`.

Run from any working directory:

```sh
/Users/adelmann/.venv-h6/bin/python \
  /Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100/audit_tracker_gpu.py \
  /Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100/remote-tracker-final \
  --run-dir gpu-integration-final
```

This command was rerun only on the already-retrieved final files. No simulations or native tests were repeated. All pre-existing JSON files remain byte-identical, including both copies of `tracker-gpu-audit.json`, `summary.json` and `native-audit.json`; hashes and exact commands are recorded in `reproducibility-check.json`.
