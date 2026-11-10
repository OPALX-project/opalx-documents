"""Rebuild frozen-tube tables and plots from immutable local evidence."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

os.environ.setdefault("MPLCONFIGDIR", "/tmp/opalx-frozen-report-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/opalx-frozen-report-cache")
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data/frozen-r2"
GENERATED = ROOT / "generated"
DIRECTIONS = ("radial", "tangential", "vertical")


def table(name, headers, rows, align):
    lines = [r"\begin{tabular}{" + align + "}", r"\toprule",
             " & ".join(headers) + r" \\", r"\midrule"]
    lines.extend(" & ".join(map(str, row)) + r" \\" for row in rows)
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (GENERATED / (name + ".tex")).write_text("\n".join(lines) + "\n")


def main():
    evidence = json.loads((DATA / "snapshot-provenance.json").read_text())["sources"]
    for item in evidence:
        path = ROOT / item["snapshot"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"Frozen-tube evidence changed: {path}")
    analysis = DATA / "analysis"
    selection = json.loads((analysis / "plot_selection.json").read_text())
    manifests = {m["name"]: m for m in json.loads((analysis / "cases_manifest.json").read_text())}
    summary = pd.read_csv(analysis / "field_summary.csv", float_precision="round_trip")
    changes = pd.read_csv(analysis / "mesh_and_control_changes.csv", float_precision="round_trip")
    centre = pd.read_csv(analysis / "centre_radial.csv", float_precision="round_trip")
    rows = []
    for kind, title in (("transverse", "Transverse"), ("longitudinal", "Longitudinal")):
        cases = [manifests[name] for name in selection[kind]]
        assert len({m["source"]["sha256"] for m in cases}) == 1
        assert len({m["reference_path_sha256"] for m in cases}) == 1
        axis = 0 if kind == "transverse" else 2
        nodes = ",".join(str(m["mesh"][axis]) for m in cases)
        source = cases[0]["source"]
        rows.append([title, "$N_" + ("x" if axis == 0 else "z") + "=" + nodes + "$",
                     rf"${source['ns']}\times{source['ncross']}$", f"{1000*cases[0]['path_step_m']:g}"])
    table("frozenmeshes", ["Scan", "Varied mesh", r"Source $N_s\times N_\perp$", "Path [mm]"], rows, "llrr")

    rows = []
    for kind, title in (("transverse", "Transverse"), ("longitudinal", "Longitudinal")):
        name = selection[kind][-1]
        for region, label in (("all", "All 43"), ("interior", "Interior 31")):
            q = summary[(summary.case == name) & (summary.region == region)].set_index("direction")
            assert len(q) == 3
            rows.append([title, label, *[f"{100*q.loc[d, 'max_abs_normalized_error']:.4g}" for d in DIRECTIONS]])
    table("frozenerrors", ["Finest scan", "Targets", r"$\max|\eta_r|$ [\%]",
                           r"$\max|\eta_s|$ [\%]", r"$\max|\eta_y|$ [\%]"], rows, "llrrr")

    tnames = selection["transverse"]
    q = changes[(changes.case_coarse == tnames[-2]) & (changes.case_fine == tnames[-1])
                & (changes.region == "all")].set_index("direction")
    assert len(q) == 3
    long_fine = selection["longitudinal"][-1]
    control = changes[(changes.case_coarse == long_fine) & (changes.region == "all")
                      & (changes.direction == "tangential") & changes.kind.isin(["particles", "path"])]
    assert len(control) >= 2
    text = (rf"The last transverse mesh change is {100*q.loc['radial', 'max_abs_normalized_change']:.3g}\% radial "
            rf"and {100*q.loc['vertical', 'max_abs_normalized_change']:.3g}\% vertical. "
            rf"Longitudinal source/path controls change $E_s$ by less than {100*control.max_abs_normalized_change.max():.3g}\% "
            r"of its scale, leaving the end-field failure unchanged.")
    (GENERATED / "frozen-controls-text.tex").write_text(text + "\n")

    q = centre[centre.case == tnames[-1]]
    assert len(q) == 1
    fft = q.E_fft_at_10pC_V_per_m.iloc[0]
    exact = q.E_sacr_at_10pC_V_per_m.iloc[0]
    relative = 100*abs(fft/exact - 1)
    text = (rf"The finest transverse run gives $E_r(0)={fft:+.6f}$ V/m, "
            rf"whereas SACR gives ${exact:+.6f}$ V/m: a {relative:.1f}\% difference "
            r"relative to the centre field itself. ")
    (GENERATED / "frozen-centre-text.tex").write_text(text + "\n")

    command = [sys.executable, str(analysis / "analyze_fields.py"), "--replot",
               "--output-dir", str(ROOT / "figures")]
    for kind in ("transverse", "longitudinal"):
        command.extend(["--" + kind + "-cases", *selection[kind]])
    command.extend(["--field-cases", *selection["direct_fields"]])
    subprocess.run(command, check=True, env=os.environ.copy())
    print("Rebuilt frozen-tube tables and publication figures from archived inputs.")


if __name__ == "__main__":
    main()
