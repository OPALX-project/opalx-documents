#!/usr/bin/env python3
"""Frozen original 2D5 straight round-beam D4-octet source control.

All source and diagnostic particles have the same macrocharge/mass. No current
build is used: its straight OPEN path is a 3D operator and is a different model.
The straight curvature correction is identically zero, so this is the honest
original slice baseline for both zero-curvature descriptions.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time

import h5py
import numpy as np
import pandas as pd
from scipy.constants import c, e, proton_mass

ROOT = Path(__file__).resolve().parent
STUDY = ROOT.parent
BINARY = Path('/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe/fix-longitudinal/binaries/opalx-before-e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf')
BINARY_SHA = 'e85bc09135bef40c6e0b9a278f45d9aab05ad595f2635e7c2088526bb1de70bf'


@dataclass(frozen=True)
class Parameters:
    radius_m: float
    length_m: float = 5.
    charge_C: float = 1e-11
    period_m: float = 12.
    box_m: float = .048
    beta: float = .001
    dt_s: float = 1e-17

    def validate(self):
        assert self.radius_m > 0 and self.length_m > 0
        assert self.period_m > self.length_m and self.box_m > 2*self.radius_m
        assert self.charge_C > 0 and 0 < self.beta < 1 and self.dt_s > 0


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(2**20), b''):
            h.update(chunk)
    return h.hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def snapshot():
    digest = sha(__file__)
    target = ROOT/'provenance'/f'run_straight_octets-{digest}.py'
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(__file__, target)
    assert sha(target) == digest
    return digest, str(target)


def quiet_cross_section(radius, nrad, nphi):
    """Exact round disk equal-area radial rule and D4 reflection/rotation octets."""
    assert nrad > 0 and nphi > 0 and nphi % 8 == 0
    r = np.sqrt((np.arange(nrad)+.5)/nrad)
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    rr, pp = np.meshgrid(r, phi, indexing='ij')
    xy = radius*np.column_stack([(rr*np.cos(pp)).ravel(), (rr*np.sin(pp)).ravel()])
    groups = np.empty(nphi, dtype=int)
    for j in range(nphi//8):
        groups[[j, nphi//4-1-j, nphi//4+j, nphi//2-1-j,
                nphi//2+j, 3*nphi//4-1-j, 3*nphi//4+j, nphi-1-j]] = j
    index = np.repeat(np.arange(nrad), nphi)*(nphi//8)+np.tile(groups, nrad)
    count = nrad*nphi//8
    order = np.argsort(np.mod(np.arange(count)*((np.sqrt(5)-1)/2), 1.))
    ranks = np.empty(count, dtype=int)
    ranks[order] = np.arange(count)
    phase = (ranks[index]+.5)/count
    assert np.allclose(xy.mean(axis=0), 0., atol=radius*1e-14, rtol=0)
    assert np.allclose(np.mean(xy**2, axis=0), radius**2/4, rtol=2e-14, atol=0)
    return xy, phase


def longitudinal_positions(profile, length, ns, phase, start, stop):
    q = (np.arange(start, stop)[:, None]+phase)/(ns//2)
    if profile == 'uniform':
        return length/2*q
    return length/2*(-np.expm1(.5*np.log1p(-q)))


def global_values(positions, beta):
    bg = beta/np.sqrt(1-beta*beta)
    values = np.zeros((len(positions), 6))
    values[:, [0, 2, 4]] = positions
    values[:, 5] = bg
    return values


def reference_path(params):
    directory = ROOT/'sources'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory/f'straight-period{params.period_m:g}m.dat'
    data = np.zeros((2, 15))
    data[:, 0] = [0., params.period_m]
    data[:, 3] = [-params.period_m/2, params.period_m/2]
    data[:, 6] = params.beta/np.sqrt(1-params.beta**2)
    if path.exists():
        assert np.array_equal(np.loadtxt(path), data)
    else:
        np.savetxt(path, data, fmt='%.17e', header='s rx ry rz px py pz ex ey ez bx by bz ke time')
    return path


def prepare_source(params, profile, ns, nrad, nphi, points_path):
    params.validate()
    assert ns >= 2 and ns % 2 == 0
    digest, driver_snapshot = snapshot()
    directory = ROOT/'sources'
    directory.mkdir(parents=True, exist_ok=True)
    name = f'{profile}-octets-a{params.radius_m:g}-L{params.length_m:g}-C{params.period_m:g}-ns{ns}-nr{nrad}-np{nphi}'
    metadata = directory/(name+'.json')
    if metadata.exists():
        saved = json.loads(metadata.read_text())
        assert saved['parameters'] == asdict(params)
        assert saved['points_sha256'] == sha(points_path)
        for key in ['distribution', 'probes_distribution', 'shared_npz', 'probes_csv', 'reference_path']:
            assert sha(saved[key]) == saved[key+'_sha256'], key
        return saved
    cross, phase = quiet_cross_section(params.radius_m, nrad, nphi)
    positions = np.empty((ns*len(cross), 3))
    offset = 0
    for start in range(0, ns//2, 8):
        sp = longitudinal_positions(profile, params.length_m, ns, phase, start, min(start+8, ns//2))
        for sign in [-1., 1.]:
            block = np.column_stack([np.tile(cross, (len(sp), 1)), sign*sp.ravel()])
            positions[offset:offset+len(block)] = block
            offset += len(block)
    assert offset == len(positions)
    rms = np.sqrt(np.mean(positions**2, axis=0))
    assert np.allclose(rms[:2], params.radius_m/2, rtol=2e-12, atol=0)
    points = pd.read_csv(points_path, float_precision='round_trip')
    probes = points[['u_m', 'y_m', 's_m']].to_numpy()
    assert np.linalg.norm(probes[:, :2], axis=1).max() < params.radius_m
    assert abs(probes[:, 2]).max() < params.length_m/2
    for j, key in enumerate(['u_m', 'y_m', 's_m']):
        points['physical_'+key] = probes[:, j]
    for j, key in enumerate(['x_m', 'global_y_m', 'z_m']):
        points[key] = probes[:, j]
    for col, label in enumerate(['b', 'n', 't']):
        for row, direction in enumerate(['x', 'y', 'z']):
            points[label+'_'+direction] = float(row == col)
    probes_csv = directory/(name+'-probes.csv')
    points.to_csv(probes_csv, index=False, float_format='%.17g')
    basis_file = directory/(name+'-probe-basis.npz')
    np.savez(basis_file, basis=np.broadcast_to(np.eye(3), (len(probes), 3, 3)).copy(),
             projected_local_m=probes, physical_material_m=probes,
             point_id=points.point_id.to_numpy(dtype=str))
    qmacro = params.charge_C/len(positions)
    shared = directory/(name+'.npz')
    np.savez_compressed(shared, positions_m=positions, physical_material_m=positions,
        macrocharge_C=qmacro, charge_C=params.charge_C,
        circumference_polyline_m=params.period_m, longitudinal_period_m=params.period_m,
        reference_s_center_m=params.period_m/2,
        source_particle_id=np.arange(len(positions), dtype=np.int64))
    distribution = directory/(name+'.dist')
    with distribution.open('w') as stream:
        stream.write(f'{len(positions)+len(probes)}\nx px y py z pz\n')
        for start in range(0, len(positions), 32768):
            np.savetxt(stream, global_values(positions[start:start+32768], params.beta), fmt='%.17e')
        np.savetxt(stream, global_values(probes, params.beta), fmt='%.17e')
    probes_distribution = directory/(name+'-probes.dist')
    with probes_distribution.open('w') as stream:
        stream.write(f'{len(probes)}\nx px y py z pz\n')
        np.savetxt(stream, global_values(probes, params.beta), fmt='%.17e')
    path = reference_path(params)
    result = dict(profile=profile, parameters=asdict(params), ns=ns, nrad=nrad, nphi=nphi,
        source_particles=len(positions), probe_particles=len(probes), source_charge_C=params.charge_C,
        nominal_charge_C=params.charge_C, macrocharge_C=qmacro,
        full_charge_C=qmacro*(len(positions)+len(probes)), probe_charge_C=qmacro*len(probes),
        distribution=str(distribution), probes_distribution=str(probes_distribution), shared_npz=str(shared),
        probes_csv=str(probes_csv), probe_basis_npz=str(basis_file), reference_path=str(path),
        generator_sha256=digest, generator_snapshot=driver_snapshot,
        points_csv=str(points_path), points_sha256=sha(points_path),
        source_mean_m=positions.mean(axis=0).tolist(), source_rms_m=rms.tolist(),
        target_transverse_RMS_m=params.radius_m/2, physical_rescaling_applied=False,
        geometry='exact straight; local(u,y,s)=(global x,global y,global z)',
        signed_curvature_per_m=0., longitudinal_period_m=params.period_m,
        circumference_polyline_m=params.period_m,
        source_physics='uniform round disk; equal-area radii; exact quiet D4 reflection/rotation octets; staggered inverse longitudinal CDF',
        ready=True)
    for key in ['distribution', 'probes_distribution', 'shared_npz', 'probes_csv', 'probe_basis_npz', 'reference_path']:
        result[key+'_sha256'] = sha(result[key])
    dump(metadata, result)
    print(json.dumps(dict(ready=str(metadata), shared_npz=str(shared), source_particles=len(positions),
                         transverse_RMS_m=rms[:2].tolist())), flush=True)
    return result


def prepare_run(name, mesh, src, probe_only=False):
    p = Parameters(**src['parameters'])
    directory = ROOT/'runs'/(name+('-probes' if probe_only else ''))
    directory.mkdir(parents=True, exist_ok=True)
    manifest = directory/'manifest.json'
    if manifest.exists():
        saved = json.loads(manifest.read_text())
        if saved.get('returncode') == 0:
            assert saved['input_sha256'] == sha(directory/'tube.in')
            return directory, saved
    count = src['probe_particles']+(0 if probe_only else src['source_particles'])
    charge = src['probe_charge_C' if probe_only else 'full_charge_C']
    sourcefile = src['probes_distribution' if probe_only else 'distribution']
    nx, ny, nz = mesh
    p0 = p.beta/np.sqrt(1-p.beta**2)*proton_mass*c*c/e/1e9
    text = f'''// Immutable original e85 independent 2D slices; straight geometry, OPEN g=6.36.
OPTION, VERSION=10900;
OPTION, PSDUMPFREQ=1;
OPTION, STATDUMPFREQ=1;
OPTION, EBDUMP=TRUE;
OPTION, MINBINEMITTED=0;
REAL P0={p0:.17g};
DIST1: DISTRIBUTION,TYPE=FROMFILE,NPARTDIST={count},FNAME="{sourcefile}";
E1: EMISSIONSOURCE,DISTRIBUTION=DIST1,R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0,ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;
ELIST1: EMISSIONSOURCELIST=(E1);
FS: FIELDSOLVER,TYPE="FFT2D5",NX={nx},NY={ny},NZ={nz},PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE=OPEN,REFPATHFNAME="{src['reference_path']}",BEAMR={p.radius_m:.17g},CLOSEDRING=TRUE,PIPESIZEX={p.box_m:.17g},PIPESIZEY={p.box_m:.17g},SCATTERLONGITUDINALLY=TRUE;
B1: BEAM,PARTICLE=PROTON,NALLOC={count},BCHARGE={charge:.17g},SOURCES="ELIST1";
D1: DRIFT,L=1,ELEMEDGE=1000;
L1: LINE=(D1);
TRACK,BEAM=B1,LINE=L1,MAXSTEPS=1,ZSTOP={{100}},DT={{{p.dt_s:.17g}}};
RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1;
ENDTRACK;
'''
    (directory/'tube.in').write_text(text)
    digest, driver_snapshot = snapshot()
    record = dict(name=directory.name, directory=str(directory), h5=str(directory/'tube.h5'),
        profile=src['profile'], geometry='straight', source=src, mesh=list(mesh),
        signed_curvature_per_m=0., bend_radius_m=None, transverse_radius_m=p.radius_m,
        full_length_m=p.length_m, radial_semiaxis_m=p.radius_m, vertical_semiaxis_m=p.radius_m,
        longitudinal_period_m=p.period_m, circumference_polyline_m=p.period_m,
        pipe_size_m=[p.box_m, p.box_m], physical_boundary='free transverse space; no conducting wall',
        longitudinal_boundary='12m periodic numerical coordinate with vacuum gap; not a physical ring',
        longitudinal_model='original local OPEN g=6.36', original_solver=True,
        nonlocal_3D_operator=False, g=6.36, closed_ring=True,
        beta=p.beta, dt_s=p.dt_s, mpi_ranks=1, probe_only=probe_only,
        expected_particles=count, charge_C=charge, macrocharge_C=src['macrocharge_C'],
        binary=str(BINARY), binary_snapshot=str(BINARY), binary_sha256=sha(BINARY),
        distribution=sourcefile, distribution_sha256=sha(sourcefile),
        reference_path=src['reference_path'], reference_path_sha256=sha(src['reference_path']),
        input_sha256=sha(directory/'tube.in'), generator_sha256=digest,
        generator_snapshot=driver_snapshot)
    dump(manifest, record)
    return directory, record


def validate_run(directory, manifest):
    src = manifest['source']
    points = pd.read_csv(src['probes_csv'], float_precision='round_trip')
    wanted = np.arange(len(points))+(0 if manifest['probe_only'] else src['source_particles'])
    original = points[['u_m', 'y_m', 's_m']].to_numpy()
    with h5py.File(directory/'tube.h5') as h:
        assert list(h) == ['Step#0']
        g = h['Step#0']
        ids = g['id'][:].astype(np.int64)
        assert len(ids) == manifest['expected_particles']
        assert np.array_equal(np.sort(ids), np.arange(len(ids)))
        q = g['q'][:]
        assert np.isfinite(q).all() and np.allclose(q, manifest['macrocharge_C'], rtol=5e-12, atol=0)
        assert math.isclose(float(q.sum()), manifest['charge_C'], rel_tol=1e-10)
        stamp = float(np.asarray(g.attrs['TIME']).ravel()[0])
        assert math.isclose(stamp, manifest['dt_s'], rel_tol=1e-10, abs_tol=1e-28)
        refp = np.asarray(g.attrs['RefPartP'], float)
        refr = np.asarray(g.attrs['RefPartR'], float)
        assert np.linalg.norm(refp[:2]) < 1e-12
        angle = np.arctan2(-refp[0], refp[2])
        co, si = np.cos(angle), np.sin(angle)
        basis = np.array([[co, 0., -si], [0., 1., 0.], [si, 0., co]])
        rows = np.argsort(ids)[wanted]
        order, back = np.argsort(rows), np.argsort(np.argsort(rows))
        def get(keys):
            return np.column_stack([g[key][rows[order]][back] for key in keys])
        position = get(['x', 'y', 'z'])@basis.T+refr
        field = get(['Ex', 'Ey', 'Ez'])@basis.T
        assert np.isfinite(field).all()
        velocity = np.array([0., 0., manifest['beta']*c])
        residual = np.linalg.norm(position-original-stamp*velocity, axis=1)
        assert residual.max() < 5e-12
        for j, key in enumerate(['Ex_global_V_m', 'Ey_global_V_m', 'Ez_global_V_m']):
            points[key] = field[:, j]
        points.to_csv(directory/'probes-global.csv', index=False, float_format='%.17g')
        checks = dict(passed=True, particles=len(ids), every_q_preserved=True, total_q_C=float(q.sum()),
            time_s=stamp, maximum_probe_kinematic_residual_m=float(residual.max()),
            reference_gamma_squared=float(1+refp@refp), global_frame_reconstruction_passed=True,
            finite_probe_fields=True, field_units={key:str(h.attrs[key+'Unit']) for key in ['Ex', 'Ey', 'Ez']},
            output_h5_sha256=sha(directory/'tube.h5'))
    dump(directory/'integrity.json', checks)
    return checks


def run(directory, manifest, threads=4):
    if manifest.get('returncode') == 0:
        return validate_run(directory, manifest)
    assert sha(BINARY) == BINARY_SHA
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS=str(threads), OMP_PROC_BIND='false')
    command = [str(BINARY), 'tube.in', '--info', '4']
    start = time.monotonic()
    with (directory/'tube.out').open('w') as stream:
        result = subprocess.run(command, cwd=directory, env=env, stdout=stream, stderr=subprocess.STDOUT)
    manifest.update(returncode=result.returncode, command=command, omp_threads=threads,
                    elapsed_s=time.monotonic()-start)
    dump(directory/'manifest.json', manifest)
    print(json.dumps({k:manifest[k] for k in ['name', 'returncode', 'elapsed_s', 'mesh']}), flush=True)
    if result.returncode:
        raise RuntimeError(str(directory/'tube.out'))
    checks = validate_run(directory, manifest)
    manifest['integrity_passed'] = True
    dump(directory/'manifest.json', manifest)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    parser.add_argument('--profile', choices=['uniform', 'triangle'], required=True)
    parser.add_argument('--radius-m', type=float, required=True)
    parser.add_argument('--length-m', type=float, default=5.)
    parser.add_argument('--charge-c', type=float, default=1e-11)
    parser.add_argument('--period-m', type=float, default=12.)
    parser.add_argument('--box-m', type=float, default=.048)
    parser.add_argument('--ns', type=int, default=128)
    parser.add_argument('--nrad', type=int, default=128)
    parser.add_argument('--nphi', type=int, default=512)
    parser.add_argument('--mesh', nargs=3, type=int, default=[128, 128, 512])
    parser.add_argument('--points', type=Path, default=STUDY/'reference/straight_points.csv')
    parser.add_argument('--threads', type=int, default=4)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    p = Parameters(radius_m=args.radius_m, length_m=args.length_m, charge_C=args.charge_c,
                   period_m=args.period_m, box_m=args.box_m)
    assert sha(BINARY) == BINARY_SHA
    src = prepare_source(p, args.profile, args.ns, args.nrad, args.nphi, args.points)
    for companion in [False, True]:
        directory, manifest = prepare_run(args.name, args.mesh, src, companion)
        if args.run:
            run(directory, manifest, args.threads)
        else:
            print(directory/'tube.in', flush=True)


if __name__ == '__main__':
    main()
