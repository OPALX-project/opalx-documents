#!/usr/bin/env python3
"""Ten-step native original-2D5 tracking with shared immutable cold particles.

The archived e85 executable uses independent 2D slices and local OPEN g=6.36.
ZeroSC retains the identical assigned charge and source with TYPE=NONE.
No current straight OPEN 3D backend, rebuild or production edit is involved.
"""
from __future__ import annotations

import argparse
import hashlib
from io import StringIO
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
TRACKING = ROOT.parent
STUDY = TRACKING.parent
BINARY = Path('/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe/fix-longitudinal/binaries/opalx-before-e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf')
BINARY_SHA = 'e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf'
LIGHT_SPEED = 299792458.
BETA, STEPS, DISTANCE, RADIUS = .001, 10, 1., 2.
PROTON_REST_ENERGY_EV = 938272088.16  # committed Physics::m_p * 1e9
TOTAL_TIME = DISTANCE/(BETA*LIGHT_SPEED)
DT = TOTAL_TIME/STEPS
MESH, BOX = [128, 128, 512], [.048, .048]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def snapshot():
    digest = sha(__file__)
    path = ROOT/'provenance'/f'run_tracking-{digest}.py'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        shutil.copy2(__file__, path)
    assert sha(path) == digest
    return digest, str(path)


def read_stat(path):
    """Existing ASCII SDDS reader convention from uniform-b-ellipsoid."""
    text = Path(path).read_text()
    columns, units = [], {}
    for block in re.findall(r'&column\b(.*?)&end', text, flags=re.S):
        name = re.search(r'\bname\s*=\s*([^,\s]+)', block).group(1).strip('"')
        columns.append(name)
        unit = re.search(r'\bunits\s*=\s*([^,\s]+)', block)
        units[name] = unit.group(1).strip('"') if unit else ''
    parameters = re.findall(r'&parameter\b.*?&end', text, flags=re.S)
    header = re.search(r'&data\b.*?&end', text, flags=re.S)
    assert header is not None and re.search(r'no_row_counts\s*=\s*1', header.group(0))
    lines = [x.strip() for x in text[header.end():].splitlines()
             if x.strip() and not x.lstrip().startswith('!')]
    frame = pd.read_csv(StringIO('\n'.join(lines[len(parameters):])), sep=r'\s+', names=columns)
    frame['time_s'] = frame.t*{'s':1., 'ms':1e-3, 'us':1e-6, 'ns':1e-9}[units['t']]
    return frame, units


def yaw_basis(reference_momentum):
    angle = np.arctan2(-reference_momentum[0], reference_momentum[2])
    co, si = np.cos(angle), np.sin(angle)
    return np.array([[co, 0., -si], [0., 1., 0.], [si, 0., co]])


def exact_circle_material(position, phase):
    """Exact R2 geometry; s is unwrapped around the current reference phase."""
    x, y, z = position.T
    theta = np.arctan2(z, x+RADIUS)
    delta = np.arctan2(np.sin(theta-phase), np.cos(theta-phase))
    u = np.hypot(x+RADIUS, z)-RADIUS
    return np.column_stack([u, y, RADIUS*delta])


def moment_record(position, momentum, time_s, step, phase=0.):
    mean = position.mean(axis=0)
    centred = position-mean
    covariance = centred.T@centred/len(position)
    result = dict(step=step, time_s=time_s, nominal_design_advance_m=BETA*LIGHT_SPEED*time_s,
                  reference_phase_rad=phase, particles=len(position))
    for j, coordinate in enumerate(['x', 'y', 'z']):
        result['mean_global_'+coordinate+'_m'] = float(mean[j])
        result['sigma_global_'+coordinate+'_m'] = float(np.sqrt(covariance[j, j]))
        result['mean_p'+coordinate+'_betagamma'] = float(momentum[:, j].mean())
        for k, second in enumerate(['x', 'y', 'z']):
            result['cov_global_'+coordinate+second+'_m2'] = float(covariance[j, k])
    return result


