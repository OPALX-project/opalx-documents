#!/usr/bin/env python3
"""Check native frozen longitudinal fields against an independent pipe model.

Requires h5py and NumPy. The reference follows Gauss's law: integrate the
uniform-disk radial electric field from a probe to the grounded circular wall,
then differentiate the piecewise-linear triangular line density. No OPALX
field or fitted coefficient enters that reference.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import sys

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def radial_potential_per_lambda(radius, a, b, epsilon):
    """Gauss-law potential, integrated separately through beam and vacuum."""
    inside = max(0., (a*a - radius*radius) / (2.*a*a)) if radius < a else 0.
    vacuum = math.log(b / max(radius, a))
    return (inside + vacuum) / (2. * math.pi * epsilon)


def validate(stat_path):
    cfg = json.loads((ROOT / "physics_config.json").read_text())
    provenance = json.loads((ROOT / "analytic_provenance.json").read_text())
    for name, expected in provenance["fixtures"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"Fixture changed without review: {name}")
    with (ROOT / "probes.csv").open(newline="") as stream:
        probes = list(csv.DictReader(stream))
    h5_path = stat_path.with_suffix(".h5")
    with h5py.File(h5_path, "r") as handle:
        if list(handle) != ["Step#0"]:
            raise ValueError("Expected exactly one frozen field snapshot")
        for key in ["ExUnit", "EyUnit", "EzUnit"]:
            value = np.asarray(handle.attrs[key]).item()
            if isinstance(value, bytes):
                value = value.decode()
            if value != "V/m":
                raise ValueError(f"Wrong field units: {key}={value}")
        step = handle["Step#0"]
        count = cfg["expected_particles"]
        ids = step["id"][:].astype(np.int64)
        if len(ids) != count or not np.array_equal(np.sort(ids), np.arange(count)):
            raise ValueError("Particle IDs/count mismatch")
        time = float(np.asarray(step.attrs["TIME"]).ravel()[0])
        charge = float(np.asarray(step.attrs["CHARGE"]).ravel()[0])
        if not math.isclose(time, cfg["dt_s"], rel_tol=1.e-11, abs_tol=0.):
            raise ValueError("Wrong snapshot time")
        if not math.isclose(charge, cfg["assigned_charge_C"], rel_tol=1.e-11, abs_tol=0.):
            raise ValueError("Wrong total charge")
        q = step["q"][:]
        if not np.allclose(q, cfg["macrocharge_C"], rtol=1.e-11, atol=0.):
            raise ValueError("Wrong per-particle charge")
        if not math.isclose(float(q.sum()), charge, rel_tol=1.e-11, abs_tol=0.):
            raise ValueError("Charge sum mismatch")
        for key in ["x", "y", "z", "px", "py", "pz", "Ex", "Ey", "Ez", "Bx", "By", "Bz"]:
            if not np.isfinite(step[key][:]).all():
                raise ValueError(f"Nonfinite native data: {key}")
        refp = np.asarray(step.attrs["RefPartP"], dtype=float)
        tangent = refp / np.linalg.norm(refp)
        if tangent[2] <= 0. or max(abs(tangent[0]), abs(tangent[1])) > 1.e-10:
            raise ValueError("Unexpected straight-beam reference direction")
        if not math.isclose(math.sqrt(1. + float(refp @ refp)), cfg["gamma"], rel_tol=1.e-10):
            raise ValueError("Unexpected reference gamma")
        e1 = np.array([tangent[2], 0., -tangent[0]])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(tangent, e1)
        basis = np.column_stack((e1, e2, tangent))
        selected = np.argsort(ids)[cfg["source_particles"]:]
        order, back = np.argsort(selected), np.argsort(np.argsort(selected))
        get = lambda keys: np.column_stack([step[k][selected[order]][back] for k in keys])
        position = get(["x", "y", "z"]) @ basis.T + np.asarray(step.attrs["RefPartR"])
        field = get(["Ex", "Ey", "Ez"]) @ basis.T
        target = np.asarray([[float(p[k]) for k in ["x_m", "y_m", "s_m"]] for p in probes])
        drift = np.array([0., 0., cfg["beta"] * 299792458. * time])
        max_motion_residual = float(np.linalg.norm(position - target - drift, axis=1).max())
        if max_motion_residual > 1.e-10:
            raise ValueError("Frozen probe positions/frame mismatch")
    slope = 4. * cfg["source_charge_C"] / cfg["full_length_m"]**2
    rows, maximum_relative, maximum_wall = [], 0., 0.
    for p, electric in zip(probes, field):
        radius = math.hypot(float(p["x_m"]), float(p["y_m"]))
        sign = math.copysign(1., float(p["s_m"]))
        expected = sign * slope * radial_potential_per_lambda(radius, cfg["beam_radius_m"], cfg["pipe_radius_m"], cfg["epsilon0_F_per_m"]) / cfg["gamma"]**2
        actual = float(electric[2])
        if radius == cfg["pipe_radius_m"]:
            error = abs(actual)
            maximum_wall = max(maximum_wall, error)
            passed = error <= cfg["wall_absolute_tolerance_V_per_m"]
        else:
            error = abs(actual / expected - 1.)
            maximum_relative = max(maximum_relative, error)
            passed = error <= cfg["relative_field_tolerance"]
        rows.append(dict(probe_id=int(p["probe_id"]), radius_m=radius, s_m=float(p["s_m"]),
                         actual_Es_V_per_m=actual, analytic_Es_V_per_m=expected, passed=passed))
    return dict(case=cfg["name"], passed=all(r["passed"] for r in rows),
                criterion="Nonzero frozen longitudinal fields within 1% of uniform-round conducting-pipe analytic solution; wall Es=0 within 1e-4V/m; exact IDs, charge, time and frame",
                maximum_relative_field_error=maximum_relative,
                maximum_wall_absolute_field_V_per_m=maximum_wall,
                max_probe_motion_residual_m=max_motion_residual,
                relative_field_tolerance=cfg["relative_field_tolerance"],
                wall_absolute_tolerance_V_per_m=cfg["wall_absolute_tolerance_V_per_m"],
                expected_particles=count, source_charge_C=cfg["source_charge_C"],
                assigned_charge_C=charge, snapshot_time_s=time,
                source_probes_self_field="Only two probe planes at +/-2.5m, separated by many gradient cells; same-plane symmetric CIC gather/deposit has zero longitudinal self contribution",
                h5_sha256=digest(h5_path), probes=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stat", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.stat)
    except (ValueError, OSError, KeyError, AssertionError) as error:
        result = dict(passed=False, error=str(error))
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
