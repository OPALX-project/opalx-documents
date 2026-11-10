from pathlib import Path
import hashlib,io,json,subprocess,tarfile
root=Path('/Users/adelmann/git/opalx-master');out=root/'tmp/pr637-audit-fixes-20261109/a100'
base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();assert base=='b1551b9c337c0c57dd21a4e2e26ccaff10fdfc93'
files={}
for row in subprocess.check_output(['git','ls-files','--stage','-z'],cwd=root).decode().split('\0'):
    if not row:continue
    meta,name=row.split('\t',1);mode=meta.split()[0]
    if mode=='160000':continue
    assert mode in ('100644','100755'),(mode,name)
    files[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
intended=json.loads((root/'tmp/pr637-audit-fixes-20261109/intended-files.json').read_text())
for name,sha in intended['files'].items():assert files[name]==sha,(name,sha,files[name])
source_id=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
manifest=dict(base_head=base,source_id=source_id,description='PR637 head plus uncommitted audit fixes2/5/6 with CUDA accessibility correction',files=files)
archive=out/f'source-{source_id[:12]}.tar.gz'
assert not archive.exists(),'Refusing duplicate source archive overwrite'
with tarfile.open(archive,'w:gz') as tar:
    for name in sorted(files):tar.add(root/name,arcname=name,recursive=False)
    data=(json.dumps(manifest,indent=2)+'\n').encode();info=tarfile.TarInfo('source-manifest.json');info.size=len(data);info.mode=0o644;tar.addfile(info,io.BytesIO(data))
(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
plan=dict(source_id=source_id,base_head=base,archive=str(archive),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),source_files=len(files),intended_changes_verified=len(intended['files']),remote_root=f'/data/user/adelmann/opalx-dev/pr637-audit-fixes-20261109/{source_id[:12]}')
(out/'submission-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps(plan,indent=2))
