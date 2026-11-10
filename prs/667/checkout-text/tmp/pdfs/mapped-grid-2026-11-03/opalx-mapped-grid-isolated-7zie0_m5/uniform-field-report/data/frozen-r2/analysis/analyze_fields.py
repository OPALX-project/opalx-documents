"""Reproducible FFT2D5/SACR frozen-field comparison at fixed diagnostic targets."""
from pathlib import Path
from functools import lru_cache
import argparse
import hashlib
import json
import os
import sys

os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-sacr-frozen-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-sacr-frozen-cache')
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True,exist_ok=True)
import h5py
import numpy as np
import pandas as pd
from scipy.constants import c, epsilon_0
from scipy.interpolate import PchipInterpolator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FormatStrFormatter, NullFormatter

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT
READONLY_INPUTS=False
STUDY=ROOT.parent
HELPER=Path('/Users/adelmann/git/opalx/docs/validation/fft2d5/uniform-b-ellipsoid')
sys.path.insert(0,str(STUDY/'reference'))
from tube_reference import tangent_endpoint, field as reference_field

DIRECTIONS=('radial','tangential','vertical')
LOCAL_ORDER=('radial','vertical','tangential')
TITLES={'radial':r'Radial $r$','tangential':r'Tangential $s$','vertical':r'Vertical $y$'}
COLORS=('#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9')

@lru_cache(maxsize=32)
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def scalar(value):
    return float(np.asarray(value).ravel()[0])

def source_layout(m):
    return m['source'].get('cross_layout',m['source'].get('layout','polar'))

def source_resolution(m):
    source=m['source']
    return source['ns'],source.get('nrad',0),source.get('nphi',0),source['ncross'],source_layout(m)

def local_fields(global_fields,points,radius):
    theta=points.s_m.to_numpy()/radius
    co,si=np.cos(theta),np.sin(theta)
    return np.c_[global_fields[:,0]*co+global_fields[:,2]*si,
                 global_fields[:,1],
                 -global_fields[:,0]*si+global_fields[:,2]*co]

def validate_inputs(m):
    if m.get('returncode')!=0:
        raise ValueError('Incomplete or failed case: '+m['name'])
    pairs=[(Path(m['directory'])/'tube.in',m['input_sha256']),
           (m['binary'],m['binary_sha256']),
           (m['distribution'],m['distribution_sha256']),
           (m['reference_path'],m['reference_path_sha256'])]
    for path,digest in pairs:
        if sha(str(path))!=digest:
            raise ValueError('Evidence hash mismatch: '+str(path))

def path_probe_geometry(m,points):
    ref=np.loadtxt(m['reference_path'])[:,1:4]
    segments=np.diff(ref,axis=0);lengths=np.linalg.norm(segments,axis=1)
    tangents=segments/lengths[:,None]
    xyz=points[['x_m','global_y_m','z_m']].to_numpy()
    angle=points.s_m.to_numpy()/m['radius_m']
    exact=np.c_[-np.sin(angle),np.zeros(len(angle)),np.cos(angle)]
    errors=[];offsets=[]
    for position,tangent in zip(xyz,exact):
        frac=np.clip(np.sum((position-ref[:-1])*segments,axis=1)/lengths**2,0,1)
        foot=ref[:-1]+frac[:,None]*segments
        best=np.argmin(np.sum((position-foot)**2,axis=1))
        errors.append(np.linalg.norm(tangents[best]-tangent))
        offsets.append(np.linalg.norm(position-foot[best]))
    error=max(errors)
    if error>1e-9:raise ValueError('Probe polyline tangent differs from exact circle: '+m['name'])
    return dict(path_polyline_length_m=float(lengths.sum()),
                max_probe_polyline_tangent_vector_error=float(error),
                max_probe_distance_from_polyline_m=float(max(offsets)))

