"""Independent source/diagnostic/metric checks for root consolidation.

Reads both codes' archived native outputs and root CSVs. Writes own audit.
Does not invoke or modify either solver or parent analysis.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def arg_value(argv, flag):
    return argv[argv.index(flag) + 1]


def main():
    points = pd.read_csv(ROOT / "common/probes.csv", float_precision="round_trip")
    shared = pd.read_csv(ROOT / "analysis/fields.csv", float_precision="round_trip")
    summary = pd.read_csv(ROOT / "analysis/summary.csv", float_precision="round_trip")
    own = pd.read_csv(OUT / "independent-probe-fields.csv", float_precision="round_trip")
    own_metrics = pd.read_csv(OUT / "independent-longitudinal-metrics.csv", float_precision="round_trip")
    checks = []
    opal = shared[shared.code == "OPALX"]
    joined = own.merge(opal, on=["case", "point_id"], suffixes=("_independent", "_shared"), validate="one_to_one")
    assert len(joined) == len(own)
    max_es_difference = float(np.max(abs(joined.Ez_Vpm - joined.Es_V_m)))
    assert max_es_difference < 1e-9
    metric_join = own_metrics.merge(summary[summary.code == "OPALX"], on="case", validate="one_to_one")
    max_metric_difference = float(np.max(abs(metric_join.physical_onaxis_max_error_percent - metric_join.max_axis_error_percent)))
    assert max_metric_difference < 1e-10
    max_native_metric_difference = float(np.max(abs(metric_join.native_model_max_error_percent - metric_join.max_axis_native_formula_error_percent)))
    assert max_native_metric_difference < 1e-10
    py_raw = {}
    for directory in sorted((ROOT / "pyorbit/runs").glob("*")):
        paths = sorted(directory.glob("manifest-rank*.json"))
        if not paths:
            continue
        ms = [json.loads(p.read_text()) for p in paths]
        m = ms[0]
        assert len(paths) == m["mpi_size"]
        assert set(x["rank"] for x in ms) == set(range(m["mpi_size"]))
        assert sum(x["source_particles_local"] for x in ms) == m["source_particles_global"]
        assert sum(x["probe_count_local"] for x in ms) == len(points)
        for x in ms:
            assert x["source_sha256"] == sha(arg_value(x["argv"], "--source"))
            assert x["probe_input_sha256"] == sha(arg_value(x["argv"], "--probes"))
            harness = Path(x["argv"][0])
            if x["harness_sha256"] != sha(harness):
                harness = ROOT / "pyorbit/harness-snapshots" / ("run_native-" + x["harness_sha256"] + ".py")
            assert x["harness_sha256"] == sha(harness)
            assert x["zero_probe_weights"] and x["probe_positions_unchanged"]
            assert x["kinetic_energy_GeV"] == .4
            assert x["full_length_m"] == 10.
            assert x["beam_radius_m"] == .005
            assert x["pipe_radius_m"] == .020
            assert x["kick_length_m"] == 1.
            assert np.isclose(x["source_number"], 1e14, rtol=1e-12, atol=0)
            if "native_weight_sum_global" in x:
                assert np.isclose(x["native_weight_sum_global"], 1e14, rtol=1e-12, atol=0)
                assert x["native_source_count_global"] == x["source_particles_global"]
                assert x["native_total_count_global"] == x["source_particles_global"] + len(points) + 6
        csvs = sorted(directory.glob("probes-rank*.csv"))
        d = pd.concat([pd.read_csv(p, float_precision="round_trip") for p in csvs], ignore_index=True)
        d = d.rename(columns={"probe_id": "point_id"})
        assert len(d) == len(points)
        assert not d.point_id.duplicated().any()
        cmp = d.merge(points, on="point_id", suffixes=("_native", "_input"), validate="one_to_one")
        for key in ["x_m", "y_m", "s_m"]:
            assert np.max(abs(cmp[key + "_native"] - cmp[key + "_input"])) < 1e-14
        assert np.isfinite(d[["Es_V_m", "Ex_V_m", "Ey_V_m", "dE_GeV"]]).all().all()
        assert np.max(abs(d.Es_V_m - d.dE_GeV * 1e9 / m["kick_length_m"])) < 1e-9
        r = np.hypot(d.x_m, d.y_m)
        expected_g = 1 + 2 * np.log(.020 / .005) - (r / .005)**2
        assert np.max(abs(d.g - expected_g)) < 1e-13
        expected_base = 1e14 * 1.602176634e-19 / 5.**2 / (4 * np.pi * 8.8541878128e-12 * m["gamma"]**2)
        sign = np.where(abs(d.s_m) < 5., np.sign(d.s_m), 0.)
        assert np.max(abs(d.Es_analytic_SI_V_m - sign * expected_base * expected_g)) < 1e-8
        mask = (abs(d.s_m) >= 1. - 1e-12) & (abs(d.s_m) <= 4. + 1e-12)
        global_base = 1e14 * 1.602176634e-19 / 5.**2 / (
            4 * np.pi * 8.8541878128e-12 * (1 + .4 / .93827208816)**2)
        analytic = sign * global_base * expected_g
        axis_ids = set(points[points.kind == "axis"].point_id)
        axis_mask = mask & d.point_id.isin(axis_ids)
        common = shared[shared.case == directory.name]
        if len(common):
            j = d.merge(common, on="point_id", suffixes=("_native", "_shared"), validate="one_to_one")
            assert len(j) == len(points)
            assert np.max(abs(j.Es_V_m_native - j.Es_V_m_shared)) < 1e-9
            numerical_max = float(np.max(abs(d.Es_V_m[axis_mask] / analytic[axis_mask] - 1)) * 100)
            stated = summary[summary.case == directory.name].iloc[0].max_axis_error_percent
            assert abs(numerical_max - stated) < 1e-10
        py_raw[directory.name] = d
        checks.append(dict(case=directory.name, native_points=len(d), mpi_size=m["mpi_size"],
                           source_particles=m["source_particles_global"],
                           native_weight_count_checks_present="native_weight_sum_global" in m,
                           actual_source_harness_probe_hashes_pass=True, geometry_matches_common_input=True,
                           energy_to_field_conversion_pass=True, radial_coefficient_pass=True,
                           shared_csv_checked=bool(len(common)),
                           output_csv_hashes={str(p): sha(p) for p in csvs}))
    comparisons = []
    for first, second in [
        ("slice-512x512x128-r1", "slice-512x512x128-r2"),
        ("slice-512x512x128-nativeaudit-r1", "slice-512x512x128-nativeaudit-r2"),
        ("slice-512x512x128-r1", "slice-512x512x128-nativeaudit-r1"),
    ]:
        if first not in py_raw or second not in py_raw:
            continue
        j = py_raw[first].merge(py_raw[second], on="point_id", suffixes=("_r1", "_r2"), validate="one_to_one")
        maximum = float(np.max(abs(j.Es_V_m_r1 - j.Es_V_m_r2)))
        scale = float(np.max(abs(j.Es_V_m_r1)))
        assert maximum / scale < 1e-10
        comparisons.append(dict(cases=[first, second], max_absolute_Es_difference_Vpm=maximum,
                                max_relative_characteristic_scale=maximum / scale, all_targets_compared=len(j)))
    result = dict(
        opalx_native_pairs=len(own_metrics), opalx_native_points=len(own),
        opalx_max_shared_field_difference_Vpm=max_es_difference,
        opalx_max_physical_metric_difference_percent=max_metric_difference,
        opalx_max_native_metric_difference_percent=max_native_metric_difference,
        pyorbit_cases=checks, pyorbit_mpi_comparison=comparisons[0] if comparisons else None,
        pyorbit_mpi_and_harness_comparisons=comparisons,
        checks_pass=True, script_sha256=sha(__file__),
        shared_fields_sha256=sha(ROOT / "analysis/fields.csv"),
        shared_summary_sha256=sha(ROOT / "analysis/summary.csv"),
    )
    (OUT / "consolidation-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
