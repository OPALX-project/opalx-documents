"""Independent-reference comparison for native uniform-round FFT2D5 fields."""
from dataclasses import replace
from pathlib import Path
import importlib.util
import json
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
sys.path.insert(0,str(STUDY));from prepare_common import sha
sys.path.insert(0,str(STUDY/'analytic-audit'));from analytic import Benchmark
spec=importlib.util.spec_from_file_location('triangle_before_analysis',STUDY/'analysis/analyze.py')
before=importlib.util.module_from_spec(spec);spec.loader.exec_module(before)
POINTS=pd.read_csv(STUDY/'common/probes.csv',float_precision='round_trip')
OUT=ROOT/'analysis';OUT.mkdir(exist_ok=True)
CASE=Benchmark()

def native_opal():
    frames=[];checks=[]
    for path in sorted((ROOT/'opalx/runs').glob('*/manifest.json')):
        m=json.loads(path.read_text())
        if m['companion'] or m.get('returncode')!=0:continue
        cp=path.parent.with_name(path.parent.name+'-probes')/'manifest.json'
        if not cp.exists():continue
        c=json.loads(cp.read_text())
        if c.get('returncode')!=0:continue
        for key in ['mesh','longitudinal_mode','physical_pipe_radius_m','binary_sha256','reference_path_sha256']:
            assert m[key]==c[key]
        full,check=before.read_opal(m);probes,pcheck=before.read_opal(c)
        assert np.isclose(c['charge_C']/c['expected_particles'],m['source']['macrocharge_C'],rtol=1e-12)
        probes[:,2]*=pcheck['gamma_squared']/check['gamma_squared']
        d=POINTS.copy();d['Es_V_m']=full[:,2]-probes[:,2]
        d['case']=m['case'];d['code']='OPALX';d['model']=m['longitudinal_mode']
        d['nx'],d['ny'],d['nz']=m['mesh'];d['mpi_size']=1
        d['width_m']=m['numerical_width_m'];d['pipe_radius_m']=m['physical_pipe_radius_m'] or .02
        d['source_particles']=m['source']['source_particles'];d['source_sha256']=m['source']['npz_sha256']
        d['binary_sha256']=m['binary_sha256'];frames.append(d);checks.extend([check,pcheck])
    return frames,checks

def native_py():
    frames=[];checks=[]
    for directory in sorted((ROOT/'pyorbit/runs').glob('*')):
        paths=list(directory.glob('manifest-rank*.json'))
        if not paths:continue
        metas=[json.loads(p.read_text()) for p in paths];m=metas[0]
        if len(metas)!=m['mpi_size']:continue
        assert set(x['rank'] for x in metas)==set(range(m['mpi_size']))
        for x in metas:
            argv=x['argv'];source=Path(argv[argv.index('--source')+1])
            assert sha(source)==x['source_sha256']
            assert sha(STUDY/'common/probes.csv')==x['probe_input_sha256']
            assert x['zero_probe_weights'] and x['probe_positions_unchanged']
            assert x['native_weight_sum_global']==1e14
            assert x['native_source_count_global']==x['source_particles_global']
        d=pd.concat([pd.read_csv(p,float_precision='round_trip') for p in directory.glob('probes-rank*.csv')],ignore_index=True)
        assert len(d)==len(POINTS) and not d.probe_id.duplicated().any()
        d=d.rename(columns={'probe_id':'point_id'}).merge(POINTS[['point_id','kind']],on='point_id',validate='one_to_one')
        coords=d.merge(POINTS,on='point_id',suffixes=('_got','_input'))
        for key in ['x_m','y_m','s_m']:
            assert np.allclose(coords[key+'_got'],coords[key+'_input'],rtol=0,atol=2e-14)
        assert np.isfinite(d.Es_V_m).all()
        assert np.allclose(d.Es_V_m,d.dE_GeV*1e9/m['kick_length_m'],rtol=2e-15,atol=1e-10)
        d['case']=directory.name;d['code']='PyORBIT';d['model']=m['model']
        d['nx']=m['nx'];d['ny']=m['ny'];d['nz']=m['nz'];d['mpi_size']=m['mpi_size']
        d['width_m']=2*m['pipe_radius_m'];d['pipe_radius_m']=m['pipe_radius_m']
        d['source_particles']=m['source_particles_global'];d['source_sha256']=m['source_sha256']
        frames.append(d);checks.append(dict(case=directory.name,code='PyORBIT',mpi_size=m['mpi_size'],
             source_particles=m['source_particles_global'],native_weight_sum_global=m['native_weight_sum_global'],
             zero_probe_weights=True,probe_positions_unchanged=True,points=len(d)))
    return frames,checks

