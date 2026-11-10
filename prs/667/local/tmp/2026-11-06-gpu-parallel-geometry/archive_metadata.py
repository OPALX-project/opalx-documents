from pathlib import Path
import tarfile
s=Path(__file__).resolve().parent
with tarfile.open(s/'results-metadata.tgz','w:gz') as t:
 for d in sorted(s.glob('gpu-*')):
  if not d.is_dir():continue
  for name in ['case.in','case.out','case.stat','timing.dat','run.json','geometry-kernels.json']:
   p=d/name
   if p.exists():t.add(p,arcname=str(p.relative_to(s)))
 for pattern in ['unit-*.log','probe-*.log','*binary.sha256','source-base.txt','jobs.json','particle-audit-*.json']:
  for p in s.glob(pattern):t.add(p,arcname=p.name)
