# Independent all-step tracking checks

The uniform-B regression cases in the companion `regression-tests-x` repository
provide a standard-library-only `validate.py` with this interface:

```sh
python3 validate.py --stat TEST.stat --output physics-validation.json
```

It checks every total RMS size against the independent analytic covariance at
each promised time, plus particle count, charge, source fixtures and complete
half-turn coverage. A successful report contains `"passed": true` and exits
zero; failed physics or malformed input returns nonzero.

## Local smoke runner

Select the hook explicitly. Other cases retain their existing `.rt` behavior;
the presence of a file named `validate.py` never makes the runner execute it.

```sh
OMP_NUM_THREADS=4 OMP_PROC_BIND=false python3 tools/run_regression_smoke.py \
  --opalx build-omp/src/opalx \
  --test-dir ../regression-tests-x/RegressionTests/FFT2D5-UniformB-ZeroSC \
  --build-dir build-omp --physics-validator validate.py
```

Repeat with `FFT2D5-UniformB-1pC`. Validator paths must be relative to and remain
inside the copied case directory. `--physics-validator` is incompatible with
`--exit-only`: physics validation is additional to the normal `.rt` checks.
Both checks must pass. The runner retains the JSON report, validator stdout and
stderr, and process result in its isolated run artifacts. `--timeout` also
limits the validator process when supplied.

The hook's integration checks run with:

```sh
python3 -m unittest discover -s tools -p test_run_regression_smoke.py
```

## CI scope

The CPU Serial GitHub workflow explicitly selects the physics validator for
the two new matrix cases, executes it after OPALX, and uploads its report and
STAT output even on validation failure. The OPALX workflow and companion
regression cases must be published together before the remote CI can use them.

The external CSCS regression runner still uses its existing `.rt` aggregation
checks. This change does not alter that external runner or claim that its jobs
already enforce the all-step criterion. These are OPALX tracking regressions;
the solver's C++ tests remain unit tests.