def read_probes(m,points):
    sys.path.insert(0,str(HELPER))
    from analyze_opalx import yaw_matrix
    validate_inputs(m)
    source=m['source'];n=m['expected_particles']
    wanted=np.arange(len(points))+(0 if m['probe_only'] else source['source_particles'])
    original=points[['x_m','global_y_m','z_m']].to_numpy()
    theta=points.s_m.to_numpy()/m['radius_m']
    velocity=m['beta']*c*np.c_[-np.sin(theta),np.zeros(len(points)),np.cos(theta)]
    with h5py.File(m['h5']) as handle:
        if list(handle)!=['Step#0']:
            raise ValueError('Expected one frozen snapshot in '+m['h5'])
        step=handle['Step#0'];ids=step['id'][:].astype(np.int64)
        if len(ids)!=n or not np.array_equal(np.sort(ids),np.arange(n)):
            raise ValueError('Particle count/ID mismatch: '+m['name'])
        charge=scalar(step.attrs['CHARGE']);time=scalar(step.attrs['TIME'])
        if not np.isclose(charge,m['charge_C'],rtol=1e-11,atol=0):
            raise ValueError('Charge mismatch: '+m['name'])
        if not np.isclose(time,m['dt_s'],rtol=1e-10,atol=1e-28):
            raise ValueError('Snapshot is not the promised tiny step: '+m['name'])
        refp=np.asarray(step.attrs['RefPartP'],dtype=float)
        refr=np.asarray(step.attrs['RefPartR'],dtype=float)
        _,basis=yaw_matrix(refp)
        row=np.argsort(ids)[wanted];order=np.argsort(row);back=np.argsort(order)
        def get(keys):
            return np.column_stack([step[key][row[order]][back] for key in keys])
        e_global=get(['Ex','Ey','Ez'])@basis.T
        position=get(['x','y','z'])@basis.T+refr
        if not np.isfinite(e_global).all() or not np.isfinite(position).all():
            raise ValueError('Non-finite diagnostic data: '+m['name'])
        displacement=np.linalg.norm(position-original,axis=1)
        kinematic_residual=np.linalg.norm(position-original-time*velocity,axis=1)
        if displacement.max()>m['beta']*c*time+5e-12:
            raise ValueError('Source moved beyond frozen bound: '+m['name'])
        # H5 RefPartP is reduced independently after the step. Near-zero
        # transverse means can rotate its reconstructed frame by ~1e-12 rad
        # at 10 million particles (picometres across this 4 m span). This
        # allowance is still <1e-7 of the smallest transverse mesh cell.
        if kinematic_residual.max()>5e-12:
            raise ValueError('Global reconstruction failed: '+m['name'])
    result=dict(case=m['name'],particles=n,charge_C=charge,time_s=time,
                max_probe_displacement_m=float(displacement.max()),
                max_probe_kinematic_residual_m=float(kinematic_residual.max()),
                refpart_p_norm=float(np.linalg.norm(refp)),
                beam_gamma_squared=float(1+refp@refp),
                h5_sha256=sha(m['h5']),input_hashes_passed=True,
                selected_fields_finite=True,particle_ids_passed=True,
                charge_passed=True,time_passed=True,position_reconstruction_passed=True)
    result['kinematic_roundoff_allowance_m']=5e-12
    return local_fields(e_global,points,m['radius_m']),result

def compare(main,companion,reference):
    for key in ('mesh','reference_path_sha256','binary_sha256','dt_s'):
        if main[key]!=companion[key]:raise ValueError('Unmatched companion '+key)
    if not np.isclose(companion['charge_C']/companion['expected_particles'],main['source']['macrocharge_C'],rtol=1e-12):
        raise ValueError('Companion macrocharge differs')
    full,check=read_probes(main,reference)
    probes,pcheck=read_probes(companion,reference)
    gamma_factor=pcheck['beam_gamma_squared']/check['beam_gamma_squared']
    probes[:,2]*=gamma_factor
    numerical=full-probes
    volume=np.pi*main['radial_semiaxis_m']*main['vertical_semiaxis_m']*main['full_length_m']
    rho=main['source']['source_charge_C']/volume
    coupling=rho/(4*np.pi*epsilon_0)
    records=[]
    for j,direction in enumerate(LOCAL_ORDER):
        scale=reference['scale_'+direction].to_numpy()
        exact=reference['F_'+direction].to_numpy()*coupling
        for i,point in reference.iterrows():
            fnum=numerical[i,j]/coupling
            records.append(dict(case=main['name'],point_id=point.point_id,label=point.label,
                ordinal=i,direction=direction,u_m=point.u_m,y_m=point.y_m,s_m=point.s_m,
                end_distance_m=point.end_distance_m,
                region='interior' if point.end_distance_m>=.05-1e-12 else 'near_end',
                NX=main['mesh'][0],NY=main['mesh'][1],NZ=main['mesh'][2],
                source_particles=main['source']['source_particles'],ns=main['source']['ns'],
                nrad=main['source'].get('nrad',0),nphi=main['source'].get('nphi',0),
                cross_layout=source_layout(main),
                path_step_m=main['path_step_m'],source_charge_C=main['source']['source_charge_C'],
                rho_C_per_m3=rho,E_full_V_per_m=full[i,j],E_probe_V_per_m=probes[i,j],
                E_fft_V_per_m=numerical[i,j],E_sacr_V_per_m=exact[i],
                E_error_V_per_m=numerical[i,j]-exact[i],
                characteristic_E_V_per_m=scale[i]*coupling,
                F_fft=fnum,F_sacr=point['F_'+direction],F_scale=scale[i],
                normalized_fft=fnum/scale[i],normalized_sacr=point['F_'+direction]/scale[i],
                normalized_error=(fnum-point['F_'+direction])/scale[i]))
    check.update(probe_companion_case=companion['name'],
                 companion_gamma_correction_factor=gamma_factor,
                 bulk_charge_C=main['source']['source_charge_C'],
                 max_subtracted_probe_E_V_per_m=float(abs(probes).max()))
    check.update(path_probe_geometry(main,reference))
    return records,[check,pcheck]

