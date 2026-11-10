"""Check retained hashes, text-only policy and matching catalog entries."""
from pathlib import Path
import hashlib,json,yaml
root=Path(__file__).resolve().parents[1];repo=root.parents[1]
assets={a['destination']:a for a in yaml.safe_load((repo/'manifest.yml').read_text())['assets']}
rows=json.loads((root/'inventory.json').read_text())
for row in rows:
 if row['disposition']=='repository-copy':
  p=root/row['archive'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],p
files=[p for p in root.rglob('*') if p.is_file() and p.name!='.DS_Store']
for p in files:
 data=p.read_bytes();assert len(data)<=1024*1024 and b'\0' not in data,p;data.decode('utf-8')
 rel=p.relative_to(repo).as_posix();assert rel==rel.lower(),rel
 assert hashlib.sha256(data).hexdigest()==assets[rel]['sha256'],p
print(f'Verified {len(files)} small text assets and all retained original hashes.')
