"""Reproduce coasting at unchanged physics settings; write every statistics step."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,time
root=Path(__file__).resolve().parent;repo=root.parents[1]
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--binary',type=Path,required=True);p.add_argument('--ranks',type=int,default=1);p.add_argument('--probes',action='store_true');a=p.parse_args()
source=repo/'tmp/ring-probes-20261023'/('coasting-10turns' if a.probes else 'coasting-10turns-control')
target=root/a.name;target.mkdir(exist_ok=False)
text=(source/'coasting.in').read_text().replace('PSDUMPFREQ=1000','PSDUMPFREQ=1000000000').replace('STATDUMPFREQ=100,','STATDUMPFREQ=1,')
(target/'coasting.in').write_text(text)
for name in ['bfield.dat','proton72.dat']:shutil.copy2(source/name,target/name)
command=['mpirun','-np',str(a.ranks),str(a.binary.resolve()),'coasting.in','--info','2']
record={'command':command,'binary_sha256':hashlib.sha256(a.binary.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(text.encode()).hexdigest(),'ranks':a.ranks,'threads':1}
start=time.monotonic()
with (target/'run.log').open('w') as log:
 r=subprocess.run(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),stdout=log,stderr=subprocess.STDOUT,timeout=300)
record.update(returncode=r.returncode,elapsed_s=time.monotonic()-start)
(target/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(r.returncode)
