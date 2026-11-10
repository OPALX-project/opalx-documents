from pathlib import Path
import shutil,json
s=Path(__file__).resolve().parent
out=Path('/Users/adelmann/git/opalx-documents/examples/2026/2d5-1/cleanup-2026-11-07/provenance/gpu')
out.mkdir(parents=True,exist_ok=True)
for name in ['build.log','build-gpu.sbatch','gpu2.sbatch','run_gpu.py','collect_gpu.sh','source-base.txt','after-binary.sha256','probe-1.log','probe-2.log','unit-testfft2d5algorithm-rank1.log','unit-testfft2d5numerics-rank1.log','unit-testfft2d5parallel-rank1.log','unit-parallel-rank2.log']:
 shutil.copy2(s/name,out/name)
for n in [1,2]:
 for mode in ['before','after']:
  d=f'gpu-{n}-{mode}';(out/d).mkdir(exist_ok=True)
  for name in ['case.in','case.out','case.stat','run.json','timing.dat']:shutil.copy2(s/d/name,out/d/name)
for name in ['build-device-constants.log','test-device-constants.log']:
 shutil.copy2(s/name,out/name)
(out/'native-locations.json').write_text(json.dumps(dict(remote='/psi/home/adelmann/opalx-dev/dba/validation-cleanup-20261107',local_cache=str(s),baseline_executable='/psi/home/adelmann/opalx-dev/dba/build/gwendolen-cuda/src/opalx.pre-cleanup-20261107',baseline_sha256='981ce971edc5485c78f48525e517d8242ddbfd456e8e18ea5cf5f51ca1126c43',note='Raw HDF5 snapshots and executables remain external; no full-turn or 16-turn runs.'),indent=2)+'\n')
