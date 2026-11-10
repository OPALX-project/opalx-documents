from pathlib import Path
import json
import h5py
import numpy as np
root=Path('/Users/adelmann/git/opalx-master/tmp/terminal-rf-roundoff-20261110')
rows=[]
for stage in ('before','after'):
 for ranks in (1,2):
  path=root/f'{stage}-r{ranks}'
  assert 'EKINSTOP reached after complete gap kick' in (path/'run.log').read_text()
  with h5py.File(path/'Cyclotron-RF-Stop.h5') as f:
   g=f[max(f,key=lambda k:int(k.split('#')[1]))]
   mass=float(g.attrs['MASS'][0])*1000
   p=np.column_stack([g[k][:] for k in ('px','py','pz')])
   energy=(np.sqrt(1+(p*p).sum(axis=1))-1)*mass
   ref=(np.sqrt(1+np.dot(g.attrs['RefPartP'],g.attrs['RefPartP']))-1)*mass
   rows.append(dict(stage=stage,ranks=ranks,particles=len(p),reference_MeV=ref,particle_MeV=energy.tolist(),max_energy_difference_MeV=float(np.max(np.abs(energy-ref)))))
   assert len(p)==1
   if stage=='after':
    assert ref>=73 and np.all(energy>=73)
    assert np.max(np.abs(energy-ref))<1e-9
(root/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
