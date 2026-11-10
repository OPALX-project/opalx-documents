from pathlib import Path
from io import StringIO
import re,json
import numpy as np,pandas as pd,h5py
root=Path('/Users/adelmann/git/opalx-master/tmp/coasting-fix-20261023')
def stat(p):
 h,b=re.split(r'&data\b.*?&end',p.read_text(),maxsplit=1,flags=re.S)
 names=[re.search(r'\bname\s*=\s*([^,\s]+)',c).group(1) for c in re.findall(r'&column\b(.*?)&end',h,re.S)]
 lines=[l for l in b.splitlines() if l.strip() and not l.lstrip().startswith('!')]
 return pd.read_csv(StringIO('\n'.join(lines[len(re.findall('&parameter',h)):])),sep=r'\s+',names=names)
for name in ['before-off','after-off','after-on','after-mpi2']:
 p=root/name
 if not (p/'manifest.json').exists():continue
 df=stat(p/'coasting.stat');off=np.linalg.norm(df[['mean_x','mean_y','mean_s']],axis=1)
 print(name,'max',off.max(),'final',off[-1], 'energy range',df.energy.min(),df.energy.max())
 bad=np.flatnonzero(off>1e-8)
 if len(bad):print('first',df.iloc[bad[0]][['t','s','mean_x','mean_s']].to_dict())
 for probe in ['radial0','radial90']:
  if (p/(probe+'.h5')).exists():
   with h5py.File(p/(probe+'.h5')) as f:print(probe,sum(len(g['id']) for g in f.values()))
 if name=='after-on':np.testing.assert_array_equal(df.to_numpy(),stat(root/'after-off/coasting.stat').to_numpy());print('ON/OFF EXACT')
