#!/usr/bin/env python3
"""Exactly ten native PyORBIT midpoint steps on the shared straight source."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys
import time

import numpy as np
import pandas as pd
from orbit.core.bunch import Bunch, BunchTwissAnalysis, SynchPartRedefinitionZdE
from orbit.core.linac import linac_tracking
from orbit.core.spacecharge import Grid1D, LSpaceChargeCalc, SpaceChargeCalcSliceBySlice2D

E, C, MASS = 1.602176634e-19, 299792458., .938272029


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-json', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--zero-sc', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    assert not (args.out/'manifest.json').exists()
    started = time.monotonic()
    source = json.loads(args.source_json.read_text())
    assert source['geometry'] == 'straight' and source['source_particles'] == 1048576
    assert sha(source['npz']) == source['npz_sha256']
    with np.load(source['npz']) as data:
        initial = data['material_m']
        ids = data['source_particle_id']
        initial_p = data['momenta_betagamma']
    count = len(initial)
    assert np.array_equal(ids, np.arange(count))
    beta = source['beta']
    gamma = 1/math.sqrt(1-beta*beta)
    total_length, steps, nx, ny, nz, width, period, physical_g = 1., 10, 128, 128, 512, .048, 12., 6.36
    ds = total_length/steps
    dt = ds/(beta*C)
    native_g = physical_g*ds/period
    ratio = math.exp((native_g-1)/2)
    macro_size = source['macrocharge_C']/E
    bunch = Bunch()
    bunch.mass(MASS)
    bunch.charge(1.)
    bunch.macroSize(macro_size)
    bunch.addPartAttr('macrosize')
    kinetic = MASS*beta*beta*gamma*gamma/(gamma+1)
    bunch.getSyncParticle().kinEnergy(kinetic)
    assert np.max(np.abs(initial_p[:, :2])) == 0.
    for x, y, z in initial:
        bunch.addParticle(float(x), 0., float(y), 0., float(z), 0.)
        bunch.partAttrValue('macrosize', bunch.getSize()-1, 0, macro_size)
    half = width/2*(1-1/nx)
    guards = np.array([[-half, 0., -period/2], [half, 0., period/2],
                       [0., -half, -period/2], [0., half, period/2],
                       [0., 0., -period/2], [0., 0., period/2]])
    for x, y, z in guards:
        bunch.addParticle(float(x), 0., float(y), 0., float(z), 0.)
        bunch.partAttrValue('macrosize', bunch.getSize()-1, 0, 0.)
    def reset_guards(reference_s=0.):
        for k, (x, y, z) in enumerate(guards):
            i = count+k
            bunch.x(i, float(x)); bunch.xp(i, 0.)
            bunch.y(i, float(y)); bunch.yp(i, 0.)
            bunch.z(i, float(z-reference_s)); bunch.dE(i, 0.)
    # Exact native deposition/gather test for the guard contribution.
    test = Bunch()
    for x, y, z in guards:
        test.addParticle(float(x), 0., float(y), 0., float(z), 0.)
    grid = Grid1D(nz, period)
    grid.setGridZ(-period/2, period/2)
    grid.setZero()
    grid.binBunchSmoothedByParticle(test)
    checked_z = np.linspace(-3., 4., 1001)
    guard_gradient = np.array([grid.calcGradient(float(z)) for z in checked_z])
    assert np.max(np.abs(guard_gradient)) == 0.
    guard_check = dict(passed=True, method='native Grid1D smoothed unit-count deposition and native finite-difference gradient',
                       physical_lab_z_interval_m=[-3., 4.], samples=len(checked_z),
                       maximum_native_gradient=0., all_guards_at_lab_ends=True)
    (args.out/'guard-check.json').write_text(json.dumps(guard_check, indent=2)+'\n')
    solver = SpaceChargeCalcSliceBySlice2D(nx, ny, nz, 1.)
    solver.longTracking(0)
    longitudinal = LSpaceChargeCalc(ratio, period, 0, 0, nz)
    longitudinal.setUseGrad(1)
    longitudinal.setSmoothGrad(0)
    shift = SynchPartRedefinitionZdE()
    analysis = BunchTwissAnalysis()
    rows, mesh_checks = [], []
    def record(step):
        analysis.analyzeBunch(bunch)
        mean = np.array([analysis.getAverage(i) for i in range(6)])
        covariance = np.array([[analysis.getCorrelation(i, j) for j in range(6)] for i in range(6)])
        charge = analysis.getGlobalMacrosize()*E
        assert math.isclose(charge, source['charge_C'], rel_tol=2e-10)
        assert np.isfinite(mean).all() and np.isfinite(covariance).all()
        row = dict(step=step, time_s=step*dt, nominal_reference_s_m=step*ds,
                   nominal_design_advance_m=step*ds, particles=count,
                   sync_time_s=bunch.getSyncParticle().time(), charge_C=charge,
                   source_particles=count, space_charge_enabled=not args.zero_sc,
                   sigma_global_x_m=math.sqrt(max(0., covariance[0, 0])),
                   sigma_global_y_m=math.sqrt(max(0., covariance[2, 2])),
                   sigma_global_z_m=math.sqrt(max(0., covariance[4, 4])),
                   sigma_u_m=math.sqrt(max(0., covariance[0, 0])),
                   sigma_y_m=math.sqrt(max(0., covariance[2, 2])),
                   sigma_s_m=math.sqrt(max(0., covariance[4, 4])),
                   mean_global_x_m=mean[0], mean_global_y_m=mean[2], mean_global_z_m=mean[4]+step*ds,
                   mean_u_m=mean[0], mean_y_m=mean[2], mean_s_m=mean[4]+step*ds)
        for i in range(6):
            row[f'native_mean_{i}'] = mean[i]
            for j in range(6):
                row[f'native_cov_{i}{j}'] = covariance[i, j]
        rows.append(row)
        pd.DataFrame(rows).to_csv(args.out/'moments.csv', index=False, float_format='%.17g')
        print(json.dumps({key: row[key] for key in ['step', 'sigma_u_m', 'sigma_y_m', 'sigma_s_m']}), flush=True)
    record(0)
    for step in range(steps):
        linac_tracking.drift(bunch, ds/2)
        midpoint = (step+.5)*ds
        if not args.zero_sc:
            shift.shift_Z(bunch, midpoint)
            reset_guards(0.)
            solver.trackBunch(bunch, ds)
            longitudinal.trackBunch(bunch)
            rho = solver.getRhoGrid()
            actual = [rho.getMinX(), rho.getMaxX(), rho.getMinY(), rho.getMaxY(),
                      rho.getMinZ()/gamma, rho.getMaxZ()/gamma]
            assert np.max(np.abs(np.array(actual)-np.array([-half, half, -half, half, -6., 6.]))) < 2e-12
            mesh_checks.append(dict(step=step+1, lab_bounds_m=actual))
            reset_guards(0.)
            shift.shift_Z(bunch, -midpoint)
        linac_tracking.drift(bunch, ds/2)
        reset_guards((step+1)*ds)
        record(step+1)
    final = np.array([[bunch.x(i), bunch.xp(i), bunch.y(i), bunch.yp(i), bunch.z(i), bunch.dE(i)]
                      for i in range(count)])
    positions = final[:, [0, 2, 4]].copy()
    positions[:, 2] += total_length
    p0 = beta*gamma
    px, py = final[:, 1]*p0, final[:, 3]*p0
    normalized_kinetic = (kinetic+final[:, 5])/MASS
    pz2 = normalized_kinetic*(normalized_kinetic+2)-px*px-py*py
    assert pz2.min() > 0.
    momentum = np.c_[px, py, np.sqrt(pz2)]
    np.savez_compressed(args.out/'final-particles.npz', source_particle_id=ids,
                        positions_m=positions, momenta_betagamma=momentum, native_state=final)
    if args.zero_sc:
        assert np.max(np.abs(positions-initial-np.array([0., 0., 1.]))) < 1e-10
        assert np.max(np.abs(momentum-initial_p)) < 1e-12
    assert len(rows) == 11 and bunch.getSize() == count+6
    assert abs(bunch.getSyncParticle().time()-steps*dt) < 1e-18
    libraries = {name: dict(path=sys.modules[name].__file__, sha256=sha(sys.modules[name].__file__))
                 for name in ['orbit.core.bunch', 'orbit.core.linac', 'orbit.core.spacecharge']}
    manifest = dict(passed=True, geometry='straight', steps=steps, reference_advance_m=1.,
                    dt_s=dt, ds_m=ds, source=source, source_json=str(args.source_json),
                    source_json_sha256=sha(args.source_json), native_driver_sha256=sha(__file__),
                    space_charge_enabled=not args.zero_sc, ZeroSC_same_nominal_charge=args.zero_sc,
                    nominal_charge_C=source['charge_C'], mesh=[nx, ny, nz], box_xy_m=[width, width],
                    longitudinal_period_m=period, physical_g=physical_g, native_encoded_step_g=native_g,
                    native_encoded_b_a=ratio, beta=beta, gamma=gamma, mass_GeV=MASS,
                    integrator='native linac half drift / native transverse+LS step kick / native linac half drift',
                    fixed_lab_mesh=True, lab_mesh_checks=mesh_checks, guard_check=guard_check,
                    transverse_work_patch=False,
                    limitation='Native transverse SC changes xp/yp without adding transverse work to dE; preserved transparently.',
                    native_libraries=libraries, python=sys.executable, argv=sys.argv,
                    elapsed_seconds=time.monotonic()-started)
    (args.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(dict(passed=True, seconds=manifest['elapsed_seconds'], out=str(args.out))), flush=True)


if __name__ == '__main__':
    main()
