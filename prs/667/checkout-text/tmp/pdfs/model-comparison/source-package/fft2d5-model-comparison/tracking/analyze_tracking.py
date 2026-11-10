#!/usr/bin/env python3
"""Compare native ten-step moments with shared-source and ZeroSC controls."""
from pathlib import Path
import argparse,json,hashlib,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
PAPER_DEFAULT=Path('/Users/adelmann/git/opalx/docs/validation/fft2d5/model-comparison-paper')
COLORS={'OPALX 2D5':'#0072B2','PyORBIT':'#D55E00'}


def read(p):return pd.read_csv(p,float_precision='round_trip')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def collect():
    rows=[];selection=[]
    for folder,code in [('opalx','OPALX 2D5'),('pyorbit','PyORBIT')]:
        for path in sorted((ROOT/folder/'runs').glob('*/manifest.json')):
            m=json.loads(path.read_text());g=m['geometry']
            if g not in ['straight','bend']:continue
            if folder=='opalx':
                integrity=path.parent/'integrity.json'
                if not integrity.exists() or not json.loads(integrity.read_text())['passed']:continue
                assert m['returncode']==0
                zero=m['zero_sc']
            else:
                if not m.get('passed'):continue
                zero=not m['space_charge_enabled']
            assert m['steps']==10
            source=m['source'];assert sha(source['npz'])==source['npz_sha256']
            frame=read(path.parent/'moments.csv').sort_values('step')
            assert frame.step.to_list()==list(range(11))
            assert np.allclose(frame.time_s,np.arange(11)/(10*.001*299792458.),rtol=1e-12,atol=1e-20)
            assert (frame.particles==source['source_particles']).all()
            for coord,cart in zip(['u','y','s'],['x','y','z']):
                prefix='global_'+cart if g=='straight' else 'frenet_'+coord
                sk='sigma_'+prefix+'_m';mk='mean_'+prefix+'_m'
                if sk not in frame and g=='bend':
                    sk='sigma_'+coord+'_m';mk='mean_'+coord+'_m'
                assert np.isfinite(frame[[sk,mk]].to_numpy()).all(),(path,sk,mk)
                for _,r in frame.iterrows():
                    mean=float(r[mk])
                    phase=float(r.get('reference_phase_rad',.1*r.step/2 if g=='bend' else 0.))
                    if g=='bend' and coord=='s':
                        if 'mean_absolute_s_m' in r:
                            mean=float(r['mean_absolute_s_m'])
                        else:
                            # OPALX exports s about its actual centroid
                            # reference; recover absolute circular arclength.
                            assert code=='OPALX 2D5'
                            mean+=2*phase
                    rows.append(dict(geometry=g,code=code,zero_sc=zero,case=path.parent.name,
                        step=int(r.step),time_s=r.time_s,advance_m=.1*r.step,component=coord,
                        sigma_m=r[sk],mean_m=mean,reference_phase_rad=phase,
                        source_sha256=source['npz_sha256']))
            selection.append(dict(geometry=g,code=code,zero_sc=zero,manifest=str(path),
                manifest_sha256=sha(path),source_sha256=source['npz_sha256'],
                steps=10,source_particles=source['source_particles']))
    d=pd.DataFrame(rows)
    assert (d.groupby('geometry').source_sha256.nunique()==1).all()
    assert not d.duplicated(['geometry','code','zero_sc','step','component']).any()
    return d,selection


def compare(d):
    pairs=[]
    for (g,c),q in d.groupby(['geometry','component']):
        a=q[(q.code=='OPALX 2D5')&~q.zero_sc].set_index('step')
        b=q[(q.code=='PyORBIT')&~q.zero_sc].set_index('step')
        za=q[(q.code=='OPALX 2D5')&q.zero_sc].set_index('step')
        zb=q[(q.code=='PyORBIT')&q.zero_sc].set_index('step')
        if any(len(x)!=11 for x in [a,b,za,zb]):continue
        for step in range(11):
            ga=a.loc[step,'sigma_m']-za.loc[step,'sigma_m'];gb=b.loc[step,'sigma_m']-zb.loc[step,'sigma_m']
            pairs.append(dict(geometry=g,component=c,step=step,advance_m=step*.1,
                opalx_sigma_m=a.loc[step,'sigma_m'],pyorbit_sigma_m=b.loc[step,'sigma_m'],
                total_rms_difference_m=b.loc[step,'sigma_m']-a.loc[step,'sigma_m'],
                total_rms_relative_difference_percent=100*(b.loc[step,'sigma_m']/a.loc[step,'sigma_m']-1),
                opalx_growth_m=ga,pyorbit_growth_m=gb,growth_difference_m=gb-ga,
                growth_relative_difference_percent=100*(gb/ga-1) if abs(ga)>1e-12 else np.nan,
                zero_sigma_difference_m=zb.loc[step,'sigma_m']-za.loc[step,'sigma_m'],
                opalx_mean_m=a.loc[step,'mean_m'],pyorbit_mean_m=b.loc[step,'mean_m'],
                opalx_centroid_response_m=a.loc[step,'mean_m']-za.loc[step,'mean_m'],
                pyorbit_centroid_response_m=b.loc[step,'mean_m']-zb.loc[step,'mean_m']))
    return pd.DataFrame(pairs)


