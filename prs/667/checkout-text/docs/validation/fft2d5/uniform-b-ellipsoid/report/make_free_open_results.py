#!/usr/bin/env python3
"""Offline free-space tables and publication figures from pinned CSV snapshots."""
from pathlib import Path
import hashlib
import json
import os
import re

os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-free-report-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-free-report-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/free-open'
FIGURES=ROOT/'figures'
GENERATED=ROOT/'generated'
COMPONENTS=['r','y','s']
TITLES=[r'Radial $E_u$',r'Vertical $E_y$',r'Tangential $E_s$']
COLORS=['#0072B2','#D55E00','#009E73','#CC79A7']
plt.rcParams.update({'font.family':'serif','mathtext.fontset':'stix','font.size':9,
    'axes.titlesize':10,'axes.labelsize':9,'legend.fontsize':8,
    'xtick.labelsize':8,'ytick.labelsize':8,'axes.linewidth':.65,
    'lines.linewidth':1.1,'pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'})


def read(path):
    return pd.read_csv(path,float_precision='round_trip')


def table(name,headers,rows,align):
    lines=[r'\begin{tabular}{'+align+'}',r'\toprule',' & '.join(headers)+r' \\',r'\midrule']
    lines += [' & '.join(map(str,row))+r' \\' for row in rows]
    lines += [r'\bottomrule',r'\end{tabular}']
    (GENERATED/(name+'.tex')).write_text('\n'.join(lines)+'\n')


def save(fig,name):
    fig.savefig(FIGURES/(name+'.pdf'),metadata={'Creator':'OPALX validation','CreationDate':None,'ModDate':None})
    fig.savefig(FIGURES/(name+'.png'),dpi=350)
    plt.close(fig)


def decorate(ax):
    ax.grid(alpha=.17,lw=.45)
    ax.tick_params(direction='in',top=True,right=True)
    ax.axhline(0,color='.6',lw=.55,zorder=0)


