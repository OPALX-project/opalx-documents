from pathlib import Path
import subprocess,hashlib,json,shutil,zipfile,re,yaml
repo=Path('/Users/adelmann/git/opalx-documents');root=repo/'examples/2026/2d5-1';native=Path('/Users/adelmann/git/opalx/tmp/2026-11-06-r2c-integration');study=root/'r2c-row-integration-2026-11-06'
snapshots={}
for p in study.rglob('*.h5'):
 name=p.parent.name;dst=native/name/'case.h5';dst.parent.mkdir(parents=True,exist_ok=True)
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 if not dst.exists():shutil.copy2(p,dst)
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==sha
 snapshots[name]={'local':str(dst),'remote':f'/psi/home/adelmann/opalx-dev/dba/validation-r2c-rows-20261106/{name}/case.h5' if name.startswith('gpu') else None,'sha256':sha,'bytes':p.stat().st_size}
 p.unlink() # duplicate removed only after verification at the native run/cache location
(study/'snapshot-locations.json').write_text(json.dumps(snapshots,indent=2)+'\n')
p=study/'analyze.py';s=p.read_text();s=s.replace('def endpoint(path):\n with h5py.File(path) as f:', '''def endpoint(path):
 if not path.exists():
  locations=json.loads((ROOT/'snapshot-locations.json').read_text())
  external=Path(os.environ.get('OPALX_SNAPSHOT_ROOT',str(Path(locations[path.parent.name]['local']).parent.parent)))/path.parent.name/path.name
  if not external.exists():
   raise FileNotFoundError(f"External particle snapshot required: {external}; set OPALX_SNAPSHOT_ROOT. Published plots/CSVs need no snapshots.")
  assert __import__('hashlib').sha256(external.read_bytes()).hexdigest()==locations[path.parent.name]['sha256']
  path=external
 with h5py.File(path) as f:''');p.write_text(s)
p=study/'README.md';s=p.read_text().replace('statistics, final particles and timers are retained under `provenance`.','statistics and timers are retained under `provenance`. Particle snapshots stay at their native run/cache locations, listed with checksums in `snapshot-locations.json`; they are not committed.').replace('Run `analyze.py` with the OPALX Python environment','Set `OPALX_SNAPSHOT_ROOT` to a directory containing the named run subdirectories and external `case.h5` files when rerunning the particle audit. Published CSVs and figures can be read without them. Run `analyze.py` with the OPALX Python environment');p.write_text(s)
old=root/'dba-one-turn-analysis-2026-11-06';src=old/'model/source.npz';dst=Path('/Users/adelmann/git/opalx/tmp/2026-11-06-dba-one-turn-analysis/model/source.npz');dst.parent.mkdir(parents=True,exist_ok=True)
if src.exists():
 if not dst.exists():shutil.copy2(src,dst)
 assert hashlib.sha256(src.read_bytes()).hexdigest()==hashlib.sha256(dst.read_bytes()).hexdigest();src.unlink()
p=old/'analyze.py';s=p.read_text().replace("H5_PATH=Path(os.environ.get('OPALX_DBA_H5',str(ROOT/'case.h5')))","H5_PATH=Path(os.environ.get('OPALX_DBA_H5','/Users/adelmann/git/opalx/tmp/2026-11-06-dba-one-turn-analysis/case.h5'))")
s=s.replace("source=np.load(MODEL/'source.npz');assert hashlib.sha256((MODEL/'source.npz').read_bytes()).hexdigest()==meta['source_sha256']","source_path=Path(os.environ.get('OPALX_DBA_SOURCE','/Users/adelmann/git/opalx/tmp/2026-11-06-dba-one-turn-analysis/model/source.npz'))\nsource=np.load(source_path);assert hashlib.sha256(source_path.read_bytes()).hexdigest()==meta['source_sha256']")
p.write_text(s)
with (old/'readme.md').open('a') as f:f.write('\nRaw particles are external: set `OPALX_DBA_H5` for the retained one-turn HDF5 and `OPALX_DBA_SOURCE` for the matched source NPZ. Neither is committed. The local source cache is `/Users/adelmann/git/opalx/tmp/2026-11-06-dba-one-turn-analysis/model/source.npz`. Native Merlin6 run locations and hashes are recorded above and in the manifests.\n')
# Strip particle files even inside the pre-existing input/analysis bundle.
for p in root.rglob('*.zip'):
 if subprocess.check_output(['git','ls-files','--',str(p.relative_to(repo))],cwd=repo).strip():continue
 with zipfile.ZipFile(p) as z:
  entries=[(i,z.read(i.filename)) for i in z.infolist() if not i.filename.endswith(('.h5','.hdf5','.npz'))]
 backup=Path('/Users/adelmann/git/opalx/tmp/2026-11-06-publish-profile')/('native-'+p.name);shutil.copy2(p,backup)
 with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for i,data in entries:z.writestr(i,data)
  z.writestr('EXTERNAL-PARTICLES.txt','Particle snapshots are excluded. Recover initial-state.h5 from the native run locations recorded in the input manifests, or regenerate the matched source using the archived source generator.\n')
# Preserve unrelated manifest entries and update only FFT2D5 asset hashes/catalog entries.
manifest=repo/'manifest.yml';data=yaml.safe_load(manifest.read_text());assets=data['assets'];by={x['destination']:x for x in assets}
files=[repo/p.decode() for p in subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z','--','examples/2026/2d5-1'],cwd=repo).split(b'\0') if p]
selected=[]
for p in files:
 if p.suffix in ['.h5','.hdf5','.npz'] or '__pycache__' in p.parts:continue
 rel=str(p.relative_to(repo));selected.append(rel);a=by.get(rel)
 if not a:
  name=p.relative_to(root);studyname=name.parts[0]
  date=re.match(r'(\d{4}-\d\d-\d\d)-',p.name)
  a=dict(title=f'FFT2D5 {studyname} — {p.name}',date=date.group(1) if date else None,category='examples/2d5-1',source=f'FFT2D5 study working files; collection {studyname}; native runs documented in each report',destination=rel,description='Supporting source, input, summary or figure for the FFT2D5 validation/performance studies. Raw particle snapshots remain external.',status='experimental',sha256='');assets.append(a);by[rel]=a
 a['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
# Refresh hashes for already tracked FFT2D5 assets if their content changed.
for a in assets:
 if a['destination'].startswith('examples/2026/2d5-1/'):
  p=repo/a['destination']
  if p.exists() and p.suffix not in ['.h5','.hdf5','.npz']:a['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
manifest.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True,width=130))
Path('/Users/adelmann/git/opalx/tmp/2026-11-06-publish-profile/docs-paths.json').write_text(json.dumps(['manifest.yml',*selected],indent=2))
print('Selected',len(selected),'FFT2D5 supporting files,',sum((repo/p).stat().st_size for p in selected),'bytes; no snapshots.')
