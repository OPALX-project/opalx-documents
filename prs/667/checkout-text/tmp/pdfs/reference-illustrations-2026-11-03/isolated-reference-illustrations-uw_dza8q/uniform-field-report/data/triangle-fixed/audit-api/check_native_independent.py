"""Independent native audit: no imported production/parent analysis or g kernel."""
from pathlib import Path
from functools import lru_cache
import hashlib
import json
import re
import numpy as np
import pandas as pd
import h5py
from scipy.integrate import quad

HERE=Path(__file__).resolve().parent
FIX=HERE.parent
STUDY=FIX.parent
POINTS=pd.read_csv(STUDY/'common/probes.csv',float_precision='round_trip')
FAMILY=pd.read_csv(FIX/'analysis/fields.csv',float_precision='round_trip')
SUM=pd.read_csv(FIX/'analysis/summary.csv',float_precision='round_trip').set_index('case')
CONFIG=json.loads((STUDY/'common/config.json').read_text())
ARCHIVES=json.loads((FIX/'binary-archives.json').read_text())
Q=CONFIG['charge_C']; L=CONFIG['full_length_m']; A=CONFIG['beam_radius_m']
EPS=CONFIG['epsilon0_F_per_m']; GAMMA=1+CONFIG['kinetic_energy_GeV']/CONFIG['proton_mass_GeV']
accepted=(POINTS.s_m.abs()>=1-1e-12)&(POINTS.s_m.abs()<=4+1e-12)

@lru_cache(maxsize=None)
def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):digest.update(block)
    return digest.hexdigest()

@lru_cache(maxsize=None)
def potential_per_line_charge(radius,wall):
    # Independently integrate the radial Gauss-law field to the grounded wall.
    # No logarithmic longitudinal coefficient is used in this reference.
    if radius<A:
        inside=quad(lambda r:r/(2*np.pi*EPS*A*A),radius,A,epsabs=1e-4,epsrel=2e-12)[0]
        annulus=quad(lambda r:1/(2*np.pi*EPS*r),A,wall,epsabs=1e-4,epsrel=2e-12)[0]
        return inside+annulus
    return quad(lambda r:1/(2*np.pi*EPS*r),radius,wall,epsabs=1e-4,epsrel=2e-12)[0]

def reference(points,wall):
    values=[]
    for p in points.itertuples():
        s=p.s_m;r=float(np.hypot(p.x_m,p.y_m))
        if s==0 or abs(s)==L/2:
            values.append(np.nan);continue
        step=.01
        line=lambda z:2*Q/L*max(0.,1-2*abs(z)/L)
        # The exact finite difference is on a linear branch for accepted targets.
        phi=potential_per_line_charge(r,wall)
        values.append(-(line(s+step)*phi-line(s-step)*phi)/(2*step*GAMMA*GAMMA))
    return np.asarray(values)

def scalar(value):return float(np.asarray(value).ravel()[0])

def expected_binary_path(m):
    if m['binary_sha256']==ARCHIVES['before']['sha256']:
        return ARCHIVES['before']['archived_path']
    assert m['binary_sha256']==ARCHIVES['after']['sha256']
    return m['binary']

