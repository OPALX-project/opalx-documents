#!/usr/bin/env python3
"""Offline before/after comparison for the explicit pointwise pipe model."""
from dataclasses import replace
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

import make_triangle_results as plots

ROOT = Path(__file__).resolve().parent
DATA = ROOT/"data/triangle-fixed"
BEFORE = ROOT/"data/triangle-pipe"
SELECT = {"before": "source16384", "after": "fixed256",
          "slice": "slice-repeat-r1", "rb": "rb-repeat-r1"}


def verify():
    plots.verify()
    entries = json.loads((DATA/"snapshot-provenance.json").read_text())["sources"]
    for item in entries:
        path = ROOT/item["snapshot"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Pointwise-pipe evidence changed: {path}")
    print(f"Verified {len(entries)} pointwise-pipe evidence snapshots.")
    selection = json.loads((DATA/"analysis/selection.json").read_text())
    assert selection["before"]["case"] == SELECT["before"]
    assert selection["primary_cases"] == {"OPALX": SELECT["after"], "PyORBIT_slice": SELECT["slice"], "PyORBIT_Baartman": SELECT["rb"]}


def load():
    spec = importlib.util.spec_from_file_location("fixed_triangle_analytic", BEFORE/"analytic-audit/analytic.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    case = module.Benchmark()
    read = lambda p: pd.read_csv(p, float_precision="round_trip")
    old_fields = read(BEFORE/"analysis/fields.csv")
    new_fields = read(DATA/"analysis/fields.csv")
    gates = json.loads((DATA/"checks/gates.json").read_text())
    assert set(new_fields.loc[new_fields.code == "OPALX", "binary_sha256"]) == {gates["binary"]["after"]["sha256"]}
    before_manifest = json.loads((BEFORE/"opalx/runs"/SELECT["before"]/"manifest.json").read_text())
    assert before_manifest["binary_sha256"] == gates["binary"]["before"]["sha256"]
    for b,index in new_fields.groupby("pipe_radius_m").groups.items():
        ref = replace(case, pipe_radius_m=b)
        q = new_fields.loc[index]
        expected = ref.longitudinal_field(q.s_m.to_numpy(), q.r_m.to_numpy())
        assert np.allclose(q.analytic_Es_V_m, expected, rtol=1e-13, atol=1e-10, equal_nan=True)
    fields = pd.concat([old_fields, new_fields], ignore_index=True)
    summary = pd.concat([read(BEFORE/"analysis/summary.csv"), read(DATA/"analysis/summary.csv")], ignore_index=True)
    assert fields.acceptance.dtype == bool
    assert not summary.case.duplicated().any()
    assert set(SELECT.values()).issubset(set(fields.case))
    for name,g in new_fields.groupby("case"):
        row = summary.set_index("case").loc[name]
        for kind,column in [("axis", "max_axis_error_percent"), ("radial", "max_radial_local_error_percent")]:
            q = g[(g.kind == kind) & g.acceptance]
            error = 100*np.max(np.abs(q.Es_V_m/q.analytic_Es_V_m-1))
            assert np.isclose(error, row[column], rtol=1e-11, atol=1e-10)
    source_hashes = [set(fields.loc[fields.case == SELECT[k], "source_sha256"]) for k in ["before", "after"]]
    assert len(source_hashes[0]) == 1 and source_hashes[0] == source_hashes[1]
    for _, row in read(DATA/"analysis/controls.csv").iterrows():
        a = fields[(fields.case == row.case_a) & fields.acceptance]
        b = fields[(fields.case == row.case_b) & fields.acceptance]
        q = a.merge(b, on="point_id", suffixes=("_a", "_b"), validate="one_to_one")
        assert len(q) == row.points
        difference = 100*np.max(np.abs((q.Es_V_m_b-q.Es_V_m_a)/q.axis_scale_V_m_a))
        assert np.isclose(difference, row.max_change_axis_scale_percent, rtol=1e-10, atol=1e-10)
    return fields, summary, case


def verify_gates():
    gates = json.loads((DATA/"checks/gates.json").read_text())
    for unit in gates["units"]:
        path = DATA/"checks"/(unit["name"]+".xml")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == unit["xml_sha256"]
        tests = list(ET.parse(path).getroot().iter("testcase"))
        passed = sum(t.find("failure") is None and t.find("skipped") is None for t in tests)
        skipped = sum(t.find("skipped") is not None for t in tests)
        assert passed == unit["passed"] and skipped == unit["skipped"]
    assert sum(u["passed"] for u in gates["units"]) == gates["total_passed"] == 100
    assert sum(u["skipped"] for u in gates["units"]) == gates["total_skipped"] == 1
    assert gates["native_rank2_guard"]["expected_rejection"]
    assert json.loads((DATA/"audit-api/checks.json").read_text())["checks_pass"]
    regression = json.loads((DATA/"regression-checks/regression-controls.json").read_text())
    assert regression["correct"]["passed"]
    assert regression["correct"]["maximum_relative_field_error"] < .01
    assert regression["correct"]["maximum_wall_absolute_field_V_per_m"] < 1e-4
    assert regression["legacy_control"]["actual_validator_exit"] == 1
    assert regression["probe_charge_cancellation_pass"]
    legacy = json.loads((DATA/"checks/legacy-regression-checks.json").read_text())
    assert legacy["all_passed"] and not legacy["case_files_modified"]


def configuration():
    original = json.loads((BEFORE/"analysis/selection.json").read_text())
    return {
        "mesh_ymin": -0.08,
        "primary": [
            {"case": SELECT["before"], "label": "OPALX CIRCULAR (before)", "color": "#777777", "marker": "x"},
            {"case": SELECT["after"], "label": "OPALX CIRCULAR_UNIFORM", "color": "#0072B2", "marker": "o"},
            {"case": SELECT["slice"], "label": "PyORBIT slices", "color": "#D55E00", "marker": "s"},
            {"case": SELECT["rb"], "label": "PyORBIT Baartman", "color": "#009E73", "marker": "^"},
        ],
        "mesh_series": [
            {"cases": ["fixed64", "fixed128", "fixed256"], "metric": "max_axis_error_percent",
             "color": "#0072B2", "marker": "o", "label": r"OPALX uniform, $N_x=N_y=N_z$"},
            {"cases": original["mesh_series"]["pyorbit_transverse_fixed_NZ128"],
             "metric": "max_axis_error_percent", "color": "#D55E00", "marker": "s",
             "label": r"PyORBIT slices, $N_z=128$, 16 rings"},
        ],
        "table_cases": [
            {"case": SELECT["before"], "label_tex": "OPALX CIRCULAR, before"},
            {"case": "fixed128", "label_tex": "OPALX uniform"},
            {"case": SELECT["after"], "label_tex": "OPALX uniform, fine"},
            {"case": SELECT["slice"], "label_tex": "PyORBIT, slices"},
            {"case": SELECT["rb"], "label_tex": "PyORBIT, Baartman"},
        ],
    }


def main():
    verify()
    verify_gates()
    fields, summary, case = load()
    config = configuration()
    plots.longitudinal_figure(fields, config, case, name="triangle-pipe-fixed-fields")
    plots.controls_figure(fields, summary, config, case, name="triangle-pipe-fixed-controls")
    plots.make_table(summary, config, name="triangle-fixed-results")
    print("Rebuilt pointwise-pipe before/after figures and table from local snapshots.")


if __name__ == "__main__":
    main()
