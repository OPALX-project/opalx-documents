#!/usr/bin/env python3
"""Refresh pointwise-pipe evidence without changing the earlier benchmark archive.

Called explicitly after native gates complete; never called by build.sh.
Large source arrays, particle H5 snapshots, binaries and build trees stay
external. Only immutable evidence and reproducible small scripts are copied.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "data/triangle-fixed"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--regression-case", type=Path)
    args = parser.parse_args()
    source = args.study.resolve()
    patterns = [
        "*.md", "*.py", "*.json", "*.log", "*.patch",
        "analysis/*.csv", "analysis/*.json", "analysis/*.py", "analysis/*.log",
        "checks/*.xml", "checks/*.json", "checks/*.log", "audit-api/*.py", "audit-api/*.json", "audit-api/*.csv", "audit-api/*.log", "audit-api/*.md",
        "checks/rank2-guard/*.log", "checks/rank2-guard/*.in",
        "opalx/runs/*/manifest.json", "opalx/runs/*/triangle.in",
        "opalx/runs/*/triangle.out", "opalx/runs/*/triangle.stat",
        "pyorbit/runs/*/manifest-rank*.json", "pyorbit/runs/*/probes-rank*.csv",
        "regression-checks/*.json", "regression-checks/*.log",
        "regression-checks/*/*.json", "regression-checks/*/*.log", "regression-checks/*/*.out",
        "regression-checks/*/*.py", "regression-checks/*/*.in", "regression-checks/*/*.md",
        "regression-checks/*/*.csv", "regression-checks/*/*.rt", "regression-checks/*/*.local",
    ]
    paths = sorted({p for pattern in patterns for p in source.glob(pattern) if p.is_file()})
    assert (source/"analysis/selection.json").exists()
    entries = []

    def copy(original, relative):
        target = DEST/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        entries.append({"original": str(original), "snapshot": str(target.relative_to(ROOT)), "sha256": sha(target)})

    for original in paths:
        copy(original, original.relative_to(source))
    # The updated native helper is separate from the immutable pre-API helper.
    copy(source.parent/"opalx/run_opalx.py", Path("opalx/run_opalx.py"))
    model_document = ROOT.parents[1]/"longitudinal-model.md"
    if model_document.exists():
        copy(model_document, Path("documentation/longitudinal-model.md"))
    if args.regression_case:
        for p in sorted(args.regression_case.rglob("*")):
            if p.is_file() and (p.suffix in {".py", ".json", ".md", ".in", ".rt", ".local", ".dat", ".csv", ".stat", ".md5"}
                                or p.name in {".gitignore", ".gitattributes"}):
                copy(p, Path("regression-case")/p.relative_to(args.regression_case))
    manifest = {"study": str(source), "date": "2026-11-02", "scope": "Pointwise uniform-round local longitudinal pipe model and native validation; no curved tracking claim", "sources": entries}
    (DEST/"snapshot-provenance.json").write_text(json.dumps(manifest,indent=2)+"\n")
    global_path = ROOT/"data/provenance.json"
    prov = json.loads(global_path.read_text())
    prov["sources"] = [e for e in prov["sources"] if not e["snapshot"].startswith("data/triangle-fixed/")]
    prov["sources"].extend(entries)
    prov["sources"].append({"original": "Report pointwise-pipe snapshot manifest", "snapshot": "data/triangle-fixed/snapshot-provenance.json", "sha256": sha(DEST/"snapshot-provenance.json")})
    global_path.write_text(json.dumps(prov,indent=2)+"\n")
    print(f"Archived {len(entries)} pointwise-pipe files; earlier benchmark snapshots unchanged.")


if __name__ == "__main__":
    main()
