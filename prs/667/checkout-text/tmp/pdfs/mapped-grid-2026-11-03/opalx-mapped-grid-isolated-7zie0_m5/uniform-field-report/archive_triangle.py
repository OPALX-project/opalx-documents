#!/usr/bin/env python3
"""Deliberately refresh the immutable triangular-pipe report evidence archive.

This is not called by build.sh. It copies completed research CSVs, inputs,
manifests, small logs and scripts, excluding source NPZ/distributions, native
H5 snapshots, compiled packages and downloaded papers. No native run occurs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "data/triangle-pipe"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    args = parser.parse_args()
    source = args.study.resolve()
    patterns = [
        "HANDOFF.md", "README.md", "prepare_common.py", "prepare_refinements.py",
        "analysis/*.csv", "analysis/*.json", "analysis/*.py",
        "analytic-audit/*.py", "analytic-audit/*.json", "analytic-audit/*.csv", "analytic-audit/*.md",
        "common/*.json", "common/probes.csv", "common/straight-path.dat",
        "opalx/run_opalx.py", "opalx/runs/*/manifest.json", "opalx/runs/*/triangle.in",
        "opalx/runs/*/triangle.out", "opalx/runs/*/triangle.stat",
        "opalx-audit/*.py", "opalx-audit/*.json", "opalx-audit/*.csv", "opalx-audit/*.md", "opalx-audit/*.log",
        "pyorbit/HANDOFF.md", "pyorbit/README.md", "pyorbit/*.py", "pyorbit/*.json", "pyorbit/*.log",
        "pyorbit/harness-snapshots/*.py", "pyorbit/provenance/*", "pyorbit/sources/*.json",
        "pyorbit/runs/*/manifest-rank*.json", "pyorbit/runs/*/probes-rank*.csv",
    ]
    paths = sorted({p for pattern in patterns for p in source.glob(pattern) if p.is_file()})
    assert paths and (source/"analysis/selection.json").exists()
    entries = []
    for original in paths:
        relative = original.relative_to(source)
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        entries.append({"original": str(original), "snapshot": str(target.relative_to(ROOT)), "sha256": sha(target)})
    manifest = {"study": str(source), "date": "2026-11-02", "scope": "Completed native frozen triangular-pipe fields/kicks; no tracking or tunes", "sources": entries}
    (DEST/"snapshot-provenance.json").write_text(json.dumps(manifest, indent=2)+"\n")
    global_path = ROOT/"data/provenance.json"
    global_prov = json.loads(global_path.read_text())
    global_prov["sources"] = [e for e in global_prov["sources"] if not e["snapshot"].startswith("data/triangle-pipe/")]
    global_prov["sources"].extend(entries)
    global_prov["sources"].append({"original": "Report triangular-pipe snapshot manifest", "snapshot": "data/triangle-pipe/snapshot-provenance.json", "sha256": sha(DEST/"snapshot-provenance.json")})
    global_path.write_text(json.dumps(global_prov, indent=2)+"\n")
    print(f"Archived {len(entries)} triangular-pipe evidence files; {sum((ROOT/e['snapshot']).stat().st_size for e in entries)} bytes.")


if __name__ == "__main__":
    main()
