"""Verify original retained bytes, text-only archive policy and catalog digests."""
from pathlib import Path
import hashlib,json,yaml
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
assets={a['destination']:a for a in yaml.safe_load((repo/'manifest.yml').read_text())['assets']}
index=json.loads((root/'inventory.json').read_text());rows=[r for part in index['parts'] for r in json.loads((root/part).read_text())]
rows+=json.loads((root/'system-tmp-inventory.json').read_text())
for row in rows:
 if row.get('disposition')=='retained-text' or 'disposition' not in row:
  p=root/row['archive'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],p
files=[p for p in root.rglob('*') if p.is_file() and p.name!='.DS_Store']
for p in files:
 b=p.read_bytes();assert len(b)<=1024*1024 and b'\0' not in b,p;b.decode('utf-8')
 rel=p.relative_to(repo).as_posix();assert rel==rel.lower();assert hashlib.sha256(b).hexdigest()==assets[rel]['sha256'],p
print(f'Verified {len(files)} small PROBE text assets and original retained hashes.')
