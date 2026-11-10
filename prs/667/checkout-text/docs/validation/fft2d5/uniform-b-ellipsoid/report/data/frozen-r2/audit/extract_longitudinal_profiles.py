"""Native all-station end profiles, with independently verified probe removal."""
from pathlib import Path
import hashlib
import json

import h5py
import numpy as np
import pandas as pd
from scipy.constants import epsilon_0

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
G, K = 6.36, 1/(4*np.pi*epsilon_0)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def physical_positions(local):
    u, y, s = np.asarray(local).T
    return np.column_stack([u*np.cos(s/2)-4*np.sin(s/4)**2,
                            y, (2+u)*np.sin(s/2)])


def path_projection(local, vertices):
    # All segments are searched, matching the production nearest-polyline
    # construction. Process small blocks to keep peak memory bounded.
    d = np.diff(vertices, axis=0)
    lengths = np.linalg.norm(d, axis=1)
    cumulative = np.r_[0., np.cumsum(lengths)]
    xyz = physical_positions(local)
    coordinates, tangents = [], []
    for start in range(0, len(xyz), 128):
        positions = xyz[start:start+128]
        delta = positions[:, None, :]-vertices[None, :-1, :]
        fraction = np.clip(np.einsum("kij,ij->ki", delta, d)/lengths[None, :]**2, 0, 1)
        closest = vertices[None, :-1, :]+fraction[:, :, None]*d[None, :, :]
        dist2 = np.sum((positions[:, None, :]-closest)**2, axis=2)
        segment = np.argmin(dist2, axis=1)
        rows = np.arange(len(positions))
        coordinates.append(cumulative[segment]+fraction[rows, segment]*lengths[segment])
        tangents.append(d[segment]/lengths[segment, None])
    return np.concatenate(coordinates), np.concatenate(tangents), cumulative[-1]


def native_fields(manifest, wanted):
    with h5py.File(manifest["h5"]) as f:
        s = f["Step#0"]
        ids = s["id"][:].astype(np.int64)
        if np.array_equal(ids, np.arange(len(ids))):
            rows = wanted
        else:
            order = np.argsort(ids)
            rows = order[wanted]
            assert np.array_equal(ids[rows], wanted)
        fields = np.column_stack([s["E"+k][:][rows] for k in "xyz"])
        refp = np.asarray(s.attrs["RefPartP"])
        angle = np.arctan2(-refp[0], refp[2])
        co, si = np.cos(angle), np.sin(angle)
        basis = np.array([[co, 0., -si], [0., 1., 0.], [si, 0., co]])
        return fields@basis.T, 1+np.dot(refp, refp)


def probe_field(probe_s, target_s, dz, nz, q, gamma2):
    cell = probe_s/dz-.5
    left = np.floor(cell).astype(int)
    fraction = cell-left
    counts = np.bincount(np.r_[left, left+1],
                         weights=np.r_[1-fraction, fraction], minlength=nz)
    density = q*counts/dz
    ghosted = np.r_[0., density, 0.]
    gradient = (ghosted[2:]-ghosted[:-2])/(2*dz)
    field = -K*G/gamma2*gradient
    cell = target_s/dz-.5
    left = np.floor(cell).astype(int)
    fraction = cell-left
    return (1-fraction)*field[left]+fraction*field[left+1]


