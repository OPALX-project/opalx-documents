#!/usr/bin/env python3
"""Require exact numerical parity with the pre-consolidation CPU runs.

Run with ~/.venv-h6/bin/python after the new 8^3 run finishes. This script never
launches a simulation, waits for one, changes a numerical tolerance, sorts away
particle ordering, or rewrites a reference. A missing/nonzero completion marker
is an error. Producer metadata and wall-clock diagnostics are the only exclusions.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys

import h5py
import numpy as np

# TIME, time, GlobalTrackStep and all physical moments deliberately remain checked.
IGNORED_ATTRIBUTES = {
    "OPAL_version", "creation_date", "creation_time", "creationDate", "creationTime",
    "date", "Date", "DATE", "wall_time", "wallTime", "wall_clock_time",
    "elapsed_s", "elapsed_time", "CPU_time", "cpu_time",
}
OUTPUT_SUFFIXES = {".h5", ".hist", ".peaks", ".loss", ".stat"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native(value):
    if isinstance(value, (bytes, np.bytes_)):
        return bytes(value).decode("utf-8", errors="replace")
    if isinstance(value, np.generic):
        return native(value.item())
    if isinstance(value, np.ndarray):
        return [native(v) for v in value.tolist()] if value.ndim else native(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return str(value)
    return value


class Comparison:
    def __init__(self, baseline: Path, current: Path):
        self.baseline, self.current = baseline, current
        self.report = {
            "baseline": str(baseline), "current": str(current),
            "exact_numerical_equality": True, "inputs_sha256": {}, "files": {},
            "checked_arrays": 0, "checked_values": 0, "checked_datasets": 0,
            "checked_attributes": 0, "max_absolute_difference": 0.0,
            "mismatches": [], "ignored_attributes": [], "matching_undefined_diagnostics": [],
        }

    def mismatch(self, name, detail):
        self.report["exact_numerical_equality"] = False
        self.report["mismatches"].append({"object": name, "detail": detail})

    def arrays(self, name, left, right):
        left, right = np.asarray(left), np.asarray(right)
        self.report["checked_arrays"] += 1
        self.report["checked_values"] += int(left.size)
        entry = {"shape": list(left.shape), "dtype": str(left.dtype)}
        if left.shape != right.shape:
            self.mismatch(name, {"baseline_shape": list(left.shape), "current_shape": list(right.shape)})
            return {**entry, "exact": False}
        if left.dtype != right.dtype:
            self.mismatch(name, {"baseline_dtype": str(left.dtype), "current_dtype": str(right.dtype)})
        equal_values = np.equal(left, right)
        # Existing one-particle correlation/#sigma diagnostics can be undefined.
        # Recognize identical NaNs without dropping the quantity: require the same
        # positions, dtype and payload bytes. For complex values this checks both
        # components, including a finite component paired with a NaN.
        if left.dtype == right.dtype and left.dtype.kind in "fc":
            left_bytes = np.ascontiguousarray(left).reshape(-1).view(np.uint8).reshape(-1, left.dtype.itemsize)
            right_bytes = np.ascontiguousarray(right).reshape(-1).view(np.uint8).reshape(-1, right.dtype.itemsize)
            equal_bytes = np.all(left_bytes == right_bytes, axis=1).reshape(left.shape)
            matching_nan = np.isnan(left) & np.isnan(right) & equal_bytes
            count = int(np.count_nonzero(matching_nan))
            if count:
                entry["matching_nan_values"] = count
                indices = np.flatnonzero(matching_nan.reshape(-1))[:4]
                self.report["matching_undefined_diagnostics"].append({
                    "object": name, "count": count,
                    "payload_bytes": [left_bytes[i].tobytes().hex() for i in indices],
                })
            equal_values |= matching_nan
        exact = bool(np.all(equal_values))
        entry["exact"] = exact and left.dtype == right.dtype
        if left.dtype.kind in "biufc" and right.dtype.kind in "biufc":
            # Extended precision avoids integer subtraction overflow and rounds
            # neither side before equality testing. Equality above uses originals.
            dtype = np.clongdouble if "c" in (left.dtype.kind, right.dtype.kind) else np.longdouble
            with np.errstate(invalid="ignore", over="ignore"):
                delta = np.abs(left.astype(dtype) - right.astype(dtype))
            finite = delta[np.isfinite(delta)]
            maximum = float(finite.max()) if finite.size else 0.0
            if np.any(np.isinf(delta)):
                maximum = float("inf")
            entry["max_absolute_difference"] = native(maximum)
            self.report["max_absolute_difference"] = max(self.report["max_absolute_difference"], maximum)
            entry["nonfinite_baseline"] = int(np.count_nonzero(~np.isfinite(left)))
            entry["nonfinite_current"] = int(np.count_nonzero(~np.isfinite(right)))
        if not exact:
            flat = np.flatnonzero(np.logical_not(equal_values).reshape(-1))[:4]
            self.mismatch(name, {
                "max_absolute_difference": entry.get("max_absolute_difference"),
                "examples": [{"index": int(i), "baseline": native(left.reshape(-1)[i]),
                              "current": native(right.reshape(-1)[i])} for i in flat],
            })
        return entry

    def attributes(self, label, left, right):
        left_keys, right_keys = set(left), set(right)
        for key in sorted((left_keys | right_keys) & IGNORED_ATTRIBUTES):
            self.report["ignored_attributes"].append(f"{label}@{key}")
        left_keys -= IGNORED_ATTRIBUTES
        right_keys -= IGNORED_ATTRIBUTES
        if left_keys != right_keys:
            self.mismatch(f"{label} attributes", {"missing_current": sorted(left_keys - right_keys),
                                                   "extra_current": sorted(right_keys - left_keys)})
        entries = {}
        for key in sorted(left_keys & right_keys):
            self.report["checked_attributes"] += 1
            entries[key] = self.arrays(f"{label}@{key}", left[key], right[key])
        return entries

    def hdf5(self, relative: str):
        result = {"kind": "HDF5", "datasets": {}, "attributes": {}, "groups": 0}
        with h5py.File(self.baseline / relative, "r") as old, h5py.File(self.current / relative, "r") as new:
            old_names, new_names = {}, {}
            old.visititems(lambda name, obj: old_names.__setitem__(name, type(obj).__name__))
            new.visititems(lambda name, obj: new_names.__setitem__(name, type(obj).__name__))
            if old_names != new_names:
                self.mismatch(f"{relative} object schema", {"baseline": old_names, "current": new_names})
            result["attributes"]["/"] = self.attributes(relative + ":/", old.attrs, new.attrs)
            for name in sorted(old_names.keys() & new_names.keys()):
                left, right = old[name], new[name]
                if type(left) is not type(right):
                    continue
                label = f"{relative}:/{name}"
                result["attributes"][name] = self.attributes(label, left.attrs, right.attrs)
                if isinstance(left, h5py.Dataset):
                    self.report["checked_datasets"] += 1
                    result["datasets"][name] = self.arrays(label, left[()], right[()])
                else:
                    result["groups"] += 1
        return result

    def sdds(self, relative: str):
        def parse(path):
            text = path.read_text()
            match = re.search(r"&data\b.*?&end", text, flags=re.S)
            if not match or "mode=ascii" not in re.sub(r"\s", "", match.group()):
                raise ValueError(f"Not supported ASCII SDDS: {path}")
            if "no_row_counts=1" not in re.sub(r"\s", "", match.group()):
                raise ValueError(f"SDDS row counts require an explicit parser: {path}")
            header = text[:match.start()]
            columns = re.findall(r"&column\b(.*?)&end", header, flags=re.S)
            parameters = re.findall(r"&parameter\b(.*?)&end", header, flags=re.S)
            field = lambda block, key: (re.search(rf"\b{key}\s*=\s*(\"[^\"]*\"|[^,\s]+)", block).group(1).strip('"')
                                        if re.search(rf"\b{key}\s*=", block) else None)
            metadata = [{key: field(block, key) for key in ("name", "type", "units")} for block in columns]
            lines = [line.strip() for line in text[match.end():].splitlines() if line.strip()]
            values = {}
            for block in parameters:
                name, fixed = field(block, "name"), field(block, "fixed_value")
                value = lines.pop(0) if fixed is None else fixed
                if name != "revision":
                    values[name] = value
            data = np.loadtxt(io.StringIO("\n".join(lines)), ndmin=2)
            if data.shape[1] != len(columns):
                raise ValueError(f"SDDS column count mismatch: {path}")
            return metadata, values, data
        old_columns, old_parameters, old_data = parse(self.baseline / relative)
        new_columns, new_parameters, new_data = parse(self.current / relative)
        if old_columns != new_columns or old_parameters != new_parameters:
            self.mismatch(relative + " SDDS schema/parameters", {"baseline_columns": old_columns,
                "current_columns": new_columns, "baseline_parameters": old_parameters, "current_parameters": new_parameters})
        return {"kind": "SDDS", "columns": old_columns, "parameters": old_parameters,
                "rows": self.arrays(relative + " rows", old_data, new_data)}

    def ascii(self, relative: str):
        old_text, new_text = (self.baseline / relative).read_text(), (self.current / relative).read_text()
        old_headers = [line for line in old_text.splitlines() if line.startswith("#")]
        new_headers = [line for line in new_text.splitlines() if line.startswith("#")]
        if old_headers != new_headers:
            self.mismatch(relative + " ASCII header", {"baseline": old_headers, "current": new_headers})
        def load(text):
            if not any(line.strip() and not line.lstrip().startswith("#") for line in text.splitlines()):
                return np.empty((0, 0), dtype=np.float64)
            return np.loadtxt(io.StringIO(text), ndmin=2)
        old_data = load(old_text)
        new_data = load(new_text)
        return {"kind": "ASCII", "byte_identical": old_text == new_text,
                "data": self.arrays(relative, old_data, new_data)}

    def run(self):
        def input_files(folder):
            return {p.name: p for p in folder.iterdir() if p.is_file() and
                    p.suffix in {".in", ".dat"} and p.name != "timing.dat"}
        old_inputs, new_inputs = input_files(self.baseline), input_files(self.current)
        if old_inputs.keys() != new_inputs.keys():
            self.mismatch("input inventory", {"baseline": sorted(old_inputs), "current": sorted(new_inputs)})
        for name in sorted(old_inputs.keys() & new_inputs.keys()):
            left, right = sha256(old_inputs[name]), sha256(new_inputs[name])
            self.report["inputs_sha256"][name] = {"baseline": left, "current": right}
            if left != right:
                self.mismatch(name + " input SHA256", "different input bytes")
        old_files = {p.name for p in self.baseline.iterdir() if p.is_file() and p.suffix in OUTPUT_SUFFIXES}
        new_files = {p.name for p in self.current.iterdir() if p.is_file() and p.suffix in OUTPUT_SUFFIXES}
        if old_files != new_files:
            self.mismatch("output inventory", {"missing_current": sorted(old_files - new_files),
                                               "extra_current": sorted(new_files - old_files)})
        if not old_files:
            self.mismatch("output inventory", "no scientific outputs to compare")
        for relative in sorted(old_files & new_files):
            if relative.endswith(".h5"):
                entry = self.hdf5(relative)
            elif relative.endswith(".stat"):
                entry = self.sdds(relative)
            else:
                entry = self.ascii(relative)
            self.report["files"][relative] = entry
        self.report["max_absolute_difference"] = native(self.report["max_absolute_difference"])
        return self.report


def completed(folder: Path):
    launch = json.loads((folder / "launch.json").read_text())
    if launch.get("returncode") != 0:
        raise RuntimeError(f"Run not successfully completed: {folder}; returncode={launch.get('returncode')!r}")
    manifest = launch.get("input_sha256")
    expected = {"acceleration.in": manifest} if isinstance(manifest, str) else manifest
    if not isinstance(expected, dict) or not expected:
        raise RuntimeError(f"Missing recorded input hashes: {folder}")
    for name, recorded in expected.items():
        if sha256(folder / name) != recorded:
            raise RuntimeError(f"Input no longer matches launch SHA256: {folder / name}")
    log = (folder / "run.log").read_text()
    stops = re.findall(r"EKINSTOP reached after complete gap kick.*?K=([0-9.eE+-]+)\s+MeV", log)
    if not stops or not 580 <= float(stops[-1]) < 582:
        raise RuntimeError(f"Expected complete-kick 580 MeV reference stop missing: {folder}")
    return {"returncode": 0, "reference_stop_MeV": float(stops[-1]),
            "binary_sha256": launch.get("binary_sha256"), "elapsed_s": launch.get("elapsed_s"),
            "recorded_input_manifest_verified": expected}


def particle_summary(folder: Path):
    summary = {}
    with h5py.File(folder / "acceleration.h5", "r") as handle:
        steps = sorted(handle, key=lambda name: int(name.split("#")[-1]))
        final = handle[steps[-1]]
        summary["phase_space_snapshots"] = len(steps)
        summary["final_particles"] = len(final["id"])
        summary["final_time_s"] = native(final.attrs["TIME"])
        summary["final_mean_energy_MeV"] = native(final.attrs["ENERGY"])
    turns = {}
    total_hits = 0
    with h5py.File(folder / "radial.h5", "r") as handle:
        for group in handle.values():
            total_hits += len(group["id"])
            values, counts = np.unique(group["turn"][()], return_counts=True)
            for value, count in zip(values, counts):
                turns[int(value)] = turns.get(int(value), 0) + int(count)
    summary["probe_hits"] = total_hits
    summary["hits_per_turn"] = dict(sorted(turns.items()))
    summary["histogram_total"] = int(np.loadtxt(folder / "radial.hist", dtype=np.int64).sum())
    if summary["histogram_total"] != total_hits:
        raise RuntimeError(f"Probe histogram count differs from saved HDF5 hits: {folder}")
    return summary


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-root", type=Path, default=here.parent / "ring-space-charge-profiles-20261023")
    parser.add_argument("--current-root", type=Path, default=here)
    parser.add_argument("--output", type=Path, default=here / "parity-report.json")
    args = parser.parse_args()
    report = {"exact_numerical_equality": False, "status": "not_checked", "cases": {},
              "undefined_values": "NaNs require identical location, dtype and complete value bytes; all other values require exact equality",
              "exclusions": {"HDF5_attributes": sorted(IGNORED_ATTRIBUTES),
                  "SDDS": "description date and producer revision only; numerical rows, column types/units and other parameters checked",
                  "files": "run.log, timing.dat, *.rt, *.local, launch timing and executable producer hash"}}
    try:
        old_run, new_run = (p / "accelerating-pic-8-580" for p in (args.baseline_root, args.current_root))
        report["completion"] = {"baseline": completed(old_run), "current": completed(new_run)}
        pairs = [("accelerating-pic-8-580", old_run, new_run)]
        for category, old_name, new_name, names in [
            ("probe", "flushing-integration", "probe-integration",
             [f"{fixture}-{mode}" for fixture in ("Cyclotron-Coasting", "Cyclotron-RF-Stop") for mode in ("off", "hdf5", "ascii")]),
            ("bunch", "bunch-integration-final", "bunch-integration", ["none", "near-zero", "charged-one", "charged-two"]),
        ]:
            old_root, new_root = args.baseline_root / old_name, args.current_root / new_name
            # A report is written only after the maintained checker finishes.
            if not (old_root / "report.json").is_file() or not (new_root / "report.json").is_file():
                raise RuntimeError(f"Missing completed {category} integration report")
            for name in names:
                pairs.append((f"{category}/{name}", old_root / name, new_root / name))
        for name, old, new in pairs:
            report["cases"][name] = Comparison(old, new).run()
        report["particles"] = {"baseline": particle_summary(old_run), "current": particle_summary(new_run)}
        report["exact_numerical_equality"] = all(case["exact_numerical_equality"] for case in report["cases"].values())
        report["status"] = "passed" if report["exact_numerical_equality"] else "failed"
    except Exception as error:
        report["status"] = "error"
        report["error"] = str(error)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "exact_numerical_equality": report["exact_numerical_equality"],
        "report": str(args.output), "error": report.get("error"),
        "cases": {name: {key: case[key] for key in ("exact_numerical_equality", "checked_datasets", "checked_attributes", "checked_values", "max_absolute_difference")}
                  for name, case in report["cases"].items()}}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