def verify():
    entries=json.loads((DATA/'snapshot-provenance.json').read_text())['sources']
    for item in entries:
        path=ROOT/item['snapshot']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError(f'Free-space evidence changed: {path}')
    selection=json.loads((DATA/'selection.json').read_text())
    fields=read(DATA/'analysis/field_comparison.csv')
    reference=read(DATA/'reference/fields_reference.csv')
    reference_check=json.loads((DATA/'reference/acceptance.json').read_text())
    assert reference_check['passed']
    assert reference_check['last_refinement_max_relative_pointwise_nonzero_component_change']<1e-9
    assert reference_check['independent_volume_max_relative_nonzero_component_error']<1e-7
    build=json.loads((DATA/'provenance/final-build.json').read_text())
    assert build['build_returncode']==0 and build['source_changes_during_build']==[]
    for name,key in [('sources-before-build.json','source_manifest_sha256'),('implementation.patch','patch_sha256')]:
        assert hashlib.sha256((DATA/'provenance'/name).read_bytes()).hexdigest()==build[key]
    source_hashes=json.loads((DATA/'provenance/sources-before-build.json').read_text())
    assert len(source_hashes)==build['source_file_count']
    for name,digest in build['new_files'].items():
        assert hashlib.sha256((DATA/'provenance/source'/name).read_bytes()).hexdigest()==digest
        assert source_hashes[name]==digest
    for path in (DATA/'provenance/source').rglob('*'):
        if path.is_file():
            name=str(path.relative_to(DATA/'provenance/source'))
            if name in source_hashes:
                assert hashlib.sha256(path.read_bytes()).hexdigest()==source_hashes[name]
    catalog=json.loads((DATA/'analysis/source_quadratures/catalog.json').read_text())
    for item in catalog:
        path=DATA/'analysis/source_quadratures'/item['compact_npz']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['compact_sha256']
        digest=hashlib.sha256()
        with np.load(path) as z:
            area=z['cross_integral_J_m2']; longitudinal=z['profile_integral_ds_m']
            density=float(z['density_normalization_C_m3'])
            for start in range(0,len(longitudinal),32):
                weights=(density*longitudinal[start:start+32,None]*area).ravel()
                digest.update(np.asarray(weights,dtype=np.float64).tobytes())
            probes=np.full(len(z['probe_uy_s_m']),float(z['probe_q_C']),dtype=np.float64)
            digest.update(probes.tobytes())
        assert digest.hexdigest()==item['full_q_attributes_sha256']
        assert item['full_q_reconstruction_passed']
    assert fields.original_target.dtype==bool
    manifests={name:json.loads((DATA/'runs'/name/'manifest.json').read_text()) for name in selection['cases']}
    for name,manifest in manifests.items():
        q=fields[fields.case==name]
        assert len(q)==51*3 and len(q[q.original_target])==43*3
        assert np.isfinite(q.E_fft_V_m).all()
        assert np.allclose(q.E_fft_V_m,q.E_full_V_m-q.E_probe_V_m,rtol=1e-13,atol=1e-12)
        assert np.allclose(q.E_error_V_m,q.E_fft_V_m-q.E_sacr_V_m,rtol=1e-13,atol=1e-12)
        assert np.allclose(q.error_over_component_scale,q.E_error_V_m/q.component_scale_V_m,rtol=1e-13,atol=1e-13)
        assert manifest['returncode']==0
        assert manifest['binary_sha256']==build['binary_sha256']
        companion=json.loads((DATA/'runs'/(name+'-probes')/'manifest.json').read_text())
        assert companion['returncode']==0 and companion['binary_sha256']==manifest['binary_sha256']
        for d in COMPONENTS:
            subset=q[q.component==d].set_index('point_id')
            exact=reference[reference.profile==manifest['profile']].set_index('point_id').loc[subset.index]
            expected=exact[f'E_{d}_V_m']*manifest['source']['source_charge_C']/1e-11
            assert np.allclose(subset.E_sacr_V_m,expected,rtol=1e-12,atol=1e-12)
            scale=max(abs(expected[subset.original_target]))
            assert np.allclose(subset.component_scale_V_m,scale,rtol=1e-13,atol=1e-12)
    acceptance=json.loads((DATA/'final-acceptance.json').read_text())
    assert acceptance['passed'] and acceptance['target_relative_accuracy']==.01
    assert not acceptance['coarse_levels_enter_fine_pass_status']
    assert acceptance['frozen_binary_sha256']==build['binary_sha256']
    assert set(acceptance['selected_fine_cases'])==set(selection['qualified_cases'])
    for name,digest in acceptance['evidence_sha256'].items():
        assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==digest
    for item in acceptance['field_metrics']:
        q=fields[(fields.case==item['case'])&fields.original_target&(fields.component==item['component'])]
        actual=q.relative_pointwise_error.abs().max()
        assert np.isclose(actual,item['max_abs_relative_pointwise_error'],rtol=1e-10,atol=1e-12)
        assert actual<=.01 and item['passed']
    for profile,names in selection['mesh_series'].items():
        mm=[manifests[name] for name in names]
        assert all(m['profile']==profile for m in mm)
        assert len({m['source']['sha256'] for m in mm})==1
        assert len({m['reference_path_sha256'] for m in mm})==1
        # Any executable change within a numerical scan must be described in
        # the deliberate selection, never mistaken for same-binary convergence.
        if len({m['binary_sha256'] for m in mm})!=1:
            assert selection.get('binary_change_within_mesh_series_explanation')
    print(f'Verified {len(entries)} free-space snapshots and recomputed physical references.')
    return selection,fields,manifests,reference_check


