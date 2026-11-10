"""Validate manual standard-generated drafts; not a unit-test/CTest dependency."""
from pathlib import Path
import hashlib
import json
import math
import re
import pandas as pd

root = Path(__file__).resolve().parent
study = root.parent
source = 'a9d38caa4f88433a5de1508b3d5c7d01bdfea95a'
regression = '737547e6ae38cf3001d6bc45cf38dd1a47d78402'
before = json.loads((root / 'preserved-inputs-before.json').read_text())
after = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in before}
assert before == after, 'standard generation changed an input/data/tolerance/launcher file'
(root / 'preserved-inputs-after.json').write_text(json.dumps(after, indent=2) + '\n')

def load_stat(path):
    text = path.read_text()
    columns = re.findall(r'&column\s+.*?name=([^,\s]+).*?&end', text, re.S)
    rows = []
    for line in text.splitlines():
        items = line.split()
        if len(items) == len(columns):
            try:
                rows.append([float(value) for value in items])
            except ValueError:
                pass
    return pd.DataFrame(rows, columns=columns)

reports = []
comparisons = []
reference_hashes = {}
for name, count, expected_rows, held_out in [
    ('FodoCell-multipoleT-fromfile', 1000, 2001,
     study / 'fodo-multipolet/baseline-master-8c1a862/FodoCell-multipoleT-fromfile.stat'),
    ('ScalingFFABasicPlacements', 10, 10,
     study / 'scaling-superposition-final/ScalingFFABasicPlacements.stat')]:
    case = root / 'RegressionTests' / name
    assert (case / 'generation-exit-code.txt').read_text().strip() == '0'
    assert source in (case / 'reference' / f'{name}.out').read_text()
    assert (case / 'checksum-validation.log').read_text().count(': OK') == 3
    frame = load_stat(case / 'reference' / f'{name}.stat')
    other = load_stat(held_out)
    assert len(frame) == len(other) == expected_rows
    assert (frame.numParticles == count).all()
    assert frame.t.equals(other.t)
    assert frame.s.is_monotonic_increasing
    assert abs(abs(frame.charge) - 1.6021766339999998e-15).max() < 1e-28
    definitions = re.findall(r'stat\s+"([^"]+)"\s+avg\s+(\S+)', (case / f'{name}.rt').read_text())
    for field, epsilon_text in definitions:
        difference = frame[field] - other[field]
        # This is NightlyBuildX's existing absolute avg statistic, sqrt(sum(d^2))/N.
        metric = math.sqrt(sum(float(value * value) for value in difference)) / len(frame)
        epsilon = float(epsilon_text)
        assert metric < epsilon
        comparisons.append(dict(case=name, field=field, rows=len(frame),
                                nightly_avg=metric, max_abs=float(abs(difference).max()),
                                epsilon=epsilon, passed=metric < epsilon,
                                held_out=str(held_out)))
    mean_separation = (frame.mean_x**2 + frame.mean_y**2 + frame.mean_s**2).pow(.5)
    reports.append(dict(case=name, rows=len(frame), comparisons=len(definitions),
                        checksums_passed=3, particles_min=float(frame.numParticles.min()),
                        particles_max=float(frame.numParticles.max()),
                        charge_C=float(frame.charge.iloc[-1]),
                        max_charge_error_C=float((abs(frame.charge)-1.6021766339999998e-15).abs().max()),
                        energy_first_MeV=float(frame.energy.iloc[0]),
                        energy_final_MeV=float(frame.energy.iloc[-1]),
                        energy_range_MeV=float(frame.energy.max()-frame.energy.min()),
                        final_t_ns=float(frame.t.iloc[-1]), final_s_m=float(frame.s.iloc[-1]),
                        final_mean_separation_m=float(mean_separation.iloc[-1]),
                        max_mean_separation_m=float(mean_separation.max())))
    for path in sorted((case / 'reference').iterdir()):
        reference_hashes[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()

assert len(comparisons) == 10
pd.DataFrame(comparisons).to_csv(root / 'comparison-results.csv', index=False)
report = dict(source_revision=source, regression_base=regression,
              executable_sha256=hashlib.sha256((root/'executable/opalx').read_bytes()).hexdigest(),
              native_unit_tests='self-contained C++; these draft scripts/data are manual integration artifacts only',
              inputs_verified_unchanged=len(before), comparisons_passed=len(comparisons),
              checksum_files_verified=6, references=reports)
(root / 'validation-report.json').write_text(json.dumps(report, indent=2) + '\n')
(root / 'reference-sha256.json').write_text(json.dumps(reference_hashes, indent=2) + '\n')
print(json.dumps(report, indent=2))
