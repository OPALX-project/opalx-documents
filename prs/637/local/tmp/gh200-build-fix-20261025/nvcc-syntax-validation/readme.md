# CUDA extended-lambda syntax validation

Compiled on Merlin6 login host `merlin-l-001.psi.ch`, 25 October 2026.
This was a tiny compiler-only check; no GPU execution, allocation, full OPALX
build or remote repository modification was performed. It validates NVCC syntax
restrictions and the two chosen remedies, not the complete GH200 CI build.

The login environment already loaded `gcc/14.3.0`, `openmpi/5.0.10_slurm`,
`cuda/12.9.1`, and `cmake/4.4.0`; no module changes were made. See
`environment.log` for all actual loaded modules and compiler version details.
The observed compiler was NVCC 12.9.86, whereas CSCS GH200 CI uses CUDA 13.1.1.

Reproducer command for each `.cu` file:

```sh
nvcc -std=c++20 --extended-lambda -arch=sm_90 -c SOURCE.cu -o SOURCE.o
```

| Case | Exit status | Result |
| --- | ---: | --- |
| bad_private_payload | 2 | Capturing private nested `Recorder::Hit` fails |
| fixed_namespace_payload | 0 | Namespace-scope payload compiles |
| bad_private_testbody | 2 | Extended lambda inside private `TestBody` fails |
| fixed_namespace_helper | 0 | Extended lambda inside namespace helper compiles |

The `.log` files preserve exact diagnostics; successful compile logs are empty.
`run.sh` reproduces the commands. Run it within this directory. `status.tsv`
preserves exit codes. No unsupported-host-compiler override was used.

Task-owned remote directory: `/tmp/opalx-gh200-cuda-syntax-20261025.700Scx`.
