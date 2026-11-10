#!/usr/bin/env python3
"""Convert native OPALX laboratory PROBE records to the FFA25 school frame.

This standalone analysis utility is not a native unit-test dependency. The
unrotated school ring has native centre (-R0, 0) in horizontal laboratory X-Z;
old school (x,y,z) = native (x+R0,z,y). Positions are metres, momenta p/(mc),
and time seconds. Reference-turn labels are preserved unless explicitly offset.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

import h5py
import numpy as np
import pandas as pd

COLUMNS = ("x", "y", "z", "px", "py", "pz", "id", "turn", "bunchNumber", "time")
INTEGER_COLUMNS = ("id", "turn", "bunchNumber")
FLOAT_COLUMNS = tuple(name for name in COLUMNS if name not in INTEGER_COLUMNS)
HEADER = "# x (m), y (m), z (m), px ( ), py ( ), pz ( ), id, turn ( ), bunchNumber ( ), time (s)"
_INT64_MAX = np.iinfo(np.int64).max


def _validated(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the ten-column record without rounding integer identities."""
    if tuple(frame.columns) != COLUMNS:
        raise ValueError(f"Expected exactly these probe columns: {', '.join(COLUMNS)}")
    result = frame.copy()
    for name in INTEGER_COLUMNS:
        # Do not pass IDs through float64, which loses integers above 2**53.
        values = []
        for value in result[name]:
            if isinstance(value, (int, np.integer)):
                integer = int(value)
            elif isinstance(value, str) and re.fullmatch(r"[+]?\d+", value):
                integer = int(value)
            else:
                raise ValueError(f"{name} must contain nonnegative integer values")
            if integer < 0 or integer > _INT64_MAX:
                raise ValueError(f"{name} must fit a nonnegative signed 64-bit integer")
            values.append(integer)
        result[name] = pd.Series(values, index=result.index, dtype="int64")
    for name in FLOAT_COLUMNS:
        result[name] = pd.to_numeric(result[name], errors="raise").astype("float64")
        if not np.isfinite(result[name].to_numpy()).all():
            raise ValueError(f"Nonfinite probe {name}")
    return result


def read_native_probe(path: str | Path) -> pd.DataFrame:
    """Read one station's native ten-column ASCII or HDF5 PROBE output.

    HDF5 Step# groups are flush batches, not reference turns. Concatenate all
    batches, then sort stably by bunch/particle/time. No contiguous-ID, unique
    (ID,turn), or one-crossing-per-turn assumption is made. HDF5 q/m datasets
    are outside the school's ten-column format and are not exported.
    """
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Probe file does not exist: {source}")
    if h5py.is_hdf5(source):
        batches = []
        with h5py.File(source, "r") as file:
            groups = sorted((key for key in file if re.fullmatch(r"Step#\d+", key)),
                            key=lambda key: int(key.split("#")[1]))
            if not groups:
                raise ValueError(f"No Step# probe batches in {source}")
            for key in groups:
                group = file[key]
                if not isinstance(group, h5py.Group):
                    raise ValueError(f"{source}:{key} is not an HDF5 group")
                missing = set(COLUMNS) - set(group)
                if missing:
                    raise ValueError(f"{source}:{key} missing probe datasets: {sorted(missing)}")
                arrays = {name: np.asarray(group[name]) for name in COLUMNS}
                if any(array.ndim != 1 for array in arrays.values()):
                    raise ValueError(f"{source}:{key} probe datasets must be one-dimensional")
                if len({len(array) for array in arrays.values()}) != 1:
                    raise ValueError(f"{source}:{key} has unequal probe dataset lengths")
                for name in INTEGER_COLUMNS:
                    if arrays[name].dtype.kind not in "iu":
                        raise ValueError(f"{source}:{key}/{name} must be an integer dataset")
                batches.append(_validated(pd.DataFrame(arrays, columns=COLUMNS)))
        frame = pd.concat(batches, ignore_index=True)
    else:
        # Read tokens as strings first so malformed widths and large IDs remain
        # visible; providing column names before parsing can hide extra columns.
        try:
            frame = pd.read_csv(source, sep=r"\s+", comment="#", header=None,
                                dtype=str, keep_default_na=False)
        except pd.errors.EmptyDataError:
            frame = pd.DataFrame(columns=COLUMNS)
        if len(frame.columns) != len(COLUMNS):
            raise ValueError(f"{source} must contain exactly ten probe columns")
        frame.columns = COLUMNS
        frame = _validated(frame)
    return frame.sort_values(["bunchNumber", "id", "time"], kind="stable").reset_index(drop=True)


def to_school_frame(native: pd.DataFrame, r0_m: float, turn_offset: int = 0) -> pd.DataFrame:
    """Convert the existing unrotated FFA25 native ring frame to the old frame.

    R0 is explicit, in metres; no centre is inferred from hit positions. The
    default retains OPALX's zero-based shared reference-turn labels. An explicit
    offset of +1 only relabels native counts. In the supplied old school inputs,
    the legacy tracker advances turn labels on an RF-frequency step budget, not
    on orbital returns: BFREQ=1 MHz gives 1 us versus about 0.59 us per 16-cell
    orbit. No constant offset reproduces those labels, even away from boundaries.
    Compare station/particle/time and chronological passage order. Never derive turns
    from per-particle crossing counts or HDF5 batch numbers.
    """
    if not np.isfinite(r0_m) or r0_m <= 0:
        raise ValueError("R0 must be finite and positive, in metres")
    if isinstance(turn_offset, bool) or not isinstance(turn_offset, (int, np.integer)):
        raise ValueError("turn_offset must be an integer")
    native = _validated(native)
    result = native.copy()
    result["x"] = native.x + r0_m
    result["y"], result["z"] = native.z, native.y
    result["px"], result["py"], result["pz"] = native.px, native.pz, native.py
    turns = [int(turn) + int(turn_offset) for turn in native.turn]
    if any(turn < 0 or turn > _INT64_MAX for turn in turns):
        raise ValueError("Turn offset produces an out-of-range reference turn")
    result["turn"] = pd.Series(turns, index=result.index, dtype="int64")
    return _validated(result)


def write_school_loss(frame: pd.DataFrame, path: str | Path) -> None:
    """Write one header and ten school-readable columns to a new file.

    Exclusive creation prevents accidental replacement of native or existing
    analysis data. Seventeen-digit floats retain the precision available in the
    source; native ASCII input itself normally has only six significant digits.
    """
    frame = _validated(frame)
    with Path(path).open("x") as output:
        output.write(HEADER + "\n")
        for row in frame.itertuples(index=False, name=None):
            output.write(" ".join(str(int(value)) if name in INTEGER_COLUMNS
                                  else format(float(value), ".17g")
                                  for name, value in zip(COLUMNS, row)) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="one native laboratory PROBE .loss or .h5 file")
    parser.add_argument("output", type=Path, help="new school-frame ten-column .loss file")
    parser.add_argument("--r0-m", type=float, required=True,
                        help="native school ring radius R0 [m]; centre is laboratory (-R0,0)")
    parser.add_argument("--turn-offset", type=int, default=0,
                        help="explicit reference-turn label offset; default 0 preserves native labels")
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must be different files")
        native = read_native_probe(args.input)
        school = to_school_frame(native, args.r0_m, args.turn_offset)
        write_school_loss(school, args.output)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        parser.exit(1, f"ffa_school_probe_adapter: {error}\n")
    print(f"Converted {len(school)} hits to {args.output}; turn offset {args.turn_offset:+d}")


if __name__ == "__main__":
    main()