def main():
    points_path = ROOT/"reference/points.csv"
    points = pd.read_csv(points_path, float_precision="round_trip")
    probe_local = points[["u_m", "y_m", "s_m"]].to_numpy()
    results, checks, provenance = [], [], []
    for nz in (512, 1024, 2048, 4096):
        name = f"xy128-z{nz}-ns5120"
        manifest_path = ROOT/"runs"/name/"manifest.json"
        m = json.loads(manifest_path.read_text())
        pm = json.loads((ROOT/"runs"/(name+"-probes")/"manifest.json").read_text())
        assert m["returncode"] == pm["returncode"] == 0
        source = m["source"]
        cross_path = Path(source["path"]).with_suffix(".npz")
        cross = np.load(cross_path)["cross_section_uy"]
        ic = int(np.argmin(np.sum(cross*cross, axis=1)))
        ns, nc = source["ns"], source["ncross"]
        arclength = -2.5+(np.arange(ns)+.5)*5/ns
        local = np.column_stack([np.tile(cross[ic], (ns, 1)), arclength])
        ids = np.arange(ns)*nc+ic
        vertices = np.loadtxt(m["reference_path"])[:, 1:4]
        source_s, source_t, actual_length = path_projection(local, vertices)
        probe_s, probe_t, _ = path_projection(probe_local, vertices)
        dz = actual_length/nz
        # Verify the independent probe-only deposition at the exact same
        # 43 probe targets before using it to subtract from source profiles.
        pe, pgamma2 = native_fields(pm, np.arange(len(points)))
        measured = np.sum(pe*probe_t, axis=1)
        predicted = probe_field(probe_s, probe_s, dz, nz, source["macrocharge_C"], pgamma2)
        difference = measured-predicted
        for index, point_id in enumerate(points.point_id):
            checks.append(dict(case=name, point_id=point_id,
                               Es_probe_native_V_per_m=measured[index],
                               Es_probe_predicted_V_per_m=predicted[index],
                               difference_V_per_m=difference[index]))
        assert np.max(abs(difference)) < 1e-7
        electric, gamma2 = native_fields(m, ids)
        native = np.sum(electric*source_t, axis=1)
        diagnostic = probe_field(probe_s, source_s, dz, nz, source["macrocharge_C"], gamma2)
        rho = source["source_charge_C"]/(np.pi*.005*.0005*5)
        frame = pd.DataFrame(dict(case=name, mesh_nz=nz,
                                  station=np.arange(ns), particle_id=ids,
                                  cross_index=ic, s_m=arclength,
                                  end_distance_m=2.5-abs(arclength),
                                  u_m=local[:, 0], y_m=local[:, 1],
                                  Es_native_V_per_m=native,
                                  Es_probe_V_per_m=diagnostic,
                                  Es_subtracted_V_per_m=native-diagnostic,
                                  F_s_subtracted_m=(native-diagnostic)/(K*rho),
                                  polyline_s_m=source_s))
        results.append(frame)
        provenance.append(dict(case=name, source_particles=source["source_particles"],
                               cross_index=ic, u_m=cross[ic, 0], y_m=cross[ic, 1],
                               maximum_probe_formula_difference_V_per_m=float(np.max(abs(difference))),
                               source_charge_C=source["source_charge_C"], rho_C_per_m3=rho,
                               actual_path_length_m=actual_length, dz_m=dz,
                               full_run_gamma2=gamma2, probe_run_gamma2=pgamma2,
                               manifest_sha256=sha(manifest_path),
                               reference_path_sha256=sha(m["reference_path"]),
                               cross_section_sha256=sha(cross_path)))
    pd.concat(results, ignore_index=True).to_csv(OUT/"native_longitudinal_profiles.csv", index=False)
    check_frame = pd.DataFrame(checks)
    check_frame.to_csv(OUT/"probe_longitudinal_formula_checks.csv", index=False)
    output = dict(scope="native source-station fields projected onto nearest-polyline tangent; diagnostic charge removed by verified 1D CIC",
                  profile_rows=sum(len(r) for r in results),
                  maximum_probe_formula_difference_V_per_m=float(check_frame.difference_V_per_m.abs().max()),
                  field_units="V/m; F_s=E_s/(k*rho) in metre",
                  interpolation="native central difference plus longitudinal CIC; actual full-run gamma for subtraction",
                  script_sha256=sha(__file__), points_sha256=sha(points_path), cases=provenance)
    (OUT/"native_longitudinal_profiles_provenance.json").write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({k:v for k,v in output.items() if k!="cases"}, indent=2))


if __name__ == "__main__":
    main()
