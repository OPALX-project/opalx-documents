"""Reproducible coarse PIC acceleration staging; source maps/samples unchanged."""
from pathlib import Path
import json,hashlib,shutil,re
import numpy as np,pandas as pd
root=Path(__file__).resolve().parent;repo=root.parents[1]
single=repo/'tmp/ring-probes-20261023/acceleration-590MeV'
sc=Path('/Users/adelmann/git/regression-tests-x/RegressionTests/Cyclotron-SC-Midpoint')
# Rotate the fixed local Gaussian offsets into the established accelerating launch.
df=pd.read_csv(sc/'gauss.dat',sep=r'\s+',skiprows=1)
positions=df[['x','y','z']].to_numpy();momenta=df[['px','py','pz']].to_numpy()
old=momenta.mean(axis=0);new=np.array([-.36920124,0,-.151830777]);direction=new/np.linalg.norm(new)
a=np.arctan2(direction[0],direction[2]);rotation=np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
positions=(positions-positions.mean(axis=0))@rotation.T
momenta=(momenta-old)@rotation.T+new
for name,steps in [('benchmark',100),('accelerating-pic',633600)]:
 target=root/name;target.mkdir(exist_ok=False)
 output=np.empty((len(df),6));output[:,::2]=positions;output[:,1::2]=momenta
 with (target/'bunch.dat').open('w') as f:
  f.write(f'{len(df)}\nx px y py z pz\n');np.savetxt(f,output,fmt='%.17e')
 text=(single/'acceleration.in').read_text()
 text=re.sub(r'^RADIAL0:.*\n|^RADIAL90:.*\n|^EXTRACT:.*\n','',text,flags=re.M)
 text=text.replace('RING=(RADIAL0,RADIAL90,EXTRACT,','RING=(RADIAL,')
 text=text.replace('MYCYCL: RING=', 'RADIAL: PROBE, XSTART=4320, XEND=4450, YSTART=0, YEND=0, STEP=0.1, OUTFN="radial";\nMYCYCL: RING=')
 text=text.replace('PSDUMPFREQ=1000','PSDUMPFREQ=1000000000').replace('STATDUMPFREQ=1000','STATDUMPFREQ=100').replace('STEPINFOFQ=10000','STEPINFOFQ=1000')
 text=text.replace('FNAME="proton.dat", NPARTDIST=1','FNAME="bunch.dat", NPARTDIST=262144').replace('NALLOC=1, BCHARGE=1.602176634e-19','NALLOC=262144, BCHARGE=3.9486673247778873e-11')
 solver='SCBIN: BINNING, MAXBINS=1, PARAMETER=GAMMAZ, ADAPTIVEBINNING=FALSE, TABLEPRINTFREQ=1000, DUMPBINSFILE="NONE";\nFS0: FIELDSOLVER, TYPE=OPEN, BINS=SCBIN, NX=32, NY=32, NZ=32, PARFFTX=TRUE, PARFFTY=TRUE, PARFFTZ=TRUE, BCFFTX=OPEN, BCFFTY=OPEN, BCFFTZ=OPEN, BBOXINCR=2, GREENSF=STANDARD;'
 text=re.sub(r'FS0: FIELDSOLVER,.*?;',solver,text)
 # Retain validated 41 ps stepping before any accuracy/cost change.
 text=text.replace('MAXSTEPS=633600',f'MAXSTEPS={steps}').replace('FIELDSOLVER=FS0;','FIELDSOLVER=FS0, SCFIELDUPDATE="MIDPOINT";')
 if name=='benchmark':text=text.replace(', EKINSTOP=0.58999999999999997','')
 (target/'acceleration.in').write_text(text)
 for filename in ['bfield.dat','rffield1.dat','rffield2.dat']:shutil.copy2(single/filename,target/filename)
 manifest={'particles':len(df),'grid':[32]*3,'charge_C':3.9486673247778873e-11,'equivalent_current_A':.002,'launch_reference_p':new.tolist(),'seeded_samples_source':str(sc/'gauss.dat'),'sample_transform':'center fixed samples; rigid y-rotation from local +z to established acceleration reference; replace mean momentum','dt_s':4.113195129976966e-11,'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}}
 (target/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(target)
