"""Audit retrieved A100 native tests and matched school outputs; not a CTest dependency."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,xml.etree.ElementTree as ET
import h5py,numpy as np

ROOT=Path('/Users/adelmann/git/opalx-master')
CPU=ROOT/'tmp/ffa-probes-implementation-20261107/native-16-cell-linked-final-hdf5-r1'
spec=importlib.util.spec_from_file_location('adapter',ROOT/'tools/probe_frame_adapter.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)

def final(path):
    with h5py.File(path) as file:
        group=file[max((k for k in file if k.startswith('Step#')),key=lambda k:int(k.split('#')[1]))]
        result={key:np.asarray(group[key]) for key in ['id','x','y','z','px','py','pz','q']}
        result.update({key:np.asarray(group.attrs[key]) for key in ['TIME','GlobalTrackStep','SPOS','RefPartR','RefPartP']})
    return result

def analyze(directory, rank_counts=(1,2)):
    metadata=json.loads((CPU/'manifest.json').read_text())
    report={'cpu_case':str(CPU),'cpu_executable_sha256':metadata['executable_sha256'],'r0_m':metadata['r0_m'],'ranks':{}}
    for ranks in rank_counts:
        native=directory/'gpu-school'/f'r{ranks}'
        for name in ['school.in','particles.dat']:
            assert (native/name).read_bytes()==(CPU/name).read_bytes(),name
        mapping=[json.loads((native/f'gpu-mapping-rank{rank}.json').read_text()) for rank in range(ranks)]
        assert len({record['gpu_uuid'] for record in mapping})==ranks
        assert all(record['kokkos_logical_device_id']==0 for record in mapping)
        stations={}
        for i in range(1,17):
            name=f'PROBE{i}'
            gpu=adapter.read_probe(native/(name+'.h5'))
            cpu=adapter.read_probe(CPU/(name+'.h5'))
            np.testing.assert_array_equal(gpu[['id','bunchNumber']],cpu[['id','bunchNumber']])
            assert len(gpu)==len(cpu)
            stations[name]={'hits':len(gpu),'reference_turn_label_mismatches':int(np.count_nonzero(gpu.turn.to_numpy()!=cpu.turn.to_numpy())),'max_abs':{key:float(np.max(np.abs(gpu[key].to_numpy()-cpu[key].to_numpy()),initial=0)) for key in adapter.FLOAT_COLUMNS}}
            assert not (native/(name+'.hist')).exists()
            assert not (native/(name+'.peaks')).exists()
        state_gpu,state_cpu=final(native/'school.h5'),final(CPU/'school.h5')
        for key in ['id','q']:
            np.testing.assert_array_equal(state_gpu[key],state_cpu[key])
        state_errors={key:float(np.max(np.abs(state_gpu[key]-state_cpu[key]),initial=0)) for key in state_cpu if key not in ['id','GlobalTrackStep']}
        report['ranks'][str(ranks)]={'gpu_mapping':mapping,'stations':stations,'total_hits':sum(s['hits'] for s in stations.values()),'same_ids_bunches':True,'final_state_max_abs':state_errors,'final_particles':len(state_gpu['id']),'global_track_step':int(state_gpu['GlobalTrackStep'].ravel()[0]),'cpu_global_track_step':int(state_cpu['GlobalTrackStep'].ravel()[0]),'input_sha256':hashlib.sha256((native/'school.in').read_bytes()).hexdigest()}
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path)
    args=parser.parse_args();report=analyze(args.directory)
    (args.directory/'gpu-school-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    summary={r:{'total_hits':v['total_hits'],'final_particles':v['final_particles'],'global_track_step':v['global_track_step'],'cpu_global_track_step':v['cpu_global_track_step'],'reference_turn_label_mismatches':sum(s['reference_turn_label_mismatches'] for s in v['stations'].values()),'max_probe_abs':{key:max(s['max_abs'][key] for s in v['stations'].values()) for key in adapter.FLOAT_COLUMNS},'final_state_max_abs':v['final_state_max_abs']} for r,v in report['ranks'].items()}
    print(json.dumps(summary,indent=2))