def add_frenet(record, position, phase):
    local = exact_circle_material(position, phase)
    mean = local.mean(axis=0)
    covariance = (local-mean).T@(local-mean)/len(local)
    for j, coordinate in enumerate(['u', 'y', 's']):
        record['mean_frenet_'+coordinate+'_m'] = float(mean[j])
        record['sigma_frenet_'+coordinate+'_m'] = float(np.sqrt(covariance[j, j]))
        for k, second in enumerate(['u', 'y', 's']):
            record['cov_frenet_'+coordinate+second+'_m2'] = float(covariance[j, k])


def prepare(geometry, zero_sc):
    source_path = TRACKING/'sources'/f'{geometry}-uniform-n1048576.json'
    source = json.loads(source_path.read_text())
    assert source['source_particles'] == 1048576 and source['charge_C'] == 1e-11
    assert source['beta'] == BETA
    for key in ['distribution', 'npz']:
        assert sha(source[key]) == source[key+'_sha256']
    assert sha(BINARY) == BINARY_SHA
    name = geometry+('-ZeroSC' if zero_sc else '-10pC')+'-10steps-e85'
    directory = ROOT/'runs'/name
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory/'manifest.json'
    if manifest.exists():
        saved = json.loads(manifest.read_text())
        if saved.get('returncode') == 0:
            assert sha(directory/'track.in') == saved['input_sha256']
            return directory, saved
    input_dir = ROOT/'inputs'
    input_dir.mkdir(parents=True, exist_ok=True)
    if geometry == 'straight':
        reference = input_dir/'straight-period12m.dat'
        data = np.zeros((2, 15))
        data[:, 0] = [0., 12.]
        data[:, 3] = [-6., 6.]
        data[:, 6] = source['momentum_betagamma']
        np.savetxt(reference, data, fmt='%.17e', header='s rx ry rz px py pz ex ey ez bx by bz ke time')
        field_element = 'D1: DRIFT,L=1,ELEMEDGE=1000;\nL1: LINE=(D1);'
        fieldmap, by = None, 0.
        period = 12.
    else:
        reference = STUDY/'curved/opalx/sources/circle-R2-step0.005.dat'
        assert reference.exists()
        path = np.loadtxt(reference)
        period = float(np.linalg.norm(np.diff(path[:, [1, 2, 3]], axis=0), axis=1).sum())
        by = source['momentum_betagamma']*PROTON_REST_ENERGY_EV/(LIGHT_SPEED*RADIUS)
        fieldmap = input_dir/'uniform-By-R2.g4blmap'
        with fieldmap.open('w') as stream:
            stream.write('param normB=1 current=1\n'
                         'grid X0=-3000 Y0=-50 Z0=-2200 dX=1550 dY=50 dZ=2200 nX=3 nY=3 nZ=3\ndata\n')
            for x in [-3000, -1450, 100]:
                for y in [-50, 0, 50]:
                    for z in [-2200, 0, 2200]:
                        stream.write(f'{x} {y} {z} 0 {by:.17g} 0\n')
        field_element = f'UB: FIELDMAP,FMAPFN="{fieldmap}",BSCALE=1,ESCALE=0,X=0,Y=0,Z=0,THETA=0,PHI=0,PSI=0;\nL1: LINE=(UB);'
    if zero_sc:
        solver = 'FS: FIELDSOLVER,TYPE=NONE,NX=8,NY=8,NZ=8,PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE;'
    else:
        solver = f'FS: FIELDSOLVER,TYPE="FFT2D5",NX=128,NY=128,NZ=512,PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE=OPEN,REFPATHFNAME="{reference}",BEAMR=.02,CLOSEDRING=TRUE,PIPESIZEX=.048,PIPESIZEY=.048,SCATTERLONGITUDINALLY=TRUE;'
    snapshot_freq = 10 if geometry == 'straight' else 1
    text = f'''// Original e85 2D5 tracking. ZeroSC keeps identical charge and TYPE=NONE.
OPTION, VERSION=10900;
OPTION, PSDUMPFREQ={snapshot_freq};
OPTION, STATDUMPFREQ=1;
OPTION, EBDUMP=TRUE;
OPTION, MINBINEMITTED=0;
DIST1: DISTRIBUTION,TYPE=FROMFILE,NPARTDIST=1048576,FNAME="{source['distribution']}";
E1: EMISSIONSOURCE,DISTRIBUTION=DIST1,R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0,ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;
ELIST1: EMISSIONSOURCELIST=(E1);
{solver}
B1: BEAM,PARTICLE=PROTON,NALLOC=1048576,BCHARGE=1e-11,SOURCES="ELIST1";
{field_element}
TRACK,BEAM=B1,LINE=L1,MAXSTEPS=10,ZSTOP={{100}},DT={{{DT:.17g}}};
RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1,SCFIELDUPDATE=MIDPOINT;
ENDTRACK;
'''
    (directory/'track.in').write_text(text)
    digest, driver_snapshot = snapshot()
    record = dict(name=name, geometry=geometry, zero_sc=zero_sc,
        self_field_model='NONE' if zero_sc else 'original independent 2D slices, OPEN g=6.36',
        original_solver=True, nonlocal_3D_operator=False, g=6.36,
        source=source, source_json=str(source_path), source_json_sha256=sha(source_path),
        expected_particles=1048576, assigned_charge_C=1e-11, macrocharge_C=source['macrocharge_C'],
        beta=BETA, steps=STEPS, dt_s=DT, total_time_s=TOTAL_TIME,
        nominal_design_path_advance_m=DISTANCE, mesh=MESH, box_m=BOX,
        reference_path=str(reference), reference_path_sha256=sha(reference), longitudinal_period_m=period,
        fieldmap=str(fieldmap) if fieldmap else None, fieldmap_sha256=sha(fieldmap) if fieldmap else None,
        By_T=by, reference_radius_m=RADIUS if geometry == 'bend' else None,
        sc_field_update='MIDPOINT', phase_space_output_interval=snapshot_freq,
        binary=str(BINARY), binary_sha256=BINARY_SHA,
        directory=str(directory), h5=str(directory/'track.h5'), stat=str(directory/'track.stat'),
        generator_sha256=digest, generator_snapshot=driver_snapshot,
        input_sha256=sha(directory/'track.in'), mpi_ranks=1, omp_threads=4,
        nominal_reference_convention='straight centroid=design; bend centroid reference differs from R2 design orbit')
    dump(manifest, record)
    return directory, record


