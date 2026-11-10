from pathlib import Path
import re,hashlib,json,shutil
import numpy as np,pandas as pd
root=Path(__file__).resolve().parent;repo=root.parents[1];src=repo/'tmp/ring-space-charge-profiles-20261023/accelerating-pic-8-580'
source=pd.read_csv(src/'bunch.dat',sep=r'\s+',skiprows=1).to_numpy();mean=source.mean(axis=0)
phi=np.deg2rad(110);c,s=np.cos(phi),np.sin(phi)
rotation=np.array([[c,0,s],[-s,0,c],[0,-1,0]]) # OPALXglobaloffset->oldlocal
old=np.empty_like(source);old[:,::2]=(source[:,::2]-mean[::2])@rotation.T;old[:,1::2]=(source[:,1::2]-mean[1::2])@rotation.T
base=Path('/Users/adelmann/git/opalx/sandbox/cyclotron/opal/acceleration590/old-lf2-2880-no-tc/acceleration.in').read_text()
for name,steps in [('smoke',12),('old-full',140000)]:
 d=root/name;d.mkdir(exist_ok=False)
 with (d/'bunch.dat').open('w') as f:f.write('4096\n');np.savetxt(f,old,fmt='%.17e')
 text=re.sub(r'^OPTION,.*?;','',base,flags=re.M)
 text='OPTION, VERSION=20200, ECHO=FALSE, STATDUMPFREQ=100, PSDUMPFREQ='+('1' if name=='smoke' else '1000')+', SPTDUMPFREQ=1, PSDUMPEACHTURN=FALSE, PSDUMPFRAME=GLOBAL;\n'+text
 for a,b in [('../../bfield.dat','bfield.dat'),('../../rffield1.dat','rffield1.dat'),('../../rffield2.dat','rffield2.dat'),('../../dist2.dat','bunch.dat')]:text=text.replace(a,b)
 text=text.replace('TYPE=FROMFILE,FNAME="bunch.dat"','TYPE=FROMFILE,FNAME="bunch.dat", INPUTMOUNITS=NONE')
 text=text.replace('FSTYPE=NONE, MX=64, MY=64, MT=64','FSTYPE=FFT, MX=8, MY=8, MT=8').replace('BCFFTT=open;','BCFFTT=open, BBOXINCR=2, GREENSF=STANDARD;')
 text=text.replace('NPART=1, BCURRENT=1.0E-6','NPART=4096, BCURRENT=0.002').replace('MAXSTEPS=633600, STEPSPERTURN=2880',f'MAXSTEPS={steps}, STEPSPERTURN=720')
 text=text.replace('L1:   LINE = (RingCycl,','RADIAL: PROBE, XSTART=1900, XEND=4700, YSTART=0, YEND=0, STEP=0.1, OUTFN="radial";\nL1:   LINE = (RingCycl,RADIAL,')
 (d/'acceleration.in').write_text(text)
 for n in ['bfield.dat','rffield1.dat','rffield2.dat']:shutil.copy2(src/n,d/n)
 (d/'manifest.json').write_text(json.dumps({'samples':4096,'grid':[8]*3,'current_A':.002,'freq_Hz':50.65e6,'old_dt_s':6/(50.65e6*720),'sample_source':str(src/'bunch.dat'),'sample_conversion':'center original offsets then rotate into radial/tangent/vertical basis at110degrees; subtract launch momentum','input_hash':hashlib.sha256(text.encode()).hexdigest(),'distribution_hash':hashlib.sha256((d/'bunch.dat').read_bytes()).hexdigest()},indent=2)+'\n')