def summarize(fields):
    rows=[]
    keys=['case','direction','NX','NY','NZ','source_particles','ns','nrad','nphi','path_step_m']
    for values,group in fields.groupby(keys,sort=False):
        base=dict(zip(keys,values))
        for region in ['all','interior','near_end']:
            selected=group if region=='all' else group[group.region==region]
            if selected.empty:continue
            error=selected.normalized_error.to_numpy()
            worst=selected.iloc[np.argmax(abs(error))]
            rows.append(dict(**base,region=region,points=len(selected),
                max_abs_normalized_error=float(abs(error).max()),
                rms_normalized_error=float(np.sqrt(np.mean(error**2))),
                max_abs_E_error_V_per_m=float(selected.E_error_V_per_m.abs().max()),
                worst_point=worst.point_id,worst_s_m=float(worst.s_m)))
    return pd.DataFrame(rows)

def classify(a,b):
    same_source=source_resolution(a)==source_resolution(b)
    same_path=a['reference_path_sha256']==b['reference_path_sha256']
    ma,mb=np.asarray(a['mesh']),np.asarray(b['mesh'])
    if same_source and same_path:
        if np.array_equal(mb[:2],2*ma[:2]) and mb[2]==ma[2]:return 'transverse'
        if np.array_equal(mb[:2],ma[:2]) and mb[2]==2*ma[2]:return 'longitudinal'
    if np.array_equal(ma,mb):
        if same_path and source_layout(a)=='polar' and source_layout(b)=='cartesian':return 'sampling_layout'
        if same_path and b['source']['source_particles']>a['source']['source_particles']:return 'particles'
        if (same_path and b['source']['ncross']>a['source']['ncross']
                and b['source']['ns']<a['source']['ns']):return 'sampling_redistribution'
        if same_source and b['path_step_m']<a['path_step_m']:return 'path'
    return None

def changes(fields,manifests):
    rows=[]
    for a in manifests:
        for b in manifests:
            kind=classify(a,b)
            if kind is None:continue
            merged=fields[fields.case==a['name']].merge(fields[fields.case==b['name']],
                on=['point_id','direction'],suffixes=('_a','_b'),validate='one_to_one')
            for direction in DIRECTIONS:
                group=merged[merged.direction==direction]
                for region in ['all','interior','near_end']:
                    selected=group if region=='all' else group[group.region_a==region]
                    delta=selected.normalized_fft_b.to_numpy()-selected.normalized_fft_a.to_numpy()
                    worst=selected.iloc[np.argmax(abs(delta))]
                    rows.append(dict(kind=kind,case_coarse=a['name'],case_fine=b['name'],
                        direction=direction,region=region,points=len(selected),
                        NX_coarse=a['mesh'][0],NX_fine=b['mesh'][0],NZ_coarse=a['mesh'][2],NZ_fine=b['mesh'][2],
                        ns_coarse=a['source']['ns'],ns_fine=b['source']['ns'],
                        ncross_coarse=a['source']['ncross'],ncross_fine=b['source']['ncross'],
                        path_step_coarse_m=a['path_step_m'],path_step_fine_m=b['path_step_m'],
                        cross_layout_coarse=source_layout(a),cross_layout_fine=source_layout(b),
                        max_abs_normalized_change=float(abs(delta).max()),
                        rms_normalized_change=float(np.sqrt(np.mean(delta**2))),worst_point=worst.point_id))
    return pd.DataFrame(rows)

def select_series(manifests,kind,names=None):
    if names:
        chosen=[m for m in manifests if m['name'] in names]
        if len(chosen)!=len(names):raise ValueError('A requested plot case is incomplete or absent')
        return sorted(chosen,key=lambda m:tuple(m['mesh']))
    groups={}
    for m in manifests:
        key=(m['source']['ns'],m['source'].get('nrad',0),m['source'].get('nphi',0),m['path_step_m'])
        key+=(source_layout(m),)
        key+=((m['mesh'][2],) if kind=='transverse' else tuple(m['mesh'][:2]))
        groups.setdefault(key,[]).append(m)
    # Independent matched-source series: favour the number of mesh levels,
    # then the denser sampling appropriate to that direction. All exploratory
    # runs and control comparisons remain in CSV even when not plotted here.
    def rank(item):
        key,group=item
        count=len({tuple(m['mesh']) for m in group})
        ncross=group[0]['source']['ncross']
        density=(ncross,key[0]) if kind=='transverse' else (key[0],ncross)
        return (count,*density,-key[3])
    _,chosen=max(groups.items(),key=rank)
    return sorted(chosen,key=lambda m:tuple(m['mesh']))

def save(fig,name):
    fig.savefig(OUTPUT/(name+'.pdf'))
    fig.savefig(OUTPUT/(name+'.png'),dpi=300)
    plt.close(fig)

