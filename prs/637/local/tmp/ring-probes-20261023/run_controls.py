from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
for case in ['coasting-10turns','acceleration-590MeV']:
    source=root/case;target=root/(case+'-control');target.mkdir(exist_ok=False)
    inputname='coasting.in' if case.startswith('coasting') else 'acceleration.in'
    text=(source/inputname).read_text()
    text=re.sub(r'^(RADIAL0|RADIAL90|EXTRACT): PROBE.*\n','',text,flags=re.M)
    text=text.replace('RING=(RADIAL0,RADIAL90,EXTRACT,','RING=(')
    (target/inputname).write_text(text)
    for path in source.glob('*.dat'):
        if path.name in ['bfield.dat','proton72.dat','proton.dat','rffield1.dat','rffield2.dat']:
            shutil.copy2(path,target/path.name)
    command=['mpirun','-np','1',manifest['binary'],inputname,'--info','2']
    start=time.monotonic()
    with (target/'run.log').open('w') as log:
        p=subprocess.run(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false',OMP_DYNAMIC='false'),stdout=log,stderr=subprocess.STDOUT,timeout=1200)
    manifest['runs'][target.name]={'command':command,'returncode':p.returncode,'elapsed_seconds':time.monotonic()-start,
        'sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in target.iterdir() if f.name in ['coasting.in','acceleration.in','bfield.dat','proton72.dat','proton.dat','rffield1.dat','rffield2.dat']}}
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(target.name,p.returncode,flush=True)
    if p.returncode:raise SystemExit(p.returncode)
