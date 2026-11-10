"""Validate native diagnostics and consolidate the triangular-pipe benchmark."""
from pathlib import Path
import json
import sys
import h5py
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));from prepare_common import sha
sys.path.insert(0,str(ROOT/'analytic-audit'));from analytic import Benchmark
HELPER=Path('/Users/adelmann/git/opalx/docs/validation/fft2d5/uniform-b-ellipsoid')
sys.path.insert(0,str(HELPER));from analyze_opalx import yaw_matrix
OUT=ROOT/'analysis';CASE=Benchmark();POINTS=pd.read_csv(ROOT/'common/probes.csv')

def read_opal(m):
    for p,k in [(m['binary'],'binary_sha256'),(m['distribution'],'distribution_sha256'),(m['reference_path'],'reference_path_sha256')]:
        if sha(p)!=m[k]:raise ValueError('Input hash '+p)
    parent=Path(m['h5']).parent
    if sha(parent/'triangle.in')!=m['input_sha256']:raise ValueError('Input hash')
    offset=0 if m['companion'] else m['source']['source_particles']
    with h5py.File(m['h5']) as f:
        assert list(f)==['Step#0'];g=f['Step#0'];ids=g['id'][:].astype(np.int64)
        assert len(ids)==m['expected_particles'];assert np.array_equal(np.sort(ids),np.arange(len(ids)))
        charge=float(np.asarray(g.attrs['CHARGE']).ravel()[0]);t=float(np.asarray(g.attrs['TIME']).ravel()[0])
        assert np.isclose(charge,m['charge_C'],rtol=1e-11,atol=0)
        assert np.isclose(t,m['config']['dt_s'],rtol=1e-10,atol=1e-30)
        row=np.argsort(ids)[np.arange(len(POINTS))+offset];order=np.argsort(row);back=np.argsort(order)
        get=lambda keys:np.column_stack([g[key][row[order]][back] for key in keys])
        refp=np.asarray(g.attrs['RefPartP']);refr=np.asarray(g.attrs['RefPartR'])
        _,basis=yaw_matrix(refp)
        fields=get(['Ex','Ey','Ez'])@basis.T
        pos=get(['x','y','z'])@basis.T+refr
        nominal=POINTS[['x_m','y_m','s_m']].to_numpy()
        delta=np.linalg.norm(pos-nominal,axis=1)
        assert np.isfinite(fields).all() and np.isfinite(pos).all()
        assert delta.max()<1e-10
    return fields,dict(case=m['case'],particles=len(ids),charge_C=charge,time_s=t,
        gamma_squared=float(1+refp@refp),max_probe_displacement_m=float(delta.max()),
        h5_sha256=sha(m['h5']),input_hashes_pass=True,ids_pass=True,charge_pass=True,time_pass=True)

def opal_rows():
    frames=[];checks=[]
    for p in sorted((ROOT/'opalx/runs').glob('*/manifest.json')):
        m=json.loads(p.read_text())
        if m['companion'] or m.get('returncode')!=0:continue
        cp=p.parent.with_name(p.parent.name+'-probes')/'manifest.json'
        if not cp.exists():continue
        comp=json.loads(cp.read_text())
        if comp.get('returncode')!=0:continue
        for k in ['mesh','numerical_width_m','binary_sha256','reference_path_sha256']:
            assert m[k]==comp[k]
        assert np.isclose(comp['charge_C']/comp['expected_particles'],m['source']['macrocharge_C'],rtol=1e-12)
        full,c=read_opal(m);probe,pc=read_opal(comp)
        probe[:,2]*=pc['gamma_squared']/c['gamma_squared'];es=full[:,2]-probe[:,2]
        d=POINTS.copy();d['code']='OPALX';d['model']='CIRCULAR';d['case']=m['case']
        d['nx'],d['ny'],d['nz']=m['mesh'];d['mpi_size']=1;d['source_particles']=m['source']['source_particles']
        d['ns']=m['source']['ns'];d['ncross']=m['source']['ncross'];d['width_m']=m['numerical_width_m']
        d['Es_V_m']=es
        d['native_Es_V_m']=CASE.opal_native_longitudinal_field(d.s_m.to_numpy(),full_width_x=m['numerical_width_m'],full_width_y=m['numerical_width_m'])
        d['source_sha256']=m['source']['npz_sha256'];frames.append(d);checks.extend([c,pc])
    return frames,checks

