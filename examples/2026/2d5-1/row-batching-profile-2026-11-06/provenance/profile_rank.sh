#!/bin/bash
set -euo pipefail
rank=${OMPI_COMM_WORLD_RANK:-0}
exec nsys profile --trace=cuda,nvtx,mpi,osrt --mpi-impl=openmpi --sample=none --cpuctxsw=none --gpu-metrics-devices=none --force-overwrite=true --output="trace-rank${rank}" "$@"