def main():
    frames,checks=native_opal();p,c=native_py();frames+=p;checks+=c
    if not frames:raise ValueError('No complete cases')
    d=pd.concat(frames,ignore_index=True)
    d['r_m']=np.hypot(d.x_m,d.y_m)
    d['analytic_Es_V_m']=np.nan
    for b,index in d.groupby('pipe_radius_m').groups.items():
        ref=replace(CASE,pipe_radius_m=b)
        d.loc[index,'analytic_Es_V_m']=ref.longitudinal_field(d.loc[index,'s_m'].to_numpy(),d.loc[index,'r_m'].to_numpy())
    s=POINTS.s_m.to_numpy();ids=set(POINTS.loc[(abs(s)>=1-1e-12)&(abs(s)<=4+1e-12),'point_id'])
    d['acceptance']=d.point_id.isin(ids)
    d['axis_scale_V_m']=CASE.longitudinal_base*CASE.g_axis
    d['error_local_percent']=100*(d.Es_V_m/d.analytic_Es_V_m-1)
    d['error_axis_scale_percent']=100*(d.Es_V_m-d.analytic_Es_V_m)/d.axis_scale_V_m
    rows=[]
    for case,g in d.groupby('case'):
        a=g[(g.kind=='axis')&g.acceptance];r=g[(g.kind=='radial')&g.acceptance];x=g.iloc[0]
        rows.append(dict(case=case,code=x.code,model=x.model,nx=x.nx,ny=x.ny,nz=x.nz,mpi_size=x.mpi_size,
             width_m=x.width_m,pipe_radius_m=x.pipe_radius_m,source_particles=x.source_particles,
             axis_points=len(a),radial_points=len(r),
             max_axis_error_percent=float(a.error_local_percent.abs().max()),
             max_radial_local_error_percent=float(r.error_local_percent.abs().max()),
             median_axis_error_percent=float(a.error_local_percent.median()),
             median_abs_axis_field_V_m=float(a.Es_V_m.abs().median())))
    d.to_csv(OUT/'fields.csv',index=False);pd.DataFrame(rows).to_csv(OUT/'summary.csv',index=False)
    (OUT/'integrity.json').write_text(json.dumps(checks,indent=2)+'\n')
    old=pd.read_csv(STUDY/'analysis/fields.csv',float_precision='round_trip')
    controls=[]
    for a,b,label in [('fixed64','fixed128','matched mesh'),('fixed128','fixed256','matched mesh'),
        ('fixed128','fixed-wide256','numerical width at fixed physical radius'),
        ('fixed128','physical-b10mm','physical pipe radius'),
        ('fixed256','slice-repeat-r1','OPALX versus PyORBIT slices'),
        ('fixed256','rb-repeat-r1','OPALX versus PyORBIT Baartman'),
        ('slice-repeat-r1','slice-repeat-r2','PyORBIT MPI')]:
        x=d[(d.case==a)&d.acceptance];y=d[(d.case==b)&d.acceptance]
        if x.empty or y.empty:continue
        v=x.merge(y,on='point_id',suffixes=('_a','_b'),validate='one_to_one')
        change=100*(v.Es_V_m_b-v.Es_V_m_a)/v.axis_scale_V_m_a
        controls.append(dict(case_a=a,case_b=b,kind=label,points=len(v),
             max_change_axis_scale_percent=float(change.abs().max()),
             max_local_relative_difference_percent=float((100*(v.Es_V_m_b-v.Es_V_m_a)/v.analytic_Es_V_m_a).abs().max())))
    # Compare old and rebuilt legacy modes using immutable cached native fields.
    for oldname,newname in [('m128-source16384','legacy128'),('slice-512x512x128-nr32np64-r1','slice-repeat-r1'),
        ('rb-128x128x256-ns65536-r1','rb-repeat-r1')]:
        x=old[(old.case==oldname)&old.acceptance];y=d[(d.case==newname)&d.acceptance]
        if x.empty or y.empty:continue
        v=x.merge(y,on='point_id',suffixes=('_a','_b'))
        controls.append(dict(case_a=oldname,case_b=newname,kind='repeat historical result',points=len(v),
             max_change_axis_scale_percent=float((100*(v.Es_V_m_b-v.Es_V_m_a)/v.axis_scale_V_m_a).abs().max())))
    pd.DataFrame(controls).to_csv(OUT/'controls.csv',index=False)
    (OUT/'provenance.json').write_text(json.dumps(dict(script_sha256=sha(__file__),
         old_fields_csv_sha256=sha(STUDY/'analysis/fields.csv'),common_points_sha256=sha(STUDY/'common/probes.csv')),
         indent=2)+'\n')
    print(pd.DataFrame(rows).to_string(index=False))
    print(pd.DataFrame(controls).to_string(index=False))

if __name__=='__main__':main()
