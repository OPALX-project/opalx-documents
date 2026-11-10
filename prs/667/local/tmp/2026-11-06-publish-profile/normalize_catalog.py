from pathlib import Path
import json,yaml,hashlib,subprocess,re
r=Path('/Users/adelmann/git/opalx-documents');state=Path('/Users/adelmann/git/opalx/tmp/2026-11-06-publish-profile');paths=json.loads((state/'docs-paths.json').read_text());renames={}
for x in paths:
 if x!=x.lower():
  old=r/x;new=r/x.lower();old.rename(new);renames[x]=x.lower()
paths=[renames.get(x,x) for x in paths];(state/'docs-paths.json').write_text(json.dumps(paths,indent=2))
p=r/'manifest.yml';data=yaml.safe_load(p.read_text());old=subprocess.check_output(['git','show','HEAD:manifest.yml'],cwd=r).decode();blocks=re.split(r'(?m)(?=^  - title:)',old);by={yaml.safe_load('assets:\n'+b)['assets'][0]['destination']:b for b in blocks[1:]};chunks=[]
for a in data['assets']:
 a['destination']=renames.get(a['destination'],a['destination']);f=r/a['destination']
 if a['destination'].startswith('examples/2026/2d5-1/') and f.exists():a['sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 prev=by.get(a['destination']);obj=yaml.safe_load('assets:\n'+prev)['assets'][0] if prev else None
 chunks.append(prev.rstrip()+'\n\n' if obj==a else ''.join('  '+line+'\n' for line in yaml.safe_dump([a],sort_keys=False,allow_unicode=True,width=130).splitlines())+'\n')
p.write_text(blocks[0]+''.join(chunks));print('lowercase catalog names',len(renames))