def read(m):
    assert m['returncode']==0 and m['mpi_ranks']==1
    directory=Path(m['h5']).parent
    for path,key in [(directory/'triangle.in','input_sha256'),
                     (m['distribution'],'distribution_sha256'),
                     (m['reference_path'],'reference_path_sha256')]:
        assert sha(str(path))==m[key],(m['case'],key)
    assert sha(expected_binary_path(m))==m['binary_sha256']
    assert sha(m['source']['npz'])==m['source']['npz_sha256']
    text=(directory/'triangle.in').read_text()
    assert f'PIPEMODE="{m.get("longitudinal_mode","CIRCULAR")}"' in text
    if m.get('physical_pipe_radius_m') is not None:
        supplied=float(re.search(r'PIPERADIUS=([^,;]+)',text).group(1))
        assert supplied==m['physical_pipe_radius_m']
    with h5py.File(m['h5']) as handle:
        assert list(handle)==['Step#0']
        for field in ['Ex','Ey','Ez']:assert handle.attrs[field+'Unit']==b'V/m'
        assert handle.attrs['TIMEUnit']==b's' and handle.attrs['CHARGEUnit']==b'C'
        g=handle['Step#0']; ids=g['id'][:].astype(np.int64)
        n=m['expected_particles'];assert len(ids)==n
        assert np.array_equal(np.sort(ids),np.arange(n))
        assert np.isclose(scalar(g.attrs['CHARGE']),m['charge_C'],rtol=1e-12,atol=0)
        assert np.isclose(scalar(g.attrs['TIME']),m['config']['dt_s'],rtol=1e-12,atol=0)
        assert handle.attrs['qUnit']==b'C'
        q=g['q'][:]
        assert np.isfinite(q).all()
        assert np.allclose(q,m['source']['macrocharge_C'],rtol=1e-12,atol=0)
        native_charge_sum=float(q.sum())
        assert np.isclose(native_charge_sum,m['charge_C'],rtol=1e-12,atol=0)
        wanted=np.arange(len(POINTS))+(0 if m['companion'] else m['source']['source_particles'])
        raw=np.argsort(ids)[wanted];order=np.argsort(raw);back=np.argsort(order)
        get=lambda names:np.column_stack([g[k][raw[order]][back] for k in names])
        p=np.asarray(g.attrs['RefPartP'],float); ref=np.asarray(g.attrs['RefPartR'],float)
        assert np.isfinite(p).all() and abs(p[1])/np.linalg.norm(p)<1e-12
        # Build the planar axes with dot/cross products, without the parent's
        # yaw angle/trigonometric transform or its read_opal helper.
        t=np.array([p[0],0.,p[2]])/np.hypot(p[0],p[2])
        y=np.array([0.,1.,0.]);x=np.cross(y,t)
        basis=np.column_stack((x,y,t))
        e=get(['Ex','Ey','Ez'])@basis.T
        position=get(['x','y','z'])@basis.T+ref
        nominal=POINTS[['x_m','y_m','s_m']].to_numpy()
        assert np.isfinite(e).all() and np.isfinite(position).all()
        displacement=np.linalg.norm(position-nominal,axis=1)
        assert displacement.max()<1e-10
        gamma2=1+float(p@p)
        assert np.isclose(gamma2,GAMMA*GAMMA,rtol=1e-11)
    return e[:,2],dict(case=m['case'],n=n,charge_C=m['charge_C'],gamma_squared=gamma2,
        native_q_sum_C=native_charge_sum,native_particle_charges_verified=True,
        time_s=m['config']['dt_s'],max_probe_displacement_m=float(displacement.max()),
        h5_sha256=sha(m['h5']),binary_sha256=m['binary_sha256'],all_checks_pass=True)

def pair(main):
    companion=main.parent.with_name(main.parent.name+'-probes')/'manifest.json'
    m=json.loads(main.read_text());c=json.loads(companion.read_text())
    for key in ['mesh','numerical_width_m','reference_path_sha256','binary_sha256']:
        assert m[key]==c[key]
    for x in [m,c]:
        assert np.isclose(x['charge_C']/x['expected_particles'],m['source']['macrocharge_C'],rtol=2e-15)
    full,mc=read(m);probe,pc=read(c)
    field=full-probe*pc['gamma_squared']/mc['gamma_squared']
    assert np.isclose(m['source']['source_charge_C'],Q,rtol=2e-15)
    return field,m,[mc,pc]

def check_py():
    out=[];fields={}
    for directory in sorted((FIX/'pyorbit/runs').glob('*')):
        metas=[json.loads(p.read_text()) for p in sorted(directory.glob('manifest-rank*.json'))]
        if not metas:continue
        m=metas[0];assert len(metas)==m['mpi_size']
        assert set(x['rank'] for x in metas)==set(range(m['mpi_size']))
        for x in metas:
            args=x['argv'];source=args[args.index('--source')+1]
            assert sha(source)==x['source_sha256']
            assert x['probe_input_sha256']==sha(str(STUDY/'common/probes.csv'))
            assert x['native_weight_sum_global']==1e14
            assert x['native_source_count_global']==x['source_particles_global']
            assert x['zero_probe_weights'] and x['probe_positions_unchanged']
            snapshot=STUDY/'pyorbit/harness-snapshots'/('run_native-'+x['harness_sha256']+'.py')
            assert sha(str(snapshot))==x['harness_sha256']
        d=pd.concat([pd.read_csv(p,float_precision='round_trip') for p in directory.glob('probes-rank*.csv')])
        assert len(d)==183 and not d.probe_id.duplicated().any()
        d=d.set_index('probe_id').loc[POINTS.point_id]
        assert np.allclose(d[['x_m','y_m','s_m']],POINTS[['x_m','y_m','s_m']],atol=2e-14,rtol=0)
        assert np.allclose(d.Es_V_m,d.dE_GeV*1e9/m['kick_length_m'],rtol=2e-15,atol=1e-10)
        values=d.Es_V_m.to_numpy();fields[directory.name]=values
        out.append(dict(case=directory.name,mpi_size=m['mpi_size'],points=len(values),
            max_axis_error_percent=float(np.max(np.abs(values[accepted&(POINTS.kind=='axis')]/reference(POINTS,.02)[accepted&(POINTS.kind=='axis')]-1))*100),
            native_charge_and_provenance_checks_pass=True))
    return fields,out

