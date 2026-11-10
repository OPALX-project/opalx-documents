"""Compact PR667 output bulk while retaining source/input and summary evidence.

Byte-identical JSON/CSV copies in historical report bundles share an existing
canonical archive file. The LaTeX inventory restores their original paths in a
scratch checkout, so all document variants remain buildable.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1];STATE=ROOT/'task-state.json'
state=json.loads(STATE.read_text());assert not state.get('compacted'), 'Already compacted'
files=[p for p in ROOT.rglob('*') if p.is_file() and p.name!='.DS_Store']
before=sum(p.stat().st_size for p in files);protected={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.suffix in ['.tex','.tikz','.bib','.cls','.sty'] or p.relative_to(ROOT).parts[0]=='inputs'}
keep_ext={'.md','.py','.in','.json','.csv','.patch','.tex','.tikz','.bib','.sty','.cls','.sh','.sbatch','.cpp','.h','.hpp','.cu','.diff','.awk','.cmake','.yml','.yaml','.sha256'}
kept=[];removed=[];renames={};aliases={};hashes={}
for p in sorted(files):
 rel=p.relative_to(ROOT).as_posix();yes=p.suffix.lower() in keep_ext and 'elementpositions' not in p.name.lower() and '.matplotlib' not in p.parts
 if p.suffix=='.csv':yes=p.stat().st_size<=65536 or rel.startswith('checkout-text/docs/validation/fft2d5/uniform-b-ellipsoid/report/data/figure-inputs/')
 if p.suffix=='.txt':yes=p.stat().st_size<=10000 and p.name not in ['link.txt','ctestcostdata.txt']
 if p.name=='.gitignore' or rel.startswith('inputs/'):yes=True
 (kept if yes else removed).append(p)
# Archived ignore rules are evidence, not active rules for the archive itself.
for p in kept:
 if p.name=='.gitignore':
  old=p.relative_to(ROOT).as_posix();q=p.with_name('original-gitignore.txt');assert not q.exists();shutil.copy2(p,q)
  assert q.read_bytes()==p.read_bytes() and not q.samefile(p);p.unlink();renames[old]=q.relative_to(ROOT).as_posix()
# Prefer existing primary report data; deduplicate only historical report-bundle data.
canonical={}
for p in sorted(kept,key=lambda p:(str(p).startswith(str(ROOT/'checkout-text/tmp/')),str(p))):
 old=p.relative_to(ROOT).as_posix();p=ROOT/renames.get(old,old)
 if p.suffix not in ['.json','.csv']:continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if old.startswith('checkout-text/tmp/pdfs/') and h in canonical:
  aliases[old]=canonical[h]
 else:canonical.setdefault(h,p.relative_to(ROOT).as_posix())
# Historical copies of retained canonical figure-input CSVs remain addressable via inventory.
actual_removed=[]
for p in removed:
 rel=p.relative_to(ROOT).as_posix()
 if p.suffix in ['.json','.csv'] and rel.startswith('checkout-text/tmp/pdfs/'):
  h=hashlib.sha256(p.read_bytes()).hexdigest()
  if h in canonical:aliases[rel]=canonical[h];continue
 actual_removed.append(p)
removed_paths={p.relative_to(ROOT).as_posix() for p in actual_removed};all_deletions=removed_paths|set(aliases)
# Preserve provenance, distinguishing deliberately discarded records from retained aliases.
def update(rows,latex=False):
 for x in rows:
  field='archive';value=x.get(field)
  # LaTeX inventory paths are relative to opalx-documents, not this PR folder.
  rel=value[len('prs/667/'):] if latex and value and value.startswith('prs/667/') else value
  if rel in renames:
   x[field]=('prs/667/' if latex else '')+renames[rel]
  elif rel in aliases:
   x[field]=('prs/667/' if latex else '')+aliases[rel];x['deduplicated_original_archive']=value
  elif rel in removed_paths:
   x['removed_archive']=x.pop(field);x['disposition']='removed-generated-output-during-compaction'
 return rows
p=ROOT/'inventory.json';p.write_text(json.dumps(update(json.loads(p.read_text())),indent=2)+'\n')
index=json.loads((ROOT/'latex-inventory.json').read_text())
for part in index['parts']:
 p=ROOT/part;p.write_text(json.dumps(update(json.loads(p.read_text()),latex=True),indent=2)+'\n')
# Check all alias targets before deleting duplicates.
for old,target in aliases.items():assert hashlib.sha256((ROOT/old).read_bytes()).digest()==hashlib.sha256((ROOT/target).read_bytes()).digest(),old
removed_bytes=sum((ROOT/p).stat().st_size for p in all_deletions)
for rel in all_deletions:(ROOT/rel).unlink()
for p in sorted(ROOT.rglob('*'),key=lambda p:len(p.parts),reverse=True):
 if p.is_dir() and not any(p.iterdir()):p.rmdir()
for rel,h in protected.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
summary=dict(before_bytes=before,removed_bytes=removed_bytes,removed_files=len(removed_paths),deduplicated_files=len(aliases),protected_latex_sources=sum(Path(x).suffix in ['.tex','.tikz','.bib','.cls','.sty'] for x in protected),protected_input_support_files=sum(x.startswith('inputs/') for x in protected),policy='Preserve LaTeX/TikZ and build inventories, OPALX/PyORBIT input packages, analysis code, notes and compact summaries. Remove bulk logs/statistics, generated displays, high-resolution raw tables and caches. Deduplicate byte-identical historical report JSON/CSV through inventory aliases.')
(ROOT/'compaction.json').write_text(json.dumps(summary,indent=2)+'\n')
state.update(compacted=True,compaction_removed_files=len(removed_paths),compaction_deduplicated_files=len(aliases),compaction_removed_bytes=removed_bytes,compaction_policy=summary['policy']);STATE.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(summary,indent=2))
