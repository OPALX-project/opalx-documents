"""Read-only numerical audit of the original 16³ failure; not a unit test."""
from pathlib import Path
import json
import re
import h5py
import pandas as pd

out = Path(__file__).resolve().parent
repo = out.parents[2]
case = repo / "tmp/ring-space-charge-profiles-20261023/accelerating-pic-16"
text = (case / "acceleration.stat").read_text()
columns = re.findall(r"&column\s+.*?name=([^,\s]+).*?&end", text, re.S)
rows = []
for line in text.splitlines():
    fields = line.split()
    if len(fields) == len(columns):
        try:
            rows.append([float(value) for value in fields])
        except ValueError:
            pass
frame = pd.DataFrame(rows, columns=columns)
launch = json.loads((case / "launch.json").read_text())
log = (case / "run.log").read_text(errors="replace")
gaps = re.findall(r"Cyclotron gap (\w+) t=([\d.eE+-]+) s K=([\d.eE+-]+) MeV", log)
peak = frame.loc[frame["max_y"].idxmax()]
with h5py.File(case / "acceleration.h5", "r") as handle:
    particle_groups = [name for name, value in handle.items() if isinstance(value, h5py.Group)]
result = {
    "run_directory": str(case),
    "exit_code": launch["returncode"],
    "rows": len(frame),
    "last_time_ns": float(frame.t.iloc[-1]),
    "last_mean_energy_MeV": float(frame.energy.iloc[-1]),
    "last_particles": int(frame.numParticles.iloc[-1]),
    "last_max_y_mm": float(frame.max_y.iloc[-1] * 1000),
    "largest_saved_max_y_mm": float(peak.max_y * 1000),
    "energy_at_largest_max_y_MeV": float(peak.energy),
    "last_logged_reference_gap": gaps[-1][0],
    "last_logged_reference_energy_MeV": float(gaps[-1][2]),
    "mpi_abort_in_log": "MPI_ABORT was invoked" in log,
    "hdf5_particle_groups": particle_groups,
    "limits": "Moment statistics cannot identify the unsaved failing particle or prove a boundary exit."
}
(out / "numeric-summary.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