def main():
    records=[];summary=[];fields={};csvdiff=[]
    axis=accepted&(POINTS.kind=='axis');radial=accepted&(POINTS.kind=='radial')
    assert axis.sum()==62 and radial.sum()==82 and accepted.sum()==144
    for path in sorted((FIX/'opalx/runs').glob('*/manifest.json')):
        m=json.loads(path.read_text())
        if m['companion']:continue
        values,m,checks=pair(path);fields[m['case']]=values;records.extend(checks)
        physical_b=m['physical_pipe_radius_m'] or .02
        expected=reference(POINTS,physical_b)
        rows=FAMILY[FAMILY.case==m['case']].set_index('point_id').loc[POINTS.point_id]
        discrepancy=float(np.max(np.abs(rows.Es_V_m.to_numpy()-values)))
        assert discrepancy<2e-8
        axerr=float(np.max(np.abs(values[axis]/expected[axis]-1))*100)
        rerr=float(np.max(np.abs(values[radial]/expected[radial]-1))*100)
        assert abs(axerr-SUM.loc[m['case'],'max_axis_error_percent'])<2e-9
        assert abs(rerr-SUM.loc[m['case'],'max_radial_local_error_percent'])<2e-9
        csvdiff.append(discrepancy)
        summary.append(dict(case=m['case'],axis_points=int(axis.sum()),radial_points=int(radial.sum()),
             max_axis_error_percent=axerr,max_radial_local_error_percent=rerr,
             max_csv_Es_difference_V_m=discrepancy))
    old_path=STUDY/'opalx/runs/m128-source16384/manifest.json'
    old,oldm,oldchecks=pair(old_path);records.extend(oldchecks)
    cached=pd.read_csv(STUDY/'analysis/fields.csv',float_precision='round_trip')
    cached=cached[cached.case=='m128-source16384'].set_index('point_id').loc[POINTS.point_id]
    old_cache=float(np.max(np.abs(old-cached.Es_V_m.to_numpy())))
    legacy_delta=float(np.max(np.abs(old-fields['legacy128'])))
    assert old_cache<2e-8 and legacy_delta<2e-8
    scale=abs(reference(POINTS,.02)[axis][0])
    width_difference=float(np.max(np.abs(fields['fixed128'][accepted]-fields['fixed-wide256'][accepted])))
    assert width_difference<1e-7
    actual=fields['physical-b10mm']-fields['fixed128']
    expected=reference(POINTS,.01)-reference(POINTS,.02)
    radius_err=float(np.max(np.abs((actual[accepted]-expected[accepted])/expected[accepted]))*100)
    assert radius_err<.03
    pfields,pchecks=check_py()
    direct={}
    for code in ['slice-repeat-r1','rb-repeat-r1']:
        direct[code]=float(np.max(np.abs((pfields[code][accepted]-fields['fixed256'][accepted])/scale))*100)
    mpi=float(np.max(np.abs(pfields['slice-repeat-r1']-pfields['slice-repeat-r2'])))
    assert mpi<1e-8
    pd.DataFrame(records).to_csv(HERE/'snapshot-checks.csv',index=False)
    pd.DataFrame(summary).to_csv(HERE/'independent-summary.csv',index=False)
    result=dict(checks_pass=True,new_opalx_pairs=len(summary),new_opalx_snapshots=2*len(summary),
        independently_reread_historical_snapshots=2,pyorbit_cases=pchecks,
        max_consolidated_Es_difference_V_m=max(csvdiff),historical_cache_difference_V_m=old_cache,
        legacy_rebuilt_difference_V_m=legacy_delta,
        numerical_width_control_difference_V_m=width_difference,
        physical_radius_change_error_percent=radius_err,
        direct_fixed256_to_py_axis_scale_difference_percent=direct,
        py_mpi_all_target_difference_V_m=mpi,
        reference='Numerical real-space integration of Gauss-law radial field to grounded wall, followed by finite-s potential derivative; no imported g kernel or parent read_opal helper.',
        analysis_csv_sha256=sha(str(FIX/'analysis/fields.csv')),
        summary_csv_sha256=sha(str(FIX/'analysis/summary.csv')),
        audit_script_sha256=sha(str(Path(__file__).resolve())))
    (HERE/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
