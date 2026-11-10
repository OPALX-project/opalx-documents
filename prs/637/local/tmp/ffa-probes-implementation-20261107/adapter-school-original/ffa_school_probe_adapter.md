# FFA25 school probe adapter

`ffa_school_probe_adapter.py` converts one station's native OPALX laboratory
PROBE output to the ten-column format read by `FFA25-school/read_dat.py`.
It is a separate analysis utility, not a dependency of native C++ unit tests.
Use the OPALX Python environment with NumPy, pandas and h5py:

```sh
~/.venv-h6/bin/python tools/ffa_school_probe_adapter.py \
    native/PROBE1.h5 school/PROBE1.loss --r0-m 4.42
```

Native ASCII `.loss` input works as well. The output directory must already
exist; output files are created exclusively to protect original data. Run once
per station. A missing probe file is an error, including a no-hit run for which
the native writer produced no file. The utility does not invent empty hits.
A supplied header-only ASCII file converts to a header-only output.

The adapter describes the **existing unrotated native school geometry**, whose
centre is laboratory `(-R0,0)` in horizontal X-Z. It applies:

| Old school column | Native OPALX laboratory value |
|---|---|
| x | x + R0 |
| y | z |
| z | y |
| px | px |
| py | pz |
| pz | py |

`R0` must be explicit, positive and in metres. This is not a general coordinate
transform for arbitrarily translated or rotated rings. Native output remains
unchanged. No field or momentum sign is adjusted beyond the axis permutation;
the native magnetic-lattice conversion already defines the physical field.
Positions are metres, momenta are p/(mc), and time is seconds.

The adapter preserves particle IDs, bunch numbers and shared reference-turn
labels exactly. IDs need not be contiguous. Rows are sorted stably by
`bunchNumber,id,time`; use those identities when comparing stations, rather
than array indices or equal row lengths. Multiple crossings in one reference
turn remain separate records. HDF5 `Step#` groups are flush batches and are
concatenated; their numbers are never used as reference turns. HDF5 charge and
mass datasets are not part of the old reader's ten-column format.

By default the output retains native OPALX's zero-based reference-turn labels.
For an analysis that explicitly wants one-based native reference-return counts,
add `--turn-offset 1`. This only relabels the native counter. The supplied old
school tracker advances its `turn` on an RF-frequency step budget, rather than
on physical orbital returns: `BFREQ=1` MHz corresponds to 1 microsecond, while
the 16-cell orbit takes about 0.59 microseconds. A constant offset cannot
reproduce the old school labels, even away from turn boundaries. Match old/new
records by station, particle ID, time and chronological passage order; compare
initial-plane sampling separately. The adapter never derives turns from the
number of crossings.

The Python API exposes `read_native_probe(path)`,
`to_school_frame(frame, r0_m, turn_offset=0)` and
`write_school_loss(frame,path)` using pandas DataFrames with columns
`x,y,z,px,py,pz,id,turn,bunchNumber,time`. Both input formats require finite
values and exact nonnegative signed-64-bit integer identities. Native ASCII
usually carries six significant digits; conversion cannot restore precision
already lost in that output. HDF5 retains its source precision.
