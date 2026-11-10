from pathlib import Path
import subprocess,yaml,hashlib,re,zipfile
r=Path('/Users/adelmann/git/opalx-documents');d=yaml.safe_load(subprocess.check_output(['git','show',':manifest.yml'],cwd=r));assets=d['assets'];errors=[];seen=set();tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=r).decode().split('\0'))-{''};infra={'.gitattributes','.gitignore','README.md','manifest.yml'};catalog={p for p in tracked if p not in infra and not p.startswith(('.github/','scripts/'))};dest=set()
for a in assets:
 p=a['destination'];dest.add(p);f=r/p
 if p in seen:errors.append('duplicate '+p)
 seen.add(p)
 if p!=p.lower() or ' ' in p:errors.append('name '+p)
 if not f.is_file():errors.append('missing '+p);continue
 if hashlib.sha256(f.read_bytes()).hexdigest()!=a['sha256']:errors.append('hash '+p)
 if isinstance(a['date'],str) and re.fullmatch(r'\d{4}(-\d{2}){0,2}',a['date']) and not f.name.startswith(a['date']):errors.append('date '+p)
 if p.endswith(('.h5','.hdf5','.npz')):errors.append('particle '+p)
 if f.suffix=='.zip':
  with zipfile.ZipFile(f) as z:
   if any(n.endswith(('.h5','.hdf5','.npz')) for n in z.namelist()):errors.append('embedded particle '+p)
for p in catalog-dest:errors.append('uncataloged '+p)
for p in dest-catalog:errors.append('not staged '+p)
base=yaml.safe_load(subprocess.check_output(['git','show','HEAD:manifest.yml'],cwd=r));base_dest={a['destination'] for a in base['assets']};base_tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=r).decode().splitlines());base_catalog={p for p in base_tracked if p not in infra and not p.startswith(('.github/','scripts/'))}
inherited={*('uncataloged '+p for p in base_catalog-base_dest),*('not staged '+p for p in base_dest-base_catalog)}
new=[e for e in errors if e not in inherited]
print('Validated staged catalog:',len(dest),'files. New errors:',len(new));print('Inherited unrelated catalog errors:',[e for e in errors if e in inherited]);print('\n'.join(new[:30]));assert not new
