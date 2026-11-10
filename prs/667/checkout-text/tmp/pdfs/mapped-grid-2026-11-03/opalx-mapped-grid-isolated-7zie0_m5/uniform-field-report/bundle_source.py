#!/usr/bin/env python3
"""Create a deterministic self-contained report source ZIP (no native H5 data)."""
from pathlib import Path
import argparse
import hashlib
import os
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    repository = ROOT.parents[4] if len(ROOT.parents) > 4 else None
    default = (repository / "output/pdf" if repository is not None
               and (repository / "src/SpaceCharge/FFT2D5").is_dir() else ROOT / "output")
    destination = args.output_dir or Path(os.environ.get("OPALX_REPORT_OUTPUT_DIR", default))
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / "fft2d5-uniform-field-validation-source.zip"
    paths = [p for p in sorted(ROOT.rglob("*")) if p.is_file()
             and not any(part in {".build", "__pycache__"} for part in p.relative_to(ROOT).parts)
             and p.suffix not in {".pyc", ".zip"} and p.name != ".DS_Store"]
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in paths:
            info = ZipInfo("uniform-field-report/" + str(path.relative_to(ROOT)), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o755 if os.access(path, os.X_OK) else 0o644) << 16
            bundle.writestr(info, path.read_bytes(), compress_type=ZIP_DEFLATED, compresslevel=9)
    with ZipFile(output) as bundle:
        if bundle.testzip() is not None or len(bundle.namelist()) != len(paths):
            raise RuntimeError("Source ZIP integrity check failed")
    print(f"{output}\n{len(paths)} files; SHA256 {hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