def field_figure(profile,selection,fields,manifests):
    cases=selection['mesh_series'][profile]
    fig,axes=plt.subplots(2,3,figsize=(6.65,3.65),layout='constrained',
                           gridspec_kw={'height_ratios':[1.2,1.]})
    handles=[Line2D([],[],color='k',ls='--',label='SACR exact Coulomb reference')]
    for k,name in enumerate(cases):
        color=COLORS[k%len(COLORS)]
        m=manifests[name]
        label=r'$%d\times%d\times%d$'%tuple(m['mesh'])
        handles.append(Line2D([],[],color=color,ls='none',marker='o',mfc='none',ms=3,label=label))
        for j,d in enumerate(COMPONENTS):
            q=fields[(fields.case==name)&fields.original_target&(fields.component==d)]
            axes[0,j].scatter(q.E_sacr_V_m,q.E_fft_V_m,s=11,facecolors='none',edgecolors=color,lw=.65)
            axes[1,j].scatter(q.s_m,100*q.error_over_component_scale,s=8,color=color,lw=.4)
    for j,d in enumerate(COMPONENTS):
        q=fields[fields.case.isin(cases)&fields.original_target&(fields.component==d)]
        lo=min(0.,q.E_sacr_V_m.min(),q.E_fft_V_m.min())
        hi=max(0.,q.E_sacr_V_m.max(),q.E_fft_V_m.max())
        pad=.05*max(hi-lo,1e-9)
        limits=(lo-pad,hi+pad)
        axes[0,j].plot(limits,limits,'k--',lw=.9,zorder=0)
        axes[0,j].set(xlim=limits,ylim=limits,title=TITLES[j],xlabel='SACR field (V/m)')
        axes[1,j].axhspan(-1,1,color='.92',zorder=-5)
        axes[1,j].axhline(1,color='.5',ls='--',lw=.5)
        axes[1,j].axhline(-1,color='.5',ls='--',lw=.5)
        axes[1,j].set(xlabel=r'Arclength $s$ (m)',xlim=(-2.6,2.6))
        for ax in axes[:,j]:
            decorate(ax)
    axes[0,0].set_ylabel('FFT2D5 field (V/m)')
    axes[1,0].set_ylabel(r'$(E_{\rm FFT2D5}-E_{\rm SACR})/E_{i,*}$ (%)')
    fig.legend(handles=handles,loc='outside lower center',ncols=2,frameon=False)
    fig.suptitle(f'{"Uniform" if profile=="uniform" else "Triangular"} physical density: 5 m, R=2 m, 10 pC',fontsize=10)
    save(fig,'free-open-'+profile)


def metrics(q):
    result=[]
    for d in COMPONENTS:
        z=q[q.component==d]
        result.append(100*z.relative_pointwise_error.abs().max())
    centre=q[(q.point_id=='centre')&(q.component=='r')].iloc[0]
    return result,centre


def mesh_figure(selection,fields,manifests):
    fig,axes=plt.subplots(1,4,figsize=(6.65,2.5),layout='constrained')
    for ip,(profile,names) in enumerate(selection['mesh_series'].items()):
        color=COLORS[ip]
        values=[]
        for name in names:
            q=fields[(fields.case==name)&fields.original_target]
            errors,centre=metrics(q)
            values.append([manifests[name]['mesh'][2],*errors,centre.E_fft_V_m,centre.E_sacr_V_m])
        values=np.asarray(values)
        for j in range(3):
            axes[j].plot(values[:,0],values[:,j+1],'-o',color=color,ms=3,label=profile.capitalize())
        axes[3].plot(values[:,0],values[:,4],'-o',color=color,ms=3,label=profile.capitalize())
        axes[3].axhline(values[-1,5],color='k',ls='--',lw=1.3,zorder=5)
    historical=read(ROOT/'data/frozen-r2/analysis/centre_radial.csv')
    before=historical[historical.case=='xy512-z512-cart'].iloc[0].E_fft_at_10pC_V_per_m
    axes[3].axhline(before,color='.45',ls=':',lw=1.)
    for j,ax in enumerate(axes):
        ax.set_xscale('log',base=2)
        ax.set_xlabel(r'$N_z$')
        decorate(ax)
        ax.set_ylim(bottom=min(0.,ax.get_ylim()[0]))
        if j<3:
            ax.axhline(1,color='.4',ls='--',lw=.8)
            ax.set_title(TITLES[j])
        else:
            ax.set_title(r'Centre $E_u(0)$')
    axes[0].set_ylabel('Max. pointwise error (%)')
    axes[3].set_ylabel(r'$E_u(0)$ (V/m)')
    handles=[Line2D([],[],color=COLORS[i],marker='o',ms=3,label=p.capitalize())
             for i,p in enumerate(selection['mesh_series'])]
    handles.append(Line2D([],[],color='k',ls='--',label='SACR centre field'))
    handles.append(Line2D([],[],color='.45',ls=':',label='Archived uniform slice field'))
    fig.legend(handles=handles,loc='outside lower center',ncols=2,frameon=False)
    save(fig,'free-open-mesh')


