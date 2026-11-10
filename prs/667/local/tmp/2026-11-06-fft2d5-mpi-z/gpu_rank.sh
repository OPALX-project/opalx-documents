#!/bin/bash
set -euo pipefail
IFS=',' read -r -a task_devices <<< "${CUDA_VISIBLE_DEVICES:?}"
task_rank=${OMPI_COMM_WORLD_LOCAL_RANK:?}
export CUDA_VISIBLE_DEVICES=${task_devices[$task_rank]:?}
exec "$@"