def plot_fields(fields,cases,roles=None):
    fig,axes=plt.subplots(2,3,figsize=(6.65,4.0),layout='constrained',sharex='col',
                           gridspec_kw={'height_ratios':[1.6,1]})
    handles=[]
    for index,m in enumerate(cases):
        color=COLORS[index%len(COLORS)]
        frame=fields[fields.case==m['name']]
        label=(roles or {}).get(m['name'],'FFT2D5')+'\n'+r'$%d\times%d\times%d$'%tuple(m['mesh'])
        handles.append(Line2D([],[],ls='none',marker='o',mfc='none',color=color,ms=3,label=label))
        for j,direction in enumerate(DIRECTIONS):
            group=frame[frame.direction==direction]
            axes[0,j].scatter(group.normalized_sacr,group.normalized_fft,s=13,facecolors='none',
                              edgecolors=color,lw=.65)
            axes[1,j].scatter(group.normalized_sacr,100*group.normalized_error,s=10,color=color,lw=.4)
    for j,direction in enumerate(DIRECTIONS):
        shown=fields[(fields.direction==direction)&fields.case.isin([m['name'] for m in cases])]
        bound=shown[['normalized_sacr','normalized_fft']].abs().to_numpy().max()*1.08
        bound=max(bound,1.)
        axes[0,j].plot([-bound,bound],[-bound,bound],'k--',lw=.8)
        axes[0,j].set(title=TITLES[direction],xlim=(-bound,bound),ylim=(-bound,bound))
        axes[1,j].axhline(0,color='.4',lw=.6)
        axes[1,j].set_xlabel(r'SACR $E_i/E_{i,*}$')
    axes[0,0].set_ylabel(r'FFT2D5 $E_i/E_{i,*}$')
    axes[1,0].set_ylabel('FFT2D5 minus SACR\n[% of component scale]')
    handles.append(Line2D([],[],color='k',ls='--',lw=.8,label='SACR identity'))
    fig.legend(handles=handles,ncol=3,frameon=False,loc='outside upper center')
    for ax in axes.flat:ax.grid(alpha=.17,lw=.5);ax.tick_params(direction='in',top=True,right=True)
    save(fig,'frozen-field-comparison')

def plot_convergence(summary,change,series):
    fig,axes=plt.subplots(2,3,figsize=(6.65,4.65),layout='constrained')
    for row,kind in enumerate(['transverse','longitudinal']):
        cases=series[kind];names=[m['name'] for m in cases]
        data=summary[(summary.case.isin(names))&(summary.region=='all')]
        interior=summary[(summary.case.isin(names))&(summary.region=='interior')]
        if kind=='transverse':
            nz=int(data.NZ.mode().iloc[0]);selected=data[data.NZ==nz];xkey='NX';xlabel=rf'$N_x$ ($N_y=N_x/2$, $N_z={nz}$)'
        else:
            counts=data.groupby(['NX','NY']).NZ.nunique();nx,ny=counts.idxmax()
            selected=data[(data.NX==nx)&(data.NY==ny)];xkey='NZ';xlabel=rf'$N_z$ ($N_x\times N_y={nx}\times{ny}$)'
        for j,direction in enumerate(DIRECTIONS):
            ax=axes[row,j];g=selected[selected.direction==direction].sort_values(xkey)
            ax.plot(g[xkey],100*g.max_abs_normalized_error,'o-',color=COLORS[j],ms=3,lw=1.1)
            core=interior[(interior.direction==direction)&interior.case.isin(g.case)].sort_values(xkey)
            ax.plot(core[xkey],100*core.max_abs_normalized_error,'^:',color=COLORS[j],ms=3,lw=.8)
            if not change.empty:
                q=change[(change.kind==kind)&(change.direction==direction)&(change.region=='all')
                         &change.case_coarse.isin(names)&change.case_fine.isin(names)]
                q=q.sort_values('NX_fine' if kind=='transverse' else 'NZ_fine')
                x=q.NX_fine if kind=='transverse' else q.NZ_fine
                ax.plot(x,100*q.max_abs_normalized_change,'s--',color='.4',ms=3,lw=.8)
            ax.axhline(1,color='.65',ls=':',lw=.7)
            ax.set_xlabel(xlabel);ax.set_ylim(bottom=0);ax.set_xscale('log',base=2)
            if len(g):
                ax.xaxis.set_major_locator(FixedLocator(sorted(g[xkey].unique())))
                ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
            if row==0:ax.set_title(TITLES[direction])
            ax.grid(alpha=.17,lw=.5);ax.tick_params(direction='in',top=True,right=True)
    for ax in axes[:,0]:ax.set_ylabel('Maximum absolute difference\n[% of component scale]')
    handles=[Line2D([],[],color='k',marker='o',ms=3,label='From SACR: all 43 targets'),
             Line2D([],[],color='k',ls=':',marker='^',ms=3,label='From SACR: at least 50 mm from ends'),
             Line2D([],[],color='.4',ls='--',marker='s',ms=3,label='Mesh change: all targets'),
             Line2D([],[],color='.65',ls=':',lw=.7,label='1% of component scale')]
    fig.legend(handles=handles,ncol=2,frameon=False,loc='outside upper center')
    save(fig,'frozen-mesh-convergence')

