"""Independent 1D CIC audit of the actual circular-source/polyline projection.

This reproduces geometry, longitudinal deposition, central differences and
linear gathering, without running OPALX or reading its fields. It quantifies
source/path sampling noise; it is not an independent implementation of the
three-dimensional physics reference.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
A, C, R, L, G = .005, .0005, 2., 5., 6.36


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry(path):
    data = np.loadtxt(path)
    nodes = data[:, 0] - 4.
    vertices = data[:, 1:4]
    length = np.linalg.norm(np.diff(vertices, axis=0), axis=1)
    cumulative = np.r_[0., np.cumsum(length)]
    return nodes, length, cumulative


def project(local, geo):
    """Nearest of the three adjoining circle chords; checked against full search."""
    nodes, lengths, cumulative = geo
    local = np.asarray(local)
    u, y, s = local.T
    base = np.searchsorted(nodes, s) - 1
    ids = np.clip(base[:, None] + np.array([-1, 0, 1]), 0, len(nodes)-2)
    mid_angle = (nodes[ids]+nodes[ids+1])/(2*R)
    half_angle = (nodes[ids+1]-nodes[ids])/(2*R)
    delta = s[:, None]/R-mid_angle
    t = (R+u[:, None])*np.sin(delta)+lengths[ids]/2
    tc = np.clip(t, 0, lengths[ids])
    distance2 = ((R+u[:, None])*np.cos(delta)-R*np.cos(half_angle))**2+(t-tc)**2
    choose = np.argmin(distance2, axis=1)
    rows = np.arange(len(local))
    return cumulative[ids[rows, choose]]+tc[rows, choose]


def source_coordinates(ns, cross, geo):
    values = []
    for start in range(0, ns, 64):
        s = -L/2+(np.arange(start, min(start+64, ns))+.5)*L/ns
        local = np.column_stack([np.tile(cross, (len(s), 1)),
                                 np.repeat(s, len(cross))])
        values.append(project(local, geo))
    return np.concatenate(values)


def triangular_primitive(x, dz):
    x = np.asarray(x)
    return np.where(x <= -dz, 0., np.where(x <= 0, (x+dz)**2/(2*dz),
                    np.where(x < dz, dz/2+x-x*x/(2*dz), dz)))


def audit(ns, nz, cross, geo, targets, scales):
    _, _, cumulative = geo
    actual_length = cumulative[-1]
    compression = actual_length/8.
    dz = actual_length/nz
    source_s = source_coordinates(ns, cross, geo)
    cell = source_s/dz-.5
    left = np.floor(cell).astype(int)
    fraction = cell-left
    counts = np.bincount(np.r_[left, left+1],
                         weights=np.r_[1-fraction, fraction], minlength=nz)
    n = ns*len(cross)
    relative_line = counts/(n/L*dz)
    centres = (np.arange(nz)+.5)*dz
    # Exact CIC deposition of a continuous, flat source on the affine-
    # compressed longitudinal coordinate supplies the finite-end baseline.
    low, high = (4.-L/2)*compression, (4.+L/2)*compression
    ideal = (triangular_primitive(high-centres, dz)-
             triangular_primitive(low-centres, dz))/(compression*dz)
    def gradient(values):
        ghosted = np.r_[0., values, 0.]
        return (ghosted[2:]-ghosted[:-2])/(2*dz)
    # F=E/(k*rho). lambda/rho=pi*a*c. gamma correction differs from one
    # by <1e-6 for this beta=.001 benchmark and is omitted in this audit.
    field = -G*np.pi*A*C*gradient(relative_line)
    ideal_field = -G*np.pi*A*C*gradient(ideal)
    noise = field-ideal_field
    target_s = project(targets[["u_m", "y_m", "s_m"]].to_numpy(), geo)
    pcell = target_s/dz-.5
    plef = np.floor(pcell).astype(int)
    pfrac = pcell-plef
    gathered = (1-pfrac)*field[plef]+pfrac*field[plef+1]
    ideal_gathered = (1-pfrac)*ideal_field[plef]+pfrac*ideal_field[plef+1]
    gathered_noise = gathered-ideal_gathered
    bulk = (centres>low+.05) & (centres<high-.05)
    detail = targets[["point_id", "label", "u_m", "y_m", "s_m", "end_distance_m"]].copy()
    detail["ns"] = ns
    detail["nz"] = nz
    detail["F_s_sampling_m"] = gathered
    detail["F_s_ideal_flat_m"] = ideal_gathered
    detail["F_s_noise_m"] = gathered_noise
    detail["noise_over_tangential_scale"] = gathered_noise/scales["tangential"]
    detail["noise_over_transverse_scale"] = gathered_noise/scales["radial"]
    summary = dict(ns=ns, nz=nz, cross_points=len(cross), source_particles=n,
                   dz_m=dz, source_spacing_m=L/ns,
                   actual_path_length_m=actual_length,
                   maximum_bulk_relative_line_density_difference=float(np.max(np.abs(relative_line[bulk]-ideal[bulk]))),
                   maximum_bulk_noise_over_tangential_scale=float(np.max(abs(noise[bulk]))/scales["tangential"]),
                   rms_bulk_noise_over_tangential_scale=float(np.sqrt(np.mean(noise[bulk]**2))/scales["tangential"]),
                   maximum_probe_noise_over_tangential_scale=float(np.max(abs(gathered_noise))/scales["tangential"]),
                   maximum_probe_noise_over_transverse_scale=float(np.max(abs(gathered_noise))/scales["radial"]),
                   maximum_probe_ideal_flat_field_m=float(np.max(abs(ideal_gathered))))
    return summary, detail


def main():
    source_path = ROOT/"sources/tube-ns2560-nr16-np64.npz"
    path_file = ROOT/"sources/path-step0.02.dat"
    points_file = ROOT/"reference/points.csv"
    cross = np.load(source_path)["cross_section_uy"]
    geo = geometry(path_file)
    targets = pd.read_csv(points_file, float_precision="round_trip")
    reference = json.loads((ROOT/"reference/acceptance.json").read_text())
    scales = reference["scales_div_k_rho_m"]
    summaries, details = [], []
    for ns, nz in [(2560, 512), (2560, 1024), (2560, 2048),
                   (2560, 4096), (5120, 4096), (10240, 4096)]:
        row, detail = audit(ns, nz, cross, geo, targets, scales)
        summaries.append(row)
        details.append(detail)
    table = pd.DataFrame(summaries)
    table.to_csv(OUT/"longitudinal_sampling_summary.csv", index=False)
    pd.concat(details, ignore_index=True).to_csv(OUT/"longitudinal_sampling_probes.csv", index=False)
    provenance = dict(scope="Independent geometry/CIC longitudinal sampling audit, no OPALX fields",
                      gamma_correction="omitted; below 1e-6 relative for beta=.001",
                      tangential_characteristic_scale_m=scales["tangential"],
                      transverse_characteristic_scale_m=scales["radial"],
                      bulk_definition="more than 50 mm from either hard end",
                      baseline="exact CIC integral of continuous flat line charge on affine-compressed path coordinate",
                      source_hashes={str(p):sha(p) for p in [__file__, source_path, path_file, points_file]})
    (OUT/"longitudinal_sampling_provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
