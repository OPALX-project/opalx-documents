"""Distinguish multicore PIC repeatability from a transport refactor change."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,re,shutil,subprocess,time,sys
import h5py,numpy as np
root=Path(__file__).resolve().parent;repo=root.parents[1]
source=repo/'tmp/ring-space-charge-profiles-20261023/accelerating-pic-8-580'
old=repo/'tmp/ring-space-charge-profiles-20261023/opalx-pre-consolidation'
new=repo/'build_openmp/src/opalx'
output=root/'repeatability'
if '--analyze-only' not in sys.argv:output.mkdir(exist_ok=False)
def run(name,binary,threads):
    target=output/name;target.mkdir()
    for filename in ['acceleration.in','bunch.dat','bfield.dat','rffield1.dat','rffield2.dat']:
        shutil.copy2(source/filename,target/filename)
    p=target/'acceleration.in';s,n=re.subn(r'MAXSTEPS=180000','MAXSTEPS=2000',p.read_text());assert n==1
    s,n=re.subn(r', EKINSTOP=[^;]+','',s);assert n==1;p.write_text(s)
    command=['mpirun','-np','1',str(binary),'acceleration.in','--info','1']
    record={'command':command,'threads':threads,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'steps':2000,'start':time.time()}
    with (target/'run.log').open('w') as log:
        result=subprocess.run(command,cwd=target,env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_PROC_BIND='false'),stdout=log,stderr=subprocess.STDOUT,timeout=180)
    record['returncode']=result.returncode;record['elapsed_s']=time.time()-record['start'];(target/'launch.json').write_text(json.dumps(record,indent=2)+'\n');assert result.returncode==0
    return target
cases=[('baseline-four-a',old,4),('baseline-four-b',old,4),('baseline-one',old,1),('consolidated-one',new,1)]
if '--analyze-only' in sys.argv:
    paths={c[0]:output/c[0] for c in cases}
    assert all(json.loads((p/'launch.json').read_text())['returncode']==0 for p in paths.values())
else:
    with ThreadPoolExecutor(max_workers=2) as pool:paths=dict(zip((c[0] for c in cases),pool.map(lambda c:run(*c),cases)))
def compare(left,right):
    result={'left':str(left),'right':str(right),'snapshots':{}}
    with h5py.File(left/'acceleration.h5') as a,h5py.File(right/'acceleration.h5') as b:
        common=sorted(set(a)&set(b));assert len(common)==2
        for key in common:
            assert np.array_equal(a[key].attrs['GlobalTrackStep'],b[key].attrs['GlobalTrackStep'])
            x,y=a[key],b[key];entry={}
            for name in ['id','x','y','z','px','py','pz']:
                av,bv=x[name][:],y[name][:];assert av.shape==bv.shape
                entry[name]={'exact':bool(np.array_equal(av,bv)),'max_absolute_difference':float(np.max(np.abs(av.astype(float)-bv.astype(float))))}
            for name in ['TIME','RefPartR','RefPartP']:
                av,bv=np.asarray(x.attrs[name]),np.asarray(y.attrs[name]);entry[name]={'exact':bool(np.array_equal(av,bv)),'max_absolute_difference':float(np.max(np.abs(av-bv)))}
            result['snapshots'][key]=entry
    return result
report={'same_baseline_four_threads':compare(paths['baseline-four-a'],paths['baseline-four-b']),
        'old_new_one_thread':compare(paths['baseline-one'],paths['consolidated-one']),
        'original_baseline_repeat_four_threads':compare(source,paths['baseline-four-a'])}
(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
for name,case in report.items():
    print(name,{k:max(v[k]['max_absolute_difference'] for v in case['snapshots'].values()) for k in next(iter(case['snapshots'].values()))})
# Refactor parity uses reproducible single-thread kernels. Multithread comparison
# is measured as evidence, without inventing/widening a numerical tolerance.
assert all(d['exact'] for s in report['old_new_one_thread']['snapshots'].values() for d in s.values())