def plot_end(fields,cases,reference):
    # Plot physical fields charge-normalized to exactly 10 pC so all controls
    # and the continuous reference share the same density.
    a=.005;cc=.0005;b=2.5;r=2.;rho=1e-11/(np.pi*a*cc*2*b)
    coupling=rho/(4*np.pi*epsilon_0)
    distances=np.geomspace(.004,2.5,140)
    exact=np.array([tangent_endpoint(a,cc,b,(0.,0.,b-d),r,512,128) for d in distances])*coupling
    if not READONLY_INPUTS:
        pd.DataFrame({'distance_to_end_m':distances,'SACR_Es_V_per_m_at_10pC':exact}).to_csv(ROOT/'end_profile_reference.csv',index=False)
    fig,axes=plt.subplots(2,1,figsize=(6.65,4.5),layout='constrained',sharex=True,
                           gridspec_kw={'height_ratios':[1.65,1]})
    axes[0].plot(distances*1000,exact,'k-',lw=1.4,label='SACR finite-tube field',zorder=5)
    for index,m in enumerate(cases):
        color=COLORS[index%len(COLORS)]
        group=fields[(fields.case==m['name'])&(fields.direction=='tangential')
                     &(fields.u_m.abs()<1e-15)&(fields.y_m.abs()<1e-15)&(fields.s_m>=0)].sort_values('end_distance_m')
        value=group.F_fft.to_numpy()*coupling
        expected=group.F_sacr.to_numpy()*coupling
        label=r'FFT2D5 $%d\times%d\times%d$'%tuple(m['mesh'])
        axes[0].plot(group.end_distance_m*1000,value,'o--',color=color,ms=3,lw=.8,label=label)
        axes[1].plot(group.end_distance_m*1000,value-expected,'o-',color=color,ms=3,lw=.8)
    axes[0].set_ylabel(r'$E_s$ [V/m, 10 pC]')
    low,high=axes[0].get_ylim();axes[0].set_ylim(bottom=min(0.,low),top=high)
    axes[1].set_ylabel('FFT2D5 minus\nSACR [V/m]');axes[1].axhline(0,color='.4',lw=.6)
    axes[1].set_xlabel('Distance from positive end along centreline [mm]')
    axes[1].set_xscale('log')
    fig.legend(ncol=2,frameon=False,loc='outside upper center')
    for ax in axes:ax.grid(which='both',alpha=.17,lw=.5);ax.tick_params(direction='in',top=True,right=True)
    save(fig,'frozen-longitudinal-end')

def plot_centre(fields,series):
    centre=fields[(fields.point_id=='centre')&(fields.direction=='radial')].copy()
    centre['E_fft_at_10pC_V_per_m']=centre.E_fft_V_per_m*1e-11/centre.source_charge_C
    centre['E_sacr_at_10pC_V_per_m']=centre.E_sacr_V_per_m*1e-11/centre.source_charge_C
    if not READONLY_INPUTS:centre.to_csv(ROOT/'centre_radial.csv',index=False)
    fig,ax=plt.subplots(1,1,figsize=(6.65,2.8),layout='constrained')
    for ax,kind in [(ax,'transverse')]:
        names=[m['name'] for m in series[kind]]
        key='NX' if kind=='transverse' else 'NZ'
        selected=centre[centre.case.isin(names)].sort_values(key)
        exact=selected.E_sacr_at_10pC_V_per_m.iloc[0]
        ax.axhline(exact,color='k',ls='--',lw=1.1)
        # Continuum limit of the current flat transverse operator applied to
        # physical-uniform curved-tube charge: rho_slice=rho*(1+u/R).
        # E_r(0)/(k*rho)=-2*pi*a^2*c/[R*(a+c)], independently integrated.
        a=.005;cc=.0005;r=2.;rho=1e-11/(np.pi*a*cc*5)
        flat=-2*np.pi*a*a*cc/(r*(a+cc))*rho/(4*np.pi*epsilon_0)
        ax.axhline(flat,color='.4',ls=':',lw=1.1)
        ax.plot(selected[key],selected.E_fft_at_10pC_V_per_m,'o-',color=COLORS[0],ms=3,lw=1)
        ax.axhline(0,color='.5',lw=.6)
        ax.set(xscale='log',xlabel=r'$N_x$' if kind=='transverse' else r'$N_z$',
               title='Transverse refinement' if kind=='transverse' else 'Longitudinal refinement')
        ax.xaxis.set_major_locator(FixedLocator(sorted(selected[key].unique())))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.grid(alpha=.17,lw=.5);ax.tick_params(direction='in',top=True,right=True)
    ax.set_ylabel(r'Centre radial field $E_r$ [V/m, 10 pC]')
    handles=[Line2D([],[],color='k',ls='--',lw=1.1,label='SACR curvature field'),
             Line2D([],[],color='.4',ls=':',lw=1.1,label='Ideal flat-slice operator'),
             Line2D([],[],color=COLORS[0],marker='o',ms=3,lw=1,label='FFT2D5')]
    fig.legend(handles=handles,ncol=3,frameon=False,loc='outside upper center')
    save(fig,'frozen-centre-radial')

