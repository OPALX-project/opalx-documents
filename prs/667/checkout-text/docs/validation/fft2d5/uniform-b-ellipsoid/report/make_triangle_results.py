#!/usr/bin/env python3
"""Rebuild triangular-pipe tables/figures from verified local snapshots only.

No solver, installation, fitting, network or external-path access is performed.
Selections explicitly identify the nominal runs and each independent control.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/opalx-triangle-report-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/opalx-triangle-report-cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data/triangle-pipe"
OUT = ROOT / "figures"
GENERATED = ROOT / "generated"

plt.rcParams.update({
    "font.family": "serif", "mathtext.fontset": "stix", "font.size": 9,
    "axes.titlesize": 10, "axes.labelsize": 9, "legend.fontsize": 8,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "pdf.fonttype": 42,
    "ps.fonttype": 42, "axes.linewidth": .65, "lines.linewidth": 1.2,
    "savefig.facecolor": "white",
})


def verify():
    entries = json.loads((DATA / "snapshot-provenance.json").read_text())["sources"]
    for item in entries:
        path = ROOT / item["snapshot"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Triangle evidence changed: {path}")
    print(f"Verified {len(entries)} triangular-pipe evidence snapshots.")


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf", metadata={"Creator": "OPALX validation", "CreationDate": None, "ModDate": None})
    fig.savefig(OUT / f"{name}.png", dpi=300)
    plt.close(fig)


def decorate(ax):
    ax.grid(alpha=.17, linewidth=.5)
    ax.tick_params(direction="in", which="both", top=True, right=True)
    ax.axhline(0, color=".55", lw=.6, zorder=0)


def subset(fields, case, kind):
    q = fields[(fields.case == case) & (fields.kind == kind)].copy()
    if q.empty:
        raise ValueError(f"No {kind} data for selected case {case}")
    return q.sort_values(["s_m", "x_m", "y_m"])


def longitudinal_figure(fields, config, case, name="triangle-pipe-fields"):
    fig, axes = plt.subplots(2, 1, figsize=(6.65, 3.65), sharex=True,
                             gridspec_kw={"height_ratios": [1.6, 1]})
    s = np.linspace(-4.5, 4.5, 901)
    axes[0].plot(s, case.longitudinal_field(s)/1000, "k--", lw=1.5,
                 label="Analytic round pipe, on axis", zorder=5)
    handles = [Line2D([], [], color="k", ls="--", label="Analytic round pipe, on axis")]
    for entry in config["primary"]:
        q = subset(fields, entry["case"], "axis")
        q = q[q.s_m.abs() <= 4.5]
        color, marker = entry["color"], entry["marker"]
        axes[0].plot(q.s_m, q.Es_V_m/1000, color=color, marker=marker,
                     ms=3.0, mfc="white", mew=.6, lw=.9, zorder=3)
        a = q[q.acceptance]
        # Separate branches avoid drawing a line through the excluded cusp.
        for branch in [-1, 1]:
            b = a[np.sign(a.s_m) == branch]
            axes[1].plot(b.s_m, b.error_axis_scale_percent, color=color,
                         marker=marker, ms=2.6, mfc="white", mew=.55, lw=.8)
        handles.append(Line2D([], [], color=color, marker=marker, mfc="white",
                              ms=3.5, label=entry["label"]))
    for ax in axes:
        for left, right in [(-4.5, -4), (-1, 1), (4, 4.5)]:
            ax.axvspan(left, right, color=".94", lw=0, zorder=-5)
        decorate(ax)
    axes[0].set_ylabel(r"$E_s$ [kV/m]")
    axes[0].set_title("(a) Frozen longitudinal field", loc="left", pad=5)
    axes[1].set_title("(b) Difference from the physical analytic field", loc="left", pad=5)
    axes[1].set_ylabel(r"$(E_s-E_s^{\rm analytic})/E_*$ [%]")
    axes[1].set_xlabel(r"Position from bunch centre $s$ [m]")
    axes[1].axhspan(-1, 1, facecolor="#cccccc", alpha=.35, lw=0, zorder=-2)
    axes[1].set_xlim(-4.5, 4.5)
    axes[1].set_xticks([-4, -2, 0, 2, 4])
    lo, hi = axes[0].get_ylim()
    ymax = max(abs(lo), abs(hi), 1)
    axes[0].set_ylim(-ymax, ymax)
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, 1.005),
               ncol=2, frameon=False, columnspacing=1.4)
    fig.subplots_adjust(left=.11, right=.98, top=.81, bottom=.12, hspace=.43)
    save(fig, name)


def controls_figure(fields, summary, config, case, name="triangle-pipe-controls"):
    fig, axes = plt.subplots(1, 2, figsize=(6.65, 2.75))
    x = np.linspace(-case.beam_radius_m, case.beam_radius_m, 401)
    axes[0].plot(x/case.beam_radius_m,
                 case.longitudinal_field(np.full_like(x, 2.5), np.abs(x))/1000,
                 "k--", lw=1.5, zorder=5, label="Analytic round pipe")
    for entry in config["primary"]:
        q = subset(fields, entry["case"], "radial")
        q = q[np.isclose(q.s_m, 2.5)].sort_values("x_m")
        assert len(q) >= 3
        axes[0].plot(q.x_m/case.beam_radius_m, q.Es_V_m/1000,
                     color=entry["color"], marker=entry["marker"], ms=2.7,
                     mfc="white", mew=.55, lw=.85, label=entry["label"])
    axes[0].set_title(r"(a) Radial dependence at $s=+2.5$ m", loc="left")
    axes[0].set_xlabel(r"$x/a$ at $y=0$")
    axes[0].set_ylabel(r"$E_s$ [kV/m]")
    axes[0].set_xlim(-1.02, 1.02)
    axes[0].set_ylim(bottom=0)
    axes[0].set_xticks([-1, -.5, 0, .5, 1])
    for entry in config["mesh_series"]:
        q = summary.set_index("case").loc[entry["cases"]]
        axes[1].plot(q[entry.get("x", "nx")], q[entry["metric"]],
                     color=entry["color"], marker=entry["marker"], ms=4,
                     mfc="white", mew=.7, lw=1, label=entry["label"])
    axes[1].axhline(1, color=".35", ls=":", lw=.9)
    axes[1].set_title("(b) Selected numerical controls", loc="left")
    axes[1].set_xlabel(config.get("mesh_xlabel", r"Transverse grid $N_x=N_y$"))
    axes[1].set_ylabel("Maximum on-axis error [%]")
    axes[1].set_xticks([64, 128, 256, 512])
    axes[1].set_ylim(bottom=config.get("mesh_ymin", 0))
    axes[1].legend(loc="best", fontsize=7.4, frameon=False)
    axes[0].legend(loc="lower center", fontsize=7.4, frameon=False)
    for ax in axes:
        decorate(ax)
    fig.subplots_adjust(left=.085, right=.985, top=.87, bottom=.20, wspace=.36)
    save(fig, name)


def make_table(summary, config, name="triangle-results"):
    def number(value):
        decimals = max(0, 2-int(np.floor(np.log10(abs(value))))) if value else 0
        return f"{value:.{decimals}f}"
    rows = [r"\begin{tabular}{llrr}", r"\toprule",
            r"Code / control & Mesh & Axis [\%] & Radial set [\%] \\", r"\midrule"]
    lookup = summary.set_index("case")
    for entry in config["table_cases"]:
        q = lookup.loc[entry["case"]]
        mesh = (f"${int(q.nx)}^3$" if q.nx == q.ny == q.nz
                else f"${int(q.nx)}^2\\!\\times\\!{int(q.nz)}$")
        rows.append(entry["label_tex"] + " & " + mesh + " & "
                    + number(q.max_axis_error_percent) + " & " + number(q.max_radial_local_error_percent)
                    + r" \\")
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    (GENERATED / f"{name}.tex").write_text("\n".join(rows) + "\n")


def configuration(selection):
    primary = selection["primary_cases"]
    return {
        "primary": [
            {"case": primary["OPALX"], "label": "OPALX CIRCULAR", "color": "#0072B2", "marker": "o"},
            {"case": primary["PyORBIT_slice"], "label": "PyORBIT slices", "color": "#D55E00", "marker": "s"},
            {"case": primary["PyORBIT_Baartman"], "label": "PyORBIT Baartman", "color": "#009E73", "marker": "^"},
        ],
        "mesh_series": [
            {"cases": selection["mesh_series"]["pyorbit_transverse_fixed_NZ128"],
             "metric": "max_axis_error_percent", "color": "#D55E00", "marker": "s",
             "label": r"PyORBIT slices, $N_z=128$, 16 rings"},
            {"cases": selection["mesh_series"]["opalx_matched_dense_source"],
             "metric": "max_axis_error_percent", "color": "#0072B2", "marker": "o",
             "label": "OPALX, matched finer source"},
        ],
        "table_cases": [
            {"case": selection["mesh_series"]["opalx_matched_dense_source"][0], "label_tex": "OPALX, matched source"},
            {"case": primary["OPALX"], "label_tex": "OPALX, refined mesh"},
            {"case": primary["PyORBIT_slice"], "label_tex": "PyORBIT, slices"},
            {"case": primary["PyORBIT_Baartman"], "label_tex": "PyORBIT, Baartman"},
        ],
    }


def main():
    verify()
    selection = json.loads((DATA / "analysis/selection.json").read_text())
    config = configuration(selection)
    fields = pd.read_csv(DATA / "analysis/fields.csv", float_precision="round_trip")
    summary = pd.read_csv(DATA / "analysis/summary.csv", float_precision="round_trip")
    assert fields.acceptance.dtype == bool
    assert not summary.case.duplicated().any()
    spec = importlib.util.spec_from_file_location("triangle_analytic_snapshot", DATA / "analytic-audit/analytic.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    case = module.Benchmark()
    expected = case.longitudinal_field(fields.s_m.to_numpy(), fields.r_m.to_numpy())
    assert np.allclose(expected, fields.analytic_Es_V_m, rtol=1e-13, atol=1e-10, equal_nan=True)
    for _, row in summary.iterrows():
        q = fields[(fields.case == row.case) & fields.acceptance & (fields.kind == "axis")]
        error = 100*np.max(np.abs(q.Es_V_m/q.analytic_Es_V_m-1))
        assert np.isclose(error, row.max_axis_error_percent, rtol=1e-11, atol=1e-10)
    longitudinal_figure(fields, config, case)
    controls_figure(fields, summary, config, case)
    make_table(summary, config)
    print("Rebuilt triangular-pipe figures/tables from archived native results.")


if __name__ == "__main__":
    main()
