"""Verify small text records, then remove the explicitly inventoried local PR667 caches.

The user authorized deletion of local snapshots, traces and saved executables.
No remote run directories, published examples, or unrelated working files are touched.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path('/Users/adelmann/git/opalx')
OUT=Path('/Users/adelmann/git/opalx-documents/prs/667')
state=json.loads((OUT/'task-state.json').read_text());rows=json.loads((OUT/'inventory.json').read_text())
assert state['phase']=='archive-verified'
limit=1024*1024

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard():
 for key in ['tracked_guard','untracked_guard']:
  for rel,h in state[key].items():assert sha(ROOT/rel)==h,rel

guard()
for x in rows:
 if x['disposition']=='repository-copy':
  p=OUT/x['archive'];assert sha(p)==x['sha256'],p
  try:
   p.read_text(encoding='utf-8');plain=b'\0' not in p.read_bytes()
  except UnicodeError:plain=False
  if p.stat().st_size>limit or not plain:
   p.unlink();x.update(disposition='deleted-large-or-binary');x.pop('archive')
 elif x['disposition']=='external-object':
  x.update(disposition='deleted-large-or-binary');x.pop('archive')
 elif x['disposition']=='regenerable':x['disposition']='deleted-regenerable'
# Remove empty subdirectories and the no-longer-applicable archive/restore tools.
for p in sorted((OUT/'local').rglob('*'),key=lambda p:len(p.parts),reverse=True):
 if p.is_dir() and not any(p.iterdir()):p.rmdir()
for name in ['archive_local.py','restore_local.py']:(OUT/'tools'/name).unlink()
external=Path(state['external_artifacts']);assert external==Path('/Users/adelmann/git/opalx-pr667-local-artifacts')
state['policy']='Only UTF-8 text files up to 1 MiB each retained; local large/raw/binary data deleted by user instruction. Remote merlin6 runs untouched.'
state['phase']='text-archive-verified-ready-to-delete'
(OUT/'inventory.json').write_text(json.dumps(rows,indent=2)+'\n');(OUT/'task-state.json').write_text(json.dumps(state,indent=2)+'\n')
# Every removal root is inside OPALX, explicitly listed and contains no tracked files.
bytes_removed=0
for rel in state['remove_roots']:
 p=ROOT/rel;assert p.exists(),p;assert not p.is_symlink(),p
 assert p.resolve().is_relative_to(ROOT) and p.resolve()!=ROOT
 tracked=subprocess.check_output(['git','ls-files','--',rel],cwd=ROOT,text=True);assert not tracked,rel
 bytes_removed+=sum(q.lstat().st_size for q in p.rglob('*') if q.is_file() and not q.is_symlink()) if p.is_dir() else p.stat().st_size
for rel in state['remove_roots']:
 p=ROOT/rel
 if p.is_dir():shutil.rmtree(p)
 else:p.unlink()
shutil.rmtree(external)
guard()
state.update(phase='complete',removed_local_bytes=bytes_removed,retained_text_files=sum(x['disposition']=='repository-copy' for x in rows),retained_text_bytes=sum(x['size'] for x in rows if x['disposition']=='repository-copy'),external_artifacts_deleted=True)
(OUT/'task-state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({k:state[k] for k in ['phase','removed_local_bytes','retained_text_files','retained_text_bytes','external_artifacts_deleted']},indent=2))
