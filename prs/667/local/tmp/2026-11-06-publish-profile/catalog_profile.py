from pathlib import Path
import yaml,hashlib,json,re
r=Path('/Users/adelmann/git/opalx-documents');p=r/'manifest.yml';text=p.read_text();d=yaml.safe_load(text);by={x['destination']:x for x in d['assets']};root=r/'examples/2026/2d5-1/row-batching-profile-2026-11-06';selected=['manifest.yml']
for f in sorted(root.rglob('*')):
 if not f.is_file():continue
 rel=str(f.relative_to(r));assert rel==rel.lower();assert f.suffix not in ['.h5','.npz','.sqlite','.nsys-rep','.ncu-rep'];selected.append(rel)
 a=dict(title='FFT2D5 row-batching profile — '+str(f.relative_to(root)),date=None,category='examples/2d5-1',source='Nsight Systems job355041, failed hardware-counter job355042 and unprofiled two-A100 calibration job355043; native data at /psi/home/adelmann/opalx-dev/dba/validation-row-profile-20261106',destination=rel,description='GPU activity, launch geometry, remaining bottlenecks and sub-one-hour-turn budget; study dated2026-11-06, canonical supporting filenames retained; raw traces and particle snapshots external.',status='experimental',sha256=hashlib.sha256(f.read_bytes()).hexdigest())
 if rel in by:raise RuntimeError('Already cataloged: '+rel)
 text+='\n'+''.join('  '+line+'\n' for line in yaml.safe_dump([a],sort_keys=False,allow_unicode=True,width=130).splitlines())
p.write_text(text)
Path('/Users/adelmann/git/opalx/tmp/2026-11-06-publish-profile/profile-paths.json').write_text(json.dumps(selected,indent=2))
print('Profile files',len(selected)-1)
