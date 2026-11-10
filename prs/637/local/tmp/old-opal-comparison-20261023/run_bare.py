from pathlib import Path
import shutil,subprocess,json,os,time
r=Path(__file__).resolve().parent;d=r/'old-bare';d.mkdir(exist_ok=False)
text=(r/'old-full/acceleration.in').read_text().replace('FSTYPE=FFT','FSTYPE=NONE').replace('NPART=4096','NPART=1')
(d/'acceleration.in').write_text(text);(d/'bunch.dat').write_text('1\n0 0 0 0 0 0\n')
for name in ['bfield.dat','rffield1.dat','rffield2.dat']:shutil.copy2(r/'old-full'/name,d/name)
t=time.time()
with (d/'run.log').open('w') as log:
 p=subprocess.run(['/bin/bash','-c','source /Users/adelmann/OPAL-2022.1/etc/profile.d/opal.sh && exec /Users/adelmann/OPAL-2022.1/bin/opal acceleration.in'],cwd=d,env=dict(os.environ,OMP_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT,timeout=600)
(d/'launch.json').write_text(json.dumps({'returncode':p.returncode,'elapsed_s':time.time()-t,'ranks':1,'threads':1,'purpose':'LF2 bare reference control, same maps/RF/dt'},indent=2)+'\n');print(p.returncode)