def native_profile_reference(profile,manifest):
    """Independent physical field in the same polyline direction as native Es.

    A log-distance interpolant is checked at additional midpoints, and the
    angular/radial reference quadrature is independently doubled. This is
    for the dense illustrative profile; fixed-target metrics use direct SACR.
    """
    curve_path=ROOT/'native_sacr_curve.csv'
    if READONLY_INPUTS:
        curve=pd.read_csv(curve_path,float_precision='round_trip')
    else:
        u=float(profile.u_m.iloc[0]);y=float(profile.y_m.iloc[0])
        dmin=float(profile.end_distance_m.min());dmax=2.5
        n=128;checks=[]
        scales=np.array([.005711986642890534,.005711986642890534,.0014202325784798471])
        while True:
            xx=np.linspace(np.log(dmin),np.log(dmax),n+1)
            dd=np.exp(xx)
            values=np.array([reference_field(.005,.0005,2.5,(u,y,2.5-d),2.,512,128) for d in dd])
            interpolator=PchipInterpolator(xx,values,axis=0)
            mid=(xx[:-1]+xx[1:])/2
            truth=np.array([reference_field(.005,.0005,2.5,(u,y,2.5-np.exp(x)),2.,512,128) for x in mid])
            change=np.abs((truth-interpolator(mid))/scales)
            error=float(change.max());checks.append(dict(nodes=len(xx),max_midpoint_error_normalized=error))
            if error<1e-6:break
            n*=2
            if n>1024:raise ValueError('Dense SACR interpolation did not converge')
        # A separate quadrature refinement at fixed positions protects this
        # illustration from using interpolation agreement alone as evidence.
        chosen=np.linspace(0,len(dd)-1,7,dtype=int)
        refined=np.array([reference_field(.005,.0005,2.5,(u,y,2.5-dd[i]),2.,1024,256) for i in chosen])
        qerror=float(np.max(np.abs((refined-values[chosen])/scales)))
        if qerror>1e-7:raise ValueError('Dense SACR angular/radial reference unresolved')
        curve=pd.DataFrame(dict(log_end_distance=xx,end_distance_m=dd,F_radial=values[:,0],
                                F_vertical=values[:,1],F_tangential=values[:,2],u_m=u,y_m=y))
        curve.to_csv(curve_path,index=False)
        (ROOT/'native_sacr_interpolation_checks.json').write_text(json.dumps(dict(
            scope='Illustrative dense profile, main43targets use direct quadrature',
            method='PCHIP in log distance, independently evaluated midpoint checks',
            refinements=checks,quadrature_double_max_normalized_change=qerror,
            nphi=512,nrad=128,passed=True),indent=2)+'\n')
    interpolator=PchipInterpolator(curve.log_end_distance,curve[['F_radial','F_vertical','F_tangential']],axis=0)
    values=interpolator(np.log(profile.end_distance_m.to_numpy()))
    # Reconstruct exactly the nearest-polyline tangent used for native fields.
    ref=np.loadtxt(manifest['reference_path'])[:,1:4]
    if READONLY_INPUTS:
        # Offline rendering receives the cached, already projected fields.
        raise RuntimeError('Native profile projection is generated only in the native analysis')
    segment=np.diff(ref,axis=0);length=np.linalg.norm(segment,axis=1)
    angle=profile.s_m.to_numpy()/2
    u=profile.u_m.to_numpy();y=profile.y_m.to_numpy()
    xyz=np.c_[u*np.cos(angle)-4*np.sin(angle/2)**2,y,(2+u)*np.sin(angle)]
    er=np.c_[np.cos(angle),np.zeros(len(angle)),np.sin(angle)]
    es=np.c_[-np.sin(angle),np.zeros(len(angle)),np.cos(angle)]
    radial_dot=[];tangent_dot=[]
    for x,rhat,shat in zip(xyz,er,es):
        frac=np.clip(np.sum((x-ref[:-1])*segment,axis=1)/length**2,0,1)
        foot=ref[:-1]+frac[:,None]*segment
        best=np.argmin(np.sum((x-foot)**2,axis=1));t=segment[best]/length[best]
        radial_dot.append(t@rhat);tangent_dot.append(t@shat)
    # Reflection: radial field is even in s; tangential field is odd.
    fs=values[:,2]*np.sign(profile.s_m.to_numpy())
    projected=values[:,0]*radial_dot+fs*np.asarray(tangent_dot)
    return projected,fs,dict(max_circle_to_polyline_projection_change_m=float(abs(projected-fs).max()))