def results(selection,fields,manifests,reference_check):
    rows=[]
    for profile,names in selection['mesh_series'].items():
        for name in names:
            q=fields[(fields.case==name)&fields.original_target]
            errors,centre=metrics(q)
            mesh=r'$%d\times%d\times%d$'%tuple(manifests[name]['mesh'])
            rows.append([profile.capitalize(),mesh,*[f'{value:.3f}' for value in errors],
                         f'{100*abs(centre.relative_pointwise_error):.3f}'])
    table('free-open-errors',['Profile','Mesh',r'$E_u$ [\%]',r'$E_y$ [\%]',r'$E_s$ [\%]',r'Centre $E_u$ [\%]'],rows,'llrrrr')
    extra=[]
    for profile,name in selection['primary'].items():
        q=fields[(fields.case==name)&~fields.original_target]
        for d in ['r','s']:
            z=q[q.component==d]
            extra.append([profile.capitalize(),r'$E_'+('u' if d=='r' else d)+'$',
                          f'{100*z.error_over_component_scale.abs().max():.3f}',
                          f'{100*z.relative_pointwise_error.abs().max():.3f}'])
    table('free-open-extra',['Profile','Component','Fixed-scale error [\%]','Nonzero-relative error [\%]'],extra,'llrr')
    kernel=read(DATA/'design/kernel_checks.csv')
    assert kernel.relative_error.abs().max()<2e-6
    text=r'''\clearpage
\subsection{Native field comparison and convergence}
One native $10^{-17}$ s step with zero external field supplies each frozen
snapshot. A matched probe-only companion removes diagnostic charge; SACR is
scaled to the actual bulk charge. This is a field-operator test, not a tracking
test. The original 43 targets retain the historical comparison set, with
end distances of at least 5 mm. Here the
fixed component scales are $E_{i,*}=\max_{43}|E_i^{\rm SACR}|$ for each profile;
8 added cusp/end targets are reported separately and do not change these scales.

The table gives maximum pointwise relative errors over nonzero reference
components at the original targets. Symmetry zeros remain in the signed
fixed-scale residuals; the weak centre radial force has its own relative check.
\tabfile{free-open-errors}

\reportfigure{free-open-uniform}{Uniform physical-density tube. Black dashed:
SACR exact Coulomb identity. Lower panels show signed differences from SACR;
the gray band marks $\pm1\%$ of each fixed original-target component scale.
All zero fields remain visible.}{fig:free-open-uniform}
\reportfigure{free-open-triangle}{Same comparison for triangular physical
density, with the identical production operator and no fitted parameter.}{fig:free-open-triangle}
\input{generated/free-open-controls-text.tex}

\clearpage
\subsection{Weak curvature response, diagnostics and limits}
\reportfigure{free-open-mesh}{Matched-source longitudinal mesh refinement, with source and reference
path held fixed within each profile. Left: maximum nonzero-target physical
errors. Right: the weak signed centre radial field; dashed lines are the SACR
values, 0.055092 and 0.091839 V/m. Gray dotted: the earlier uniform slice result from its separate study,
not a matched mesh datum. Errors use their own reference components, not the
larger transverse scale.}{fig:free-open-mesh}
The additional targets include 1 mm and 0.1 mm end distances and the triangular
cusp neighbourhood. They do not alter the original acceptance scales.
\tabfile{free-open-extra}

The implementation accepts straight references or horizontal constant-radius
arcs shorter than a full turn, $\max|\kappa u|\le0.01$ across the numerical
mesh and halo, and one MPI rank. General varying-curvature paths are rejected.
Curved OPEN uses an electrostatic approximation with an explicit
$\beta\le0.1$ guard; the present validation uses $\beta=0.001$.
The operator retains the full bend angle but does not include radiation or
retarded curved-beam electrodynamics. Straight references retain their Lorentz
stretch and field transformation. No percent-level tracking claim follows.
'''
    (GENERATED/'free-open-results.tex').write_text(text)


