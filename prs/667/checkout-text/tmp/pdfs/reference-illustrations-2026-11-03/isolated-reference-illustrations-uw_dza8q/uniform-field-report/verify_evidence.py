"""Reject missing or altered report snapshots before rebuilding the report."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent
provenance = json.loads((root / "data/provenance.json").read_text())
for item in provenance["sources"]:
    source = root / item["snapshot"]
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != item["sha256"]:
        raise SystemExit(f"Evidence hash mismatch: {source}")
print(f"Verified {len(provenance['sources'])} archived evidence files.")
