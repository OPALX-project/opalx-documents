#!/usr/bin/env python3
"""Build and independently validate round straight and R=2 m field references."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import shutil
import sys

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad, quad_vec
from scipy.constants import epsilon_0

from straight_reference import axis_field, axis_potential, field, peak_density

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parents[1]/'sacr/free-r2-profiles/reference'
A, H, Q, R = .020, 2.5, 1e-11, 2.
K = 1/(4*np.pi*epsilon_0)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def curved_modules():
    destination = ROOT/'provenance'
    destination.mkdir(exist_ok=True)
    for name in ['uniform_reference.py', 'profile_reference.py']:
        copied = destination/(name.removesuffix('.py')+'-'+sha(OLD/name)+'.py')
        if not copied.exists():
            shutil.copy2(OLD/name, copied)
    spec = importlib.util.spec_from_file_location('uniform_reference', OLD/'uniform_reference.py')
    uniform = importlib.util.module_from_spec(spec)
    sys.modules['uniform_reference'] = uniform
    spec.loader.exec_module(uniform)
    spec = importlib.util.spec_from_file_location('round_triangle_reference', OLD/'profile_reference.py')
    triangle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(triangle)
    return uniform, triangle


def direct_straight(profile, target, nphi=512, nrad=64):
    """Original 3D vector integral, with linear radial map and adaptive s."""
    x, y, s = target
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    cp, sp = np.cos(phi), np.sin(phi)
    b = x*cp+y*sp
    limit = -b+np.sqrt(b*b+A*A-x*x-y*y)
    g, w = leggauss(nrad)
    t = (g[:, None]+1)/2
    radius = limit*t
    weights = (w[:, None]/2)*limit*radius*(2*np.pi/nphi)
    dx, dy = -radius*cp, -radius*sp
    rho = peak_density(A, H, Q, profile)
    def vector(source_s):
        dz = s-source_s
        d3 = (radius*radius+dz*dz)**1.5
        density = 1. if profile == 'uniform' else 1-abs(source_s)/H
        return density*np.array([np.sum(weights*dx/d3), np.sum(weights*dy/d3),
                                 np.sum(weights*dz/d3)])
    value, error = quad_vec(vector, -H, H, points=sorted(set([0., s])),
                            epsabs=2e-12, epsrel=2e-10, limit=1200)
    return K*rho*value, float(K*rho*error)


def direct_curved_center(profile, nrad=96, nphi=128):
    """Independent literal Cartesian source vectors; no boundary identity."""
    gr, wr = leggauss(nrad)
    gp, wp = leggauss(nphi)
    r, dr = (gr+1)/2, wr/2
    phi, dphi = np.pi*(gp+1)/4, wp*np.pi/4
    u, y = A*r[:, None]*np.cos(phi), A*r[:, None]*np.sin(phi)
    weights = A*A*r[:, None]*dr[:, None]*dphi
    def vector(source_s):
        angle = source_s/R
        co, si = np.cos(angle), np.sin(angle)
        bend = 2*R*np.sin(angle/2)**2
        xp, xm = u*co-bend, -u*co-bend
        zp, zm = (R+u)*si, (R-u)*si
        pair = (1+u/R)*(-xp)/(xp*xp+y*y+zp*zp)**1.5
        pair += (1-u/R)*(-xm)/(xm*xm+y*y+zm*zm)**1.5
        density = 1. if profile == 'uniform' else 1-source_s/H
        return float(4*np.sum(weights*pair)*density)
    value, error = quad(vector, 0., H, points=np.geomspace(1e-9, .25, 24),
                        epsabs=2e-15, epsrel=2e-11, limit=1000)
    return K*peak_density(A, H, Q, profile)*value, float(K*peak_density(A, H, Q, profile)*error)


def pde_check(profile):
    target = np.array([.3*A, .2*A, .5*H])
    step = A*1e-3
    jac = np.empty((3, 3))
    potential_gradient = np.empty(3)
    for j in range(3):
        offset = np.eye(3)[j]*step
        plus, pplus = field(A, H, Q, target+offset, profile, 1024, 80, True)
        minus, pminus = field(A, H, Q, target-offset, profile, 1024, 80, True)
        jac[:, j] = (plus-minus)/(2*step)
        potential_gradient[j] = (pplus-pminus)/(2*step)
    local_rho = peak_density(A, H, Q, profile)*(1 if profile == 'uniform' else 1-abs(target[2])/H)
    scale = local_rho/epsilon_0
    divergence = float(np.trace(jac))
    curl = np.array([jac[2, 1]-jac[1, 2], jac[0, 2]-jac[2, 0], jac[1, 0]-jac[0, 1]])
    center = field(A, H, Q, target, profile, 1024, 80)
    assert abs(divergence/scale-1) < 2e-6
    assert np.max(abs(curl))/scale < 2e-7
    assert np.max(abs(center+potential_gradient)) < 2e-7
    return dict(profile=profile, target_m=target.tolist(), difference_step_m=step,
                divergence_V_m2=divergence, rho_over_epsilon_V_m2=scale,
                relative_divergence_error=divergence/scale-1,
                curl_V_m2=curl.tolist(), max_curl_over_rho_epsilon=float(np.max(abs(curl))/scale),
                max_E_plus_grad_potential_V_m=float(np.max(abs(center+potential_gradient))))


def first_order_center(profile):
    lam = Q/(H if profile == 'triangle' else 2*H)
    curvature = 1/R
    finite = curvature*np.log(8*R*np.tan(H/(4*R)))
    if profile == 'triangle':
        integral, _ = quad(lambda s: s/np.sin(s/(2*R)) if s else 2*R, 0., H,
                           epsabs=1e-12, epsrel=2e-13)
        finite -= curvature*curvature*integral/(2*H)
    return K*lam*(finite-curvature*(np.log(A)+1))


def main():
    uniform, triangle = curved_modules()
    convergence, axis_checks, volume_checks, pde, central, output_hashes = [], [], [], [], [], {}
    for geometry in ['straight', 'curved_R2']:
        points = pd.read_csv(ROOT/(geometry+'_points.csv'), float_precision='round_trip')
        targets = points[['u_m', 'y_m', 's_m']].to_numpy()
        for profile in ['uniform', 'triangle']:
            previous = None
            final = None
            rules = [(256, 32), (512, 64), (1024, 96)]
            if geometry == 'curved_R2' and profile == 'uniform':
                # The 0.1 mm end probes resolve a 20 mm round cap. Converge
                # its linear radial disk rule independently of side angles.
                rules.append((1024, 160))
            for nphi, nrad in rules:
                if geometry == 'straight':
                    values = np.array([field(A, H, Q, target, profile, nphi, nrad) for target in targets])
                else:
                    evaluator = uniform.field if profile == 'uniform' else triangle.triangle_field
                    density = peak_density(A, H, Q, profile)
                    values = np.array([K*density*evaluator(A, A, H, target, R, nphi, nrad)
                                       for target in targets])
                if previous is not None:
                    differences = np.max(abs(values-previous), axis=0)
                    convergence.append(dict(geometry=geometry, profile=profile, nphi=nphi, nrad=nrad,
                                            max_change_Eu_V_m=differences[0], max_change_Ey_V_m=differences[1],
                                            max_change_Es_V_m=differences[2]))
                previous = final = values
            pd.DataFrame(convergence).to_csv(ROOT/'quadrature-convergence.csv', index=False, float_format='%.17g')
            assert max(convergence[-1][key] for key in ['max_change_Eu_V_m', 'max_change_Ey_V_m', 'max_change_Es_V_m']) < 2e-8, convergence[-1]
            out = points.copy()
            for j, direction in enumerate(['r', 'y', 's']):
                out['E_'+direction+'_V_m'] = final[:, j]
            out['rho_normalization_C_m3'] = peak_density(A, H, Q, profile)
            path = ROOT/(geometry+'_'+profile+'_fields.csv')
            out.to_csv(path, index=False, float_format='%.17g')
            output_hashes[path.name] = sha(path)
            if geometry == 'straight':
                axis = np.flatnonzero(abs(targets[:, 0])+abs(targets[:, 1]) == 0)
                exact = axis_field(A, H, Q, targets[axis, 2], profile)
                maximum = float(np.max(abs(final[axis, 2]-exact)))
                assert maximum < 2e-8
                axis_checks.append(dict(profile=profile, axis_targets=len(axis), max_abs_Es_error_V_m=maximum,
                                        max_axis_transverse_field_V_m=float(np.max(abs(final[axis, :2])))))
                for target in [[0., 0., 0.], [.3*A, .2*A, .5*H], [0., 0., H-.005]]:
                    direct, error = direct_straight(profile, np.array(target))
                    semi = field(A, H, Q, target, profile, 1024, 96)
                    difference = float(np.max(abs(direct-semi)))
                    assert difference < 2e-7
                    volume_checks.append(dict(geometry=geometry, profile=profile, target_m=target,
                                              max_vector_difference_V_m=difference, adaptive_error_V_m=error))
                pde.append(pde_check(profile))
            else:
                direct, error = direct_curved_center(profile)
                center = final[points.point_id.to_list().index('centre'), 0]
                assert abs(direct-center) < 2e-8
                central.append(dict(profile=profile, SACR_centre_Eu_V_m=float(center),
                                    independent_Cartesian_Eu_V_m=float(direct), difference_V_m=float(direct-center),
                                    first_order_slice_Eu_V_m=first_order_center(profile),
                                    first_order_relative_error_percent=100*(first_order_center(profile)-center)/center))
            print(json.dumps(dict(completed=path.name, targets=len(points))), flush=True)
    pd.DataFrame(convergence).to_csv(ROOT/'quadrature-convergence.csv', index=False, float_format='%.17g')
    result = dict(passed=True, parameters=json.loads((ROOT/'parameters.json').read_text()),
                  field_units='SI electrostatic V/m, local outward-u/y/s components',
                  straight_reference='Independent analytic longitudinal integration plus target-centred physical-disk quadrature.',
                  curved_reference='Audited exact finite-source SACR boundary identity, evaluated anew at a=c20mm,R2m.',
                  source_J='straight J=1; curved J=1+u/R in physical-volume Coulomb source',
                  curved_source_mean_u_m=A*A/(4*R), curved_source_rms_u_about_centroid_m=np.sqrt(A*A/4-A**4/(16*R*R)),
                  curved_source_rms_y_about_centroid_m=A/2, axis_checks=axis_checks,
                  direct_volume_checks=volume_checks, poisson_and_curl_checks=pde, curved_center_checks=central,
                  output_sha256=output_hashes,
                  source_sha256={name:sha(ROOT/name) for name in ['straight_reference.py', 'build_reference.py', 'create_points.py']},
                  prior_SACR_source_sha256={name:sha(OLD/name) for name in ['uniform_reference.py', 'profile_reference.py']})
    (ROOT/'acceptance.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