def pipe_control():
    base=DATA/'pipe-control/analysis'
    validation=json.loads((base/'validation.json').read_text())
    build=json.loads((DATA/'provenance/final-build.json').read_text())
    assert validation['passed'] and validation['binary_sha256']==build['binary_sha256']
    fields=read(base/'fields.csv')
    summary=read(base/'summary.csv')
    physical=validation['analytic']
    a=physical['beam_radius_m']; b=physical['pipe_radius_m']
    gamma=1+physical['kinetic_energy_GeV']/physical['rest_energy_GeV']
    base_field=4*physical['charge_C']/physical['length_m']**2/(4*np.pi*8.8541878128e-12*gamma**2)
    for _,row in summary.iterrows():
        q=fields[(fields.case==row.case)&fields.acceptance]
        assert len(q)==144
        r=q.r_m.to_numpy()
        g=1+2*np.log(b/a)-r*r/a**2
        expected=np.sign(q.s_m.to_numpy())*base_field*g
        assert np.allclose(q.analytic_Es_V_m,expected,rtol=2e-8,atol=1e-7)
        for kind,column in [('axis','max_axis_relative_error_percent'),('radial','max_radial_relative_error_percent')]:
            z=q[q.kind==kind]
            error=100*np.max(np.abs(z.Es_V_m/z.analytic_Es_V_m-1))
            assert np.isclose(error,row[column],rtol=1e-10,atol=1e-9)
    assert validation['wall']['passed']
    assert validation['wall']['max_wall_absolute_field_V_m']<1e-4
    selected=['opalx-pipe256','pyorbit-slice-r1','pyorbit-rb-r1']
    names=['OPALX CIRCULAR\_UNIFORM','PyORBIT slices','PyORBIT Baartman']
    rows=[]
    for name,label in zip(selected,names):
        r=summary.set_index('case').loc[name]
        rows.append([label,r'$%d\times%d\times%d$'%(r.nx,r.ny,r.nz),
                     f'{r.max_axis_relative_error_percent:.4f}',f'{r.max_radial_relative_error_percent:.4f}'])
    table('free-open-pipe-control',['Code/model','Mesh',r'On-axis $E_s$ [\%]',r'Off-axis $E_s$ [\%]'],rows,'llrr')
    text=r'''\subsection{Repeated straight conducting-pipe control}
The same final OPALX executable reruns the independent straight benchmark in
\cref{sec:triangle-pipe}; this does not replace the free-space SACR comparison.
The fixed $1\le|s|\le4$ m window contains 62 axis and 82 beam-radial targets.
Maximum pointwise relative errors are
\tabfile{free-open-pipe-control}
The OPALX source has 8,388,608 particles. Repeated PyORBIT one-/two-rank
fields agree within $7\times10^{-9}\%$ of the local analytic field. The
maximum OPALX--PyORBIT difference is 0.447\% (slices) or 0.167\%
(Baartman). A separate native annulus/wall control has 0.00352\% maximum
nonzero-field error and exactly zero wall field. This confirms the retained
straight local pipe model; it supplies no curved free-space validation.
'''
    (GENERATED/'free-open-pipe-control-text.tex').write_text(text)


def software_checks(selection):
    gates=json.loads((DATA/'checks/tests.json').read_text())
    build=json.loads((DATA/'provenance/final-build.json').read_text())
    assert gates['binary_sha256']==build['binary_sha256'] and gates['ctest_pass']
    log=(DATA/'checks/ctest-unit-output.log').read_text()
    passed=sum(map(int,re.findall(r'\[  PASSED  \]\s+(\d+) tests?\.',log)))
    skipped=sum(map(int,re.findall(r'\[  SKIPPED \]\s+(\d+) tests?, listed below:',log)))
    assert passed==gates['unit_tests_passed']
    assert skipped==gates['unit_tests_skipped']
    assert log.count('Test Passed.')==gates['ctest_executables']
    assert 'Test Failed.' not in log
    mpi=(DATA/'checks/unit-mpi-guard-final.log').read_text()
    assert sum(map(int,re.findall(r'\[  PASSED  \]\s+(\d+) tests?\.',mpi)))==gates['mpi_guard_ranks']==2
    fields=read(DATA/'analysis/field_comparison.csv')
    for name in selection['cases']:
        audit=json.loads((DATA/'audit-weighted'/(name+'.json')).read_text())
        assert audit['initialization_valid'] and audit['comparison_interpretable']
        for role in ['full','companion']:
            item=audit[role]
            assert item['binary_sha256']==build['binary_sha256']
            assert item['q_preserved_by_id'] and item['m_preserved_by_id']
            assert item['initialization_valid']
        independent=read(DATA/'audit-weighted'/(name+'-fields.csv')).set_index('point_id')
        primary=fields[fields.case==name].pivot(index='point_id',columns='component',values='E_fft_V_m')
        for d in COMPONENTS:
            assert np.allclose(primary[d],independent.loc[primary.index,f'native_E_{d}_V_m'],rtol=1e-11,atol=1e-9)
    negative=json.loads((DATA/'audit-weighted/triangle-weighted-smoke-final.json').read_text())
    assert not negative['initialization_valid'] and not negative['comparison_interpretable']
    text=rf'''\subsection{{Nonlocal OPEN verification}}
Six selected CTest executables pass {passed} unit tests; {skipped} MPI-only test
is skipped in the one-rank invocation and passes separately on two ranks.
FFT2D5 therefore still rejects unsupported distributed execution. Backend
checks include a finite source-cell self integral and independent ellipsoid
fields at $\gamma=1,2$; geometry and frame checks are separate from native
physical-field convergence. No existing physical tolerance was relaxed.

Weighted checkpoint sources require preserving each particle's charge and
mass. An auxiliary fix prevents the emission stage from overwriting these
attributes when no emitter is active. Independent sorted-ID audits verify
q/m, total weighted charge, source geometry and frozen motion for both final
profiles. The pre-fix smoke run changed the profile and is explicitly invalid;
it supplies no field-accuracy evidence. The existing header charge diagnostic
can be wrong for nonuniform weights; source normalization uses the actual
sum of particle weights and never that header value.
'''
    (GENERATED/'free-open-verification.tex').write_text(text)


