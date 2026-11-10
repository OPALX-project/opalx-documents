"""Compare preserved pre-audit and post-audit fixed-time bunch outputs exactly.

Runs are produced separately by tools/check_cyclotron_bunch.py. This comparison
never launches a simulator and never changes simulation or reference data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import h5py
import numpy as np

TASK = Path('/Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109')
BASE = TASK/'bunch-baseline'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--new-dir', type=Path, default=TASK/'bunch-integration')
parser.add_argument('--output', type=Path, default=TASK/'bunch-before-after.json')
args = parser.parse_args()
NEW = args.new_dir.resolve()
OUTPUT = args.output.resolve()
CASES = ('none','near-zero','charged-one','charged-two')
DATASETS = ('id','x','y','z','px','py','pz','q')
ATTRIBUTES = ('TIME','GlobalTrackStep','RefPartR','RefPartP','SPOS')
INPUTS = ('Cyclotron-RF-Stop.in','bunch.dat','bfield.dat','rffield1.dat','rffield2.dat')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path):
    with h5py.File(path,'r') as file:
        groups = sorted((key for key in file if key.startswith('Step#')),key=lambda key:int(key.split('#')[1]))
        assert groups, path
        group = file[groups[-1]]
        order = np.argsort(group['id'][:],kind='stable')
        arrays = {name:np.asarray(group[name])[order] for name in DATASETS}
        attrs = {name:np.asarray(group.attrs[name]) for name in ATTRIBUTES}
        return groups,arrays,attrs


def difference(before,after):
    assert before.shape==after.shape,(before.shape,after.shape)
    equal = np.array_equal(before,after)
    result = dict(shape=list(before.shape),before_dtype=str(before.dtype),after_dtype=str(after.dtype),exact=bool(equal),byte_identical=bool(before.dtype==after.dtype and before.tobytes()==after.tobytes()))
    if before.dtype.kind in 'iuf' and after.dtype.kind in 'iuf':
        diff=np.abs(after-before)
        result.update(changed_values=int(np.count_nonzero(before!=after)),max_abs_delta=float(np.max(diff,initial=0)))
        if not equal:
            index=np.unravel_index(np.argmax(diff),diff.shape)
            result.update(max_delta_index=list(map(int,index)),before_at_max=np.asarray(before[index]).tolist(),after_at_max=np.asarray(after[index]).tolist())
    return result


report = dict(baseline_binary_sha256=json.loads((BASE/'report.json').read_text())['binary_sha256'],new_binary_sha256=json.loads((NEW/'report.json').read_text())['binary_sha256'],cases={},all_exact=True,numerical_tolerance_used=False)
for case in CASES:
    olddir,newdir=BASE/case,NEW/case
    checks={name:dict(baseline_sha256=sha(olddir/name),new_sha256=sha(newdir/name)) for name in INPUTS}
    for name,check in checks.items():
        check['identical']=check['baseline_sha256']==check['new_sha256']
        assert check['identical'],(case,name,check)
    oldgroups,olddata,oldattrs=inspect(olddir/'Cyclotron-RF-Stop.h5')
    newgroups,newdata,newattrs=inspect(newdir/'Cyclotron-RF-Stop.h5')
    assert oldgroups==newgroups,(case,oldgroups,newgroups)
    datasets={name:difference(olddata[name],newdata[name]) for name in DATASETS}
    attributes={name:difference(oldattrs[name],newattrs[name]) for name in ATTRIBUTES}
    exact=all(value['exact'] for value in [*datasets.values(),*attributes.values()])
    report['cases'][case]=dict(input_files=checks,step_groups=oldgroups,final_particle_count=len(olddata['id']),datasets=datasets,attributes=attributes,all_exact=exact)
    report['all_exact'] &= exact
report['note']='Each before/after comparison uses the same rank count and sorted stable IDs. Cross-rank physical-state-set differences are checked separately by the existing integration driver; no tolerance was used or widened in this before/after comparison.'
report['all_byte_identical']=all(value['byte_identical'] for case in report['cases'].values() for group in ('datasets','attributes') for value in case[group].values())
report['baseline_directory']=str(BASE)
report['new_directory']=str(NEW)
report['current_binary_sha256']=sha(TASK.parents[1]/'build_openmp/src/opalx')
report['current_binary_matches_new_runs']=report['current_binary_sha256']==report['new_binary_sha256']
OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
summary={case:dict(all_exact=data['all_exact'],particles=data['final_particle_count'],input_files_identical=all(item['identical'] for item in data['input_files'].values()),step_groups=data['step_groups']) for case,data in report['cases'].items()}
print(json.dumps(dict(all_exact=report['all_exact'],all_byte_identical=report['all_byte_identical'],new_binary_sha256=report['new_binary_sha256'],current_binary_matches_new_runs=report['current_binary_matches_new_runs'],cases=summary),indent=2))
assert report['all_exact'], f'Physical states differ; inspect {OUTPUT}'