def analyze(directory, manifest):
    source = manifest['source']
    with np.load(source['npz']) as data:
        initial_position = data['cartesian_m']
        initial_momentum = data['momenta_betagamma']
    initial = moment_record(initial_position, initial_momentum, 0., 0)
    for coordinate in ['x', 'y', 'z']:
        initial['sigma_tracker_'+coordinate+'_m'] = initial['sigma_global_'+coordinate+'_m']
    if manifest['geometry'] == 'bend':
        add_frenet(initial, initial_position, 0.)
    stat, units = read_stat(directory/'track.stat')
    assert len(stat) == STEPS
    assert np.all(stat.numParticles == manifest['expected_particles'])
    assert np.allclose(stat.charge, manifest['assigned_charge_C'], rtol=1e-10, atol=0)
    assert np.allclose(stat.time_s, DT*np.arange(1, STEPS+1), rtol=2e-10, atol=1e-15)
    assert np.isfinite(stat[['rms_x', 'rms_y', 'rms_s', 'mean_x', 'mean_y', 'mean_s']]).all().all()
    rows = [initial]
    for j, row in enumerate(stat.itertuples()):
        reference_r = np.array([row.ref_x, row.ref_y, row.ref_z])
        reference_p = np.array([row.ref_px, row.ref_py, row.ref_pz])
        basis = yaw_basis(reference_p)
        mean = np.array([row.mean_x, row.mean_y, row.mean_s])@basis.T+reference_r
        record = dict(step=j+1, time_s=row.time_s, nominal_design_advance_m=BETA*LIGHT_SPEED*row.time_s,
            particles=int(row.numParticles), sigma_tracker_x_m=row.rms_x,
            sigma_tracker_y_m=row.rms_y, sigma_tracker_z_m=row.rms_s,
            reference_phase_rad=float(np.arctan2(reference_r[2], reference_r[0]+RADIUS))
                if manifest['geometry'] == 'bend' else 0.)
        for k, name in enumerate(['x', 'y', 'z']):
            record['mean_global_'+name+'_m'] = float(mean[k])
            if manifest['geometry'] == 'straight':
                record['sigma_global_'+name+'_m'] = float([row.rms_x, row.rms_y, row.rms_s][k])
        rows.append(record)
    saved = []
    with h5py.File(directory/'track.h5') as h:
        groups = sorted(h, key=lambda x: int(x.split('#')[-1]))
        assert len(groups) == (1 if manifest['geometry'] == 'straight' else 10)
        for key in groups:
            g = h[key]
            stamp = float(np.asarray(g.attrs['TIME']).ravel()[0])
            step = int(round(stamp/DT))
            assert 1 <= step <= STEPS
            ids = g['id'][:].astype(np.int64)
            assert len(ids) == manifest['expected_particles']
            assert np.array_equal(np.sort(ids), np.arange(len(ids)))
            q = g['q'][:]
            assert np.allclose(q, manifest['macrocharge_C'], rtol=5e-12, atol=0)
            reference_r = np.asarray(g.attrs['RefPartR'], float)
            reference_p = np.asarray(g.attrs['RefPartP'], float)
            basis = yaw_basis(reference_p)
            local = np.column_stack([g[k][:] for k in ['x', 'y', 'z']])
            local_p = np.column_stack([g[k][:] for k in ['px', 'py', 'pz']])
            position, momentum = local@basis.T+reference_r, local_p@basis.T
            assert np.isfinite(position).all() and np.isfinite(momentum).all()
            phase = float(np.arctan2(reference_r[2], reference_r[0]+RADIUS)) if manifest['geometry'] == 'bend' else 0.
            actual = moment_record(position, momentum, stamp, step, phase)
            if manifest['geometry'] == 'bend':
                add_frenet(actual, position, phase)
            for j, name in enumerate(['x', 'y', 'z']):
                expected = stat.iloc[step-1][['rms_x', 'rms_y', 'rms_s'][j]]
                assert abs(local[:, j].std()-expected) < 1e-9
            rows[step].update(actual)
            saved.append(step)
            if step == STEPS:
                order = np.argsort(ids)
                np.savez_compressed(directory/'final-particles.npz', positions_m=position[order],
                    momenta_betagamma=momentum[order], particle_id=ids[order],
                    reference_position_m=reference_r, reference_momentum_betagamma=reference_p,
                    time_s=stamp, reference_phase_rad=phase)
                if manifest['zero_sc'] and manifest['geometry'] == 'straight':
                    expected = initial_position.copy()
                    expected[:, 2] += DISTANCE
                    assert np.max(np.abs(position[order]-expected)) < 1e-9
                    assert np.max(np.abs(momentum[order]-initial_momentum)) < 1e-12
    frame = pd.DataFrame(rows)
    frame.to_csv(directory/'moments.csv', index=False, float_format='%.17g')
    dump(directory/'integrity.json', dict(passed=True, all_stat_counts_charge_time_finite_passed=True,
        saved_particle_steps=saved, all_saved_ids_q_frames_finite_passed=True,
        steps=10, initial_plus_endpoint_rows=len(rows), output_h5_sha256=sha(directory/'track.h5'),
        final_particle_npz_sha256=sha(directory/'final-particles.npz'),
        zero_sc_kinematics_checked=manifest['zero_sc'] and manifest['geometry'] == 'straight'))
    return frame


def run(directory, manifest):
    if manifest.get('returncode') == 0:
        return analyze(directory, manifest)
    assert sha(BINARY) == BINARY_SHA
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='4', OMP_PROC_BIND='false')
    command = [str(BINARY), 'track.in', '--info', '4']
    start = time.monotonic()
    with (directory/'track.out').open('w') as stream:
        result = subprocess.run(command, cwd=directory, env=env, stdout=stream, stderr=subprocess.STDOUT)
    manifest.update(command=command, returncode=result.returncode, elapsed_s=time.monotonic()-start)
    dump(directory/'manifest.json', manifest)
    print(json.dumps({key:manifest[key] for key in ['name', 'returncode', 'elapsed_s']}), flush=True)
    if result.returncode:
        raise RuntimeError(str(directory/'track.out'))
    frame = analyze(directory, manifest)
    manifest['integrity_passed'] = True
    dump(directory/'manifest.json', manifest)
    return frame


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry', choices=['straight', 'bend'], required=True)
    parser.add_argument('--zero-sc', action='store_true')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    directory, manifest = prepare(args.geometry, args.zero_sc)
    if args.run:
        run(directory, manifest)
    else:
        print(directory/'track.in')
