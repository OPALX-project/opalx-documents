"""Run the parent-approved controlled native-OPALX longitudinal sweep."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
CASES = [(f"xy128-z{nz}-ns5120", nz, 5120, .02)
         for nz in (512, 1024, 2048, 4096)]
CASES += [("xy128-z4096-ns10240", 4096, 10240, .02),
          ("xy128-z4096-ns5120-path01", 4096, 5120, .01)]


def main():
    path = OUT/"longitudinal_native_runs.json"
    rows = []
    for name, nz, ns, step in CASES:
        command = [sys.executable, str(ROOT/"run_study.py"), name,
                   "--mesh", "128", "64", str(nz), "--ns", str(ns),
                   "--path-step", str(step), "--run"]
        print("START", name, flush=True)
        start = time.monotonic()
        result = subprocess.run(command, cwd=ROOT)
        row = dict(name=name, command=command, returncode=result.returncode,
                   controller_elapsed_s=time.monotonic()-start)
        for suffix, key in (("", "source_run"), ("-probes", "probe_run")):
            manifest_path = ROOT/"runs"/(name+suffix)/"manifest.json"
            if manifest_path.exists():
                manifest = json.loads(manifest_path.read_text())
                row[key] = dict(manifest=str(manifest_path),
                                sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                                elapsed_s=manifest.get("elapsed_s"),
                                returncode=manifest.get("returncode"),
                                expected_particles=manifest.get("expected_particles"),
                                binary_sha256=manifest.get("binary_sha256"))
        rows.append(row)
        path.write_text(json.dumps(rows, indent=2)+"\n")
        print("FINISH", json.dumps(row), flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
