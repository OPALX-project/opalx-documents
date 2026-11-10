#!/bin/bash
set -euo pipefail
if test "$#" -ne 2 || test "$2" != --execute; then
    printf 'Usage: %s /absolute/path/to/updated/opalx --execute\n' "$0" >&2
    exit 2
fi
binary=$1
if ! test -x "$binary"; then printf 'Not executable: %s\n' "$binary" >&2; exit 2; fi
study=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repository=/Users/adelmann/git/opalx-master
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
shasum -a 256 "$binary" > "$study/executable.sha256"
git -C "$repository" rev-parse HEAD > "$study/source-head.txt"
git -C "$repository" diff -- src/Algorithms/ParallelTracker.cpp src/Algorithms/ParallelTracker.h \
    src/Algorithms/TrackReferenceStep.cpp src/Algorithms/TrackReferenceStep.h \
    src/Algorithms/DeviceExternalField.h src/Structure/LossDataSink.cpp > "$study/source.diff"
(cd "$repository" && shasum -a 256 src/Algorithms/ParallelTracker.cpp src/Algorithms/ParallelTracker.h \
    src/Algorithms/TrackReferenceStep.cpp src/Algorithms/TrackReferenceStep.h \
    src/Algorithms/DeviceExternalField.h src/Structure/LossDataSink.cpp) > "$study/source.sha256"
: > "$study/run-summary.tsv"
for entry in one-proton-one-rank:1 one-proton-two-ranks:2 two-protons-one-rank:1 two-protons-two-ranks:2 failure-one-rank:1 failure-two-ranks:2; do
    IFS=: read -r name ranks <<< "$entry"
    case_dir="$study/$name"
    if test -e "$case_dir/run.log"; then
        printf 'Refusing to duplicate existing manual run %s\n' "$case_dir" >&2
        exit 1
    fi
    printf 'mpirun -np %s %q Cyclotron-RF-Stop.in --info 2\n' "$ranks" "$binary" > "$case_dir/command.txt"
    date -u '+%Y-%m-%dT%H:%M:%SZ' > "$case_dir/started.txt"
    set +e
    (cd "$case_dir" && /usr/bin/time -p mpirun -np "$ranks" "$binary" Cyclotron-RF-Stop.in --info 2) > "$case_dir/run.log" 2>&1
    result=$?
    set -e
    printf '%s\n' "$result" > "$case_dir/exit-code.txt"
    date -u '+%Y-%m-%dT%H:%M:%SZ' > "$case_dir/finished.txt"
    printf '%s\t%s\n' "$name" "$result" >> "$study/run-summary.tsv"
done
shasum -a 256 "$binary" > "$study/executable-after.sha256"
cmp "$study/executable.sha256" "$study/executable-after.sha256"
