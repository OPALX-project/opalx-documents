#!/usr/bin/env python3
"""Rebuild report figures using only the archived figure-inputs CSV files.

No tracking runs, fitted parameters or external data access are performed.
Run with the OPALX Python environment from any working directory.
"""
from pathlib import Path
import json
import hashlib
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/opalx-uniform-b-report-mpl")
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "figure-inputs"
OUT = ROOT / "figures"
COMPLETED = ROOT / "data" / "10pc-completed"
DIRS = ("radial", "tangential", "vertical")
TITLES = (r"Radial $r$", r"Tangential $s$", r"Vertical $y_{\rm OPALX}$")
COLORS = ("#333333", "#0072B2", "#009E73", "#D55E00")
plt.rcParams.update({
    "font.family": "serif", "mathtext.fontset": "stix", "font.size": 9,
    "axes.titlesize": 10, "axes.labelsize": 9, "legend.fontsize": 8.5,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5, "pdf.fonttype": 42,
    "ps.fonttype": 42, "axes.linewidth": .65, "lines.linewidth": 1.2,
    "savefig.facecolor": "white",
})


def load(name):
    return pd.read_csv(DATA / name)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=220)
    plt.close(fig)


def decorate(ax, *, angle=True, zero=False):
    ax.grid(alpha=.17, linewidth=.5)
    ax.tick_params(direction="in", which="both", top=True, right=True)
    if angle:
        ax.set_xlim(0, 180)
        ax.set_xticks([0, 90, 180])
    if zero:
        lo, hi = ax.get_ylim()
        ax.set_ylim(min(0, lo), hi)


def angle(frame):
    return np.rad2deg(frame.phase_model_rad)


def curve_pair(ax, x, actual, model, color, marker="o"):
    # Separate solid observations from dashed independent prediction in every panel.
    ax.plot(x, actual, color=color, lw=1.15, marker=marker, markevery=12,
            markersize=2.2, markeredgewidth=.35, markerfacecolor="white")
    ax.plot(x, model, color=color, ls=(0, (4, 2)), lw=1.15)


def convention_handles():
    return [Line2D([], [], color="black", marker="o", markersize=3,
                   markerfacecolor="white", label="OPALX"),
            Line2D([], [], color="black", ls="--", label="Independent ellipsoid")]


def baseline():
    data = load("baseline-all-steps.csv")
    cases = [("final-zero", "Space charge off"), ("final-q0p1", "0.1 pC"),
             ("final-q0p3", "0.3 pC"), ("fft2d5-example-q1", "1 pC")]
    fig, axes = plt.subplots(2, 3, figsize=(6.65, 4.15), sharex=True,
                             gridspec_kw={"height_ratios": [1.4, 1]})
    for (case, label), color in zip(cases, COLORS):
        f = data[data.case == case]
        for j, direction in enumerate(DIRS):
            curve_pair(axes[0, j], angle(f), f[f"sigma_{direction}_m"] * 1e3,
                       f[f"model_sigma_{direction}_m"] * 1e3, color)
            axes[1, j].plot(angle(f), f[f"{direction}_relative_error"] * 100,
                            color=color)
    for j, title in enumerate(TITLES):
        axes[0, j].set_title(title)
        axes[0, j].set_ylabel("RMS size [mm]" if j == 0 else "")
        axes[1, j].set_ylabel("Size error [%]" if j == 0 else "")
        axes[1, j].set_xlabel("Orbit angle [deg]")
        axes[0, j].set_ylim(bottom=0)
        axes[1, j].axhline(0, color=".5", lw=.5)
        axes[1, j].set_ylim(-1.05, 1.05)
        for i in range(2):
            decorate(axes[i, j])
    handles = [Line2D([], [], color=c, label=l) for (_, l), c in zip(cases, COLORS)]
    fig.legend(handles=handles, loc="upper center", ncol=4, bbox_to_anchor=(.5, 1.005), frameon=False)
    fig.legend(handles=convention_handles(), loc="upper center", ncol=2,
               bbox_to_anchor=(.5, .947), frameon=False)
    fig.subplots_adjust(top=.82, bottom=.11, left=.085, right=.965, hspace=.20, wspace=.36)
    save(fig, "baseline-rms")


def convergence():
    f = load("baseline-convergence.csv")
    x = np.arange(len(f)); width = .23
    fig, ax = plt.subplots(figsize=(6.65, 2.6))
    for j, (direction, color) in enumerate(zip(DIRS, [COLORS[1], COLORS[3], COLORS[2]])):
        values = f[f"{direction}_max_relative_change"].to_numpy() * 100
        bars = ax.bar(x + (j - 1) * width, values, width, color=color,
                      label=TITLES[j], edgecolor="white", linewidth=.4)
        for bar, value in zip(bars, values):
            ax.annotate(f"{value:.3f}", (bar.get_x() + bar.get_width()/2, value),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x, ["Transverse mesh ×2", "Longitudinal mesh ×2", "Time step /2", "Particle count ×2"])
    ax.set_ylabel("Maximum RMS change [%]")
    ax.set_ylim(0, .37)
    decorate(ax, angle=False)
    ax.legend(ncol=3, frameon=False, loc="upper right")
    fig.subplots_adjust(left=.10, right=.99, top=.95, bottom=.19)
    save(fig, "baseline-refinement")


