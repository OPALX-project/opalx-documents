from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
root=Path(__file__).resolve().parent
repo=root.parents[1]
binary=repo/'build_openmp/src/opalx'
source=Path('/Users/adelmann/git/opalx/sandbox/Regression-Tests')
legacy=Path('/Users/adelmann/git/opalx/sandbox/cyclotron/opal')
(root/'legacy').mkdir(exist_ok=False)
for name in ['cyclotron1.in','cyclotron2.in']:
    shutil.copy2(legacy/name,root/'legacy'/name)
probes='''// Global cyclotron probes; legacy Y endpoints denote laboratory Z [mm].
RADIAL0: PROBE, XSTART=1900, XEND=4700, YSTART=0, YEND=0, STEP=1, OUTFN="radial0";
RADIAL90: PROBE, XSTART=0, XEND=0, YSTART=1900, YEND=4700, STEP=1, OUTFN="radial90";
// Geometry copied from the old OPAL manual's cyclotron PROBE example.
EXTRACT: PROBE, XSTART=4166.16, XEND=4250, YSTART=-1226.85, YEND=-1241.3, STEP=1, OUTFN="extraction";
'''
manifest={'binary':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
          'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),
          'mpi_ranks':1,'openmp_threads':1,'runs':{}}
manifest['working_tree_diff_sha256']=hashlib.sha256(subprocess.check_output(['git','diff'],cwd=repo)).hexdigest()
manifest['new_source_sha256']={str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted((repo/'src/Algorithms').glob('CyclotronProbe*'))}
for case,folder,infile,files in [
 ('coasting-10turns','ring-cyclotron-coasting-1','coasting.in',['bfield.dat','proton72.dat']),
 ('acceleration-590MeV','ring-cyclotron-accelera-1','acceleration.in',['bfield.dat','rffield1.dat','rffield2.dat','proton.dat'])]:
    target=root/case;target.mkdir(exist_ok=False)
    original=source/folder/infile
    text=original.read_text()
    text=text.replace('MYCYCL: RING=(',probes+'MYCYCL: RING=(RADIAL0,RADIAL90,EXTRACT,',1)
    if case.startswith('coasting'):
        text=text.replace('TURNS=1','TURNS=10').replace('MAXSTEPS=2000','MAXSTEPS=20000')
        text=text.replace('PSDUMPFREQ=1, STATDUMPFREQ=1, ASCIIDUMP=TRUE',
                          'PSDUMPFREQ=1000, STATDUMPFREQ=100, STEPINFOFQ=1000, ASCIIDUMP=FALSE')
    (target/infile).write_text(text)
    for name in files: shutil.copy2(source/folder/name,target/name)
    command=['mpirun','-np','1',str(binary),infile,'--info','2']
    record={'source_input':str(original),'command':command,
            'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir() if p.is_file()}}
    manifest['runs'][case]=record
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('START',case,flush=True);started=time.monotonic()
    with (target/'run.log').open('w') as log:
        result=subprocess.run(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false',OMP_DYNAMIC='false'),
                              stdout=log,stderr=subprocess.STDOUT,timeout=1200)
    record.update(returncode=result.returncode,elapsed_seconds=time.monotonic()-started)
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('FINISH',case,record['returncode'],record['elapsed_seconds'],flush=True)
    if result.returncode: raise SystemExit(result.returncode)
