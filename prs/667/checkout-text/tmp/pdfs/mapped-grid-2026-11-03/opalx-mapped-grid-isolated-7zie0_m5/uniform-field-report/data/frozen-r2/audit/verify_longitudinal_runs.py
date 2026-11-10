"""Check completed native frozen-run snapshots independently of field plots."""
from pathlib import Path
import hashlib
import json

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(manifest_path, points):
    m = json.loads(manifest_path.read_text())
    assert m["returncode"] == 0
    directory = manifest_path.parent
    assert sha(directory/"tube.in") == m["input_sha256"]
    assert sha(m["binary"]) == m["binary_sha256"]
    assert sha(m["reference_path"]) == m["reference_path_sha256"]
    n = m["expected_particles"]
    with h5py.File(m["h5"]) as f:
        assert list(f) == ["Step#0"]
        s = f["Step#0"]
        assert abs(float(np.asarray(s.attrs["TIME"]).item())/m["dt_s"]-1) < 1e-12
        assert abs(float(np.asarray(s.attrs["CHARGE"]).item())/m["charge_C"]-1) < 1e-12
        ids = s["id"][:].astype(np.int64)
        assert len(ids) == n
        assert np.array_equal(np.sort(ids), np.arange(n))
        q = s["q"][:]
        assert np.isfinite(q).all()
        assert abs(q.sum()/m["charge_C"]-1) < 1e-12
        assert np.max(abs(q-m["source"]["macrocharge_C"])) < 1e-12*abs(q[0])
        # Track-frame to global rotation for this planar x-z test.
        refp = np.asarray(s.attrs["RefPartP"])
        angle = np.arctan2(-refp[0], refp[2])
        co, si = np.cos(angle), np.sin(angle)
        basis = np.array([[co, 0., -si], [0., 1., 0.], [si, 0., co]])
        max_geometry_excess = -np.inf
        max_arclength_excess = -np.inf
        for start in range(0, n, 262144):
            stop = min(n, start+262144)
            position = np.column_stack([s[k][start:stop] for k in "xyz"])
            assert np.isfinite(position).all()
            for key in ["px", "py", "pz", "Ex", "Ey", "Ez", "Bx", "By", "Bz"]:
                assert np.isfinite(s[key][start:stop]).all()
            global_position = position@basis.T+s.attrs["RefPartR"]
            u = np.hypot(global_position[:, 0]+2., global_position[:, 2])-2.
            y = global_position[:, 1]
            arc = 2*np.arctan2(global_position[:, 2], global_position[:, 0]+2.)
            max_geometry_excess = max(max_geometry_excess, float(np.max((u/.005)**2+(y/.0005)**2)-1))
            max_arclength_excess = max(max_arclength_excess, float(np.max(abs(arc))-2.5))
        assert max_geometry_excess < 1e-8
        assert max_arclength_excess < 1e-9
        first_probe = 0 if m["probe_only"] else m["source"]["source_particles"]
        selection = np.flatnonzero(ids >= first_probe)
        probe_ids = ids[selection]-first_probe
        assert np.array_equal(np.sort(probe_ids), np.arange(len(points)))
        probe_positions = np.column_stack([s[k][selection] for k in "xyz"])
        probe_positions = probe_positions@basis.T+s.attrs["RefPartR"]
        expected = points[["x_m", "global_y_m", "z_m"]].to_numpy()[probe_ids]
        maximum_displacement = float(np.max(np.linalg.norm(probe_positions-expected, axis=1)))
        assert maximum_displacement < 1e-10
    return dict(name=m["name"], passed=True, particles=n,
                charge_C=m["charge_C"], dt_s=m["dt_s"],
                maximum_probe_displacement_m=maximum_displacement,
                maximum_cross_section_excess=max_geometry_excess,
                maximum_arclength_excess_m=max_arclength_excess,
                elapsed_s=m["elapsed_s"], binary_sha256=m["binary_sha256"],
                manifest=str(manifest_path), manifest_sha256=sha(manifest_path))


def main():
    runs = json.loads((OUT/"longitudinal_native_runs.json").read_text())
    points = pd.read_csv(ROOT/"reference/points.csv", float_precision="round_trip")
    results = []
    for run in runs:
        for key in ("source_run", "probe_run"):
            results.append(check(Path(run[key]["manifest"]), points))
    pd.DataFrame(results).to_csv(OUT/"longitudinal_snapshot_checks.csv", index=False)
    result = dict(passed=all(r["passed"] for r in results), cases=len(results),
                  maximum_probe_displacement_m=max(r["maximum_probe_displacement_m"] for r in results),
                  checked="return codes, input/binary/path hashes, N/IDs/Q, finite coordinates/momenta/fields, tube geometry and probe displacement",
                  script_sha256=sha(__file__))
    (OUT/"longitudinal_snapshot_acceptance.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
