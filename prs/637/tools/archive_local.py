"""Archive small PR637 text records, verify hashes; delete nothing."""
from pathlib import Path
import hashlib,json,subprocess,shutil
ROOT=Path('/Users/adelmann/git/opalx-master');OUT=Path('/Users/adelmann/git/opalx-documents/prs/637')
notes=['ACCELERATING_SC_STATE.md','COASTING_FIX_STATE.md','CONSOLIDATION_STATE.md','GH200_BUILD_STATE.md','PROBE_PLAN.md']
roots=[p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'tmp').iterdir())]+notes+['build_openmp']
state={'goal':'Archive merged PR637 notes, scripts, inputs, logs and LaTeX; verify before deleting local tmp/build data.','phase':'inventory','source_root':str(ROOT),'source_branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'delete_roots':roots,'tracked_guard':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()},'policy':'Only UTF-8 text <=1MiB/file, no snapshots/traces/images/executables; tracked source untouched; no commits or pushes.'}
(OUT/'task-state.json').write_text(json.dumps(state,indent=2)+'\n');rows=[]
files=set()
for rel in roots:
 p=ROOT/rel
 if rel=='build_openmp':
  files.update(p.rglob('CMakeCache.txt'));files.update(p.glob('*.md'));files.update(p.glob('compile_commands.json'));files.update(q for q in (p/'Testing').rglob('*') if q.is_file())
 elif p.is_dir():files.update(q for q in p.rglob('*') if q.is_file() and not q.is_symlink())
 else:files.add(p)
files.update(ROOT.glob('src/Fields/Interpolation/*.tex'))
files.update(p for p in [ROOT/'tools/check_cyclotron_probe.py',ROOT/'tools/probe_frame_adapter.py'] if p.exists())
for p in sorted(files):
 b=p.read_bytes();row={'original':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 try:b.decode('utf-8');plain=b'\0' not in b
 except UnicodeError:plain=False
 if plain and len(b)<=1024*1024 and p.suffix.lower() not in ['.pdf','.svg','.png','.pyc'] and '__pycache__' not in p.parts:
  dst=OUT/'local'/row['original'].lower();dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==b,dst
  else:shutil.copy2(p,dst)
  assert hashlib.sha256(dst.read_bytes()).hexdigest()==row['sha256'],p
  row.update(disposition='retained-text',archive=dst.relative_to(OUT).as_posix())
 else:row['disposition']='excluded-large-binary-or-generated'
 rows.append(row)
parts=[];folder=OUT/'inventory';folder.mkdir(exist_ok=True)
for i in range(0,len(rows),300):
 name=f'inventory/part-{i//300+1:03}.json';(OUT/name).write_text(json.dumps(rows[i:i+300],indent=2)+'\n');parts.append(name)
(OUT/'inventory.json').write_text(json.dumps({'parts':parts,'count':len(rows)},indent=2)+'\n')
state.update(phase='copied-and-hash-verified',retained_files=sum(x['disposition']=='retained-text' for x in rows),retained_bytes=sum(x['bytes'] for x in rows if x['disposition']=='retained-text'))
(OUT/'task-state.json').write_text(json.dumps(state,indent=2)+'\n');print('PR637 retained',state['retained_files'],'small text files; original records',len(rows))
