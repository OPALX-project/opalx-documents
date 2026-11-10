"""Manual OPALX integration analysis; never called by native unit tests or CTest."""
from pathlib import Path
import hashlib
import json
import math
import re
import pandas as pd

here = Path(__file__).resolve().parent
name = 'ScalingFFABasicPlacements'

def load_stat(path):
    text = path.read_text()
    columns = re.findall(r'&column\s+.*?name=([^,\s]+).*?&end', text, re.S)
    rows = []
    for line in text.splitlines():
        fields = line.split()
        if len(fields) == len(columns):
            try:
                rows.append([float(value) for value in fields])
            except ValueError:
                pass
    return pd.DataFrame(rows, columns=columns)

before = load_stat(here.parent / 'master-baseline' / 'scaling-baseline.stat')
after = load_stat(here / f'{name}.stat')
columns = ['t', 's', 'numParticles', 'charge', 'energy', 'mean_x', 'mean_y', 'mean_s',
           'ref_x', 'ref_y', 'ref_z', 'ref_px', 'ref_py', 'ref_pz']
after[columns].to_csv(here / 'trajectory.csv', index=False)

def separation(frame):
    return (frame.mean_x**2 + frame.mean_y**2 + frame.mean_s**2).pow(.5)

report = {
    'rows': len(after),
    'old_final_mean_x_m': float(before.mean_x.iloc[-1]),
    'old_final_mean_s_m': float(before.mean_s.iloc[-1]),
    'old_final_mean_separation_m': float(separation(before).iloc[-1]),
    'fixed_final_mean_x_m': float(after.mean_x.iloc[-1]),
    'fixed_final_mean_s_m': float(after.mean_s.iloc[-1]),
    'fixed_final_mean_separation_m': float(separation(after).iloc[-1]),
    'fixed_max_mean_separation_m': float(separation(after).max()),
    'fixed_particle_count_min': float(after.numParticles.min()),
    'fixed_energy_range_MeV': float(after.energy.max() - after.energy.min()),
    'max_charge_error_C': float(abs(after.charge - 1.6021766339999998e-15).max()),
    'limitation': 'One unchanged 1000-step fixture, sampled every100 steps; not a general FFA convergence study or device-backend validation.'
}
assert (after.numParticles == 10).all()
assert report['max_charge_error_C'] < 1e-28
assert len(after) == 10 and abs(after.t.iloc[-1] - 100.) < 1e-10
(here / 'analysis.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
