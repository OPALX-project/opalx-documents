"""Run a fresh staged accelerating PIC case and retain launch/provenance data."""
from pathlib import Path
import hashlib,json,os,subprocess,time
root=Path(__file__).resolve().parent;repo=root.parents[1];target=root/'accelerating-pic-16'
binary=root/'opalx-run'
p=target/'acceleration.in';text=p.read_text().replace('DT=4.1131951299769659e-11','DT=1.6452780519907864e-10').replace('MAXSTEPS=633600','MAXSTEPS=180000');p.write_text(text)
command=['mpirun','-np','1',str(binary),'acceleration.in','--info','2']
record={'command':command,'ranks':1,'threads':4,'dt_s':1.6452780519907864e-10,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'start_unix':time.time(),'git_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'git_diff':subprocess.check_output(['git','diff','--stat'],cwd=repo,text=True)}
(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
with (target/'run.log').open('w') as log:
 process=subprocess.Popen(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false'),stdout=log,stderr=subprocess.STDOUT)
 record['pid']=process.pid;(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
 record['returncode']=process.wait()
record['elapsed_s']=time.time()-record['start_unix'];(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(record['returncode'])
