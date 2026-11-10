from pathlib import Path
import hashlib,json,os,subprocess,tarfile
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');task=root/'ownership-20261109';source=root/'src';build=root/'build'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((task/'source-update.json').read_text());assert digest(task/'source-update.tgz')==record['archive_sha256']
original=json.loads((task/'before/inventory.json').read_text());assert (task/'before/terminal-verification.json').is_file()
assert digest(root/'validation-evidence.tgz')==original['frozen_prior_archive']
for name,h in original['source_sha256'].items():assert digest(source/name)==h,name
assert not(source/'unit_tests/TemporaryDirectory.h').exists()
lib=digest(build/'src/libopalx.so');assert lib==original['binary_sha256']['src/libopalx.so']
with tarfile.open(task/'source-update.tgz') as tar:
 members={m.name:m for m in tar.getmembers()};assert 'manifest.json'in members
 for name,m in members.items():
  p=Path(name);assert not p.is_absolute() and '..'not in p.parts and m.isfile(),name
 manifest=json.loads(tar.extractfile('manifest.json').read());assert set(members)==set(manifest['files'])|{'manifest.json'}
 expected=dict(original['source_sha256']);target_paths={}
 for name,h in manifest['files'].items():
  assert name.startswith('unit_tests/') and Path(name).suffix in ['.cpp','.h'],name
  data=tar.extractfile(name).read();assert hashlib.sha256(data).hexdigest()==h,name
  if name.endswith('.cpp'):target_paths[Path(name).stem]=name
 assert set(target_paths)==set(manifest['targets'])
 listing=json.loads(subprocess.check_output(['ctest','--test-dir',str(build),'--show-only=json-v1'],text=True));entries={x['name']:x for x in listing['tests']}
 binary_hashes={}
 for name in manifest['targets']:
  binaries=[Path(x)for x in entries[name]['command']if Path(x).name==name];assert len(binaries)==1,(name,binaries)
  binary_hashes[name]=digest(binaries[0])
 for name,h in manifest['files'].items():
  data=tar.extractfile(name).read();path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);os.utime(path,None);assert digest(path)==h,name;expected[name]=h
 for name,h in expected.items():assert digest(source/name)==h,name
 for name,h in manifest['prior_files_unchanged'].items():assert digest(source/name)==h,name
 (task/'manifest.json').write_text(json.dumps(manifest,indent=2))
 stage={'manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),'expected_source_sha256':expected,'baseline_binary_sha256':binary_hashes,'production_library_sha256':lib,'prior_archive_sha256':original['frozen_prior_archive'],'source_files_verified':len(expected),'changed_files':len(manifest['files']),'targets':manifest['targets'],'source_write_method':'write_bytes+utime; no copied timestamps'}
 (task/'stage.json').write_text(json.dumps(stage,indent=2))
 print(json.dumps({k:v for k,v in stage.items()if k not in ['expected_source_sha256','baseline_binary_sha256']}))
