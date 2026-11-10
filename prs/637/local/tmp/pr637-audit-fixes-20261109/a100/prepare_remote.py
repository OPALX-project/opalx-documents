from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
root=Path('/data/user/adelmann/opalx-dev/pr637-audit-fixes-20261109/3320cf6fc490')
for parent in [Path('/'),Path('/data'),Path('/data/user'),Path('/data/user/adelmann'),Path('/data/user/adelmann/opalx-dev'),root.parent]:
    p=parent/'AGENTS.md'
    if p.is_file():
        print('Inspect remote instructions before proceeding: '+str(p)+'\n'+p.read_text(),flush=True)
        raise SystemExit(2)
archive=root/'source.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='85722baa2123dc044f6d88dab95e6e2813e18d0ba75eab4d1c353a9e3f3ce22d'
source=root/'src';assert not source.exists(),'Refusing to overlay prior source'
source.mkdir()
with tarfile.open(archive) as tar:
    for member in tar.getmembers():
        p=Path(member.name)
        assert not p.is_absolute() and '..' not in p.parts
        assert member.isfile() or member.isdir(),member.name
    tar.extractall(source)
m=json.loads((source/'source-manifest.json').read_text())
assert m['source_id']=='3320cf6fc490a8be7dc2a33468b35cd99804cf179fd13d07f4d62d00e4bc2ae3'
for name,digest in m['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
(source/'src/OPALXrevision.h').write_text('#define GIT_VERSION "audit-source-'+'3320cf6fc490a8be7dc2a33468b35cd99804cf179fd13d07f4d62d00e4bc2ae3'[:12]+' (base b1551b9c3, uncommitted)"\n')
evidence=root/'evidence';evidence.mkdir(exist_ok=True)
(evidence/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
old=Path('/data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643')
expected={'ippl':'d6216553e39dcf4405849c027517cc3401fefee5','kokkos':'8e15454876298832f013ebcaf08d53825b5bda40','heffte':'6e16996e5a3eb65c60fd62fd4d93c4b2df833033','gtest':'6910c9d9165801d8827d628cb72eb7ea9dd538c5','h5hut':'b5c74f760bc9919d409f46b5472e9eedf9a764d5'}
deps=root/'deps';deps.mkdir()
report={}
for name,sha in expected.items():
    seed=old/'deps'/(name+'-src');target=deps/(name+'-src')
    assert subprocess.check_output(['git','-C',str(seed),'status','--porcelain'],text=True).strip()=='',name
    actual=subprocess.check_output(['git','-C',str(seed),'rev-parse','HEAD'],text=True).strip();assert actual==sha,(name,actual)
    subprocess.run(['git','clone','--shared','--no-checkout',str(seed),str(target)],check=True)
    subprocess.run(['git','-C',str(target),'checkout','--detach',sha],check=True)
    report[name]={'sha':sha,'source':str(target),'seed':str(seed)}
for name in ['hdf5','opalx_lapack']:
    seed=old/'build/_deps'/(name+'-src');target=deps/(name+'-src')
    assert seed.is_dir(),str(seed)
    if (seed/'.git').exists():
        assert subprocess.check_output(['git','-C',str(seed),'status','--porcelain'],text=True).strip()=='',name
        sha=subprocess.check_output(['git','-C',str(seed),'rev-parse','HEAD'],text=True).strip()
        subprocess.run(['git','clone','--shared','--no-checkout',str(seed),str(target)],check=True)
        subprocess.run(['git','-C',str(target),'checkout','--detach',sha],check=True)
        report[name]={'sha':sha,'source':str(target),'seed':str(seed)}
    else:
        shutil.copytree(seed,target,symlinks=True)
        report[name]={'source':str(target),'seed':str(seed),'method':'isolated source copy, no modifications'}
# IPPL3.4 hardcodes this launcher source cache path even with source overrides.
launcher=root/'build/_deps/ippl-build/_deps/kokkos-src'
launcher.parent.mkdir(parents=True,exist_ok=True)
launcher.symlink_to(deps/'kokkos-src',target_is_directory=True)
(evidence/'dependency-sources.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'source_id':m['source_id'],'verified_files':len(m['files']),'dependencies':report},indent=2),flush=True)
