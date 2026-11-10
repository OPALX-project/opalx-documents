from pathlib import Path
import hashlib,json,subprocess
r=Path('/Users/adelmann/git/opalx-documents');root=r/'examples/2026/2d5-1/cleanup-2026-11-07'
blocks=[]
for p in sorted(root.rglob('*')):
 if not p.is_file():continue
 assert p.suffix.lower() not in ['.h5','.hdf5','.npz','.sqlite','.pyc','.tgz'],p
 rel=p.relative_to(r).as_posix();name=p.relative_to(root).as_posix()
 row=dict(title='FFT2D5 solver cleanup and verification — '+name,date=None,category='examples/2d5-1',source='CPU Release cleanup validation and paired one/two-A100 jobs355063/355064; source bf5bf8433; native runs /psi/home/adelmann/opalx-dev/dba/validation-cleanup-20261107',destination=rel,description='Study dated 2026-11-07; method decomposition, exact component checks and matched CPU/CUDA tracking and timing audits; native particles/executables remain external.',status='experimental',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 blocks.append('\n  - '+ '\n    '.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in row.items())+'\n')
def rebuild(text):
 parts=text.split('\n  - title:')
 return parts[0]+''.join('\n  - title:'+p for p in parts[1:] if 'examples/2026/2d5-1/cleanup-2026-11-07/' not in p)+''.join(blocks)
manifest=r/'manifest.yml';manifest.write_text(rebuild(manifest.read_text()))
base=subprocess.check_output(['git','show','HEAD:manifest.yml'],cwd=r,text=True)
p=Path('/tmp/opalx-cleanup-gpu-index-manifest.yml');p.write_text(rebuild(base))
subprocess.run(['git','add',str(root.relative_to(r))],cwd=r,check=True)
blob=subprocess.check_output(['git','hash-object','-w',str(p)],cwd=r,text=True).strip()
subprocess.run(['git','update-index','--cacheinfo',f'100644,{blob},manifest.yml'],cwd=r,check=True)
print('Cataloged',len(blocks),'snapshot-free files; unrelated manifest changes unstaged.')
