"""Independently verify completed triangular-pipe OPALX frozen snapshots.

Only reads parent-owned inputs and H5 files. Writes audit CSV/JSON here.
Run with ~/.venv-h6/bin/python check_native.py after native runs finish.
"""
from pathlib import Path
import hashlib
import json
import re

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
_HASH_CACHE = {}


def sha(path):
    path = Path(path)
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key not in _HASH_CACHE:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(block)
        _HASH_CACHE[key] = digest.hexdigest()
    return _HASH_CACHE[key]


def scalar(value):
    return float(np.asarray(value).item())


def read(path, points):
    m = json.loads(path.read_text())
    assert m["returncode"] == 0, str(path)
    for actual, key in [
        (m["binary"], "binary_sha256"),
        (path.parent / "triangle.in", "input_sha256"),
        (m["distribution"], "distribution_sha256"),
        (m["reference_path"], "reference_path_sha256"),
    ]:
        assert sha(actual) == m[key], (str(path), key)
    src, cfg = m["source"], m["config"]
    first = 0 if m["companion"] else src["source_particles"]
    n = m["expected_particles"]
    wanted = first + np.arange(len(points))
    with h5py.File(m["h5"], "r") as f:
        assert list(f) == ["Step#0"]
        s = f["Step#0"]
        assert np.isclose(scalar(s.attrs["TIME"]), cfg["dt_s"], rtol=1e-12, atol=0)
        assert np.isclose(scalar(s.attrs["CHARGE"]), m["charge_C"], rtol=1e-12, atol=0)
        for key in ("ExUnit", "EyUnit", "EzUnit"):
            unit = f.attrs[key]
            if isinstance(unit, np.ndarray):
                unit = unit.item()
            if isinstance(unit, bytes):
                unit = unit.decode()
            assert str(unit) == "V/m", (key, unit)
        ids = s["id"][:].astype(np.int64)
        assert len(ids) == n
        assert np.array_equal(np.sort(ids), np.arange(n))
        rows = np.argsort(ids)[wanted]
        order, back = np.argsort(rows), np.argsort(np.argsort(rows))

        def get(keys):
            return np.column_stack([s[k][rows[order]][back] for k in keys])

        refp = np.asarray(s.attrs["RefPartP"], dtype=float)
        tangent = refp / np.linalg.norm(refp)
        e1 = np.array([tangent[2], 0., -tangent[0]])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(tangent, e1)
        basis = np.column_stack((e1, e2, tangent))
        electric = get(["Ex", "Ey", "Ez"]) @ basis.T
        position = get(["x", "y", "z"]) @ basis.T + np.asarray(s.attrs["RefPartR"])
        target = points[["x_m", "y_m", "s_m"]].to_numpy()
        motion = np.array([0., 0., cfg["beta"] * 299792458. * cfg["dt_s"]])
        residual = np.linalg.norm(position - target - motion, axis=1)
        assert float(residual.max()) < 1e-10
        charge_sum = 0.
        max_charge_error = 0.
        for start in range(0, n, 262144):
            stop = min(start + 262144, n)
            q = s["q"][start:stop]
            charge_sum += q.sum()
            max_charge_error = max(max_charge_error, float(np.max(abs(q / src["macrocharge_C"] - 1))))
            for key in ["x", "y", "z", "px", "py", "pz", "Ex", "Ey", "Ez", "Bx", "By", "Bz"]:
                assert np.isfinite(s[key][start:stop]).all(), (m["case"], key)
        assert np.isclose(charge_sum, m["charge_C"], rtol=1e-12, atol=0)
        assert max_charge_error < 1e-12
        assert np.isfinite(electric).all()
    return m, electric, dict(
        case=m["case"], particles=n, charge_C=charge_sum,
        max_probe_position_residual_m=float(residual.max()),
        gamma_squared=float(1 + np.dot(refp, refp)),
        input_hashes_pass=True, particle_ids_pass=True, finite_data_pass=True,
        charge_pass=True, units_pass=True, mpi_ranks=m["mpi_ranks"],
        h5_sha256=sha(m["h5"]),
    )


