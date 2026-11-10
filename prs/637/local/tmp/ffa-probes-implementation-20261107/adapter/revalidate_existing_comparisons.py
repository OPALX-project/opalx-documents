from pathlib import Path
import importlib.util
import json
import hashlib
import numpy as np
import pandas as pd

root = Path('/Users/adelmann/git/opalx-master')
task = root/'tmp/ffa-probes-implementation-20261107'
def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
adapter=load('general_probe_adapter',root/'tools/probe_frame_adapter.py')
old_adapter=load('archived_probe_adapter',task/'adapter-school-original/ffa_school_probe_adapter.py')
results=[]
for run in sorted(task.glob('native-*')):
    manifest=run/'manifest.json';converted=run/'school-frame'
    if not manifest.exists() or not converted.is_dir():
        continue
    info=json.loads(manifest.read_text());count=0;updated_tokens=0;maximum=0.0
    for reference in sorted(converted.glob('PROBE*.loss')):
        native_path=run/(reference.stem+('.loss' if info['variant']=='ascii' else '.h5'))
        source=adapter.read_probe(native_path)
        before=old_adapter.read_native_probe(native_path)
        # Assess the generalized transformation independently of the reader fix.
        legacy=old_adapter.to_school_frame(before,info['r0_m'])
        general=adapter.transform_frame(before,(-info['r0_m'],0,0),((1,0,0),(0,0,1),(0,1,0)))
        pd.testing.assert_frame_equal(general,legacy,check_exact=True)
        saved=pd.read_csv(reference,sep=r'\s+',comment='#',header=None,names=adapter.COLUMNS,
                          float_precision='round_trip',dtype={name:('int64' if name in adapter.INTEGER_COLUMNS
                                                                 else 'float64') for name in adapter.COLUMNS})
        pd.testing.assert_frame_equal(general,saved,check_exact=True)
        if native_path.suffix=='.loss':
            # New reader must match a separate correctly rounded decimal parser.
            oracle=pd.read_csv(native_path,sep=r'\s+',comment='#',header=None,names=adapter.COLUMNS,
                               float_precision='round_trip',dtype={name:('int64' if name in adapter.INTEGER_COLUMNS
                                                                      else 'float64') for name in adapter.COLUMNS})
            oracle=oracle.sort_values(['bunchNumber','id','time'],kind='stable').reset_index(drop=True)
            pd.testing.assert_frame_equal(source,oracle,check_exact=True)
        else:
            pd.testing.assert_frame_equal(source,before,check_exact=True)
        delta=np.abs(source[list(adapter.FLOAT_COLUMNS)].to_numpy()-before[list(adapter.FLOAT_COLUMNS)].to_numpy())
        updated_tokens+=int(np.count_nonzero(delta))
        maximum=max(maximum,float(np.max(delta,initial=0)))
        pd.testing.assert_frame_equal(source[list(adapter.INTEGER_COLUMNS)],before[list(adapter.INTEGER_COLUMNS)],check_exact=True)
        count+=len(source)
    results.append(dict(run=run.name,crossings=count,frame_transform_exact_against_archived_conversion=True,
                        correctly_rounded_ascii_tokens_changed=updated_tokens,max_decoded_input_delta=maximum))
assert len(results)>=18,len(results)
report=dict(adapter_sha256=hashlib.sha256((root/'tools/probe_frame_adapter.py').read_bytes()).hexdigest(),
            runs=results,converted_crossings=sum(run['crossings'] for run in results),
            correctly_rounded_ascii_tokens_changed=sum(run['correctly_rounded_ascii_tokens_changed'] for run in results),
            result='General transform exactly reproduces archived conversion for identical decoded input. Updated ASCII reader separately matches correctly rounded decimal parsing. HDF5 unchanged. No simulation rerun.')
(task/'adapter/existing-comparisons-general.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({key:value for key,value in report.items() if key!='runs'},indent=2))
