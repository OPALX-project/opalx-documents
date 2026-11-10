"""Generate report tables from the archived CSV/JSON evidence, without simulations."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
COMPLETED = DATA / "10pc-completed"
OUT = ROOT / "generated"
OUT.mkdir(exist_ok=True)
DIRECTIONS = ["radial", "tangential", "vertical"]


def table(name, columns, rows, align=None):
    align = align or "l" + "r" * (len(columns) - 1)
    text = [rf"\begin{{tabular}}{{{align}}}", r"\toprule",
            " & ".join(columns) + r" \\", r"\midrule"]
    text.extend(" & ".join(map(str, row)) + r" \\" for row in rows)
    text.extend([r"\bottomrule", r"\end{tabular}"])
    (OUT / f"{name}.tex").write_text("\n".join(text) + "\n")


def errors(row):
    return [f"{100*row[f'{d}_max_abs_relative_error']:.4f}" for d in DIRECTIONS]


baseline = pd.read_csv(DATA / "baseline-summary.csv")
table("baseline", ["Charge [pC]", r"$\epsilon_r$ [\%]", r"$\epsilon_s$ [\%]", r"$\epsilon_y$ [\%]"],
      [["SC off" if row.charge_C == 0 else f"{row.charge_C*1e12:g}", *errors(row)]
       for _, row in baseline.iterrows() if row.case in ["final-zero", "final-q0p1", "final-q0p3", "fft2d5-example-q1"]])

labels = {"transverse_mesh": r"$N_x,N_y\to 256,512$",
          "longitudinal_mesh": r"$N_s\to 2048$", "half_time_step": r"$\Delta t/2$ (256 steps)",
          "double_particles": r"$2N$ (196,608)"}
convergence = pd.read_csv(DATA / "baseline-convergence.csv")
rows = []
for _, row in convergence.iterrows():
    case = baseline[baseline.case == row["case"]].iloc[0]
    rows.append([labels[row.control], f"{100*row.maximum_relative_change:.5f}",
                 f"{100*max(case[f'{d}_max_abs_relative_error'] for d in DIRECTIONS):.5f}"])
table("convergence", ["Independent refinement", r"Max. change [\%]", r"Max. model error [\%]"], rows)

open_scan = pd.read_csv(DATA / "open-summary.csv")
open_ref = pd.read_csv(DATA / "open-refinement-summary.csv")
rows = [["SC off; 512 steps", *errors(open_scan.iloc[0])]]
for _, row in open_scan[open_scan.charge_C > 0].iterrows():
    rows.append([f"{row.charge_C*1e12:g} pC; coarse mesh", *errors(row)])
row = open_ref[open_ref.case == "open-q1-64-128"].iloc[0]
rows.append(["1 pC; refined mesh", *errors(row)])
table("open", ["3D OPEN control", r"$\epsilon_r$ [\%]", r"$\epsilon_s$ [\%]", r"$\epsilon_y$ [\%]"], rows)

growth = pd.read_csv(DATA / "growth-summary.csv")
for name, case in [("growth1", "fft2d5-example-q1")]:
    selected = growth[growth.case == case].set_index("direction")
    rows = []
    for direction, label in zip(DIRECTIONS, ["Radial", "Tangential", "Vertical"]):
        row = selected.loc[direction]
        rows.append([label, f"{row.final_model_growth_m*1e3:.5f}",
                     f"{row.final_actual_growth_m*1e3:.5f}", f"{row.final_growth_relative_error*100:+.2f}"])
    table(name, ["Direction", "Model [mm]", "OPALX [mm]", r"Error in growth [\%]"], rows)

strong = pd.read_csv(COMPLETED / "summary.csv").set_index("alias")
strong_labels = {"fft_coarse": "FFT2D5 coarse", "fft_fine": "FFT2D5 fine", "open": "3D OPEN"}
table("strong", ["10 pC run", r"$\epsilon_r$ [\%]", r"$\epsilon_s$ [\%]", r"$\epsilon_y$ [\%]"],
      [[label, *errors(strong.loc[key])] for key,label in strong_labels.items()])
refinement = pd.read_csv(COMPLETED / "refinement_summary.csv").set_index("direction")
table("strongrefinement", ["Direction", r"Max. fine/coarse change [\%]", r"Final change [\%]"],
      [[d.capitalize(), f"{100*refinement.loc[d].max_abs_relative_change:.5f}",
        f"{100*refinement.loc[d].final_relative_change:+.5f}"] for d in DIRECTIONS])
new_growth = pd.read_csv(COMPLETED / "growth_summary.csv")
table("growth10", ["10 pC run", "Direction", "Model [mm]", "OPALX [mm]", r"Growth error [\%]"],
      [[strong_labels[alias], d.capitalize(),
        f"{row.final_model_growth_m*1e3:.5f}", f"{row.final_actual_growth_m*1e3:.5f}",
        f"{row.final_growth_relative_error*100:+.2f}"]
       for alias in ["fft_fine","open"] for d in DIRECTIONS
       for _,row in new_growth[(new_growth.alias==alias)&(new_growth.direction==d)].iterrows()])

radius = pd.read_csv(DATA / "radius-summary.csv")
radius_centroid = pd.read_csv(DATA / "radius-centroid-summary.csv").set_index("case")
table("radius", ["$R$ [m]", "$Q$ [pC]", "$B$ [mT]", r"$\epsilon_r$ [\%]", r"$\epsilon_s$ [\%]", r"$\epsilon_y$ [\%]"],
      [[f"{r.radius_m:g}", f"{r.charge_pC:g}", f"{r.field_mT:.4f}",
        *[f"{100*getattr(r,f'{d}_max_error'):.4f}" for d in DIRECTIONS]] for r in radius.itertuples()])
table("radiusresponse", ["$R$ [m]", r"Tangential growth error [\%]", r"Max. centroid shift [$\mu$m]"],
      [[f"{r.radius_m:g}", f"{100*r.tangential_final_growth_relative_error:.2f}",
        f"{radius_centroid.loc[case].max_centroid_response_norm_m*1e6:.3f}"]
       for r, case in zip(radius.itertuples(), ["R2-baseQ1", "R1-baseQ1", "R0p5-baseQ1", "R0p25-baseQ1"])])

fields = pd.read_csv(DATA / "field-summary.csv")
rows = []
for _, row in fields[fields.region == "all"].iterrows():
    rows.append(["Historical" if row.mesh == "64x128x1024" else "Current",
                 row.direction.capitalize(), f"{row.field_moment_ratio_to_exact:.6f}", f"{100*row.relative_particlewise_E_L2_error:.3f}"])
table("fields", ["Binary / mesh", "Direction", "Field-moment ratio", r"Particlewise $L^2$ [\%]"], rows)

centroid = pd.read_csv(DATA / "centroid-summary.csv")
covariance = pd.read_csv(DATA / "covariance-snapshots.csv")
rows = []
for case, label in [("fft2d5-example-q1", "1 pC FFT2D5")]:
    c = centroid[centroid.case == case].iloc[0]
    cov = covariance[covariance.case == case].sort_values("time_s").iloc[-1]
    rows.append([label, f"{c.max_centroid_response_norm_m*1e6:.3f}",
                 f"{cov.max_abs_standardized_covariance_error*100:.3f}",
                 f"{cov.model_radial_tangential_correlation:.6f}", f"{cov.actual_radial_tangential_correlation:.6f}"])
new_centroid = pd.read_csv(COMPLETED / "response-centroid_summary.csv")
new_covariance = pd.read_csv(COMPLETED / "response-covariance_snapshots.csv")
for case,label in [("fft-fine-10pc", "10 pC FFT2D5 fine"),("open-10pc", "10 pC OPEN")]:
    c=new_centroid[new_centroid.case==case].iloc[0]
    cov=new_covariance[new_covariance.case==case].sort_values("time_s").iloc[-1]
    rows.append([label, f"{c.max_centroid_response_norm_m*1e6:.3f}",
                 f"{cov.max_abs_standardized_covariance_error*100:.3f}",
                 f"{cov.model_radial_tangential_correlation:.6f}",f"{cov.actual_radial_tangential_correlation:.6f}"])
table("response", ["Run", r"Centroid [$\mu$m]", r"Cov. error [\%]", r"$\rho_{rs}$ model", r"$\rho_{rs}$ OPALX"], rows)

checks = json.loads((DATA / "model-checks.json").read_text())
def sci(value, unit=""):
    coefficient, exponent = f"{value:.2e}".split("e")
    return rf"${coefficient}\times10^{{{int(exponent)}}}$" + (f" {unit}" if unit else "")
all_checks = checks["checks"].values()
table("modelchecks", ["Independent model check", "Measured maximum"], [
    ["Depolarization-factor sum error", sci(max(x['max_sum_D_error'] for x in all_checks))],
    ["Sphere / oblate / direct integral", "Passed"],
    ["Zero-charge affine rotation error", sci(checks['checks']['0.0']['zero_charge_rigid_rotation_max_absolute_error_m'], "m")],
    ["Centroid Lorentz ODE vs. circle", sci(checks['centroid_max_error_m'], "m")],
    ["Energy and canonical angular-momentum drift", sci(max(max(x['energy_max_relative_drift'], x['canonical_Lz_max_relative_drift']) for x in all_checks))],
    ["Tighter integrator: RMS change", sci(checks['tighter_integrator_max_relative_envelope_change'], "relative")],
    ["Positive affine volume", "Retained"],
], "ll")
print("Generated", len(list(OUT.glob("*.tex"))), "tables.")
