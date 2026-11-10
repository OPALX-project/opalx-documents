"""Inspect independent short-run and full-run regression evidence; no rebaselining."""
from pathlib import Path
from io import StringIO
import hashlib
import json
import math
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
CASE = "ScalingFFABasicPlacements"


def load_stat(path):
    text = path.read_text()
    columns = re.findall(r"&column\s+name=(\w+),", text)
    data = re.split(r"&data\b.*?&end\s*\n", text, flags=re.S)[1].splitlines()
    return pd.read_csv(StringIO("\n".join(data[3:])), sep=r"\s+", names=columns)


old = load_stat(ROOT / "pristine" / "RegressionTests" / CASE / "reference" / f"{CASE}.stat")
short = load_stat(ROOT / "ten-steps" / f"{CASE}.stat")
full = load_stat(ROOT / "thousand-steps" / "reference" / f"{CASE}.stat")
columns = ["t", "s", "numParticles", "charge", "energy", "mean_x", "mean_y", "mean_s",
           "ref_x", "ref_y", "ref_z", "ref_px", "ref_py", "ref_pz"]
comparison = pd.DataFrame({"old": old.iloc[-1][columns], "short": short.iloc[-1][columns]})
comparison["difference"] = comparison["short"] - comparison["old"]
comparison.to_csv(ROOT / "one-ns-comparison.csv")
full[columns].to_csv(ROOT / "full-trajectory.csv", index=False)
assert len(old) == len(short) == 1 and len(full) == 10
assert np.allclose(full.t, np.arange(10., 101., 10.), rtol=0, atol=2e-12)
assert (full.numParticles == 10).all()
assert np.max(abs(full.charge - 1.6021766339999998e-15)) < 1e-28
assert np.max(abs(comparison.loc[["ref_x", "ref_y", "ref_z"], "difference"])) < 1e-14
assert np.max(abs(comparison.loc[["ref_px", "ref_py", "ref_pz"], "difference"])) < 1e-14
assert abs(comparison.loc["energy", "difference"]) < 1e-11
energy = (math.sqrt(1 + .3195**2) - 1) * .93827208816 * 1e3
assert np.max(abs(full.energy - energy)) < 2e-11
assert (full.ref_y == 0).all() and (full.ref_py == 0).all()

# ElementPositions.txt is written in z,x,y column order with ten significant figures.
found = []
positions = ROOT / "ten-steps" / "data" / f"{CASE}_ElementPositions.txt"
for line in positions.read_text().splitlines():
    if line.startswith('"BEGIN:'):
        z, x, y = map(float, line.split('"', 2)[2].split())
        found.append([x, y, z])
settings = [(0., 3.), (.5, 3.), (.5, -3.), (1., 3.), (1.5, 3.), (1.5, -3.), (2., 3.)]
expected = [[r * (math.cos(s / r) - 1), 0., r * math.sin(s / r)] for s, r in settings]
assert len(found) == len(expected) == 7
placement_error = float(np.max(abs(np.asarray(found) - expected)))
assert placement_error < 5e-10  # Printed geometry precision, not a changed tracking tolerance.
report = {
    "executable_sha256": hashlib.sha256((ROOT / "executable" / "opalx").read_bytes()).hexdigest(),
    "embedded_revision": "61c90499b3f5638f2e26612561e149839774666d",
    "reference_rows": len(old), "short_rows": len(short), "full_rows": len(full),
    "max_short_reference_position_difference_m": float(comparison.loc[["ref_x", "ref_y", "ref_z"], "difference"].abs().max()),
    "max_short_reference_momentum_difference": float(comparison.loc[["ref_px", "ref_py", "ref_pz"], "difference"].abs().max()),
    "short_energy_difference_MeV": float(comparison.loc["energy", "difference"]),
    "full_energy_range_MeV": float(full.energy.max() - full.energy.min()),
    "full_max_analytic_energy_difference_MeV": float(abs(full.energy - energy).max()),
    "max_printed_placement_error_m": placement_error,
    "final_mean_x_m": float(full.mean_x.iloc[-1]), "final_mean_s_m": float(full.mean_s.iloc[-1]),
    "limitation": "The full run has large particle/reference separation; draft reference is not accepted physics validation.",
}
(ROOT / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
