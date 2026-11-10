from pathlib import Path
import subprocess,json,hashlib,os,time
r=Path(__file__).resolve().parent;d=r/'old-full';binary=Path('/Users/adelmann/OPAL-2022.1/bin/opal')
command=['/bin/bash','-c','source /Users/adelmann/OPAL-2022.1/etc/profile.d/opal.sh && exec /Users/adelmann/OPAL-2022.1/bin/opal acceleration.in']
record={'command':command,'ranks':1,'threads':1,'start_unix':time.time(),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256((d/'acceleration.in').read_bytes()).hexdigest()}
(d/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
with (d/'run.log').open('w') as log:
 process=subprocess.Popen(command,cwd=d,env=dict(os.environ,OMP_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT)
 record['pid']=process.pid;(d/'launch.json').write_text(json.dumps(record,indent=2)+'\n');record['returncode']=process.wait()
record['elapsed_s']=time.time()-record['start_unix'];(d/'launch.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(record['returncode'])