def result_tex(pairs,paper):
    final=pairs[pairs.step==10].set_index(['geometry','component'])
    geometries=[g for g in ['straight','bend'] if g in final.index.get_level_values(0)]
    tex=r'''\section{First native tracking comparison}
The first tracking case uses the uniform longitudinal profile and the same
physical disk and length, sampled by $1\,048\,576$ equal-charge particles.
Each geometry shares identical initial particle coordinates and momenta
between the codes. Cold protons at $\beta=10^{-3}$ advance a nominal 1 m in
exactly ten midpoint steps, $\Delta t=\SI{0.333564}{\micro s}$.
A ZeroSC companion keeps the same nominal charge and particle mass while
disabling self-fields. We compare both total centred RMS sizes and
$\Delta\sigma_i=\sigma_i(10\,\mathrm{pC})-\sigma_i(\mathrm{ZeroSC})$.

OPALX uses the original slice baseline, not the transverse curvature
extension. PyORBIT uses its native drift and sector-bend body maps with
native transverse slices and local longitudinal kicks. Both retain the
physical $g=6.36$; PyORBIT's per-turn longitudinal normalization is scaled
by step length divided by numerical period. The grid is
$128^2\times512$ in a 48 mm transverse box. The straight numerical period
is 12 m; the bend uses the common reference-polyline circumference.
The transverse PyORBIT kick retains its native approximation of omitting
transverse work from its energy coordinate.

\begin{figure}[!ht]\centering
\includegraphics[width=\linewidth]{figures/tracking-comparison.pdf}
\caption{Exactly ten native tracking steps per case, with a same-source
ZeroSC companion. Upper rows show centred RMS sizes; lower rows isolate
the self-field response. Straight $u=x$; bend $u,y,s$ are local circular
coordinates, rather than whole-bunch Cartesian projections. The horizontal
axis is nominal central-particle flight. All size and response axes
include zero.}\label{fig:tracking-comparison}\end{figure}
'''
    a=final.loc[('straight','u')];s=final.loc[('straight','s')]
    maxr=abs(pairs[pairs.geometry=='straight'].total_rms_relative_difference_percent).max()
    tex+=f'The straight ZeroSC bunch translates without changing shape. After ten charged steps, $\\sigma_x=\\sigma_y$ is {a.opalx_sigma_m*1e3:.5f} mm in OPALX and {a.pyorbit_sigma_m*1e3:.5f} mm in PyORBIT. '
    tex+=f'The maximum total-RMS difference over the straight trajectory is {maxr:.4f}\\%. The endpoint transverse and longitudinal growth increments differ by {abs(a.growth_relative_difference_percent):.2f}\\% and {abs(s.growth_relative_difference_percent):.2f}\\%, respectively. '
    tex+='Relative errors in the smallest early-step increments are larger; the endpoint growth figures do not describe every step.\n'
    if 'bend' in geometries:
        tex+=r'''
\begin{samepage}
The bend continuation uses a uniform Cartesian magnetic field,
$B_y=\SI{1.564870}{mT}$, and $R=2$ m. OPALX's ZeroSC particles satisfy
the independent discrete Boris orbit at all ten endpoints. Native PyORBIT
bend-map controls check the expected focusing and longitudinal signs.
The native maps have different transport approximations: ten-step Boris
has a finite phase lag, while PyORBIT uses a paraxial sector-bend model.
Against the exact continuous uniform-field ZeroSC orbit, PyORBIT's final
Cartesian position components differ by up to 95.1 micrometres under the stated
coordinate embedding. Thus close RMS agreement alone does not certify
individual trajectories or centroids.
OPALX also projects onto a polyline; its maximum circle--chord sagitta is
1.563 micrometres, whereas PyORBIT retains native Frenet coordinates.
This is a geometric bound, not a force-error bound. Longitudinal centroid
comparisons use absolute circular arclength from the same initial phase.
'''
        b=final.loc['bend'];maxb=abs(pairs[pairs.geometry=='bend'].total_rms_relative_difference_percent).max()
        tex+=f'The maximum total-RMS difference over the bent trajectory is {maxb:.4f}\\%. '
        tex+='\n\\par\\end{samepage}\n'
        tex+=r'''\begin{table}[H]\centering\small
\caption{Bend endpoint after ten charged steps. RMS sizes and self-field
changes are in mm and micrometres, respectively.}\begin{tabular}{lrrrr}\toprule
 &\multicolumn{2}{c}{RMS (mm)}&\multicolumn{2}{c}{$\Delta\sigma$ (\si{\micro m})}\\
 Component&OPALX&PyORBIT&OPALX&PyORBIT\\\midrule
'''
        for c in ['u','y','s']:
            r=b.loc[c];tex+=f'${c}$&{r.opalx_sigma_m*1e3:.5f}&{r.pyorbit_sigma_m*1e3:.5f}&{r.opalx_growth_m*1e6:.3f}&{r.pyorbit_growth_m*1e6:.3f}\\\\\n'
        tex+=r'\bottomrule\end{tabular}\label{tab:tracking-bend}\end{table}'+'\n'
        tex+='\\begin{samepage}\n'
        largest=abs(b.growth_relative_difference_percent).max()
        du=abs(b.loc['u','pyorbit_centroid_response_m']-b.loc['u','opalx_centroid_response_m'])*1e6
        ds=abs(b.loc['s','pyorbit_centroid_response_m']-b.loc['s','opalx_centroid_response_m'])*1e6
        tex+=f'The bend endpoint growth differences remain below {np.ceil(largest*100)/100:.2f}\\% in all three directions. '
        tex+=f'The charged-minus-ZeroSC radial and longitudinal centroid responses differ by {du:.2f} and {ds:.2f} micrometres, respectively. '
        tex+='These weak centroid responses do not agree at the 1\\% level. '
        tex+='The charged-minus-ZeroSC comparison separates self-field changes from the native transport mismatch. '
    tex+='These ten-step runs screen code-to-code tracking consistency for the original slice models. They establish neither step convergence nor accuracy against full finite-source curved dynamics, and do not validate tracking with the curvature extension.\n'
    if 'bend' in geometries:tex+='\\par\\end{samepage}\n'
    (paper/'results/tracking.tex').write_text(tex)
    abstract='Ten-step native tracking comparisons test the original slice models with matched-source ZeroSC controls.\n'
    (paper/'results/tracking-abstract.tex').write_text(abstract)


