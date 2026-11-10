"""Standalone adapter validation; never registered in native CTest."""
from pathlib import Path
import importlib.util
import json
import tempfile
import h5py
import numpy as np
import pandas as pd

ROOT=Path('/Users/adelmann/git/opalx-master')
spec=importlib.util.spec_from_file_location('adapter', ROOT/'tools/ffa_school_probe_adapter.py')
adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
checks=[]
def check(name, fn):
    fn(); checks.append(name)
def reject(fn):
    try: fn()
    except (ValueError, OSError): return
    raise AssertionError('Invalid input was accepted')

with tempfile.TemporaryDirectory(prefix='ffa-adapter-') as directory:
    work=Path(directory)
    source=work/'native.loss'
    source.write_text(adapter.HEADER+'\n'+'-4.42 0.003 4.7 0.01 0.02 0.03 9007199254740993 0 3 2e-9\n'+'-4.40 -0.002 4.8 0.04 0.05 0.06 7 1 1 3e-9\n')
    native=adapter.read_native_probe(source)
    original=native.copy(deep=True)
    school=adapter.to_school_frame(native,4.42)
    check('exact_large_and_noncontiguous_ids',lambda: np.testing.assert_array_equal(native.id,[7,9007199254740993]))
    check('coordinate_and_momentum_mapping',lambda: np.testing.assert_allclose(school[['x','y','z','px','py','pz']].to_numpy(),[[0.02,4.8,-0.002,0.04,0.06,0.05],[0,4.7,0.003,0.01,0.03,0.02]],rtol=0,atol=1e-15))
    check('native_input_unchanged',lambda: pd.testing.assert_frame_equal(native,original))
    check('turn_labels_preserved',lambda: np.testing.assert_array_equal(school.turn,[1,0]))
    one=adapter.to_school_frame(native,4.42,1)
    check('explicit_one_based_turn_labels',lambda: np.testing.assert_array_equal(one.turn,[2,1]))
    output=work/'school.loss'; adapter.write_school_loss(school,output)
    check('ten_column_round_trip',lambda: pd.testing.assert_frame_equal(adapter.read_native_probe(output),school))
    check('existing_output_refused',lambda: reject(lambda: adapter.write_school_loss(school,output)))
    h5=work/'native.h5'
    with h5py.File(h5,'w') as file:
        for group,index in [('Step#10',0),('Step#2',1)]:
            batch=file.create_group(group)
            for column in adapter.COLUMNS: batch[column]=native[column].iloc[[index]].to_numpy()
    check('hdf5_batches_match_ascii',lambda: pd.testing.assert_frame_equal(adapter.read_native_probe(h5),native))
    malformed=work/'bad.loss'; malformed.write_text('1 2 3\n')
    check('bad_ascii_width_refused',lambda: reject(lambda: adapter.read_native_probe(malformed)))
    check('missing_file_refused',lambda: reject(lambda: adapter.read_native_probe(work/'missing.loss')))
    empty=work/'empty.loss'; empty.write_text(adapter.HEADER+'\n')
    check('header_only_ascii_supported',lambda: np.testing.assert_equal(len(adapter.read_native_probe(empty)),0))
    check('invalid_geometry_refused',lambda: reject(lambda: adapter.to_school_frame(native,float('nan'))))
    check('negative_shifted_turn_refused',lambda: reject(lambda: adapter.to_school_frame(native,4.42,-1)))
    check('overflow_shifted_turn_refused',lambda: reject(lambda: adapter.to_school_frame(native,4.42,2**63)))
    bad=native.copy(); bad.loc[0,'x']=float('nan')
    check('nonfinite_record_refused',lambda: reject(lambda: adapter.to_school_frame(bad,4.42)))
    bad=native.copy(); bad['id']=bad.id.astype(float)
    check('floating_point_ids_refused',lambda: reject(lambda: adapter.to_school_frame(bad,4.42)))
    with h5py.File(work/'bad.h5','w') as file: file.create_group('Step#0')['x']=[1.]
    check('missing_hdf5_dataset_refused',lambda: reject(lambda: adapter.read_native_probe(work/'bad.h5')))
    with h5py.File(work/'unequal.h5','w') as file:
        batch=file.create_group('Step#0')
        for column in adapter.COLUMNS: batch[column]=native[column].to_numpy()[:1 if column=='x' else 2]
    check('unequal_hdf5_datasets_refused',lambda: reject(lambda: adapter.read_native_probe(work/'unequal.h5')))
    duplicate=pd.concat([native,native],ignore_index=True)
    check('multiple_same_turn_crossings_retained',lambda: np.testing.assert_equal(len(adapter.to_school_frame(duplicate,4.42)),4))

real=ROOT/'tmp/pr637-upstream-merge-20261107/probe-integration'
real_ascii=adapter.read_native_probe(real/'Cyclotron-Coasting-ascii/hits.loss')
real_hdf5=adapter.read_native_probe(real/'Cyclotron-Coasting-hdf5/hits.h5')
check('real_hits_ascii_hdf5_counts_and_ids',lambda: np.testing.assert_array_equal(real_ascii[['id','turn','bunchNumber']],real_hdf5[['id','turn','bunchNumber']]))
check('real_hits_ascii_hdf5_float_precision',lambda: np.testing.assert_allclose(real_ascii[list(adapter.FLOAT_COLUMNS)],real_hdf5[list(adapter.FLOAT_COLUMNS)],rtol=6e-6,atol=1e-10))
report={'checks':checks,'passed':len(checks),'real_hits':len(real_hdf5),'note':'Real pre-existing cyclotron files validate native record parsing only, not FFA physics.'}
Path(__file__).with_name('validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
