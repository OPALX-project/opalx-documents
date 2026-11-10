"""Rebuild SACR figures/tables solely from archived multi-point field results."""
from pathlib import Path
import hashlib
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/opalx-sacr-report-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/opalx-sacr-report-cache")
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True,exist_ok=True)
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "sacr"
FIGURES = ROOT / "figures"
GENERATED = ROOT / "generated"
DIRECTIONS = ("radial", "tangential", "vertical")
TITLES = (r"Radial $r$", r"Tangential $s$", r"Vertical $y$")
CASES = ("sphere", "previous_100mm_ellipsoid", "five_metre_ellipsoid")
LABELS = {"sphere": "Sphere", "previous_100mm_ellipsoid": "100 mm ellipsoid",
          "five_metre_ellipsoid": "5 m ellipsoid"}
COLORS = ("#0072B2", "#D55E00", "#009E73")


def verify():
    entries = json.loads((DATA / "snapshot-provenance.json").read_text())["sources"]
    for entry in entries:
        path = ROOT / entry["snapshot"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"SACR evidence changed: {path}")


def save(fig, name):
    fig.savefig(FIGURES / f"{name}.pdf")
    fig.savefig(FIGURES / f"{name}.png", dpi=300)
    plt.close(fig)


def table(name, headers, rows, align=None):
    align = align or "l"+"r"*(len(headers)-1)
    lines = [rf"\begin{{tabular}}{{{align}}}", r"\toprule",
             " & ".join(headers)+r" \\", r"\midrule"]
    lines.extend(" & ".join(map(str,row))+r" \\" for row in rows)
    lines.extend([r"\bottomrule",r"\end{tabular}"])
    (GENERATED/f"{name}.tex").write_text("\n".join(lines)+"\n")


def scientific(value):
    if value == 0:
        return "0"
    base,power = f"{value:.2e}".split("e")
    return rf"${base}\times10^{{{int(power)}}}$"


def make_flat(fields):
    selected = fields[np.isinf(fields.radius_m)].copy()
    keys = ["case","point_id","direction"]
    selected = selected.sort_values("nphi").groupby(keys,as_index=False).tail(1)
    fig,axes = plt.subplots(2,3,figsize=(6.65,3.8),sharex="col",layout="constrained",
                            gridspec_kw={"height_ratios":[1.65,1]})
    markers = ("o","s","^")
    for j,direction in enumerate(DIRECTIONS):
        for case,color,marker in zip(CASES,COLORS,markers):
            frame=selected[(selected.case==case)&(selected.direction==direction)]
            x=frame.dubin_field/frame.characteristic_scale
            y=frame.sacr_field/frame.characteristic_scale
            axes[0,j].scatter(x,y,s=14,marker=marker,facecolors="none",edgecolors=color,
                               linewidths=.7,zorder=3)
            axes[1,j].scatter(x,100*frame.normalized_difference,s=12,marker=marker,
                              color=color,linewidths=.6,zorder=3)
        axes[0,j].plot([-1,1],[-1,1],"k--",lw=.85,zorder=2)
        axes[0,j].set(title=TITLES[j],xlim=(-1,1),ylim=(-1,1))
        axes[1,j].axhline(0,color=".4",lw=.6)
        axes[1,j].set_xlabel(r"Dubin $E_i/E_{i,*}$")
        axes[1,j].ticklabel_format(axis="y",style="sci",scilimits=(-2,2),useMathText=True)
    axes[0,0].set_ylabel(r"SACR $E_i/E_{i,*}$")
    axes[1,0].set_ylabel("Difference\n[% of scale]")
    for ax in axes.flat:
        ax.grid(alpha=.17,lw=.5)
        ax.tick_params(direction="in",top=True,right=True)
    handles=[Line2D([],[],color=color,marker=marker,markerfacecolor="none",ls="none",
                    ms=4,label=LABELS[case]) for case,color,marker in zip(CASES,COLORS,markers)]
    handles.append(Line2D([],[],color="black",ls="--",lw=.85,label="Dubin identity"))
    fig.legend(handles=handles,loc="outside upper center",ncol=2,frameon=False)
    save(fig,"sacr-flat-limit")
    rows=[]
    for case in CASES:
        frame=selected[selected.case==case]
        count=frame.point_id.nunique()
        values=[100*frame[frame.direction==d].normalized_difference.abs().max() for d in DIRECTIONS]
        rows.append([LABELS[case],count,*map(scientific,values)])
    table("sacrflat",["Shape","Points",r"$\max|\delta_r|$ [\%]",r"$\max|\delta_s|$ [\%]",r"$\max|\delta_y|$ [\%]"],rows)


