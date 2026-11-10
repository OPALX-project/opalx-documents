#!/usr/bin/env python3
"""Native FFA probe integration driver; separate from native C++ unit tests.

Prepare/run matched school particles, inspect immutable native output, convert
hits through the general frame adapter and compare chronological station/ID passages.
The original school files are only read. No physics baseline is rewritten.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCHOOL = Path('/Users/adelmann/git/FFA25-school/opalx')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def match_legacy_ring_placement(geometry):
    """Map authentic RingSection clockwise placement to native laboratory angles.

    The existing school template used the old accumulated angle directly as a
    native CCW angle. Old Ring starts from +oldY clockwise; its centre must be
    reflected about pi/4, with spiral handedness reversed. This repairs copied
    comparison inputs only and leaves all original school files unchanged.
    """
    statements = [part.strip() for part in geometry.split(';') if part.strip()]
    lengths = {}
    for statement in statements:
        match = re.match(r'(\w+)\s*:\s*ASYMMETRIC_ENGE\s*,',statement)
        if match:
            start = re.search(r'\bSTART_HALF_LENGTH=([^,]+)',statement).group(1)
            end = re.search(r'\bEND_HALF_LENGTH=([^,]+)',statement).group(1)
            lengths[match[1]] = f'(({start})+({end}))'
    changed = 0
    for index,statement in enumerate(statements):
        match = re.search(r'\bEND_FIELD_MODEL=(\w+)',statement)
        if not match or ': SCALINGFFAMAGNET,' not in statement:
            continue
        length = lengths[match[1]]
        phi = re.search(r'\bTHETA=-(\w+)',statement).group(1)
        corrected = f'(PI/2-({phi})-{length}/R0)'
        for old,new in [(f'X=R0*(COS({phi})-1)',f'X=R0*(COS({corrected})-1)'),
                        (f'Z=R0*SIN({phi})',f'Z=R0*SIN({corrected})'),
                        (f'THETA=-{phi}',f'THETA=-{corrected}'),
                        ('TAN_DELTA=TAN(SPIRAL_ANGLE)','TAN_DELTA=-TAN(SPIRAL_ANGLE)')]:
            if statement.count(old) != 1:
                raise ValueError('Unexpected native magnet placement: '+old)
            statement = statement.replace(old,new,1)
        statements[index] = statement
        changed += 1
    if changed != 32:
        raise ValueError(f'Expected 32 transformed physical magnets, got {changed}')
    return ';\n'.join(statements)+';'


def prepare(old_run, output, variant, ranks, steps=None, dt_scale=1., part_count=1,
            legacy_ring_placement=False):
    old_run, output = Path(old_run).resolve(), Path(output).resolve()
    old = json.loads((old_run/'launch.json').read_text())
    if old.get('returncode') != 0:
        raise RuntimeError('Old run did not complete successfully')
    if 'physical_mass_MeV' not in old:
        raise ValueError('Old launch metadata must include corrected physical mass')
    school = module('ffa_school_geometry', SCHOOL/'school.py')
    case = next(case for case in school.CASES if case.key == old['case'])
    adapter = module('ffa_probe_adapter', REPO/'tools/probe_frame_adapter.py')
    output.mkdir(parents=True, exist_ok=False)
    steps = old['steps'] if steps is None else steps
    dt = old['dt_s'] * dt_scale
    x,y,z,px,py,pz = old['initial_old_x_y_z_px_py_pz']
    native = [x-case.r0, px, z, pz, y, py]  # FROMFILE order x px y py z pz.
    (output/'particles.dat').write_text(
        str(part_count)+'\nx px y py z pz\n' + '\n'.join(' '.join(format(v,'.17g') for v in native)
                                                        for _ in range(part_count))+'\n')
    overrides = dict(P_MASS=old['physical_mass_MeV'], N_PARTICLES=part_count,
                     TRACK_DT=dt, TRACK_MAXSTEPS=steps,
                     PS_DUMP_FREQ=1000000000, STAT_DUMP_FREQ=1000000,
                     BUNCH_CHARGE=1e-19, REPART_FREQ=0)
    constants, geometry = school._definitions(case, overrides)
    if legacy_ring_placement:
        geometry = match_legacy_ring_placement(geometry)
    probe_definitions, names = [], []
    if variant != 'off':
        for j in range(old['stations']):
            phi = 2*math.pi*j/old['stations']
            start, end = ((case.r0-1)*math.cos(phi)-case.r0,
                          (case.r0+1)*math.cos(phi)-case.r0)
            zstart, zend = (case.r0-1)*math.sin(phi), (case.r0+1)*math.sin(phi)
            name = f'PROBE{j+1}'
            names.append(name)
            probe_definitions.append(
                f'{name}: PROBE, XSTART={1000*start:.17g}, XEND={1000*end:.17g}, '
                f'YSTART={1000*zstart:.17g}, YEND={1000*zend:.17g}, STEP=1, OUTFN="{name}";')
        geometry, count = re.subn(r'(SCHOOL\s*:\s*RING\s*=\s*\()',
                                  lambda m:m[1]+','.join(names)+',', geometry)
        if count != 1:
            raise ValueError('Expected one SCHOOL ring')
    lines = ['OPTION, ECHO=FALSE;', constants,
             'OPTION, ENABLEHDF5=TRUE, ENABLELINEARTRANSFERMAPS=FALSE, '
             f'ASCIIDUMP={"TRUE" if variant == "ascii" else "FALSE"}, '
             'PSDUMPFREQ=PS_DUMP_FREQ, STATDUMPFREQ=STAT_DUMP_FREQ, '
             'REPARTFREQ=REPART_FREQ, VERSION=INPUT_VERSION;',
             *probe_definitions, geometry, *school._source_lines(case, fromfile=True),
             'FS: FIELDSOLVER, TYPE=NONE, NX=N_GRID, NY=N_GRID, NZ=N_GRID;',
             'TRACK, LINE=SCHOOL, BEAM=BEAM1, DT={TRACK_DT}, '
             'MAXSTEPS=TRACK_MAXSTEPS, ZSTOP=TRACK_ZSTOP;',
             'RUN, METHOD="PARALLEL", FIELDSOLVER=FS;', 'ENDTRACK;', 'STOP;']
    (output/'school.in').write_text(school.format_input('\n'.join(lines)+'\n'))
    info = dict(case=case.key, r0_m=case.r0, old_run=str(old_run), variant=variant,
                ranks=ranks, steps=steps, dt_s=dt, input_particles=part_count,
                mass_GeV=old['physical_mass_MeV']/1000,
                initial_native_x_px_y_py_z_pz=native,
                old_reference=old,
                legacy_ring_placement=legacy_ring_placement,
                geometry_correction=('theta_entrance=PI/2-phi_template-L/R0; TAN_DELTA sign reversed'
                                     if legacy_ring_placement else None),
                native_template_sha256=digest(SCHOOL/case.template),
                school_module_sha256=digest(SCHOOL/'school.py'),
                input_sha256=digest(output/'school.in'),
                particle_sha256=digest(output/'particles.dat'),
                probe_stations=names,
                notes=['Native output remains lab X-Z horizontal/Y vertical.',
                       'Legacy initial-plane t=0 samples are reported separately.',
                       'Native turn is directed reference returns; old turn is RF-step bookkeeping.',
                       'No TURNS stop; compare fixed nominal step/time budgets.'])
    write_json(output/'manifest.json', info)
    return info


def run(path, executable):
    path, executable = Path(path).resolve(), Path(executable).resolve()
    if (path/'run.log').exists():
        raise FileExistsError('Use a fresh run directory')
    info = json.loads((path/'manifest.json').read_text())
    command = ['mpiexec', '-n', str(info['ranks']), str(executable), '--info', '1', 'school.in']
    env = dict(os.environ, OMP_NUM_THREADS='1', IPPL_OPENMP_THREADS='1', OMP_PROC_BIND='false')
    env.pop('OPALX_TEST_PASSIVE_RING_PROBES', None)
    info.update(executable=str(executable), executable_sha256=digest(executable),
                command=command, start_unix=time.time())
    with (path/'run.log').open('w') as stream:
        process = subprocess.Popen(command, cwd=path, env=env, stdout=stream, stderr=subprocess.STDOUT)
        info['pid'] = process.pid
        write_json(path/'manifest.json',info)
        info['returncode'] = process.wait()
    info['elapsed_s'] = time.time()-info['start_unix']
    write_json(path/'manifest.json',info)
    if info['returncode'] != 0:
        raise RuntimeError(f'Native run failed ({info["returncode"]}); inspect {path}/run.log')
    result = analyze(path)
    print(json.dumps({key:result.get(key) for key in ['directory','variant','ranks','final_particles','global_steps','final_time_s','elapsed_s','native_hits','matched_hits','unmatched_old','unmatched_native','max_abs_deltas']},indent=2,allow_nan=False), flush=True)
    return result


def final_snapshot(path):
    path = Path(path)
    with h5py.File(path/'school.h5','r') as file:
        keys = sorted((key for key in file if key.startswith('Step#')),
                      key=lambda key:int(key.split('#')[1]))
        if not keys:
            raise ValueError('No beam snapshots')
        group = file[keys[-1]]
        ids = np.asarray(group['id'])
        order = np.argsort(ids,kind='stable')
        arrays = {key:np.asarray(group[key])[order] for key in ('id','x','y','z','px','py','pz','q')}
        for key in ('GlobalTrackStep','TIME','SPOS','RefPartR','RefPartP'):
            arrays[key] = np.asarray(group.attrs[key])
    return arrays


def analyze(path):
    path = Path(path)
    info = json.loads((path/'manifest.json').read_text())
    snapshot = final_snapshot(path)
    count = len(snapshot['id'])
    if count != info['input_particles']:
        raise RuntimeError(f'Particle loss: {count}/{info["input_particles"]} survive')
    report = dict(directory=str(path), variant=info['variant'], ranks=info['ranks'],
                  final_particles=count,
                  final_charge_C=float(np.sum(snapshot['q'])),
                  global_steps=int(np.ravel(snapshot['GlobalTrackStep'])[0]),
                  final_time_s=float(np.ravel(snapshot['TIME'])[0]),
                  elapsed_s=info.get('elapsed_s'))
    np.savez(path/'final-state.npz',**snapshot)
    if info['variant'] == 'off':
        report['probe_outputs'] = len(list(path.glob('PROBE*')))
        if report['probe_outputs']:
            raise AssertionError('Probe-free run created probe output')
        write_json(path/'analysis.json',report)
        return report
    adapter = module('ffa_probe_adapter',REPO/'tools/probe_frame_adapter.py')
    station_reports, deltas = [], []
    converted = path/'school-frame'; converted.mkdir(exist_ok=True)
    extension = '.loss' if info['variant'] == 'ascii' else '.h5'
    for station in info['probe_stations']:
        native = adapter.read_probe(path/(station+extension))
        school = adapter.transform_frame(native, origin_m=(-info['r0_m'],0,0), basis=((1,0,0),(0,0,1),(0,1,0)))
        school_path = converted/(station+'.loss')
        if not school_path.exists():
            adapter.write_probe_ascii(school,school_path)
        old = adapter.read_probe(Path(info['old_run'])/(station+'.loss'))
        initial = old[old.time == 0].copy()
        old = old[(old.time > 0) & (old.time <= report['final_time_s'])].copy()
        school = school[school.time > 0].copy()
        for frame in (old,school):
            frame['passage'] = frame.groupby(['id','bunchNumber'],sort=False).cumcount()
        joined = old.merge(school,on=['id','bunchNumber','passage'],suffixes=('_old','_native'),
                           how='outer',indicator=True,validate='one_to_one')
        matched = joined[joined['_merge'] == 'both'].copy()
        station_report = dict(station=station, native_hits=len(school), old_positive_time_hits=len(old),
                              old_initial_hits=len(initial), matched=len(matched),
                              unmatched_old=int((joined['_merge']=='left_only').sum()),
                              unmatched_native=int((joined['_merge']=='right_only').sum()),
                              native_turns=sorted(map(int,school.turn.unique())),
                              old_turns=sorted(map(int,old.turn.unique())))
        if len(matched):
            for name in ['x','y','z','px','py','pz','time']:
                matched['delta_'+name] = matched[name+'_native']-matched[name+'_old']
                station_report['max_abs_delta_'+name] = float(matched['delta_'+name].abs().max())
            matched['station'] = station
            deltas.append(matched)
        station_reports.append(station_report)
    report['stations'] = station_reports
    report['native_hits'] = sum(station['native_hits'] for station in station_reports)
    report['matched_hits'] = sum(station['matched'] for station in station_reports)
    report['old_initial_hits_excluded'] = sum(station['old_initial_hits'] for station in station_reports)
    report['unmatched_old'] = sum(station['unmatched_old'] for station in station_reports)
    report['unmatched_native'] = sum(station['unmatched_native'] for station in station_reports)
    report['radial_summary_files'] = [p.name for ext in ('*.hist','*.peaks') for p in path.glob(ext)]
    if report['radial_summary_files']:
        raise AssertionError('FFA probe emitted laboratory-origin radial summaries')
    if deltas:
        all_deltas = pd.concat(deltas,ignore_index=True)
        all_deltas.to_csv(path/'crossing-comparison.csv',index=False)
        report['max_abs_deltas'] = {name:float(all_deltas['delta_'+name].abs().max())
                                    for name in ['x','y','z','px','py','pz','time']}
    write_json(path/'analysis.json',report)
    return report


def compare_states(paths):
    reference = final_snapshot(paths[0])
    results = []
    for path in paths[1:]:
        candidate = final_snapshot(path)
        entries = {}
        for key,value in reference.items():
            other = candidate[key]
            entries[key] = dict(exact=np.array_equal(value,other),
                                max_abs_delta=float(np.max(np.abs(value-other)))
                                if value.shape == other.shape and value.size else None,
                                reference_shape=list(value.shape),candidate_shape=list(other.shape))
        results.append(dict(reference=str(paths[0]),candidate=str(path),fields=entries,
                            exact=all(entry['exact'] for entry in entries.values())))
    result = dict(comparisons=results, all_exact=all(entry['exact'] for entry in results))
    print(json.dumps(result,indent=2,allow_nan=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode',required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--old-run',type=Path,required=True)
    prep.add_argument('--output',type=Path,required=True)
    prep.add_argument('--variant',choices=['off','ascii','hdf5'],required=True)
    prep.add_argument('--ranks',type=int,default=1)
    prep.add_argument('--steps',type=int)
    prep.add_argument('--dt-scale',type=float,default=1.)
    prep.add_argument('--particles',type=int,default=1)
    prep.add_argument('--legacy-ring-placement',action='store_true')
    runner = sub.add_parser('run'); runner.add_argument('directory',type=Path)
    runner.add_argument('--executable',type=Path,default=REPO/'build_openmp/src/opalx')
    analysis = sub.add_parser('analyze'); analysis.add_argument('directory',type=Path)
    compare = sub.add_parser('compare-states'); compare.add_argument('directories',nargs='+',type=Path)
    args = parser.parse_args()
    if args.mode == 'prepare':
        result = prepare(args.old_run,args.output,args.variant,args.ranks,args.steps,args.dt_scale,args.particles,args.legacy_ring_placement)
        print(json.dumps(result,indent=2,allow_nan=False))
    elif args.mode == 'run':
        run(args.directory,args.executable)
    elif args.mode == 'analyze':
        print(json.dumps(analyze(args.directory),indent=2,allow_nan=False))
    else:
        result = compare_states(args.directories)
        if not result['all_exact']:
            raise SystemExit(1)

if __name__ == '__main__':
    main()