def pyorbit_rows():
    frames=[];checks=[]
    for directory in sorted((ROOT/'pyorbit/runs').glob('*')):
        paths=sorted(directory.glob('manifest-rank*.json'))
        if not paths:continue
        ms=[json.loads(p.read_text()) for p in paths];m=ms[0]
        if len(paths)!=m['mpi_size']:continue
        assert set(x['rank'] for x in ms)==set(range(m['mpi_size']))
        assert sum(x['probe_count_local'] for x in ms)==len(POINTS)
        for x in ms:
            assert x['zero_probe_weights'] and x['probe_positions_unchanged']
            assert x['source_sha256']==m['source_sha256'] and x['probe_input_sha256']==sha(ROOT/'common/probes.csv')
            assert np.isclose(x['source_number'],CASE.real_protons,rtol=1e-12)
            argv=x['argv'];source=Path(argv[argv.index('--source')+1])
            assert sha(source)==x['source_sha256']
            assert sha(ROOT/'common/probes.csv')==x['probe_input_sha256']
        d=pd.concat([pd.read_csv(p) for p in sorted(directory.glob('probes-rank*.csv'))],ignore_index=True)
        assert not d.probe_id.duplicated().any();assert len(d)==len(POINTS)
        d=d.rename(columns={'probe_id':'point_id'}).merge(POINTS[['point_id','kind']],on='point_id',validate='one_to_one')
        coordinates=d.merge(POINTS,on='point_id',suffixes=('_got','_input'),validate='one_to_one')
        for key in ['x_m','y_m','s_m']:
            assert np.allclose(coordinates[key+'_got'],coordinates[key+'_input'],rtol=0,atol=2e-14)
        assert np.isfinite(d.Es_V_m).all()
        d['code']='PyORBIT';d['model']=m['model'];d['case']=directory.name
        d['nx']=m['nx'];d['ny']=m['ny'];d['nz']=m['nz'];d['mpi_size']=m['mpi_size']
        d['source_particles']=m['source_particles_global'];d['ns']=np.nan;d['ncross']=np.nan;d['width_m']=.04
        d['source_sha256']=m['source_sha256'];d['native_Es_V_m']=d.Es_analytic_native_constants_V_m
        frames.append(d);checks.append(dict(case=directory.name,code='PyORBIT',mpi_size=m['mpi_size'],
            source_particles=m['source_particles_global'],source_charge_C=m['source_charge_C'],
            zero_probe_weights=True,positions_unchanged=True,probe_count=len(d),source_sha256=m['source_sha256']))
    return frames,checks