def plots(d,pairs,paper):
    geometries=[g for g in ['straight','bend'] if g in pairs.geometry.unique()]
    fig,axs=plt.subplots(2*len(geometries),3,figsize=(7.2,3.3*len(geometries)+.5),squeeze=False)
    fig.subplots_adjust(left=.09,right=.99,top=.93,bottom=.12,wspace=.38,hspace=.68)
    for i,g in enumerate(geometries):
        for j,c in enumerate(['u','y','s']):
            ax,inc=axs[2*i,j],axs[2*i+1,j]
            q=d[(d.geometry==g)&(d.component==c)]
            scale=1. if c=='s' else 1e3;unit='m' if c=='s' else 'mm'
            for code in COLORS:
                for zero in [True,False]:
                    p=q[(q.code==code)&(q.zero_sc==zero)].sort_values('step')
                    ax.plot(p.advance_m,p.sigma_m*scale,color=COLORS[code],ls='--' if zero else '-',
                        marker=None if zero else ('o' if code=='OPALX 2D5' else 's'),
                        ms=2.5,mfc='white',alpha=.6 if zero else 1,
                        label=code+(' ZeroSC' if zero else ' 10 pC'))
                p=pairs[(pairs.geometry==g)&(pairs.component==c)].sort_values('step')
                inc.plot(p.advance_m,p['opalx_growth_m' if code=='OPALX 2D5' else 'pyorbit_growth_m']*1e6,
                    color=COLORS[code],marker='o' if code=='OPALX 2D5' else 's',ms=2.5,mfc='white')
            ax.set(title=('Straight' if g=='straight' else '$R=2$ m bend')+f': $\\sigma_{c}$',ylabel=f'RMS ({unit})')
            inc.set(xlabel='Nominal reference flight (m)',ylabel='10 pC − ZeroSC (µm)')
            for a in [ax,inc]:
                a.axhline(0,color='.6',lw=.55);a.grid(alpha=.14)
                lo,hi=a.get_ylim();a.set_ylim(min(0,lo),max(0,hi));a.set_xlim(0,1)
    h,l=axs[0,0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',bbox_to_anchor=(.5,.005),ncol=2,frameon=False,fontsize=7)
    fig.suptitle('Native tracking: ten steps, 1 m flight, $L=5$ m, $Q=10$ pC',fontsize=10)
    for ext in ['png','pdf']:fig.savefig(paper/'figures'/f'tracking-comparison.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--from-csv',action='store_true');p.add_argument('--paper-dir',type=Path,default=PAPER_DEFAULT)
    a=p.parse_args();out=ROOT/'analysis';out.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,'axes.titlesize':8,'axes.labelsize':7.5,
       'xtick.labelsize':7,'ytick.labelsize':7,'axes.spines.top':False,'axes.spines.right':False,'lines.linewidth':1.,'savefig.facecolor':'white'})
    if a.from_csv:d=read(out/'moments.csv');selection=json.loads((out/'selection.json').read_text())
    else:d,selection=collect()
    pairs=compare(d);assert len(pairs)>0
    d.to_csv(out/'moments.csv',index=False,float_format='%.17g');pairs.to_csv(out/'comparison.csv',index=False,float_format='%.17g')
    (out/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    final=pairs[pairs.step==10];final.to_csv(out/'final-comparison.csv',index=False,float_format='%.17g')
    plots(d,pairs,a.paper_dir.resolve())
    result_tex(pairs,a.paper_dir.resolve())
    print(final.to_string(index=False))

if __name__=='__main__':main()