def make_radius(fields, quadrature):
    selected=fields[(fields.case=="five_metre_ellipsoid")&np.isfinite(fields.radius_m)].copy()
    selected=selected.sort_values("nphi").groupby(["radius_m","point_id","direction"],as_index=False).tail(1)
    maxima=selected.groupby(["radius_m","direction"]).normalized_difference.agg(lambda s:s.abs().max()).reset_index()
    fig,ax=plt.subplots(figsize=(6.65,3.45),layout="constrained")
    for direction,title,color in zip(DIRECTIONS,TITLES,COLORS):
        frame=maxima[maxima.direction==direction].sort_values("radius_m")
        positive=frame.normalized_difference>0
        ax.plot(frame.radius_m[positive],100*frame.normalized_difference[positive],color=color,
                marker="o",ms=3,mfc="white",lw=1.15)
        q=quadrature[(quadrature.case=="five_metre_ellipsoid")
                     &np.isfinite(quadrature.radius_m)&(quadrature.direction==direction)]
        q=q.sort_values("radius_m")
        positive=q.max_normalized_change>0
        ax.plot(q.radius_m[positive],100*q.max_normalized_change[positive],color=color,
                ls="--",lw=.85)
    ax.set(xscale="log",yscale="log",xlabel="Bend radius $R$ [m]",
           ylabel="Maximum over test points\n[% of component scale]")
    ax.grid(which="both",alpha=.17,lw=.5)
    ax.tick_params(direction="in",which="both",top=True,right=True)
    handles=[Line2D([],[],color=color,marker="o",mfc="white",ms=3,lw=1.15,label=title)
             for title,color in zip(TITLES,COLORS)]
    handles.extend([Line2D([],[],color="black",lw=1.15,label="SACR minus straight Dubin"),
                    Line2D([],[],color="black",ls="--",lw=.85,label="Quadrature refinement change")])
    fig.legend(handles=handles,ncol=3,frameon=False,loc="outside upper center")
    save(fig,"sacr-radius-limit")
    rows=[]
    for radius in (2.,20.,200.,2000.):
        frame=maxima[maxima.radius_m==radius].set_index("direction")
        if len(frame)==3:
            rows.append([f"{radius:g}",*[scientific(100*frame.loc[d,"normalized_difference"]) for d in DIRECTIONS]])
    table("sacrradius",["$R$ [m]",r"$\max|\delta_r|$ [\%]",r"$\max|\delta_s|$ [\%]",r"$\max|\delta_y|$ [\%]"],rows)


def main():
    verify()
    plt.rcParams.update({"font.family":"serif","mathtext.fontset":"stix","font.size":9,
                         "axes.titlesize":10,"axes.labelsize":9,"legend.fontsize":8,
                         "xtick.labelsize":8,"ytick.labelsize":8,"pdf.fonttype":42})
    FIGURES.mkdir(exist_ok=True)
    GENERATED.mkdir(exist_ok=True)
    fields=pd.read_csv(DATA/"fields.csv",float_precision="round_trip")
    quadrature=pd.read_csv(DATA/"quadrature_summary.csv",float_precision="round_trip")
    make_flat(fields)
    make_radius(fields,quadrature)
    print("Generated SACR figures and tables from archived data.")


if __name__=="__main__":
    main()
