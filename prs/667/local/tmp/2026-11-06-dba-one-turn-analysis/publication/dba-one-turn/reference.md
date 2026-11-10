# Retained one-turn DBA reference

Keep this run at its present location. Do not rerun into this directory or overwrite its native outputs. Future comparisons belong in a new directory.

The run completed with job 354991 on one A100, one rank, batch64: 100k particles, 5.602 nC, 64×64×512, 3 ps, 393240 steps over one reference circumference. All IDs and charge are retained. The pinned executable is ../opalx; its full identity and source-fix commit are in REFERENCE.json. No executable was rebuilt or replaced when recording this reference.

Use reference-input.in for the exact executed input. case.in was reformatted after completion; it and its backup are preserved. Native case.h5, case.stat, checkpoint, log and manifest remain untouched. REFERENCE.json provides SHA256 hashes of the native files, executable and supporting inputs.

The matched-KV analysis, plots, frozen model and scripts are in analysis/. From this run directory, reproduce using OPALX_DBA_H5="$PWD/case.h5" python analysis/analyze.py, followed by python analysis/plot.py in a suitable NumPy/SciPy/pandas/h5py/matplotlib environment. Geometry/optics conventions and the limits of the comparison are documented in analysis/readme.md.