def main():
    points = pd.read_csv(ROOT / "common/probes.csv", float_precision="round_trip")
    manifests = sorted((ROOT / "opalx/runs").glob("*/manifest.json"))
    checks, metrics, fields = [], [], []
    for path in manifests:
        raw = json.loads(path.read_text())
        if raw["companion"] or raw.get("returncode") != 0:
            continue
        companion = path.parent.with_name(path.parent.name + "-probes") / "manifest.json"
        if not companion.exists():
            continue
        a, ea, ca = read(path, points)
        b, eb, cb = read(companion, points)
        assert a["mesh"] == b["mesh"]
        assert a["reference_path_sha256"] == b["reference_path_sha256"]
        assert a["binary_sha256"] == b["binary_sha256"]
        assert a["source"]["macrocharge_C"] == b["source"]["macrocharge_C"]
        eb[:, 2] *= cb["gamma_squared"] / ca["gamma_squared"]
        efield = ea - eb
        checks.extend([ca, cb])
        cfg = a["config"]
        input_text = (path.parent / "triangle.in").read_text()
        widths = [float(re.search(r"PIPESIZE" + dim + r"\s*=\s*([0-9.eE+-]+)", input_text).group(1))
                  for dim in ("X", "Y")]
        box = min(widths)
        g_native = .67 + 2 * np.log(box / cfg["beam_radius_m"])
        g_axis = 1 + 2 * np.log(cfg["pipe_radius_m"] / cfg["beam_radius_m"])
        prefactor = 4 * cfg["charge_C"] / cfg["full_length_m"]**2 / (
            4 * np.pi * cfg["epsilon0_F_per_m"] * cfg["gamma"]**2)
        signed = np.sign(points.s_m.to_numpy())
        analytic_native = signed * prefactor * g_native
        analytic_axis = signed * prefactor * g_axis
        dz = cfg["path_length_m"] / a["mesh"][2]
        edge_margin = 1.
        keep = ((points.kind == "axis") & (abs(points.s_m) >= 1. - 1e-12)
                & (abs(points.s_m) <= 4. + 1e-12)).to_numpy()
        numerical = efield[:, 2]
        metrics.append(dict(
            case=a["case"], nx=a["mesh"][0], ny=a["mesh"][1], nz=a["mesh"][2],
            accepted_axis_points=int(keep.sum()), exclusion_margin_m=edge_margin,
            acceptance_window="1<=abs(s)<=4m; same fixed targets for every mesh",
            pipe_input_full_width_m=box,
            inferred_g_median=float(np.median(numerical[keep] / (signed[keep] * prefactor))),
            native_g=g_native, analytic_onaxis_g=g_axis,
            native_model_max_error_percent=float(np.max(abs(numerical[keep] - analytic_native[keep])) / (prefactor * g_native) * 100),
            physical_onaxis_max_error_percent=float(np.max(abs(numerical[keep] - analytic_axis[keep])) / (prefactor * g_axis) * 100),
            expected_physical_plateau_bias_percent=float((g_native / g_axis - 1) * 100),
        ))
        p = points.copy()
        p["case"] = a["case"]
        p[["Ex_Vpm", "Ey_Vpm", "Ez_Vpm"]] = efield
        fields.append(p)
    if not metrics:
        raise RuntimeError("No completed native main/probe run pairs found")
    pd.DataFrame(checks).to_csv(OUT / "snapshot-checks.csv", index=False)
    pd.DataFrame(metrics).to_csv(OUT / "independent-longitudinal-metrics.csv", index=False)
    pd.concat(fields, ignore_index=True).to_csv(OUT / "independent-probe-fields.csv", index=False)
    result = dict(
        completed_pairs=len(metrics), snapshots=len(checks), checks_pass=True,
        checked="returncodes, input/binary/distribution/path hashes, Step#0, SI E units, time, source/probe macrocharges, IDs, finite source/probe data, frame-reconstructed probe position and predicted native g",
        script_sha256=sha(__file__),
        scope="Independent frozen-field audit; no new native runs and no tracking claim",
        metrics=metrics,
    )
    (OUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
