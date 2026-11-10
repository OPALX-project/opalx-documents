"""Refresh only the requested PR archives and their LaTeX figure/report assets."""
from pathlib import Path
import hashlib,json
repo=Path(__file__).resolve().parents[3]
prefixes=['prs/667/','prs/637/','examples/2026/2d5-1/latex-assets/','reports/2026/pr667/','reports/2026/pr637/']
m=repo/'manifest.yml';parts=m.read_text().split('\n  - title:')
text=parts[0]+''.join('\n  - title:'+p for p in parts[1:] if not any('destination: "'+q in p for q in prefixes))
count=0
for prefix in prefixes:
 for p in sorted((repo/prefix).rglob('*')):
  if not p.is_file() or p.name=='.DS_Store':continue
  rel=p.relative_to(repo).as_posix();b=p.read_bytes();assert rel==rel.lower(),rel
  if rel.startswith('prs/'):
   assert len(b)<=1024*1024 and b'\0' not in b,p;b.decode('utf-8')
  row=dict(title='Merged PR archive — '+rel,date=None,category=rel.split('/')[0],source='Local OPALX PR667/PR637 supporting records, archived2026-11-10. See each archive inventory and LaTeX validation record.',destination=rel,description='PR folders contain small text only. Required compact LaTeX figure assets and compiled reports are cataloged separately. Historical experimental models are distinguished from merged solver behavior.',status='archived',sha256=hashlib.sha256(b).hexdigest())
  text+='\n  - '+'\n    '.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in row.items())+'\n';count+=1
m.write_text(text);print('Cataloged',count,'archive/report/figure assets.')
