"""Analyze native frozen fields against independent uniform/triangle SACR."""
from pathlib import Path
import argparse
import hashlib
import json
import os

os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-sacr-free-profiles-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-sacr-free-profiles-cache')
import h5py
import numpy as np
import pandas as pd
from scipy.constants import c
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/'analysis'
COMPONENTS=('r','y','s')
TITLES=(r'Radial $E_r$',r'Vertical $E_y$',r'Tangential $E_s$')
COLORS=('#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scalar(value):
    return float(np.asarray(value).ravel()[0])


def local_fields(global_fields,points,radius):
    theta=points.s_m.to_numpy()/radius;co,si=np.cos(theta),np.sin(theta)
    return np.c_[global_fields[:,0]*co+global_fields[:,2]*si,global_fields[:,1],
                 -global_fields[:,0]*si+global_fields[:,2]*co]


def validate_manifest(manifest):
    if manifest.get('returncode')!=0:
        raise ValueError('Incomplete case '+manifest['name'])
    binary_evidence=manifest.get('binary_snapshot',manifest['binary'])
    pairs=[(Path(manifest['directory'])/'tube.in',manifest['input_sha256']),
           (binary_evidence,manifest['binary_sha256']),
           (manifest['distribution'],manifest['distribution_sha256']),
           (manifest['reference_path'],manifest['reference_path_sha256']),
           (ROOT/'reference/points_extended.csv',manifest['points_sha256']),
           (ROOT/f'reference/{manifest["profile"]}_fields_reference.csv',manifest['reference_fields_sha256'])]
    for path,expected in pairs:
        if sha(path)!=expected:
            raise ValueError('Evidence hash mismatch: '+str(path))


def read_probes(manifest,points):
    validate_manifest(manifest)
    source=manifest['source'];n=manifest['expected_particles']
    wanted=np.arange(len(points))+(0 if manifest['probe_only'] else source['source_particles'])
    original=points[['x_m','global_y_m','z_m']].to_numpy()
    theta=points.s_m.to_numpy()/manifest['radius_m']
    velocity=manifest['beta']*c*np.c_[-np.sin(theta),np.zeros(len(points)),np.cos(theta)]
    with h5py.File(manifest['h5']) as handle:
        if list(handle)!=['Step#0']:
            raise ValueError('Expected exactly one frozen snapshot')
        step=handle['Step#0'];ids=step['id'][:].astype(np.int64)
        if len(ids)!=n or not np.array_equal(np.sort(ids),np.arange(n)):
            raise ValueError('Particle count/ID mismatch '+manifest['name'])
        reported_charge=scalar(step.attrs['CHARGE']);charge=reported_charge
        q_digest=None
        if manifest.get('weighted_source'):
            # Existing getTotalCharge() reports first local q times global N
            # in attribute mode. Audit the authoritative particle q dataset.
            q_values=step['q'][:]
            if not np.isfinite(q_values).all() or np.any(q_values<=0):
                raise ValueError('Weighted source has invalid particle charges')
            charge=float(np.sum(q_values))
            q_digest=hashlib.sha256(q_values[np.argsort(ids)].tobytes()).hexdigest()
            if q_digest!=manifest['expected_q_dataset_sha256']:
                raise ValueError('Native output q attributes differ from the checkpoint source')
        time=scalar(step.attrs['TIME'])
        if not np.isclose(charge,manifest['charge_C'],rtol=1e-11,atol=0):
            raise ValueError('Snapshot charge mismatch')
        if not np.isclose(time,manifest['dt_s'],rtol=1e-10,atol=1e-28):
            raise ValueError('Snapshot time mismatch')
        refp=np.asarray(step.attrs['RefPartP'],dtype=float);refr=np.asarray(step.attrs['RefPartR'],dtype=float)
        if np.linalg.norm(refp)==0 or abs(refp[1])/np.linalg.norm(refp)>1e-9:
            raise ValueError('Expected planar x-z reference momentum')
        angle=np.arctan2(-refp[0],refp[2]);co,si=np.cos(angle),np.sin(angle)
        basis=np.array([[co,0.,-si],[0.,1.,0.],[si,0.,co]])
        rows=np.argsort(ids)[wanted];order=np.argsort(rows);back=np.argsort(order)
        def get(keys):
            return np.column_stack([step[key][rows[order]][back] for key in keys])
        e_global=get(['Ex','Ey','Ez'])@basis.T
        position=get(['x','y','z'])@basis.T+refr
        if not np.isfinite(e_global).all() or not np.isfinite(position).all():
            raise ValueError('Non-finite frozen data')
        displacement=np.linalg.norm(position-original,axis=1)
        residual=np.linalg.norm(position-original-time*velocity,axis=1)
        if displacement.max()>manifest['beta']*c*time+5e-12 or residual.max()>5e-12:
            raise ValueError('Frozen position/global frame reconstruction failed')
    checks=dict(case=manifest['name'],profile=manifest['profile'],mpi_ranks=manifest['mpi_ranks'],
        particles=n,charge_C=charge,time_s=time,max_probe_displacement_m=float(displacement.max()),
        max_probe_kinematic_residual_m=float(residual.max()),beam_gamma_squared=float(1+refp@refp),
        h5_sha256=sha(manifest['h5']),binary_sha256=manifest['binary_sha256'],input_hashes_passed=True)
    checks.update(h5_reported_CHARGE_C=reported_charge,authoritative_q_sum_C=charge,
                  authoritative_q_dataset_sha256=q_digest,
                  h5_reported_CHARGE_matches_sum=bool(np.isclose(reported_charge,charge,rtol=1e-11,atol=0)))
    if manifest.get('audit_output_checkpoint'):
        with h5py.File(Path(manifest['directory'])/'tube_checkpoint.h5') as handle:
            step=handle['Step#0'];order=np.argsort(step['id'][:])
            for dataset in ['q','m']:
                actual=hashlib.sha256(step[dataset][:][order].tobytes()).hexdigest()
                if actual!=manifest[f'expected_{dataset}_dataset_sha256']:
                    raise ValueError('Output checkpoint changed '+dataset+' attributes')
                checks[f'output_checkpoint_{dataset}_attributes_passed']=True
    return local_fields(e_global,points,manifest['radius_m']),checks


def compare(main,companion,reference):
    for key in ['profile','mesh','reference_path_sha256','binary_sha256','dt_s','mpi_ranks']:
        if main[key]!=companion[key]:
            raise ValueError('Unmatched probe companion '+key)
    if not np.isclose(companion['charge_C']/companion['expected_particles'],main['source']['macrocharge_C'],rtol=1e-12):
        raise ValueError('Companion macrocharge mismatch')
    full,checks=read_probes(main,reference)
    probes,probechecks=read_probes(companion,reference)
    # The finite curved OPEN operator is electrostatic (gamma=1). Its native
    # diagnostic-particle contribution is subtracted directly in all directions.
    gamma_factor=1.
    numerical=full-probes
    source_fraction=main['source']['source_charge_C']/main['source']['nominal_charge_C']
    rows=[]
    for j,component in enumerate(COMPONENTS):
        exact=reference[f'E_{component}_V_m'].to_numpy()*source_fraction
        # Keep the acceptance scale tied to the agreed 43 targets; the added
        # very-near-end diagnostics must not relax the uniform end-field test.
        scale=max(abs(exact[reference.original_target.to_numpy(dtype=bool)]))
        for i,point in reference.iterrows():
            error=numerical[i,j]-exact[i]
            finite_relative=abs(exact[i])>scale*1e-10
            rows.append(dict(case=main['name'],profile=main['profile'],point_id=point.point_id,label=point.label,
                original_target=bool(point.original_target),ordinal=i,component=component,
                u_m=point.u_m,y_m=point.y_m,s_m=point.s_m,end_distance_m=point.end_distance_m,
                region='interior' if point.end_distance_m>=.05-1e-12 else 'near_end',
                NX=main['mesh'][0],NY=main['mesh'][1],NZ=main['mesh'][2],mpi_ranks=main['mpi_ranks'],
                ns=main['source']['ns'],nrad=main['source']['nrad'],nphi=main['source']['nphi'],
                source_particles=main['source']['source_particles'],longitudinal_stagger=main['source']['longitudinal_stagger'],
                source_layout=main['source']['layout'],
                path_step_m=main['path_step_m'],source_charge_C=main['source']['source_charge_C'],
                E_full_V_m=full[i,j],E_probe_V_m=probes[i,j],E_fft_V_m=numerical[i,j],E_sacr_V_m=exact[i],
                E_error_V_m=error,component_scale_V_m=scale,error_over_component_scale=error/scale,
                relative_pointwise_error=error/exact[i] if finite_relative else np.nan,
                weak_centre_radial=point.point_id=='centre' and component=='r'))
    checks.update(companion_gamma_correction_factor=gamma_factor,source_charge_C=main['source']['source_charge_C'],
                  reference_gamma_squared_ratio=probechecks['beam_gamma_squared']/checks['beam_gamma_squared'],
                  field_operator='finite curved OPEN electrostatic, gamma=1; direct companion subtraction',
                  max_subtracted_probe_field_V_m=float(abs(probes).max()))
    return rows,[checks,probechecks]


def summarize(fields):
    rows=[]
    keys=['case','profile','component','NX','NY','NZ','mpi_ranks','source_particles','ns','nrad','nphi','path_step_m']
    for values,group in fields.groupby(keys,sort=False):
        base=dict(zip(keys,values))
        for selection in ['original_all','original_interior','original_near_end','extra_diagnostic','weak_centre_radial']:
            if selection=='weak_centre_radial':
                chosen=group[group.weak_centre_radial]
            elif selection=='extra_diagnostic':
                chosen=group[~group.original_target]
            else:
                chosen=group[group.original_target]
                if selection.endswith('_interior'):
                    chosen=chosen[chosen.region=='interior']
                elif selection.endswith('_near_end'):
                    chosen=chosen[chosen.region=='near_end']
            if chosen.empty:
                continue
            worst=chosen.iloc[np.argmax(abs(chosen.error_over_component_scale))]
            rel=chosen.relative_pointwise_error.abs().dropna()
            rows.append(base|dict(selection=selection,points=len(chosen),
                max_abs_error_over_component_scale=float(chosen.error_over_component_scale.abs().max()),
                max_abs_relative_pointwise_error=float(rel.max()) if len(rel) else np.nan,
                max_abs_E_error_V_m=float(chosen.E_error_V_m.abs().max()),
                worst_point_over_component_scale=worst.point_id,
                passes_one_percent_component_scale=bool(chosen.error_over_component_scale.abs().max()<.01),
                passes_one_percent_pointwise=bool(rel.max()<.01) if len(rel) else True))
    return pd.DataFrame(rows)


def convergence(fields,manifests):
    rows=[]
    for ia,aa in enumerate(manifests):
        for bb in manifests[ia+1:]:
            if aa['profile']!=bb['profile']:
                continue
            a=fields[fields.case==aa['name']];b=fields[fields.case==bb['name']]
            merged=a.merge(b,on=['point_id','component'],suffixes=('_a','_b'),validate='one_to_one')
            same_source=aa['source']['sha256']==bb['source']['sha256']
            same_mesh=aa['mesh']==bb['mesh']
            same_path=aa['reference_path_sha256']==bb['reference_path_sha256']
            if same_source and same_mesh and same_path and aa['mpi_ranks']!=bb['mpi_ranks']:
                kind='MPI rank'
            elif same_source and same_mesh and not same_path:
                kind='reference path'
            elif not same_source and same_mesh and same_path:
                kind='source sampling'
            elif same_source and not same_mesh and same_path:
                kind='mesh'
            else:
                kind='combined refinement'
            for component,group in merged.groupby('component',sort=False):
                original=group[group.original_target_a]
                delta=original.E_fft_V_m_b-original.E_fft_V_m_a
                scale=original.component_scale_V_m_b.iloc[0]
                centre=original[original.point_id=='centre']
                rows.append(dict(case_a=aa['name'],case_b=bb['name'],profile=aa['profile'],component=component,
                    refinement=kind,max_change_over_component_scale=float(abs(delta).max()/scale),
                    centre_change_V_m=float(centre.E_fft_V_m_b.iloc[0]-centre.E_fft_V_m_a.iloc[0]),
                    source_a=aa['source']['source_particles'],source_b=bb['source']['source_particles'],
                    NZ_a=aa['mesh'][2],NZ_b=bb['mesh'][2]))
    return pd.DataFrame(rows)


def plot(fields,manifests):
    plt.rcParams.update({'font.family':'serif','font.size':9,'axes.labelsize':9,'axes.titlesize':10,
                         'legend.fontsize':7,'xtick.labelsize':8,'ytick.labelsize':8,'pdf.fonttype':42,
                         'axes.linewidth':.6,'lines.linewidth':1.,'savefig.bbox':'tight'})
    for profile in ['uniform','triangle']:
        cases=[mm for mm in manifests if mm['profile']==profile]
        if not cases:
            continue
        # Retain each valid series in data; show at most six latest resolutions.
        shown=sorted(cases,key=lambda mm:(tuple(mm['mesh']),mm['source']['source_particles']))[-6:]
        fig,axes=plt.subplots(2,3,figsize=(7.1,4.6),layout='constrained')
        handles=[]
        for k,manifest in enumerate(shown):
            color=COLORS[k%len(COLORS)]
            group=fields[(fields.case==manifest['name'])&fields.original_target]
            label=r'$%d\times%d\times%d$'%tuple(manifest['mesh'])
            handles.append(Line2D([],[],ls='none',marker='o',mfc='none',color=color,ms=3,label=label))
            for j,component in enumerate(COMPONENTS):
                subset=group[group.component==component]
                axes[0,j].scatter(subset.E_sacr_V_m,subset.E_fft_V_m,s=13,facecolors='none',edgecolors=color,lw=.6)
                axes[1,j].scatter(subset.s_m,100*subset.error_over_component_scale,s=10,color=color,lw=.4)
        for j,(component,title) in enumerate(zip(COMPONENTS,TITLES)):
            subset=fields[(fields.profile==profile)&fields.original_target&(fields.component==component)]
            lo=min(0.,subset.E_sacr_V_m.min(),subset.E_fft_V_m.min())
            hi=max(0.,subset.E_sacr_V_m.max(),subset.E_fft_V_m.max())
            padding=.05*max(hi-lo,1e-12);limits=(lo-padding,hi+padding)
            axes[0,j].plot(limits,limits,'k-',lw=.7,zorder=0)
            axes[0,j].set(xlim=limits,ylim=limits,title=title,xlabel=r'SACR reference field (V/m)')
            axes[1,j].axhline(0,color='k',lw=.6)
            axes[1,j].axhline(1,color='.5',ls='--',lw=.6);axes[1,j].axhline(-1,color='.5',ls='--',lw=.6)
            axes[1,j].set(xlabel=r'Arclength $s$ (m)',xlim=(-2.55,2.55))
            for axis in axes[:,j]:
                axis.tick_params(direction='in',top=True,right=True)
                axis.grid(alpha=.18,lw=.4)
        axes[0,0].set_ylabel('FFT2D5 electric field (V/m)')
        axes[1,0].set_ylabel(r'$(E_{\rm FFT2D5}-E_{\rm SACR})/E_{\max}$ (%)')
        handles.insert(0,Line2D([],[],color='k',lw=.7,label='SACR exact Coulomb reference'))
        fig.legend(handles=handles,loc='outside lower center',ncols=min(4,len(handles)),frameon=False)
        fig.suptitle(f'{profile.capitalize()} physical-density tube: L=5 m, R=2 m, Q=10 pC',fontsize=10)
        fig.savefig(OUTPUT/f'{profile}_fields.pdf');fig.savefig(OUTPUT/f'{profile}_fields.png',dpi=400);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',nargs='*',help='specific main case names; default all successful pairs')
    args=parser.parse_args();OUTPUT.mkdir(exist_ok=True)
    manifests=[];records=[];checks=[];excluded=[]
    for path in sorted((ROOT/'runs').glob('*/manifest.json')):
        manifest=json.loads(path.read_text())
        if manifest['probe_only'] or manifest.get('returncode')!=0:
            continue
        if args.cases and manifest['name'] not in args.cases:
            continue
        if manifest.get('invalid_physics_reason'):
            excluded.append(dict(case=manifest['name'],reason=manifest['invalid_physics_reason']))
            continue
        companion_path=path.parent.parent/(manifest['name']+'-probes')/'manifest.json'
        if not companion_path.exists():
            continue
        companion=json.loads(companion_path.read_text())
        if companion.get('returncode')!=0:
            continue
        reference=pd.read_csv(ROOT/f'reference/{manifest["profile"]}_fields_reference.csv',float_precision='round_trip')
        rows,integrity=compare(manifest,companion,reference)
        manifests.append(manifest);records.extend(rows);checks.extend(integrity)
    if args.cases and {mm['name'] for mm in manifests}!=set(args.cases):
        raise ValueError('Requested case is absent, incomplete or lacks a successful companion')
    if not records:
        print('No successful paired native runs to analyze. Input generation is available through run_study.py.')
        return
    fields=pd.DataFrame(records);summary=summarize(fields)
    fields.to_csv(OUTPUT/'field_comparison.csv',index=False)
    summary.to_csv(OUTPUT/'field_summary.csv',index=False)
    pd.DataFrame(checks).to_csv(OUTPUT/'run_integrity_checks.csv',index=False)
    pd.DataFrame(excluded,columns=['case','reason']).to_csv(OUTPUT/'explicitly_invalid_cases.csv',index=False)
    convergence(fields,manifests).to_csv(OUTPUT/'convergence_changes.csv',index=False)
    plot(fields,manifests)
    result=dict(reference='independent exact physical-profile SACR',target_relative_accuracy=.01,
        original_target_count=43,extra_diagnostic_target_count=8,cases=[mm['name'] for mm in manifests],
        original_component_scale_all_pass=bool(summary[summary.selection=='original_all'].passes_one_percent_component_scale.all()),
        original_pointwise_nonzero_all_pass=bool(summary[summary.selection=='original_all'].passes_one_percent_pointwise.all()),
        weak_centre_radial_all_pass=bool(summary[summary.selection=='weak_centre_radial'].passes_one_percent_pointwise.all()),
        explicitly_invalid_cases=excluded,
        note='Convergence, source sampling and MPI rank controls must also be assessed; agreement alone is not an error bound.',
        analysis_sha256=sha(__file__))
    (OUTPUT/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    print(summary.to_string(index=False));print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