def completed_comparison(kind):
    name = "all_step_comparisons.csv" if kind == "rms" else "all_step_growth.csv"
    data = pd.read_csv(COMPLETED / name)
    cases = [("fft_coarse", "FFT2D5 coarse", "#56B4E9", ":", None),
             ("fft_fine", "FFT2D5 fine", COLORS[1], "-", "o"),
             ("open", "3D OPEN", COLORS[3], "-", "s")]
    fig, axes = plt.subplots(2, 3, figsize=(6.65, 3.9), sharex=True,
                             gridspec_kw={"height_ratios": [1.5, 1]})
    for alias, label, color, linestyle, marker in cases:
        f = data[data.alias == alias]
        for j, direction in enumerate(DIRS):
            key = f"sigma_{direction}_m" if kind == "rms" else f"growth_{direction}_m"
            axes[0, j].plot(angle(f), f[key]*1e3, color=color, ls=linestyle,
                            marker=marker, markersize=2.4, markerfacecolor="white",
                            markeredgewidth=.55, markevery=max(1,len(f)//12), lw=1.2)
            residual = f[f"{direction}_relative_error"]*100 if kind == "rms" else f[f"growth_{direction}_error_m"]*1e3
            axes[1, j].plot(angle(f), residual, color=color, ls=linestyle)
    # Draw the independent model last so agreement with OPEN cannot hide it.
    for alias, _, _, _, _ in cases:
        f = data[data.alias == alias]
        for j, direction in enumerate(DIRS):
            key = f"sigma_{direction}_m" if kind == "rms" else f"growth_{direction}_m"
            axes[0,j].plot(angle(f), f["model_"+key]*1e3, color="black", ls="--", lw=1.05,zorder=5)
    for j in range(3):
        axes[0,j].set_title(TITLES[j]);axes[0,j].set_ylim(bottom=0)
        axes[0,j].set_ylabel("RMS size [mm]" if kind == "rms" and j==0 else ("RMS increase [mm]" if j==0 else ""))
        axes[1,j].set_ylabel(("Size error [%]" if kind=="rms" else "Growth error [mm]") if j==0 else "")
        axes[1,j].set_xlabel("Orbit angle [deg]");axes[1,j].axhline(0,color=".5",lw=.5)
        if kind=="rms":
            axes[1,j].axhline(1,color=".6",ls=":",lw=.55)
            axes[1,j].axhline(-1,color=".6",ls=":",lw=.55)
        for i in range(2):decorate(axes[i,j])
    handles=[Line2D([],[],color=c,ls=ls,marker=mk,markerfacecolor="white",markersize=3,label=l)
             for _,l,c,ls,mk in cases]
    handles.append(Line2D([],[],color="black",ls="--",label="Independent analytic model"))
    fig.legend(handles=handles,loc="upper center",ncol=2,bbox_to_anchor=(.5,1.015),frameon=False)
    fig.subplots_adjust(top=.81,bottom=.12,left=.09,right=.965,hspace=.22,wspace=.35)
    save(fig,"strong-charge-rms" if kind=="rms" else "collective-growth")


def strong_total():
    completed_comparison("rms")


def collective_growth():
    completed_comparison("growth")


def radius_scan():
    fig, axes = plt.subplots(2, 3, figsize=(6.65, 4.15), sharex=True,
                             gridspec_kw={"height_ratios": [1.4, 1]})
    cases = [("R2", "R = 2 m"), ("R1", "R = 1 m"), ("R0p5", "R = 0.5 m"), ("R0p25", "R = 0.25 m")]
    for (case, label), color in zip(cases, COLORS):
        f = load(f"radius-{case}.csv")
        for j, direction in enumerate(DIRS):
            axes[0, j].plot(angle(f), f[f"sigma_{direction}_m"]*1e3, color=color,
                            marker="o", markevery=12, markersize=2, markerfacecolor="white")
            axes[1, j].plot(angle(f), f[f"{direction}_relative_error"]*100, color=color)
    f = load("radius-R1.csv")
    for j, direction in enumerate(DIRS):
        axes[0, j].plot(angle(f), f[f"model_sigma_{direction}_m"]*1e3, color="black", ls="--", lw=1.2)
        axes[0, j].set_title(TITLES[j]); axes[0, j].set_ylabel("RMS size [mm]" if j == 0 else ""); axes[0, j].set_ylim(bottom=0)
        axes[1, j].set_ylabel("Size error [%]" if j == 0 else ""); axes[1, j].set_xlabel("Orbit angle [deg]")
        axes[1, j].axhline(0, color=".5", lw=.5); axes[1, j].set_ylim(-1.05, 1.05)
        for i in range(2):
            decorate(axes[i, j])
    handles = [Line2D([], [], color=c, label=l) for (_, l), c in zip(cases, COLORS)]
    fig.legend(handles=handles, loc="upper center", ncol=4, bbox_to_anchor=(.5, 1.005), frameon=False)
    fig.legend(handles=convention_handles(), loc="upper center", ncol=2,
               bbox_to_anchor=(.5, .947), frameon=False)
    fig.subplots_adjust(top=.82, bottom=.11, left=.085, right=.965, hspace=.20, wspace=.36)
    save(fig, "radius-similarity")


def field_diagnostics():
    data = load("field-moments.csv")
    data = data[data.region == "all"]
    meshes = ["64x128x1024", "128x256x2048"]
    fig, axes = plt.subplots(1, 2, figsize=(6.65, 2.8))
    x = np.arange(3); width=.30
    for k, (mesh, color) in enumerate(zip(meshes, [COLORS[1], COLORS[3]])):
        f = data[data.mesh == mesh].set_index("direction").loc[list(DIRS)]
        history = "Historical: " if k == 0 else "Current: "
        axes[0].bar(x+(k-.5)*width, f.field_moment_ratio_to_exact, width, color=color,
                    label=history + mesh.replace("x", " × "))
        axes[1].bar(x+(k-.5)*width, f.relative_particlewise_E_L2_error*100, width, color=color)
    axes[0].axhline(1, color="black", ls="--", lw=.8)
    axes[0].set_ylabel("Field moment / exact"); axes[0].set_ylim(0, 1.39)
    axes[1].set_ylabel(r"Particlewise $E$ error [%]"); axes[1].set_ylim(0, 41)
    for ax in axes:
        ax.set_xticks(x, [r"$r$", r"$s$", r"$y_{\rm OPALX}$"]); decorate(ax, angle=False)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False)
    fig.subplots_adjust(top=.82, bottom=.16, left=.09, right=.99, wspace=.38)
    save(fig, "initial-fields")


def g_diagnostic():
    data=load("model-g.csv")
    fig, ax = plt.subplots(figsize=(6.65, 2.45))
    for case, label, color in [("fft2d5-example-q1", "1 pC ellipsoid", COLORS[1]), ("q10-pilot", "10 pC ellipsoid", COLORS[3])]:
        f=data[data.case==case]
        ax.plot(np.rad2deg(f.phase_rad),f.exact_ellipsoid_longitudinal_pressure_g,color=color,label=label)
    ax.axhline(6.36,color="black",ls="--",label="Configured constant g = 6.36")
    ax.set(xlabel="Orbit angle [deg]",ylabel=r"Moment-equivalent $g$",ylim=(0,7))
    decorate(ax)
    ax.legend(loc="lower left",ncol=1,frameon=False)
    fig.subplots_adjust(top=.96,bottom=.20,left=.10,right=.965)
    save(fig,"longitudinal-model")


def centroid_covariance():
    old=load("response-all-steps.csv");old_cov=load("covariance.csv")
    new=pd.read_csv(COMPLETED/"response-all_step_collective_response.csv")
    new_cov=pd.read_csv(COMPLETED/"response-covariance_snapshots.csv")
    cases=[(old,old_cov,"fft2d5-example-q1","1 pC FFT2D5", "#009E73"),
           (new,new_cov,"fft-fine-10pc","10 pC FFT2D5 fine",COLORS[1]),
           (new,new_cov,"open-10pc","10 pC OPEN",COLORS[3])]
    fig,axes=plt.subplots(1,2,figsize=(6.65,2.9))
    for data,cov,case,label,color in cases:
        f=data[data.case==case]
        axes[0].plot(angle(f),f.centroid_response_norm_m*1e6,color=color,label=label)
        f=cov[cov.case==case].sort_values("time_s")
        axes[1].plot(f.time_s/(np.pi/180/(.01*299792458)),
                     f.max_abs_standardized_covariance_error*100,color=color,
                     marker="o",ms=2.6,label=label,clip_on=False)
    axes[0].set(xlabel="Orbit angle [deg]",ylabel=r"$|C_Q-C_0|$ [$\mu$m]",ylim=(0,140))
    axes[1].set(xlabel="Orbit angle [deg]",ylabel="Max. standardized covariance error [%]",ylim=(0,46))
    for ax in axes:decorate(ax)
    axes[0].legend(loc="upper left",frameon=False,fontsize=8)
    fig.subplots_adjust(top=.95,bottom=.18,left=.09,right=.965,wspace=.38)
    save(fig,"centroid-covariance")


def main():
    for record in json.loads((ROOT/"data/provenance.json").read_text())["sources"]:
        if record["snapshot"].startswith("data/10pc-completed/"):
            actual=hashlib.sha256((ROOT/record["snapshot"]).read_bytes()).hexdigest()
            if actual!=record["sha256"]:
                raise ValueError(f"Completed-study input changed: {record['snapshot']}")
    for record in json.loads((DATA/"provenance.json").read_text()):
        actual=hashlib.sha256((DATA/record["copy"]).read_bytes()).hexdigest()
        if actual!=record["sha256"]:
            raise ValueError(f"Archived figure input changed: {record['copy']}")
    baseline();convergence();strong_total();collective_growth();radius_scan()
    field_diagnostics();g_diagnostic();centroid_covariance()
    print(f"Wrote 8 vector PDFs and PNG previews to {OUT}")


if __name__=="__main__":
    main()