def plot_native_end(series):
    cached=ROOT/'native_profiles_comparison.csv'
    audit=STUDY/'audit/native_longitudinal_profiles.csv'
    if READONLY_INPUTS:
        if not cached.exists():return
        data=pd.read_csv(cached,float_precision='round_trip')
    else:
        if not audit.exists():return
        profile=pd.read_csv(audit,float_precision='round_trip')
        wanted=[m['name'] for m in series['longitudinal']]
        profile=profile[profile.case.isin(wanted)].copy()
        if profile.empty:return
        manifest=next(m for m in series['longitudinal'] if m['name']==profile.case.iloc[0])
        cache_meta=dict(input_sha256=sha(str(audit)),reference_evaluator_sha256=sha(str(STUDY/'reference/tube_reference.py')),
                        cases=wanted,reference_path_sha256=manifest['reference_path_sha256'],formula_version=1)
        meta_path=ROOT/'native_profile_cache.json'
        if cached.exists() and meta_path.exists() and json.loads(meta_path.read_text())==cache_meta:
            data=pd.read_csv(cached,float_precision='round_trip')
        else:
            first=profile[profile.case==manifest['name']].sort_values('station')
            projected,circle,check=native_profile_reference(first,manifest)
            check.update(u_m=float(first.u_m.iloc[0]),y_m=float(first.y_m.iloc[0]),
                         source_column='fixed source cross-section index47, every longitudinalstation')
            lookup=pd.DataFrame(dict(station=first.station,F_sacr_native_m=projected,F_sacr_circle_m=circle))
            data=profile.merge(lookup,on='station',validate='many_to_one')
            data.to_csv(cached,index=False)
            (ROOT/'native_profile_projection_check.json').write_text(json.dumps(check,indent=2)+'\n')
            meta_path.write_text(json.dumps(cache_meta,indent=2)+'\n')
    a=.005;cc=.0005;coupling=1e-11/(np.pi*a*cc*5)/(4*np.pi*epsilon_0)
    selected=data[data.s_m>=0].copy()
    fig,axes=plt.subplots(2,1,figsize=(6.65,4.1),layout='constrained',sharex=True,
                           gridspec_kw={'height_ratios':[1.6,1]})
    exact=selected[selected.case==selected.case.iloc[0]].sort_values('end_distance_m')
    axes[0].plot(exact.end_distance_m*1000,exact.F_sacr_native_m*coupling,'k-',lw=1.4,
                 label='SACR, same polyline direction',zorder=5)
    for index,(name,group) in enumerate(selected.groupby('case',sort=False)):
        group=group.sort_values('end_distance_m');color=COLORS[index%len(COLORS)]
        axes[0].plot(group.end_distance_m*1000,group.F_s_subtracted_m*coupling,color=color,lw=.95,
                    label=rf'FFT2D5 $N_z={int(group.mesh_nz.iloc[0])}$')
        axes[1].plot(group.end_distance_m*1000,(group.F_s_subtracted_m-group.F_sacr_native_m)*coupling,
                    color=color,lw=.9)
    for ax in axes:
        ax.axhline(0,color='.5',lw=.6);ax.grid(which='both',alpha=.17,lw=.5)
        ax.tick_params(direction='in',top=True,right=True)
    axes[0].set_ylabel(r'Native longitudinal $E_s$ [V/m, 10 pC]')
    axes[1].set_ylabel('FFT2D5 minus\nSACR [V/m]')
    axes[1].set(xscale='log',xlabel='Distance from positive end [mm]')
    fig.legend(ncol=3,frameon=False,loc='outside upper center')
    save(fig,'frozen-native-longitudinal-end')

def source_checks(manifests):
    rows=[];seen=set()
    for m in manifests:
        source=m['source'];path=Path(source['path']).with_suffix('.npz')
        if str(path) in seen:continue
        seen.add(str(path))
        cross=np.load(path)['cross_section_uy'];a=m['radial_semiaxis_m'];cc=m['vertical_semiaxis_m']
        area_ratio=np.nan
        if source_layout(m)=='cartesian':
            area_ratio=(m['pipe_size_m'][0]/source['nrad'])*(m['pipe_size_m'][1]/source['nphi'])*len(cross)/(np.pi*a*cc)
        rows.append(dict(source=source['path'],layout=source_layout(m),ns=source['ns'],ncross=len(cross),
            nrad=source.get('nrad',0),nphi=source.get('nphi',0),source_particles=source['source_particles'],
            clipped_midpoint_area_over_exact=area_ratio,
            mean_u_m=float(cross[:,0].mean()),exact_mean_u_m=a*a/(4*m['radius_m']),
            mean_y_m=float(cross[:,1].mean()),
            mean_u_squared_over_exact=float(np.mean(cross[:,0]**2)/(a*a/4)),
            mean_y_squared_over_exact=float(np.mean(cross[:,1]**2)/(cc*cc/4))))
    pd.DataFrame(rows).to_csv(ROOT/'source_checks.csv',index=False)

