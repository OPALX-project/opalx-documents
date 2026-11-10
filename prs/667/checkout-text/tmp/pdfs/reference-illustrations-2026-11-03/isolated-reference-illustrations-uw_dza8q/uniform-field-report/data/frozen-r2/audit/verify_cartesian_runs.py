"""Apply independent frozen-snapshot checks to the matched Cartesian meshes."""
from pathlib import Path
import json

import pandas as pd

from verify_longitudinal_runs import check, sha

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent


def main():
    points = pd.read_csv(ROOT/"reference/points.csv", float_precision="round_trip")
    rows, pending = [], []
    for nx in (128, 256, 512):
        for suffix in ("", "-probes"):
            name = f"xy{nx}-z512-cart"+suffix
            path = ROOT/"runs"/name/"manifest.json"
            if not path.exists() or json.loads(path.read_text()).get("returncode") != 0:
                pending.append(name)
                continue
            rows.append(check(path, points))
    pd.DataFrame(rows).to_csv(OUT/"cartesian_snapshot_checks.csv", index=False)
    result = dict(passed=not pending and all(row["passed"] for row in rows),
                  completed_cases=len(rows), pending=pending,
                  maximum_probe_displacement_m=max(row["maximum_probe_displacement_m"] for row in rows),
                  source_layout="Cartesian Nx512/Ny512 midpoint cloud, Ns640, physical-Jacobian inverse",
                  checked="return codes, input/binary/path hashes, N/IDs/Q, finite coordinates/momenta/fields, tube geometry and probe displacement",
                  script_sha256=sha(__file__))
    (OUT/"cartesian_snapshot_acceptance.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
