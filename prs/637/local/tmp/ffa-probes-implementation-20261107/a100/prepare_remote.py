import hashlib,json,pathlib,shutil,subprocess,tarfile
root=pathlib.Path('/data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643')
for path in ['/AGENTS.md','/data/AGENTS.md','/data/user/AGENTS.md','/data/user/adelmann/opalx-dev/opalx-probe-615/AGENTS.md']:
 p=pathlib.Path(path)
 if p.is_file():
  print('New instructions require inspection: '+str(p)+'\n'+p.read_text(),flush=True);raise SystemExit(2)
archive=root/'source.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='79fecb6412362da127d7a9e42bb1a18a7699e267d0c85e8bcd44a0d9bcce2624'
src=root/'src'
assert not src.exists(),'Refusing to overlay an existing source snapshot'
src.mkdir()
with tarfile.open(archive) as tar:
 for member in tar.getmembers():
  name=pathlib.PurePosixPath(member.name)
  assert not name.is_absolute() and '..' not in name.parts
  assert member.isfile() or member.isdir(),'Unexpected archive link '+member.name
 tar.extractall(src)
manifest=json.loads((src/'source-manifest.json').read_text())
assert manifest['source_id']=='790abac196432fcfca893ad73d0e045de4efca21768a32fa6cfc33a53ba47afa'
for name,expected in manifest['files'].items():
 assert hashlib.sha256((src/name).read_bytes()).hexdigest()==expected,name
# Generated, untracked build metadata; immutable source manifest remains unchanged.
(src/'src/OPALXrevision.h').write_text('#define GIT_VERSION "source-790abac19643 (base ec4319ac)"\n')
(root/'evidence/source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Verified all '+str(len(manifest['files']))+' source files',flush=True)
old=pathlib.Path('/data/user/adelmann/opalx-dev/opalx-probe-615/build/gwendolen-cuda132-shared-release/_deps')
deps=root/'deps';deps.mkdir()
seeds={
 'gtest':(old/'gtest-src','6910c9d9165801d8827d628cb72eb7ea9dd538c5'),
 'h5hut':(old/'h5hut-src','b5c74f760bc9919d409f46b5472e9eedf9a764d5'),
 'kokkos':(old/'ippl-build/_deps/kokkos-src','8e15454876298832f013ebcaf08d53825b5bda40'),
 'heffte':(old/'ippl-build/_deps/heffte-src','6e16996e5a3eb65c60fd62fd4d93c4b2df833033'),
}
report={}
for name,(seed,sha) in seeds.items():
 assert subprocess.check_output(['git','-C',str(seed),'status','--porcelain'],text=True).strip()=='',name
 actual=subprocess.check_output(['git','-C',str(seed),'rev-parse','HEAD'],text=True).strip();assert actual==sha,(name,actual)
 target=deps/(name+'-src')
 subprocess.run(['git','clone','--shared','--no-checkout',str(seed),str(target)],check=True)
 subprocess.run(['git','-C',str(target),'checkout','--detach',sha],check=True)
 report[name]={'sha':sha,'source':str(target),'seed':str(seed)}
 print('Prepared isolated '+name,flush=True)
# Current project dependency, not the old checkout's unrelated IPPL master.
ippl=deps/'ippl-src'
subprocess.run(['git','clone','--branch','IPPL-3.4.0','--depth','1','https://github.com/IPPL-framework/ippl.git',str(ippl)],check=True)
sha=subprocess.check_output(['git','-C',str(ippl),'rev-parse','HEAD'],text=True).strip()
assert sha=='d6216553e39dcf4405849c027517cc3401fefee5',sha
report['ippl']={'sha':sha,'source':str(ippl)}
(root/'evidence/dependency-sources.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'source_id':manifest['source_id'],'files_verified':len(manifest['files']),'dependencies':report},indent=2),flush=True)
