"""Audit short actual-tracker CUDA outputs; separate from native CTest."""
from pathlib import Path
import argparse,hashlib,json
import h5py
import numpy as np

def snapshot(path):
    with h5py.File(path,'r') as file:
        groups=[key for key in file if key.startswith('Step#')]
        group=file[max(groups,key=lambda key:int(key.split('#')[1]))]
        result={name:group[name][:] for name in ['id','x','y','z','px','py','pz','q']}
        result.update({name:np.asarray(group.attrs[name]) for name in ['TIME','GlobalTrackStep','SPOS','RefPartR','RefPartP','MASS','CHARGE']})
    assert len(result['id'])==256
    assert len(np.unique(result['id']))==256
    assert len(np.unique(result['x']))==256
    assert all(np.isfinite(values).all() for values in result.values())
    return result

def compare(reference,candidate):
    np.testing.assert_array_equal(np.sort(candidate['id']),np.sort(reference['id']))
    # FROMFILE IDs are assigned after rank distribution; compare physical state
    # sets using the already-verified unique x coordinate, without assuming equal
    # sample-to-ID mapping across rank counts.
    first=np.argsort(reference['x']);second=np.argsort(candidate['x'])
    errors={}
    for name in ['x','y','z','px','py','pz']:
        a,b=reference[name][first],candidate[name][second]
        np.testing.assert_allclose(b,a,rtol=0,atol=1e-10)
        errors[name]=float(np.max(np.abs(b-a)))
    np.testing.assert_array_equal(candidate['q'][second],reference['q'][first])
    for name in ['TIME','GlobalTrackStep','MASS','CHARGE']:
        np.testing.assert_array_equal(candidate[name],reference[name])
    for name in ['SPOS','RefPartR','RefPartP']:
        np.testing.assert_allclose(candidate[name],reference[name],rtol=0,atol=1e-10)
        errors[name]=float(np.max(np.abs(candidate[name]-reference[name])))
    return errors

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory',type=Path)
args=parser.parse_args();root=args.directory
runs=json.loads((root/'gpu-integration-final/run-report.json').read_text())
assert len(runs['runs'])==4 and all(r['passed'] and not r['timeout'] for r in runs['runs'])
manifest=json.loads((root/'gpu-integration-final/fixture-manifest.json').read_text())
for name,sha in manifest['files'].items():
    assert hashlib.sha256((root/'gpu-integration-final/fixture'/name).read_bytes()).hexdigest()==sha,name
cpu=snapshot(root/'gpu-integration-final/fixture/cpu-reference.h5')
report={'source_id':manifest['source_id'],'ranks':{},'failure_runs':[],'absolute_comparison_bound':1e-10,'note':'Short NONE-solver tracker correctness checks; not GPU PIC throughput or mesh convergence. Existing 1e-10 absolute bounds retained; no physics tolerance change.'}
gpu={}
for ranks in [1,2]:
    path=root/'gpu-integration-final/runs'/('valid-r'+str(ranks));gpu[ranks]=snapshot(path/'Cyclotron-RF-Stop.h5')
    record=next(r for r in runs['runs'] if r['case']=='valid' and r['ranks']==ranks)
    assert len({m['gpu_uuid'] for m in record['gpu_mapping']})==ranks
    for mapping in record['gpu_mapping']:
        assert mapping['runtime_device_count']==1
        assert mapping['cuda_runtime_library']==mapping['probe_cuda_runtime_library']
        assert mapping['cuda_runtime_version']==mapping['compiled_cudart_version']
    report['ranks'][str(ranks)]={'particles':len(gpu[ranks]['id']),'total_charge_C':float(np.sum(gpu[ranks]['q'])),'ids_unique':True,'ids_equal_cpu_as_set':True,'all_finite':True,'max_abs_gpu_cpu':compare(cpu,gpu[ranks]),'gpu_mapping':record['gpu_mapping'],'binary_sha256':record['binary_sha256'],'input_sha256':record['input_sha256'],'particle_sha256':record['particle_sha256']}
    failure=next(r for r in runs['runs'] if r['case']=='failure' and r['ranks']==ranks)
    assert failure['returncode']!=0 and failure['captured_failures']
    report['failure_runs'].append({key:failure[key] for key in ['ranks','returncode','timeout','elapsed_s','captured_failures','gpu_mapping','input_sha256','particle_sha256']})
report['max_abs_two_gpu_one_gpu']=compare(gpu[1],gpu[2])
(root/'tracker-gpu-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