def main():
    frames,checks=opal_rows();pf,pc=pyorbit_rows();frames+=pf;checks+=pc
    if not frames:raise ValueError('No completed cases')
    d=pd.concat(frames,ignore_index=True);r=np.hypot(d.x_m,d.y_m)
    d['r_m']=r;d['analytic_Es_V_m']=CASE.longitudinal_field(d.s_m.to_numpy(),r.to_numpy())
    d['axis_scale_V_m']=CASE.longitudinal_base*CASE.g_axis
    d['error_axis_scale_percent']=100*(d.Es_V_m-d.analytic_Es_V_m)/d.axis_scale_V_m
    d['error_local_percent']=100*(d.Es_V_m/d.analytic_Es_V_m-1)
    # Select the same intended physical target IDs in every code. CSV decimal
    # round trips near exactly1m/4m must not change the comparison set.
    target_s=POINTS.s_m.to_numpy();inside=(np.abs(target_s)>=1-1e-12)&(np.abs(target_s)<=4+1e-12)
    accepted=set(POINTS.loc[inside,'point_id']);d['acceptance']=d.point_id.isin(accepted)
    rows=[]
    for case,g in d.groupby('case',sort=False):
        axis=g[(g.kind=='axis')&g.acceptance];rad=g[(g.kind=='radial')&g.acceptance]
        first=g.iloc[0]
        rows.append(dict(case=case,code=first.code,model=first.model,nx=first.nx,ny=first.ny,nz=first.nz,
             mpi_size=first.mpi_size,source_particles=first.source_particles,width_m=first.width_m,
             axis_points=len(axis),max_axis_error_percent=float(axis.error_local_percent.abs().max()),
             median_axis_error_percent=float(axis.error_local_percent.median()),
             max_radial_error_axis_scale_percent=float(rad.error_axis_scale_percent.abs().max()),
             max_radial_local_error_percent=float(rad.error_local_percent.abs().max()),
             max_axis_native_formula_error_percent=float((100*(axis.Es_V_m/axis.native_Es_V_m-1)).abs().max()),
             median_abs_axis_field_V_m=float(axis.Es_V_m.abs().median())))
    d.to_csv(OUT/'fields.csv',index=False);pd.DataFrame(rows).to_csv(OUT/'summary.csv',index=False)
    (OUT/'integrity.json').write_text(json.dumps(checks,indent=2)+'\n')
    controls=[]
    pairs=[('m64','m128','OPALX coupled mesh'),('m128','m256','OPALX coupled mesh'),
        ('m256','source16384','OPALX longitudinal source'),
        ('m128-source16384','source16384','OPALX matched finer-source mesh'),
        ('slice-64x64x128-r1','slice-128x128x128-r1','PyORBIT transverse mesh'),
        ('slice-128x128x128-r1','slice-256x256x128-r1','PyORBIT transverse mesh'),
        ('slice-256x256x128-r1','slice-512x512x128-r1','PyORBIT transverse mesh'),
        ('slice-256x256x128-r1','slice-256x256x256-ns65536-r1','PyORBIT longitudinal mesh plus source'),
        ('slice-512x512x128-r1','slice-512x512x128-nr32np64-r1','PyORBIT cross-section source'),
        ('slice-512x512x128-r1','slice-512x512x128-r2','PyORBIT MPI ranks'),
        ('slice-512x512x128-r1','slice-512x512x128-nativeaudit-r2','PyORBIT native-audited MPI ranks'),
        ('slice-512x512x128-nr32np64-r1','slice-512x512x128-nr32np64-boundary256m64-r1','PyORBIT conducting boundary resolution'),
        ('rb-128x128x128-r1','rb-128x128x256-ns65536-r1','PyORBIT RB longitudinal mesh plus source')]
    for a,b,kind in pairs:
        x=d[(d.case==a)&d.acceptance];y=d[(d.case==b)&d.acceptance]
        if x.empty or y.empty:continue
        z=x.merge(y,on='point_id',suffixes=('_a','_b'),validate='one_to_one')
        controls.append(dict(case_a=a,case_b=b,kind=kind,points=len(z),
            max_change_axis_scale_percent=float((100*(z.Es_V_m_b-z.Es_V_m_a)/z.axis_scale_V_m_a).abs().max())))
    pd.DataFrame(controls).to_csv(OUT/'controls.csv',index=False)
    quadrature=[]
    for nr in [16,32]:
        g=2*np.log(CASE.pipe_radius_m/CASE.beam_radius_m)-np.log((np.arange(nr)+.5)/nr).mean()
        quadrature.append(dict(nrad=nr,discrete_axis_g=float(g),continuum_axis_g=CASE.g_axis,
             predicted_axis_error_percent=float(100*(g/CASE.g_axis-1))))
    (OUT/'source-quadrature.json').write_text(json.dumps(quadrature,indent=2)+'\n')
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=='__main__':main()
