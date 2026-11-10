#!/usr/bin/env python3
"""Join frozen native models with independent references and build paper figures.

Only octet/D4 sources are primary. Historical quartet controls are retained
in their original folders. No native field or reference is fitted/rescaled.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-round-paper-cache')
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True,exist_ok=True)
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
PAPER=Path('/Users/adelmann/git/opalx/docs/validation/fft2d5/model-comparison-paper')
OUT=ROOT/'analysis'
COLOURS={'Original 2D5':'#0072B2','Corrected 2D5':'#009E73','PyORBIT':'#D55E00'}


def read(path):return pd.read_csv(path,float_precision='round_trip')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exact_basis(geometry,s):
    theta=np.asarray(s)/2 if geometry=='curved' else np.zeros(len(s))
    co,si=np.cos(theta),np.sin(theta)
    return np.stack([np.c_[co,np.zeros(len(s)),si],np.tile([0.,1.,0.],(len(s),1)),
                     np.c_[-si,np.zeros(len(s)),co]],axis=2)


def probe_basis(path,ids):
    p=read(path).set_index('point_id').loc[ids]
    return np.stack([p[[f'{b}_{d}' for d in 'xyz']].to_numpy() for b in ['b','n','t']],axis=2)


def collect():
    rows=[];selection=[]
    refs={(g,p):read(ROOT/'reference'/f'{"straight" if g=="straight" else "curved_R2"}_{p}_fields.csv').set_index('point_id')
          for g in ['straight','curved'] for p in ['uniform','triangle']}
    for geometry,model,folder in [('straight','Original 2D5',ROOT/'opalx'),
        ('curved','Original 2D5',ROOT/'curved/opalx'),('curved','Corrected 2D5',ROOT/'curved/corrected')]:
        for path in sorted((folder/'runs').glob('*/manifest.json')):
            m=json.loads(path.read_text())
            if m.get('probe_only') or m.get('returncode')!=0 or m['source']['source_particles']<1e6:continue
            if model=='Original 2D5' and 'octets' not in path.parent.name:continue
            companion=path.parent.with_name(path.parent.name+'-probes')
            c=json.loads((companion/'manifest.json').read_text())
            if c.get('returncode')!=0:continue
            profile=m['profile'];ref=refs[geometry,profile];ids=ref.index
            f=read(path.parent/'probes-global.csv').set_index('point_id').loc[ids]
            p=read(companion/'probes-global.csv').set_index('point_id').loc[ids]
            fc=json.loads((path.parent/'integrity.json').read_text());pc=json.loads((companion/'integrity.json').read_text())
            assert fc['passed'] and pc['passed']
            assert sha(m['source']['shared_npz'])==m['source']['shared_npz_sha256']
            basis=exact_basis(geometry,ref.s_m) if model=='Corrected 2D5' else probe_basis(m['source']['probes_csv'],ids)
            t=basis[:,:,2]
            keys=['Ex_global_V_m','Ey_global_V_m','Ez_global_V_m']
            full=f[keys].to_numpy();probe=p[keys].to_numpy()
            full+=((fc['reference_gamma_squared']-1)*np.sum(full*t,axis=1))[:,None]*t
            probe+=((pc['reference_gamma_squared']-1)*np.sum(probe*t,axis=1))[:,None]*t
            e=np.einsum('nji,nj->ni',exact_basis(geometry,ref.s_m),full-probe)
            add(rows,geometry,model,profile,m['mesh'],path.parent.name,e,ref,m['source']['shared_npz_sha256'])
            selection.append(dict(geometry=geometry,model=model,profile=profile,mesh=m['mesh'],
                manifest=str(path),source=m['source']['shared_npz'],source_sha256=m['source']['shared_npz_sha256'],
                binary_sha256=m['binary_sha256']))
    for path in sorted((ROOT/'pyorbit/runs').glob('*/manifest-rank0.json')):
        m=json.loads(path.read_text());name=path.parent.name
        if not name.endswith('-octet') or m['mpi_size']!=1:continue
        geometry='straight' if m['geometry']['kind']=='straight' else 'curved'
        profile=m['profile'];ref=refs[geometry,profile];ids=ref.index
        assert sha(m['source_file'])==m['source_sha256']
        native=read(path.parent/'fields-rank0.csv').set_index('point_id').loc[ids]
        e=native[['Eu_V_m','Ey_V_m','Es_V_m']].to_numpy()
        e[:,2]*=m['native_cases'][0]['gamma']**2
        global_e=np.einsum('nij,nj->ni',probe_basis(m['probes_file'],ids),e)
        e=np.einsum('nji,nj->ni',exact_basis(geometry,ref.s_m),global_e)
        mesh=[m['nx'],m['ny'],m['nz']]
        add(rows,geometry,'PyORBIT',profile,mesh,name,e,ref,m['source_sha256'])
        selection.append(dict(geometry=geometry,model='PyORBIT',profile=profile,mesh=mesh,
            manifest=str(path),source=m['source_file'],source_sha256=m['source_sha256'],native_revision=m['pyorbit_revision']))
    frame=pd.DataFrame(rows)
    # Every native code at a given geometry/profile/grid must use identical source bytes.
    assert (frame.groupby(['geometry','profile','NX','NY','NZ']).source_sha256.nunique()==1).all()
    return frame,selection


def add(rows,geometry,model,profile,mesh,case,e,ref,source_hash):
    for j,component in enumerate(['u','y','s']):
        refkey=f'E_{"r" if component=="u" else component}_V_m'
        scale=float(abs(ref.loc[ref.original_target,refkey]).max())
        for i,(point_id,p) in enumerate(ref.iterrows()):
            value=float(e[i,j]);exact=float(p[refkey]);err=value-exact
            rows.append(dict(geometry=geometry,model=model,profile=profile,case=case,
                NX=mesh[0],NY=mesh[1],NZ=mesh[2],point_id=point_id,component=component,
                u_m=p.u_m,y_m=p.y_m,s_m=p.s_m,end_distance_m=p.end_distance_m,
                original_target=bool(p.original_target),native_V_m=value,reference_V_m=exact,error_V_m=err,
                component_scale_V_m=scale,error_percent_component_scale=100*err/scale,
                relative_error_percent=100*err/exact if abs(exact)>max(scale*1e-10,1e-14) else np.nan,
                source_sha256=source_hash))


def save(fig,name):
    (PAPER/'figures').mkdir(parents=True,exist_ok=True)
    for ext in ['png','pdf']:
        fig.savefig(PAPER/'figures'/f'{name}.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)


def field_plots(data,geometry):
    g=data[(data.geometry==geometry)&(data.NX==256)]
    fig,axs=plt.subplots(4,3,figsize=(7.2,6.8),gridspec_kw={'height_ratios':[1.8,1,1.8,1]})
    fig.subplots_adjust(left=.085,right=.99,top=.93,bottom=.22,wspace=.39,hspace=.70)
    handles=[];labels=[]
    for ip,profile in enumerate(['uniform','triangle']):
        for j,component in enumerate(['u','y','s']):
            q=g[(g.profile==profile)&(g.component==component)]
            if component=='u':q=q[(abs(q.y_m)<1e-12)&(abs(q.s_m)<1e-12)];x='u_m';factor=1e3;xlabel='$u$ (mm)'
            elif component=='y':q=q[(abs(q.u_m)<1e-12)&(abs(q.s_m)<1e-12)];x='y_m';factor=1e3;xlabel='$y$ (mm)'
            else:q=q[(abs(q.u_m)<1e-12)&(abs(q.y_m)<1e-12)&(q.s_m>=0)&(q.end_distance_m>0)];x='end_distance_m';factor=1e3;xlabel='Distance to end (mm)'
            ref=q.drop_duplicates('point_id').sort_values(x)
            ax,err=axs[2*ip,j],axs[2*ip+1,j]
            line,=ax.plot(ref[x]*factor,ref.reference_V_m,'k--',marker='.',ms=3,label='SACR / finite-source reference',zorder=7)
            if ip==0 and j==0:handles.append(line);labels.append(line.get_label())
            for model,marker,ls in [('Original 2D5','o','-'),('Corrected 2D5','^','-'),('PyORBIT','s','-.')]:
                d=q[q.model==model].sort_values(x)
                if d.empty:continue
                label='2D5: original = corrected ($\kappa=0$)' if geometry=='straight' and model=='Original 2D5' else model
                line,=ax.plot(d[x]*factor,d.native_V_m,color=COLOURS[model],marker=marker,ms=3,mfc='white',ls=ls,label=label)
                err.plot(d[x]*factor,d.error_V_m,color=COLOURS[model],marker=marker,ms=2.5,mfc='white',ls=ls)
                if ip==0 and j==0:handles.append(line);labels.append(label)
            for a in [ax,err]:
                a.axhline(0,color='.6',lw=.55);a.grid(alpha=.15)
                lo,hi=a.get_ylim();a.set_ylim(min(lo,0),max(hi,0))
                if component=='s':a.set_xscale('log')
            ax.set_title(f'{profile.capitalize()}: $E_{component}$',fontsize=8.5)
            ax.set_ylabel('Field (V/m)')
            err.set(xlabel=xlabel,ylabel='Native − ref. (V/m)')
    fig.suptitle(('Straight bunch' if geometry=='straight' else 'Circular bunch: $R=2$ m')+' | $L=5$ m, $Q=10$ pC, $a=20$ mm',fontsize=10)
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.005),ncol=2,frameon=False,fontsize=7.3)
    fig.text(.5,.105,'Fine mesh: 256 × 256 × 1024. Markers are direct probes; connecting segments guide the eye.',ha='center',fontsize=7)
    save(fig,f'{geometry}-fields')


def even_plot(data):
    rows=[];g=data[(data.geometry=='curved')&(data.component=='u')&(abs(data.y_m)<1e-12)&(abs(data.s_m)<1e-12)].copy()
    g['u_key']=g.u_m.round(12)
    fig,axs=plt.subplots(1,2,figsize=(7.2,2.25));fig.subplots_adjust(left=.09,right=.99,bottom=.45,top=.87,wspace=.28)
    for ax,profile in zip(axs,['uniform','triangle']):
        q=g[g.profile==profile]
        ref=q.drop_duplicates('point_id').set_index('u_key');xs=sorted(x for x in ref.index if x>=0)
        exact=np.array([(ref.loc[x,'reference_V_m']+ref.loc[-x,'reference_V_m'])/2 for x in xs])
        ax.plot(np.array(xs)*1e3,exact,'k--',marker='.',label='SACR',zorder=7)
        for (model,nx,ny,nz),d in q.groupby(['model','NX','NY','NZ'],sort=False):
            d=d.set_index('u_key');values=np.array([(d.loc[x,'native_V_m']+d.loc[-x,'native_V_m'])/2 for x in xs])
            for x,v,r in zip(xs,values,exact):rows.append(dict(profile=profile,model=model,NX=nx,NY=ny,NZ=nz,u_m=x,native_even_V_m=v,reference_even_V_m=r,relative_error_percent=100*(v-r)/r))
            ax.plot(np.array(xs)*1e3,values,color=COLOURS[model],marker='o' if nx==128 else 's',ms=3.5,
                mfc='white' if nx==128 else COLOURS[model],alpha=.55 if nx==128 else 1,label=f'{model}, {nx}²×{nz}')
        ax.axhline(0,color='.6',lw=.6);ax.grid(alpha=.15);lo,hi=ax.get_ylim();ax.set_ylim(min(lo,0),max(hi,0))
        ax.set(title=profile.capitalize(),xlabel='$|u|$ (mm)',ylabel='Even radial field (V/m)')
    h,l=axs[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',bbox_to_anchor=(.5,-.015),ncols=3,fontsize=6.5,frameon=False)
    save(fig,'curved-even-field');return pd.DataFrame(rows)


def charge_plot(selection,from_csv=False):
    rows=[];fig,axs=plt.subplots(1,3,figsize=(7.2,2.25));fig.subplots_adjust(left=.07,right=.99,bottom=.22,top=.88,wspace=.35)
    a=.02;x=np.linspace(-a,a,301);pdf=2*np.sqrt(np.maximum(0,a*a-x*x))/(np.pi*a*a)
    axs[0].plot(x*1e3,pdf/1e3,'k-',lw=1,label='Straight density')
    axs[0].plot(x*1e3,pdf*(1+x/2)/1e3,color='#009E73',ls='--',label='Curved charge marginal')
    axs[1].plot(x*1e3,pdf/1e3,'k-',lw=1)
    s=np.linspace(-2.5,2.5,501)
    axs[2].plot(s,np.full_like(s,2.),'k-',lw=1,label='Uniform')
    axs[2].plot(s,4*(1-abs(s)/2.5),'k--',lw=1,label='Triangular')
    for geometry,marker,colour in [('straight','o','#0072B2'),('curved','s','#009E73')]:
        for profile in ['uniform','triangle']:
            if from_csv:
                hist=read(OUT/'source-histograms.csv')
                hist=hist[(hist.geometry==geometry)&(hist.profile==profile)]
                for j,coordinate in enumerate(['u','y','s']):
                    d=hist[hist.coordinate==coordinate].sort_values('bin_centre_m')
                    if d.empty:continue
                    centres=d.bin_centre_m.to_numpy();values=d.probability_density_per_m.to_numpy()
                    if j<2:axs[j].plot(centres*1e3,values/1e3,color=colour,marker=marker,ms=2.3,mfc='white',ls='none')
                    else:axs[j].plot(centres,values*10,color=colour,marker=marker,ms=2,mfc='white',ls='none',alpha=.7)
                rows.extend(hist.to_dict('records'))
                continue
            case=next(r for r in selection if r['geometry']==geometry and r['model']=='Original 2D5' and r['profile']==profile)
            src=Path(case['source']);m=json.loads(src.with_suffix('.json').read_text())
            with np.load(src) as z:
                key='physical_material_m' if 'physical_material_m' in z else 'positions_m'
                positions=z[key]
                for j in [0,1,2]:
                    if j<2 and profile!='uniform':continue
                    edges=np.linspace(-a,a,33) if j<2 else np.linspace(-2.5,2.5,51)
                    count,_=np.histogram(positions[:,j],bins=edges);centres=(edges[1:]+edges[:-1])/2
                    values=count/len(positions)/np.diff(edges)
                    if j<2:axs[j].plot(centres*1e3,values/1e3,color=colour,marker=marker,ms=2.3,mfc='white',ls='none')
                    else:axs[j].plot(centres,values*10,color=colour,marker=marker,ms=2,mfc='white',ls='none',alpha=.7)
                    for c,v in zip(centres,values):rows.append(dict(geometry=geometry,profile=profile,coordinate=['u','y','s'][j],bin_centre_m=c,probability_density_per_m=v))
            del positions
    axs[0].set(xlabel='$u$ (mm)',ylabel='Marginal density (1/mm)',title='Radial source')
    axs[1].set(xlabel='$y$ (mm)',ylabel='Marginal density (1/mm)',title='Vertical source')
    axs[2].set(xlabel='$s$ (m)',ylabel='$\lambda$ (pC/m)',title='Longitudinal source')
    for ax in axs:ax.set_ylim(bottom=0);ax.grid(alpha=.15)
    axs[0].legend(fontsize=5.6,frameon=False);axs[2].legend(fontsize=6,frameon=False)
    save(fig,'charge-distribution');pd.DataFrame(rows).to_csv(OUT/'source-histograms.csv',index=False)


def tex_results(data,even):
    target=PAPER/'results';target.mkdir(exist_ok=True)
    for geometry in ['straight','curved']:
        if geometry=='straight':
            text=r'''\begin{figure}[!ht]
\centering\includegraphics[width=\linewidth]{figures/straight-fields.pdf}
\caption{Straight-bunch fields for uniform (upper rows) and triangular
(lower rows) profiles. Transverse cuts pass through the centre; the
longitudinal cut follows the positive axis and uses logarithmic distance
to the end. Lower panels show native minus finite-source reference.
The original and curvature-corrected slice models coincide at zero curvature.
All field axes retain zero.}\label{fig:straight-fields}\end{figure}
'''
            s=data[(data.geometry=='straight')&(data.NX==256)&(data.component=='s')&(abs(data.s_m-1.25)<1e-8)&(abs(data.u_m)<1e-12)&(abs(data.y_m)<1e-12)]
            triangle=s[s.profile=='triangle'];r=triangle.reference_V_m.iloc[0];v=triangle[triangle.model=='Original 2D5'].native_V_m.iloc[0]
            text+=f'The straight triangular bunch already exposes the longitudinal limitation: at $s=1.25$ m, the local models give ${v:.5f}$ V/m, versus ${r:.5f}$ V/m from the finite-source reference ({100*(1-v/r):.1f}\\% low). '
            text+='For the uniform bunch, the local derivative vanishes in the interior although the finite-source end field remains nonzero. Refining the numerical end stencil cannot supply that nonlocal tail.\n'
            text+='The symmetric particle rule removes artificial $x/y$ anisotropy at fixed particle count. Residual point-kernel/source sampling errors remain, especially in PyORBIT; the two meshes do not establish monotonic convergence.\n'
        else:
            text=r'''\begin{figure}[!ht]
\centering\includegraphics[width=\linewidth]{figures/curved-fields.pdf}
\caption{Circular-bunch fields for the same source at $R=2$ m, with the
same cuts and residual convention as Fig.~\ref{fig:straight-fields}.
The correction changes the transverse field; its longitudinal field still
uses the local $g=6.36$ closure.}\label{fig:curved-fields}\end{figure}
\FloatBarrier
\begin{figure}[H]
\centering\includegraphics[width=\linewidth]{figures/curved-even-field.pdf}
\caption{Weak radial curvature field, isolated as
$[E_u(+u)+E_u(-u)]/2$ at $y=s=0$. The two meshes are shown separately;
the zero line is retained.}\label{fig:even}\end{figure}
'''
            c=data[(data.geometry=='curved')&(data.component=='u')&(data.point_id=='centre')]
            text+=r'\begin{table}[!ht]\centering\small\caption{Centre radial field in V/m; positive is outward.}\begin{tabular}{llrr}\toprule Profile&Model&$128^2\!\times512$&$256^2\!\times1024$\\\midrule'+'\n'
            for profile in ['uniform','triangle']:
                for model in ['Original 2D5','Corrected 2D5','PyORBIT']:
                    q=c[(c.profile==profile)&(c.model==model)].sort_values('NX')
                    text+=f'{profile.capitalize()}&{model}&{q.native_V_m.iloc[0]:+.6f}&{q.native_V_m.iloc[-1]:+.6f}\\\\\n'
                ref=c[c.profile==profile].reference_V_m.iloc[0]
                text+=f'&SACR&{ref:+.6f}&{ref:+.6f}\\\\\n'
                if profile=='uniform':text+='\\addlinespace\n'
            text+='\\bottomrule\\end{tabular}\\label{tab:centre}\\end{table}\n'
            fixed=c[c.model=='Corrected 2D5'];maximum=abs(fixed.relative_error_percent).max()
            e=even[even.model=='Corrected 2D5'];maxeven=abs(e.relative_error_percent).max()
            bound=np.ceil(maximum*100)/100;even_bound=np.ceil(maxeven*100)/100
            text+=f'The corrected centre fields agree with SACR within {bound:.2f}\\% on both meshes. Across the sampled midplane pairs, the weak-field relative errors stay below {even_bound:.2f}\\%. '
            text+='The original model and matched PyORBIT retain the inward centre field. The correction repairs this transverse curvature contribution; the longitudinal discrepancy persists.\n'
        (target/f'{geometry}.tex').write_text(text)
    (target/'source.tex').write_text(r'''\begin{figure}[!ht]\centering
\includegraphics[width=\linewidth]{figures/charge-distribution.pdf}
\caption{Common physical source and charge marginals. Lines describe the
prescribed density; circles and squares are histograms of the shared
straight and curved particle sources. All native models use the same
source files within each geometry. The small curved radial asymmetry is
the volume factor $J$; it does not change the physical disk radius.}
\label{fig:source}\end{figure}
Each frozen-field native case uses $8\,388\,608$ equal-charge source particles. The
transverse numerical box is $48\times48$ mm. We compare
$128^2\times512$ and $256^2\times1024$ meshes with the same source;
these test two resolutions rather than establish asymptotic convergence.
''')
    (target/'abstract.tex').write_text('The transverse curvature correction recovers the outward centre field; the local longitudinal models retain finite-source errors already visible in the straight bunch.\n')


def main():
    global PAPER
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-csv',action='store_true',help='Replay figures from archived small CSVs without native/source files.')
    parser.add_argument('--paper-dir',type=Path,default=PAPER)
    args=parser.parse_args();PAPER=args.paper_dir.resolve()
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,'axes.titlesize':8,'axes.labelsize':7.5,
        'xtick.labelsize':7,'ytick.labelsize':7,'axes.spines.top':False,'axes.spines.right':False,
        'svg.fonttype':'none','lines.linewidth':1.0,'savefig.facecolor':'white'})
    if args.from_csv:
        data=read(OUT/'all-fields.csv');selection=json.loads((OUT/'selection.json').read_text())
    else:data,selection=collect()
    data.to_csv(OUT/'all-fields.csv',index=False,float_format='%.17g')
    (OUT/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    for g in ['straight','curved']:field_plots(data,g)
    even=even_plot(data);even.to_csv(OUT/'even-fields.csv',index=False,float_format='%.17g')
    charge_plot(selection,args.from_csv);tex_results(data,even)
    c=data[(data.component=='u')&(data.point_id=='centre')]
    c.to_csv(OUT/'centres.csv',index=False,float_format='%.17g')
    print(c[['geometry','profile','model','NX','NZ','native_V_m','reference_V_m','relative_error_percent']].to_string(index=False))
    result=dict(native_primary_cases=len(selection),field_samples=len(data),no_fitted_scale=True,
        source_charge_C=1e-11,nominal_transverse_rms_m=.01,physical_radius_m=.02,
        corrected_centre_max_relative_error_percent=float(abs(c[c.model=='Corrected 2D5'].relative_error_percent).max()),
        corrected_even_max_relative_error_percent=float(abs(even[even.model=='Corrected 2D5'].relative_error_percent).max()))
    (OUT/'status.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
