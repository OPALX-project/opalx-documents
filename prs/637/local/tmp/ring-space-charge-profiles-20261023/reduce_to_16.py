from pathlib import Path
import json,hashlib,shutil
import numpy as np,pandas as pd
root=Path('/Users/adelmann/git/opalx-master/tmp/ring-space-charge-profiles-20261023');old=root/'accelerating-pic';new=root/'accelerating-pic-16';new.mkdir(exist_ok=False)
df=pd.read_csv(old/'bunch.dat',sep=r'\s+',skiprows=1)
# Seeded sample without replacement; retain physical covariance through whitening.
a=df.sample(n=32768,random_state=61516).to_numpy().copy()
for cols in [[0,2,4],[1,3,5]]:
 original=df.iloc[:,cols].to_numpy();mean=original.mean(axis=0)
 sample=a[:,cols];sample-=sample.mean(axis=0)
 # Preserve the full sampled 6D covariance below, including position-momentum correlations.
 a[:,cols]=sample+mean
mean=df.to_numpy().mean(axis=0);center=a-a.mean(axis=0)
source_cov=np.cov(df.to_numpy(),rowvar=False,bias=True);sample_cov=np.cov(center,rowvar=False,bias=True)
center=center@np.linalg.inv(np.linalg.cholesky(sample_cov)).T@np.linalg.cholesky(source_cov).T
a=center+mean
with (new/'bunch.dat').open('w') as f:
 f.write('32768\nx px y py z pz\n');np.savetxt(f,a,fmt='%.17e')
text=(old/'acceleration.in').read_text().replace('NX=32, NY=32, NZ=32','NX=16, NY=16, NZ=16').replace('NPARTDIST=262144','NPARTDIST=32768').replace('NALLOC=262144','NALLOC=32768')
(new/'acceleration.in').write_text(text)
for name in ['bfield.dat','rffield1.dat','rffield2.dat']:shutil.copy2(old/name,new/name)
manifest={'source':str(old),'particles':32768,'grid':[16]*3,'charge_C':3.9486673247778873e-11,'selection_seed':61516,'sample_transform':'seeded sample without replacement, centered and 6D covariance matched to original population by Cholesky factors','maximum_mean_error':float(abs(a.mean(axis=0)-mean).max()),'maximum_covariance_error':float(abs(np.cov(a,rowvar=False,bias=True)-source_cov).max()),'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in new.iterdir()}}
(new/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Same launcher, frozen executable, distinct output directory.
s=(root/'run_acceleration.py').read_text().replace("target=root/'accelerating-pic'","target=root/'accelerating-pic-16'").replace("binary=repo/'build_openmp/src/opalx'","binary=root/'opalx-run'")
(root/'run_acceleration_16.py').write_text(s)
s=(root/'plot_last_eight.py').read_text().replace("run=root/'accelerating-pic'","root=Path(__file__).resolve().parent/'profiles-16';root.mkdir(exist_ok=True)\nrun=root.parent/'accelerating-pic-16'").replace('262144','32768').replace('32³ mesh · 262,144','16³ mesh · 32,768')
(root/'plot_last_eight_16.py').write_text(s)
s=(root/'finish_when_done.py').read_text().replace("root/'accelerating-pic/launch.json'","root/'accelerating-pic-16/launch.json'").replace("root/'plot_last_eight.py'","root/'plot_last_eight_16.py'")
(root/'finish_when_done_16.py').write_text(s)
print(json.dumps(manifest,indent=2))
