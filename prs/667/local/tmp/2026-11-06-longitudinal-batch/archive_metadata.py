from pathlib import Path
import tarfile
s=Path(__file__).resolve().parent
with tarfile.open(s/'results-metadata.tgz','w:gz') as t:
 for d in sorted(s.glob('gpu-*')):
  if not d.is_dir():continue
  for name in ['case.in','case.out','case.stat','timing.dat','run.json','density-launches.json','export.log']:
   p=d/name
   if p.exists():t.add(p,arcname=str(p.relative_to(s)))
 for pattern in ['after-*.log','baseline-*.log','*binary*.sha256','*binaries.sha256','*-particle-audit.json','*-source.txt']:
  for p in s.glob(pattern):t.add(p,arcname=p.name)
