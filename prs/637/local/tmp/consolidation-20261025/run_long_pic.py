"""Repeat the unchanged accepted 8^3/4096-particle case after source consolidation."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path(__file__).resolve().parent;repo=root.parents[1]
baseline=repo/'tmp/ring-space-charge-profiles-20261023/accelerating-pic-8-580'
target=root/'accelerating-pic-8-580';target.mkdir(exist_ok=False)
for name in ['acceleration.in','bunch.dat','bfield.dat','rffield1.dat','rffield2.dat']:
    shutil.copy2(baseline/name,target/name)
binary=root/'opalx-consolidated';shutil.copy2(repo/'build_openmp/src/opalx',binary)
command=['mpirun','-np','1',str(binary),'acceleration.in','--info','2']
record={'command':command,'ranks':1,'threads':4,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()},'baseline':str(baseline),'start_unix':time.time()}
(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
with (target/'run.log').open('w') as log:
    process=subprocess.Popen(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false'),stdout=log,stderr=subprocess.STDOUT)
    record['pid']=process.pid;(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
    record['returncode']=process.wait()
record['elapsed_s']=time.time()-record['start_unix'];(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(record['returncode'])
