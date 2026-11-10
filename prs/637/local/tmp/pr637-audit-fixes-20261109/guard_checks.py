"""Standalone RF preparation/failure integration guards; not native unit tests."""
from pathlib import Path
import argparse,hashlib,json,os,re,shutil,signal,subprocess,time
import numpy as np

ROOT=Path('/Users/adelmann/git/opalx-master')
TASK=ROOT/'tmp/pr637-audit-fixes-20261109'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=TASK/'guard-integration',
                    help='New result directory; existing output is never replaced')
parser.add_argument('--bunch-root',type=Path,default=TASK/'bunch-integration/none',
                    help='Completed Cyclotron-RF-Stop bunch fixture for particle-only failures')
args=parser.parse_args()
OUT=args.output_dir.resolve()
BUNCH_ROOT=args.bunch_root.resolve()
FIXTURE=Path('/Users/adelmann/git/regression-tests-x/RegressionTests/Cyclotron-RF-Stop')
NEW=ROOT/'build_openmp/src/opalx'
OLD=ROOT/'tmp/ffa-probes-implementation-20261107/bin/opalx-linked-final'
INFILE='Cyclotron-RF-Stop.in'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(name,base=FIXTURE):
    target=OUT/name
    target.mkdir(parents=True,exist_ok=False)
    for source in base.glob('*.dat'):shutil.copy2(source,target/source.name)
    text=(base/INFILE).read_text()
    text=re.sub(r'MAXSTEPS=\d+','MAXSTEPS=1',text)
    text=re.sub(r', EKINSTOP=[^;]+','',text)
    return target,text

def run(name,binary,ranks,text,expected,base=FIXTURE,already=None):
    target=already
    if target is None:target,_=prepare(name,base)
    (target/INFILE).write_text(text)
    command=['mpirun','-np',str(ranks),str(binary),INFILE,'--info','2']
    start=time.monotonic()
    with (target/'run.log').open('w') as log:
        p=subprocess.Popen(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),
                           stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=p.wait(timeout=40)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL);p.wait()
            raise AssertionError(name+' timed out; own process group terminated')
    log=(target/'run.log').read_text(errors='replace')
    markers=[line for line in log.splitlines() if any(s in line for s in ['SINGLEGAP','Done executing ParallelTracker','Exception during execution'])]
    success=(code==0 and 'Done executing ParallelTracker' in log) if expected=='success' else (code!=0 and expected in log)
    report=dict(name=name,binary=str(binary),binary_sha256=digest(binary),ranks=ranks,returncode=code,
                elapsed_s=time.monotonic()-start,expected=expected,passed=success,markers=markers,
                command=command,input_sha256=digest(target/INFILE),timeout=False)
    (target/'launch.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
    return report

OUT.mkdir(exist_ok=False)
results=[]
# The host path deliberately has unrestricted gap bookkeeping; the device mask
# still supports64 descriptors. Clone the existing RF0 placement into60 distinctly
# named diagnostic-free occurrences (5 original +60 =65). One step precedes RF.
target,text=prepare('new-host-65')
rf0=re.search(r'^RF0: RFCAVITY[^\n]+',text,re.M).group(0)
names=[f'RF_EXTRA_{i:02d}' for i in range(60)]
clones='\n'.join(rf0.replace('RF0:',name+':',1) for name in names)+'\n'
text=text.replace('MYCYCL: RING=',clones+'MYCYCL: RING=',1)
text=text.replace('SM7,RF0,RF1,RF2,RF3,RF4)', 'SM7,RF0,RF1,RF2,RF3,RF4,'+','.join(names)+')')
assert len(re.findall(r'^\w+: RFCAVITY',text,re.M))==65
results.append(run('new-host-65',NEW,1,text,'success',already=target))
results.append(run('old-host-65',OLD,1,text,'success'))
limit='SINGLEGAP requires magnetic sectors and at most 64 gaps.'
results.append(run('new-device-65',NEW,2,text,limit))
results.append(run('old-device-65',OLD,2,text,limit))
# An accepted parser species with the wrong rest mass must be rejected by the
# common preparation stage before any stepping, on both execution branches.
target,species=prepare('new-electron-r1')
species=species.replace('PARTICLE=PROTON','PARTICLE=ELECTRON')
proton='SINGLEGAP requires an unpolarized positive proton and does not support restart.'
results.append(run('new-electron-r1',NEW,1,species,proton,already=target))
results.append(run('new-electron-r2',NEW,2,species,proton))
# Keep the reference launch centred and valid while two physical particles lie
# beyond the magnetic map's vertical extent, exercising collective pusher failure.
bunch=BUNCH_ROOT
for ranks in [1,2]:
    name=f'new-particle-support-failure-r{ranks}'
    target,text=prepare(name,bunch)
    values=np.loadtxt(target/'bunch.dat',skiprows=2)
    values[0,2]+=10.;values[1,2]-=10.
    values[:,::2]-=values[:,::2].mean(axis=0)
    with (target/'bunch.dat').open('w') as stream:
        stream.write('256\nx px y py z pz\n');np.savetxt(stream,values,fmt='%.17e')
    item=run(name,NEW,ranks,text,'SINGLEGAP particle transport failed',already=target)
    log=(target/'run.log').read_text(errors='replace')
    item['coherent_failure']=bool(re.search(r'SINGLEGAP failure rank=\d+ id=\d+ cause=field-support gap-index=-?\d+ t\[s\]=.*Rlab\[m\]=.*Plab\[beta\*gamma\]=',log))
    item['passed'] &= item['coherent_failure']
    results.append(item)
report=dict(results=results,passed=sum(r['passed'] for r in results),total=len(results),
            output_dir=str(OUT),bunch_root=str(BUNCH_ROOT),
            note='Separate standalone integration cases only; no native unit-test dependency or production source changes.')
new_stat=(OUT/'new-host-65/Cyclotron-RF-Stop.stat').read_text()
old_stat=(OUT/'old-host-65/Cyclotron-RF-Stop.stat').read_text()
# The SDDS description records wall time, not a simulated quantity. Require all
# other bytes, including all physical statistics, to match the frozen executable.
def normalize_stat_metadata(text):
    return re.sub(r"(text=\"Statistics data '[^']*' )\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}(?=\")",r"\1<TIMESTAMP>",text)
report['host_stats_byte_identical']=new_stat==old_stat
report['host_stats_identical_except_timestamp']=normalize_stat_metadata(new_stat)==normalize_stat_metadata(old_stat)
assert report['host_stats_identical_except_timestamp']
report['host_stats_sha256']={name:digest(OUT/(name+'/Cyclotron-RF-Stop.stat')) for name in ['new-host-65','old-host-65']}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['passed']==report['total'],report