def main():
    global OUTPUT, READONLY_INPUTS
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases',nargs='*');p.add_argument('--require-all',action='store_true')
    p.add_argument('--transverse-cases',nargs='*');p.add_argument('--longitudinal-cases',nargs='*')
    p.add_argument('--field-cases',nargs='*')
    p.add_argument('--replot',action='store_true',help='Use archived CSV/manifest data; no H5 or OPALX binary required')
    p.add_argument('--output-dir',type=Path,help='Figure output directory, defaults to this analysis directory')
    p.add_argument('--no-plots',action='store_true');args=p.parse_args()
    # A saved explicit selection is part of the published study design.
    # Rebuilding should preserve it rather than prefer an older exploratory
    # series merely because that series contains more grid levels.
    selection_path=ROOT/'plot_selection.json'
    if selection_path.exists():
        saved=json.loads(selection_path.read_text())
        for attribute,key in [('transverse_cases','transverse'),('longitudinal_cases','longitudinal'),('field_cases','direct_fields')]:
            if getattr(args,attribute) is None and key in saved:
                setattr(args,attribute,saved[key])
    reference=pd.read_csv(STUDY/'reference/fields_reference.csv',float_precision='round_trip')
    if args.output_dir:
        OUTPUT=args.output_dir.resolve();OUTPUT.mkdir(parents=True,exist_ok=True)
    if args.replot:
        READONLY_INPUTS=True
        fields=pd.read_csv(ROOT/'fields_comparison.csv',float_precision='round_trip')
        summary=pd.read_csv(ROOT/'field_summary.csv',float_precision='round_trip')
        change=pd.read_csv(ROOT/'mesh_and_control_changes.csv',float_precision='round_trip')
        valid=json.loads((ROOT/'cases_manifest.json').read_text())
        render(fields,summary,change,valid,reference,args)
        print('Replotted archived frozen-field data only',flush=True)
        return
    allmanifests=[];archived=[]
    for path in sorted((STUDY/'runs').glob('*/manifest.json')):
        m=json.loads(path.read_text())
        if path.parent.name!=m['name'] or Path(m['directory']).resolve()!=path.parent.resolve():
            archived.append(str(path));continue
        allmanifests.append(m)
    candidates=[m for m in allmanifests if not m['probe_only'] and (not args.cases or m['name'] in args.cases)]
    rows=[];checks=[];valid=[];pending=[]
    byname={m['name']:m for m in allmanifests}
    for m in candidates:
        companion=byname.get(m['name']+'-probes')
        if m.get('returncode')!=0 or companion is None or companion.get('returncode')!=0:
            pending.append(m['name']);continue
        record,check=compare(m,companion,reference)
        rows.extend(record);checks.extend(check);valid.append(m)
    if args.require_all and pending:raise ValueError('Incomplete main/companion pairs: '+', '.join(pending))
    if not rows:
        print(json.dumps({'completed_pairs':0,'pending':pending}));return
    fields=pd.DataFrame(rows);summary=summarize(fields);change=changes(fields,valid)
    fields.to_csv(ROOT/'fields_comparison.csv',index=False)
    summary.to_csv(ROOT/'field_summary.csv',index=False)
    change.to_csv(ROOT/'mesh_and_control_changes.csv',index=False)
    pd.DataFrame(checks).to_csv(ROOT/'run_integrity_checks.csv',index=False)
    result=dict(scope='Sampled frozen electric fields; no tracking claim',completed_pairs=len(valid),
        cases=[m['name'] for m in valid],pending=pending,excluded_archived_manifests=archived,
        points=reference.point_id.nunique(),
        all_completed_pair_integrity_checks_passed=True,
        component_scale_definition='SACR fixed characteristic transverse scales; tangential maximum over fixed43points',
        interior_definition='At least50mm from either end; all points strictlyinside',
        diagnostic_fields_subtracted=True,
        correction='Probe-only Es rescaled by gamma_probe^2/gamma_main^2 before subtraction',
        max_frozen_probe_displacement_m=max(x['max_probe_displacement_m'] for x in checks),
        max_probe_kinematic_residual_m=max(x['max_probe_kinematic_residual_m'] for x in checks),
        source_reference=sha(str(STUDY/'reference/fields_reference.csv')),
        reference_acceptance=json.loads((STUDY/'reference/acceptance.json').read_text()),
        source_hashes={'analyze_fields.py':sha(__file__),'yaw_helper':sha(str(HELPER/'analyze_opalx.py'))})
    (ROOT/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'cases_manifest.json').write_text(json.dumps(valid,indent=2)+'\n')
    source_checks(valid)
    if not args.no_plots:
        render(fields,summary,change,valid,reference,args)
    print(summary[summary.region=='all'][['case','direction','max_abs_normalized_error','max_abs_E_error_V_per_m']].to_string(index=False))
    print(json.dumps({'completed_pairs':len(valid),'pending':pending}),flush=True)

def render(fields,summary,change,valid,reference,args):
        plt.rcParams.update({'font.family':'serif','mathtext.fontset':'stix','font.size':9,
            'axes.labelsize':9,'axes.titlesize':10,'xtick.labelsize':8,'ytick.labelsize':8,
            'legend.fontsize':8,'pdf.fonttype':42})
        series={kind:select_series(valid,kind,getattr(args,kind+'_cases'))
                for kind in ['transverse','longitudinal']}
        if args.field_cases:
            direct=select_series(valid,'transverse',args.field_cases)
        else:
            direct=list({m['name']:m for m in [series['transverse'][-1],series['longitudinal'][-1]]}.values())
        selection={
            **{kind:[m['name'] for m in selected] for kind,selected in series.items()},
            'direct_fields':[m['name'] for m in direct],
            'selection_rule':'Independent matched-source scans; highest number of meshlevels, then denser transverse/longitudinal sampling. Explicit CLI lists override.'}
        if not READONLY_INPUTS:(ROOT/'plot_selection.json').write_text(json.dumps(selection,indent=2)+'\n')
        roles={m['name']:('Transverse study' if source_layout(m)=='cartesian'
                         or m['name'] in [x['name'] for x in series['transverse']]
                         else 'Longitudinal study') for m in direct}
        plot_fields(fields,direct,roles);plot_convergence(summary,change,series)
        plot_end(fields,series['longitudinal'],reference);plot_centre(fields,series)
        plot_native_end(series)

if __name__=='__main__':main()
