#!/usr/bin/env bash
set -euo pipefail
report_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$report_dir/../../../../.." && pwd)"
report_python="${OPALX_REPORT_PYTHON:-/Users/adelmann/.venv-h6/bin/python}"
if [[ -d "$repo_dir/src/SpaceCharge/FFT2D5" ]]; then
  default_output="$repo_dir/output/pdf"
else
  default_output="$report_dir/output"
fi
report_output="${OPALX_REPORT_OUTPUT_DIR:-$default_output}"
cd "$report_dir"
mkdir -p .build "$report_output"
"$report_python" verify_evidence.py
"$report_python" make_tables.py
"$report_python" make_figures.py
"$report_python" make_sacr_figures.py
"$report_python" make_frozen_results.py
"$report_python" make_triangle_results.py
"$report_python" make_fixed_triangle_results.py
"$report_python" make_free_open_results.py
latexmk -pdf -halt-on-error -interaction=nonstopmode -outdir=.build main.tex > .build/latexmk.stdout.log 2>&1
cp .build/main.pdf "$report_output/fft2d5-uniform-field-validation.pdf"
latexmk -pdf -halt-on-error -interaction=nonstopmode -outdir=.build mapped-grid-note.tex > .build/mapped-grid-note.stdout.log 2>&1
cp .build/mapped-grid-note.pdf "$report_output/fft2d5-mapped-grid-explanation.pdf"
echo "$report_output/fft2d5-uniform-field-validation.pdf"
echo "$report_output/fft2d5-mapped-grid-explanation.pdf"
