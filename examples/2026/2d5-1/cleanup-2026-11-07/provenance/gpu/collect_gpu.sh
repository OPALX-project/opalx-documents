#!/bin/bash
set -euo pipefail
cd /psi/home/adelmann/opalx-dev/dba/validation-cleanup-20261107
for n in 1 2; do
 for mode in before after; do test -f gpu-$n-$mode/run.json; done
done
files=(build.log build-gpu.sbatch gpu2.sbatch run_gpu.py source-base.txt after-binary.sha256 probe-1.log probe-2.log unit-*.log)
for d in gpu-{1,2}-{before,after}; do
 files+=("$d/case.in" "$d/case.out" "$d/case.stat" "$d/run.json" "$d/timing.dat")
done
tar czf compact-results.tgz "${files[@]}"
tar czf native-snapshots.tgz gpu-{1,2}-{before,after}/case.h5
