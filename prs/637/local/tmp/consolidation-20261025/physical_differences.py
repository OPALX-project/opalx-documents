#!/usr/bin/env python3
"""Describe identity-aligned differences without changing strict parity results.

Positions [m], momenta beta*gamma, times [s], emittances [m rad]. Probe records
are aligned by unique (turn,id) keys. No numerical acceptance tolerance is used.
The diagnostic report never modifies parity-report.json or simulation outputs.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import re

import h5py
import numpy as np
import pandas as pd


def metrics(a, b):
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape:
        return {"shape_equal": False, "baseline_shape": list(a.shape), "current_shape": list(b.shape)}
    equality = a == b
    matched_nan = 0
    if a.dtype == b.dtype and a.dtype.kind in "fc":
        same_bytes = np.all(
            np.ascontiguousarray(a).reshape(-1).view(np.uint8).reshape(-1, a.dtype.itemsize)
            == np.ascontiguousarray(b).reshape(-1).view(np.uint8).reshape(-1, b.dtype.itemsize), axis=1).reshape(a.shape)
        both_nan = np.isnan(a) & np.isnan(b) & same_bytes
        matched_nan = int(both_nan.sum())
        equality |= both_nan
    d = b.astype(np.longdouble) - a.astype(np.longdouble)
    finite = d[np.isfinite(d)]
    return {"count": int(a.size), "exact": bool(np.all(equality) and a.dtype == b.dtype),
            "differing_values": int(np.count_nonzero(~equality)), "matching_nan_values": matched_nan,
            "max_abs_difference": float(np.max(np.abs(finite))) if finite.size else 0.0,
            "rms_difference": float(np.sqrt(np.mean(finite * finite))) if finite.size else 0.0}


def update_max(aggregate, name, values, where):
    if name not in aggregate:
        aggregate[name] = {**values, "worst_location": where, "compared_groups": 1}
        return
    entry = aggregate[name]
    entry["count"] += values["count"]
    entry["differing_values"] += values["differing_values"]
    entry["matching_nan_values"] += values["matching_nan_values"]
    entry["exact"] &= values["exact"]
    entry["compared_groups"] += 1
    if values["max_abs_difference"] > entry["max_abs_difference"]:
        entry["max_abs_difference"] = values["max_abs_difference"]
        entry["worst_location"] = where
    entry["rms_difference"] = max(entry["rms_difference"], values["rms_difference"])


def step_names(handle):
    return sorted((name for name in handle if name.startswith("Step#")), key=lambda name: int(name[5:]))


def attribute_differences(old, new, name):
    result = {}
    if set(old.attrs) != set(new.attrs):
        result["schema"] = {"missing": sorted(set(old.attrs) - set(new.attrs)),
                            "extra": sorted(set(new.attrs) - set(old.attrs))}
    for key in old.attrs.keys() & new.attrs.keys():
        a, b = np.asarray(old.attrs[key]), np.asarray(new.attrs[key])
        if a.dtype.kind in "biuf" and b.dtype.kind in "biuf":
            result[key] = metrics(a, b)
    return result


def phase_space(baseline, current):
    report = {"dataset_maxima": {}, "attribute_maxima": {}, "derived_moment_maxima": {}, "snapshots": [],
              "centroid_attribute_note": "Existing H5PartWrapperForPT writes the first three components of DistributionMoments unnormalized 6D sums as centroid; use derived position_mean_m for actual spatial mean differences"}
    with h5py.File(baseline / "acceleration.h5") as old, h5py.File(current / "acceleration.h5") as new:
        old_names, new_names = step_names(old), step_names(new)
        report["snapshot_names_equal"] = old_names == new_names
        report["snapshot_counts"] = [len(old_names), len(new_names)]
        final_ids = []
        for name in old_names:
            a, b = old[name], new[name]
            ia, ib = np.argsort(a["id"][()]), np.argsort(b["id"][()])
            ids_a, ids_b = a["id"][()][ia], b["id"][()][ib]
            if len(np.unique(ids_a)) != len(ids_a) or len(np.unique(ids_b)) != len(ids_b):
                raise ValueError(f"Repeated particle ID in phase snapshot {name}")
            equal_ids = np.array_equal(ids_a, ids_b)
            detail = {"snapshot": name, "particles": [len(ids_a), len(ids_b)],
                      "particle_ID_sets_equal": equal_ids, "datasets": {}}
            if not equal_ids:
                detail["missing_IDs"] = np.setdiff1d(ids_a, ids_b).tolist()
                detail["extra_IDs"] = np.setdiff1d(ids_b, ids_a).tolist()
                raise ValueError(f"Particle ID mismatch at {name}: {detail}")
            for key in a:
                values = metrics(a[key][()][ia], b[key][()][ib])
                update_max(report["dataset_maxima"], key, values, name)
                detail["datasets"][key] = values["max_abs_difference"]
            for key, values in attribute_differences(a, b, name).items():
                if "count" in values:
                    update_max(report["attribute_maxima"], key, values, name)
            detail["derived_moments"] = {}
            for moment, function in [("position_mean_m", np.mean), ("position_rms_m", np.std)]:
                va = np.array([function(a[key][()][ia]) for key in ("x", "y", "z")])
                vb = np.array([function(b[key][()][ib]) for key in ("x", "y", "z")])
                values = metrics(va, vb)
                update_max(report["derived_moment_maxima"], moment, values, name)
                detail["derived_moments"][moment] = values
            report["snapshots"].append(detail)
            final_ids = [ids_a, ids_b]
        final_a, final_b = old[old_names[-1]], new[new_names[-1]]
        report["final"] = {"particle_IDs_equal": np.array_equal(*final_ids),
            "particles": [len(ids) for ids in final_ids],
            "lost_IDs": [np.setdiff1d(np.arange(4096), ids).tolist() for ids in final_ids],
            "attributes": attribute_differences(final_a, final_b, old_names[-1])}
    return report, final_ids


def read_probe(path):
    with h5py.File(path) as handle:
        frames = [pd.DataFrame({key: handle[name][key][()] for key in handle[name]}) for name in step_names(handle)]
    return pd.concat(frames, ignore_index=True)


def probe_differences(baseline, current, final_ids):
    a, b = read_probe(baseline / "radial.h5"), read_probe(current / "radial.h5")
    raw_order = metrics(a.id.to_numpy(), b.id.to_numpy())
    if a.duplicated(["turn", "id"]).any() or b.duplicated(["turn", "id"]).any():
        raise ValueError("Probe keys (turn,id) are not unique; explicit occurrence matching required")
    a = a.set_index(["turn", "id"]).sort_index()
    b = b.set_index(["turn", "id"]).sort_index()
    if not a.index.equals(b.index):
        raise ValueError(f"Probe key mismatch: missing={a.index.difference(b.index).tolist()[:20]}, extra={b.index.difference(a.index).tolist()[:20]}")
    report = {"records": [len(a), len(b)], "unique_turn_ID_keys_equal": True,
              "serialized_ID_order": raw_order,
              "aligned_dataset_differences": {key: metrics(a[key].to_numpy(), b[key].to_numpy()) for key in a},
              "per_turn": []}
    report["aligned_dataset_differences"]["id"] = metrics(a.index.get_level_values("id"), b.index.get_level_values("id"))
    report["aligned_dataset_differences"]["turn"] = metrics(a.index.get_level_values("turn"), b.index.get_level_values("turn"))
    a["radius_mm"] = np.hypot(a.x, a.z) * 1000
    b["radius_mm"] = np.hypot(b.x, b.z) * 1000
    complete_a = [int(turn) for turn, group in a.groupby(level="turn") if set(final_ids[0]).issubset(set(group.index.get_level_values("id")))]
    complete_b = [int(turn) for turn, group in b.groupby(level="turn") if set(final_ids[1]).issubset(set(group.index.get_level_values("id")))]
    report["complete_turn_lists_equal"] = complete_a == complete_b
    selected = complete_a[-8:]
    if len(selected) != 8:
        raise ValueError("Fewer than eight complete final probe passages")
    selected_a = a.loc[selected]
    selected_b = b.loc[selected]
    low = np.floor(min(selected_a.radius_mm.min(), selected_b.radius_mm.min()) * 10) / 10
    high = np.ceil(max(selected_a.radius_mm.max(), selected_b.radius_mm.max()) * 10) / 10
    edges = np.arange(low, high + .100001, .1)
    final_profiles = []
    for turn, ga in a.groupby(level="turn"):
        gb = b.xs(turn, level="turn", drop_level=False)
        entry = {"turn": int(turn), "particles": [len(ga), len(gb)],
                 "charge_C": [float(ga.q.sum()), float(gb.q.sum())],
                 "mean_radius_mm": [float(ga.radius_mm.mean()), float(gb.radius_mm.mean())],
                 "rms_radius_mm": [float(ga.radius_mm.std(ddof=0)), float(gb.radius_mm.std(ddof=0))],
                 "max_paired_radius_difference_mm": float(np.max(np.abs(ga.radius_mm.to_numpy() - gb.radius_mm.to_numpy())))}
        report["per_turn"].append(entry)
        if int(turn) in selected:
            ha = np.histogram(ga.radius_mm, bins=edges, weights=abs(ga.q) * 1e12)[0] / np.diff(edges)
            hb = np.histogram(gb.radius_mm, bins=edges, weights=abs(gb.q) * 1e12)[0] / np.diff(edges)
            entry = {**entry, "density_pC_per_mm": metrics(ha, hb),
                     "aligned_datasets": {key: metrics(ga[key], gb[key]) for key in ga if key != "radius_mm"}}
            final_profiles.append(entry)
    report["final_eight"] = {"turns_zero_based": selected, "common_bin_width_mm": .1,
                             "density_bins": len(edges) - 1, "turns": final_profiles,
                             "all_density_bins_exact": all(e["density_pC_per_mm"]["exact"] for e in final_profiles)}
    report["group_attribute_maxima"] = {}
    with h5py.File(baseline / "radial.h5") as old, h5py.File(current / "radial.h5") as new:
        for name in step_names(old):
            for key, value in attribute_differences(old[name], new[name], name).items():
                if "count" in value:
                    update_max(report["group_attribute_maxima"], key, value, name)
    report["histogram"] = metrics(np.loadtxt(baseline / "radial.hist"), np.loadtxt(current / "radial.hist"))
    report["histogram"]["byte_identical"] = (baseline / "radial.hist").read_bytes() == (current / "radial.hist").read_bytes()
    report["peaks_mm"] = metrics(np.loadtxt(baseline / "radial.peaks"), np.loadtxt(current / "radial.peaks"))
    return report


def statistics(baseline, current):
    def read(path):
        text = path.read_text()
        data = re.search(r"&data\b.*?&end", text, re.S)
        header = text[:data.start()]
        names = [re.search(r"\bname\s*=\s*([^,\s]+)", block).group(1) for block in re.findall(r"&column\b(.*?)&end", header, re.S)]
        parameters = len(re.findall(r"&parameter\b", header))
        lines = [line for line in text[data.end():].splitlines() if line.strip()][parameters:]
        return pd.DataFrame(np.loadtxt(io.StringIO("\n".join(lines)), ndmin=2), columns=names)
    a, b = read(baseline / "acceleration.stat"), read(current / "acceleration.stat")
    return {"rows": [len(a), len(b)], "columns": {key: metrics(a[key], b[key]) for key in a}}


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=here.parent / "ring-space-charge-profiles-20261023/accelerating-pic-8-580")
    parser.add_argument("--current", type=Path, default=here / "accelerating-pic-8-580")
    parser.add_argument("--output", type=Path, default=here / "physical-differences.json")
    args = parser.parse_args()
    for folder in (args.baseline, args.current):
        launch = json.loads((folder / "launch.json").read_text())
        if launch.get("returncode") != 0:
            raise RuntimeError(f"Not a completed successful run: {folder}")
    phase, final_ids = phase_space(args.baseline, args.current)
    report = {"baseline": str(args.baseline), "current": str(args.current),
              "purpose": "Diagnostic identity alignment; strict parity report remains unchanged; no acceptance tolerance applied",
              "aggregate_rms_note": "For phase/group attribute aggregates, rms_difference is the largest per-group RMS difference",
              "phase_space": phase, "probe": probe_differences(args.baseline, args.current, final_ids),
              "statistics": statistics(args.baseline, args.current)}
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output": str(args.output), "phase_max": {key: value["max_abs_difference"] for key, value in phase["dataset_maxima"].items()},
                      "probe_aligned_max": {key: value["max_abs_difference"] for key, value in report["probe"]["aligned_dataset_differences"].items()},
                      "histogram": report["probe"]["histogram"], "peaks_mm": report["probe"]["peaks_mm"],
                      "final8_density_exact": report["probe"]["final_eight"]["all_density_bins_exact"]}, indent=2))


if __name__ == "__main__":
    main()
