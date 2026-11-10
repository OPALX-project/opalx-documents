"""Stage requested 8^3/4096-particle 580 MeV case; keep charge and full 6D covariance."""
from pathlib import Path
import hashlib,json,shutil
import pandas as pd,numpy as np
root=Path(__file__).resolve().parent;old=root/'accelerating-pic-16';new=root/'accelerating-pic-8-580';new.mkdir(exist_ok=False)
df=pd.read_csv(old/'bunch.dat',sep=r'\s+',skiprows=1);source=df.to_numpy();a=df.sample(n=4096,random_state=6158).to_numpy().copy();a-=a.mean(axis=0)
a=a@np.linalg.inv(np.linalg.cholesky(np.cov(a,rowvar=False,bias=True))).T@np.linalg.cholesky(np.cov(source,rowvar=False,bias=True)).T+source.mean(axis=0)
with (new/'bunch.dat').open('w') as f:f.write('4096\nx px y py z pz\n');np.savetxt(f,a,fmt='%.17e')
s=(old/'acceleration.in').read_text().replace('NX=16, NY=16, NZ=16','NX=8, NY=8, NZ=8').replace('32768','4096').replace('EKINSTOP=0.58999999999999997','EKINSTOP=0.58').replace('XSTART=4320, XEND=4450','XSTART=1900, XEND=4700').replace('PSDUMPFREQ=1000000000','PSDUMPFREQ=1000')
(new/'acceleration.in').write_text(s)
for name in ['bfield.dat','rffield1.dat','rffield2.dat']:shutil.copy2(old/name,new/name)
manifest={'particles':4096,'mesh':[8]*3,'target_reference_MeV':580,'charge_C':3.9486673247778873e-11,'selection_seed':6158,'sample_transform':'subset centered and full 6D covariance matched to original16 case','mean_error':float(abs(a.mean(axis=0)-source.mean(axis=0)).max()),'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in new.iterdir()}}
(new/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
s=(root/'run_acceleration_16.py').read_text().replace("target=root/'accelerating-pic-16'","target=root/'accelerating-pic-8-580'").replace("binary=root/'opalx-run'","binary=root/'opalx-flush-run'")
(root/'run_acceleration_8.py').write_text(s)
print(json.dumps(manifest,indent=2))
