"""Keep PR637 source/summary evidence; remove generated run-output bulk."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
state=json.loads((ROOT/'task-state.json').read_text());assert not state.get('compacted'), 'Already compacted'
refs=set()
for p in ROOT.rglob('*.in'):
 refs.update(Path(m).name.lower() for m in re.findall(r'(?:FNAME|FMAPFN|REFPATHFNAME)\s*=\s*["\']([^"\']+)',p.read_text(),re.I))
keep_ext={'.md','.py','.in','.json','.csv','.patch','.tex','.tikz','.sh','.sbatch','.cpp','.h','.hpp','.cmake','.yml','.yaml','.sha256'}
keep=[];drop=[]
for p in ROOT.rglob('*'):
 if not p.is_file():continue
 yes=p.suffix.lower() in keep_ext and 'elementpositions' not in p.name.lower()
 if p.suffix=='.txt':yes=p.name=='cmakelists.txt' or (p.stat().st_size<10000 and p.name not in ['link.txt','ctestcostdata.txt'])
 if p.suffix in ['.dat','.dist','.map','.g4blmap']:yes=p.name in refs and p.stat().st_size<=128*1024
 (keep if yes else drop).append(p)
original_bytes=sum(p.stat().st_size for p in keep+drop);removed_bytes=sum(p.stat().st_size for p in drop)
removed={p.relative_to(ROOT).as_posix() for p in drop};guards={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in keep}
# Update original provenance records so they never claim removed files remain.
index=json.loads((ROOT/'inventory.json').read_text())
for part in index['parts']:
 p=ROOT/part;rows=json.loads(p.read_text())
 for x in rows:
  if x.get('archive') in removed:
   x['disposition']='removed-generated-output-during-compaction';x['removed_archive']=x.pop('archive')
 p.write_text(json.dumps(rows,indent=2)+'\n')
p=ROOT/'system-tmp-inventory.json';rows=json.loads(p.read_text())
for x in rows:
 if x['archive'] in removed:x['disposition']='removed-generated-output-during-compaction';x['removed_archive']=x.pop('archive')
p.write_text(json.dumps(rows,indent=2)+'\n')
counts=Counter(p.suffix for p in drop)
for p in drop:p.unlink()
for p in sorted(ROOT.rglob('*'),key=lambda p:len(p.parts),reverse=True):
 if p.is_dir() and not any(p.iterdir()):p.rmdir()
modified=set(index['parts'])|{'system-tmp-inventory.json'}
for rel,h in guards.items():
 if rel not in modified:assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
summary=dict(before_bytes=original_bytes,removed_bytes=removed_bytes,removed_files=len(drop),removed_by_extension=dict(counts),policy='Keep notes, analysis scripts, input decks, source patches and compact JSON/CSV validation summaries. Remove generated orbit/display tables, run statistics, bulk logs and CI output. Retain small data/map files directly named by input decks.',original_inputs_retained=sum(p.suffix=='.in' for p in keep),development_notes_retained=sum(p.suffix=='.md' for p in keep))
(ROOT/'compaction.json').write_text(json.dumps(summary,indent=2)+'\n')
state.update(compacted=True,compaction_removed_files=len(drop),compaction_removed_bytes=removed_bytes,retained_files_after_compaction=sum(p.is_file() for p in ROOT.rglob('*')))
(ROOT/'task-state.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps(summary,indent=2))