def numerical_controls(selection,fields,manifests):
    rows=[]
    for control in selection.get('controls',[]):
        a,b=control['case_a'],control['case_b']
        ma,mb=manifests[a],manifests[b]
        assert ma['profile']==mb['profile']
        assert ma['binary_sha256']==mb['binary_sha256']
        if 'source' in b:
            assert ma['mesh']==mb['mesh']
            assert ma['reference_path_sha256']==mb['reference_path_sha256']
        elif 'mesh' in b:
            assert ma['source']['sha256']==mb['source']['sha256']
            assert ma['reference_path_sha256']==mb['reference_path_sha256']
        elif 'path' in b:
            assert ma['source']['sha256']==mb['source']['sha256']
            assert ma['mesh']==mb['mesh']
        else:
            raise ValueError(f'Unclassified numerical control {b}')
        values=[]
        for d in COMPONENTS:
            qa=fields[(fields.case==a)&fields.original_target&(fields.component==d)].set_index('point_id')
            qb=fields[(fields.case==b)&fields.original_target&(fields.component==d)].set_index('point_id').loc[qa.index]
            assert len(qa)==len(qb)==43
            assert np.allclose(qa.E_sacr_V_m,qb.E_sacr_V_m,rtol=1e-12,atol=1e-12)
            mask=qa.relative_pointwise_error.notna()
            change=100*np.max(np.abs((qb.E_fft_V_m[mask]-qa.E_fft_V_m[mask])/qa.E_sacr_V_m[mask]))
            values.append(change)
        def format_value(v):
            if v==0:
                return '0'
            if v<1e-4:
                mantissa,exponent=f'{v:.2e}'.split('e')
                return rf'${mantissa}\times10^{{{int(exponent)}}}$'
            return f'{v:.5f}'
        rows.append([control['label'],*[format_value(v) for v in values]])
    if not rows:
        (GENERATED/'free-open-controls-text.tex').write_text('')
        return
    table('free-open-controls',['Separate control',r'$\Delta E_u$ [\%]',r'$\Delta E_y$ [\%]',r'$\Delta E_s$ [\%]'],rows,'lrrr')
    text=r'''\subsection{Independent source, transverse-mesh and path controls}
The source refinement keeps the field mesh fixed; the transverse field-mesh
refinement then holds that refined source fixed. The path control changes
only reference sampling. The table gives maximum changes divided by each
nonzero local SACR reference field over the original 43 targets.
\tabfile{free-open-controls}
These numerical changes are separate from the absolute physical errors above.
All seven fine and control cases have maximum nonzero-target physical field
error below 0.565\% over the original 43 points.
'''
    (GENERATED/'free-open-controls-text.tex').write_text(text)


def main():
    selection,fields,manifests,checks=verify()
    for profile in selection['mesh_series']:
        field_figure(profile,selection,fields,manifests)
    mesh_figure(selection,fields,manifests)
    results(selection,fields,manifests,checks)
    pipe_control()
    software_checks(selection)
    numerical_controls(selection,fields,manifests)
    print('Rebuilt free-space figures and physical-error tables from local snapshots.')


if __name__=='__main__':
    main()
