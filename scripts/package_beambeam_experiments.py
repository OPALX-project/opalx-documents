#!/usr/bin/env python3
"""Package the four OPALX BeamBeam studies without generated results or caches."""

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile


README = """# BeamBeam experiments 1–4: inputs and scripts

Extract this archive at the root of an OPALX Git checkout, preserving sandbox/.
Check existing files before extraction: tar can overwrite local work.
All four experiments are bundled because they share launchers and analytic helpers.
The OPALX executable and Python environment are not included. Neither are generated
results, plots, caches, reference presentations, or the OPALX–IMPACT study.

Use a Python environment with numpy, scipy, pandas, matplotlib and h5py installed:

```bash
export OPALX_PYTHON=/absolute/path/to/python
sandbox/experiment-1/run.sh --opalx /absolute/path/to/opalx --smoke
sandbox/experiment-2/run.sh --opalx /absolute/path/to/opalx --smoke
sandbox/experiment-3/run.sh --opalx /absolute/path/to/opalx
sandbox/experiment-4/run.sh --opalx /absolute/path/to/opalx
```

Use --prepare-only to prepare inputs without a simulation; --threads accepts 1–4.
Use --help for options. Git is required for run provenance. When overrides are not
set, the launchers use build_openmp/src/opalx and $HOME/.venv-h6/bin/python.
All generated output is placed in the selected experiment's results/ directory.
The smoke/coarse defaults check workflows, not the fine-grid CAIN benchmark.
Experiment 2 --smoke runs only three steps and does not compare full trajectories.
Experiment 4 defaults to a primary-only lifecycle smoke; --full tracks witnesses.
--merlin6 is not implemented. Retained older batch scripts are reference material.

See Experiments.md for the study map and BEAMBEAM_PHYSICS_AND_VALIDATION.md for
scientific qualifications. Those documents also describe historical outputs that
are intentionally absent here. Helpers analyzing those outputs need regenerated
or separately obtained data. Legacy input decks are retained, not certified as
current examples. The supported local entry points are experiment-N/run.sh.

DOWNLOAD-MANIFEST.json identifies the source revision and SHA-256 of every source
file in this bundle. The source revision alone does not identify untracked study
files; the per-file hashes are authoritative for this archive snapshot.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="OPALX checkout")
    parser.add_argument("--output", type=Path, required=True, help="New .tar.gz file")
    args = parser.parse_args()
    root = args.source.resolve()
    selected = [root / "sandbox" / name for name in
                ("Experiments.md", "BEAMBEAM_PHYSICS_AND_VALIDATION.md")]
    folders = [root / "sandbox/scripts"]
    for number in range(1, 5):
        experiment = root / f"sandbox/experiment-{number}"
        selected.append(experiment / "run.sh")
        folders.extend((experiment / "inputs", experiment / "scripts"))
    for folder in folders:
        if not folder.is_dir():
            raise FileNotFoundError(folder)
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Unexpected symlink: {path}")
            if path.is_file() and not any(part.startswith(".") or part == "__pycache__"
                                          for part in path.relative_to(folder).parts):
                if path.suffix not in (".pyc", ".pyo", ".pptx", ".pdf"):
                    selected.append(path)
    payload = {str(path.relative_to(root)): (path.read_bytes(),
               0o755 if path.stat().st_mode & 0o111 else 0o644) for path in selected}
    payload["sandbox/DOWNLOAD-LICENSE"] = ((root / "LICENSE").read_bytes(), 0o644)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    manifest = {"source_revision": revision, "scope": "inputs and scripts; no results",
                "files": {name: hashlib.sha256(data).hexdigest()
                          for name, (data, _) in sorted(payload.items())}}
    payload["sandbox/DOWNLOAD.md"] = (README.encode(), 0o644)
    payload["sandbox/DOWNLOAD-MANIFEST.json"] = (
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(), 0o644)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Stable ordering, modes, ownership and timestamps make the archive reproducible.
    with args.output.open("xb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                for name, (data, mode) in sorted(payload.items()):
                    member = tarfile.TarInfo(name)
                    member.size, member.mode = len(data), mode
                    archive.addfile(member, io.BytesIO(data))
    print(f"{len(payload)} files, {args.output.stat().st_size} bytes")
    print(hashlib.sha256(args.output.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
