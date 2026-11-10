#!/usr/bin/env python3
"""Reproduce independent curved-tube validation figures/tables from small CSVs."""
from pathlib import Path
import argparse,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
DEFAULT_PAPER=Path('/Users/adelmann/git/opalx/docs/validation/fft2d5/model-comparison-paper')
COLORS={'uniform':'#0072B2','triangle':'#D55E00'}


def read(path):return pd.read_csv(path,float_precision='round_trip')


def save(fig,paper,name):
    for ext in ['png','pdf']:
        fig.savefig(paper/'figures'/f'{name}.{ext}',dpi=300,bbox_inches='tight')
    plt.close(fig)


def volume_plot(paper):
    d=read(ROOT/'reference-extension/volume_checks.csv')
    ids=read(ROOT/'reference-extension/volume_points.csv').point_id.tolist()
    fig,axs=plt.subplots(2,3,figsize=(7.2,4.0))
    fig.subplots_adjust(left=.09,right=.99,top=.90,bottom=.20,wspace=.38,hspace=.56)
    for j,c in enumerate(['u','y','s']):
        ax,err=axs[:,j]
        q=d[d.component==c]
        lo=min(0.,q.sacr_V_m.min(),q.direct_V_m.min());hi=max(0.,q.sacr_V_m.max(),q.direct_V_m.max())
        pad=max((hi-lo)*.07,.01)
        ax.plot([lo-pad,hi+pad],[lo-pad,hi+pad],'k--',lw=.8,label='Identity')
        for profile,marker in [('uniform','o'),('triangle','s')]:
            p=q[q.profile==profile].set_index('point_id').loc[ids]
            ax.plot(p.sacr_V_m,p.direct_V_m,marker,ms=3.5,mfc='none',mec=COLORS[profile],label=profile.capitalize())
            x=np.arange(1,len(p)+1)
            err.errorbar(x+(-.08 if profile=='uniform' else .08),p.difference_V_m*1e12,
                yerr=abs(p.refinement_delta_V_m)*1e12,fmt=marker,ms=3,mfc='none',
                color=COLORS[profile],elinewidth=.7,capsize=1.5,label=profile.capitalize())
        ax.set(title=f'$E_{c}$',xlabel='SACR (V/m)',ylabel='Volume integral (V/m)')
        ax.set_xlim(lo-pad,hi+pad);ax.set_ylim(lo-pad,hi+pad)
        err.set(xlabel='Probe index',ylabel='Volume − SACR (pV/m)',xticks=[1,2,3,4,5,6,7,8])
        for a in [ax,err]:
            a.axhline(0,color='.6',lw=.55);a.grid(alpha=.14)
            low,high=a.get_ylim();a.set_ylim(min(0.,low),max(0.,high))
    h,l=axs[0,0].get_legend_handles_labels()
    fig.legend(h,l,loc='lower center',bbox_to_anchor=(.5,.035),ncol=3,frameon=False,fontsize=7)
    fig.suptitle('Independent Cartesian volume integration: $R=2$ m',fontsize=10)
    save(fig,paper,'sacr-volume-validation')


def radius_plot(paper):
    d=read(ROOT/'reference-extension/radius-sweep/radius-error-summary.csv')
    fig,axs=plt.subplots(1,3,figsize=(7.2,2.4))
    fig.subplots_adjust(left=.085,right=.99,top=.84,bottom=.29,wspace=.40)
    for j,c in enumerate(['u','y','s']):
        ax=axs[j]
        for profile,marker in [('uniform','o'),('triangle','s')]:
            q=d[(d.component==c)&(d.profile==profile)].copy()
            q['kappa']=np.where(np.isfinite(q.R_m),1/q.R_m,0.)
            q=q.sort_values('kappa')
            ax.plot(q.kappa,100*q.max_abs_difference_over_fixed_scale,color=COLORS[profile],marker=marker,
                    mfc='white',ms=3,label=profile.capitalize())
        ax.set(title=f'$E_{c}$',xlabel='$1/R$ (m$^{-1}$)',ylabel='Difference from straight (%)',xlim=(-.01,.52))
        ax.axhline(0,color='.6',lw=.6);ax.grid(alpha=.15)
        ax.set_ylim(bottom=0)
    h,l=axs[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',bbox_to_anchor=(.5,.005),ncol=2,frameon=False,fontsize=7)
    fig.suptitle('Fixed source and material targets; straight cylinder at $1/R=0$',fontsize=9.5)
    save(fig,paper,'sacr-radius-convergence')


def result_tex(paper):
    v=json.loads((ROOT/'reference-extension/volume_acceptance.json').read_text())
    r=json.loads((ROOT/'reference-extension/radius-sweep/acceptance.json').read_text())
    inf=max(x['curved_producer_inf_vs_independent_straight_max_V_m'] for x in r['endpoint_checks'] if 'curved_producer_inf_vs_independent_straight_max_V_m' in x)
    tex=r'''\section{Independent validation of SACR}
The reference is checked directly for the current constant-radius tube.
A separate implementation integrates the original Cartesian Coulomb vector
with the physical volume factor $J$, without surface formulas, softening or
charge renormalization. Eight targets per profile include mixed transverse
bulk points, off-axis points 10 and 5 mm from an end, and an axis point
0.1 mm from an end. Five targets per profile have all three field components
nonzero. Angular and radial refinements are independent of the SACR rule.
\begin{figure}[!ht]\centering
\includegraphics[width=\linewidth]{figures/sacr-volume-validation.pdf}
\caption{Independent volume integration versus SACR for both profiles and
all three field components. Lower panels retain signed differences; bars
show the change under the final volume-rule refinement, not a statistical
confidence interval. Probe indices are centre (1), bulk (2--3), off-axis
10 mm from the end (4--5), axis 5 mm and 0.1 mm from the end (6--7), and
off-axis 5 mm from the end (8). All axes include zero.}
\label{fig:sacr-volume-validation}\end{figure}
'''
    tex+=f'The largest observed difference among {v["scalar_components"]} components is ${v["maximum_absolute_difference_V_m"]:.2g}$ V/m; the final independent refinement changes a component by at most ${v["maximum_last_refinement_delta_V_m"]:.2g}$ V/m. '
    tex+=r'''These are sampled numerical checks rather than a uniform error bound.

\begin{samepage}
A second check keeps charge, tube cross-section, line-density profile and
15 material targets fixed while increasing $R$ from 2 to 1000 m. The same
curved SACR implementation also evaluates $R=\infty$ and is compared with
the separately derived finite-cylinder reference. Define
\begin{equation}
 \Delta_i(R)=\frac{\max_{15\ {\rm targets}}
 |E_i^{\rm SACR}(R)-E_i^{\rm cylinder}|}{E_{i,*}},\qquad
 E_{i,*}=\max_{51\ {\rm straight\ targets}}|E_i^{\rm cylinder}|.
\end{equation}
The fixed component scale retains targets with zero field. Finite-radius
differences measure the physical change in source geometry.
\end{samepage}
\begin{figure}[!ht]\centering
\includegraphics[width=\linewidth]{figures/sacr-radius-convergence.pdf}
\caption{Constant-section SACR approaches the straight-cylinder field as
curvature tends to zero. Each point is the maximum difference over the same
15 material targets, divided by its fixed straight component scale.
Both axes retain zero; the point at $1/R=0$ is an actual infinite-radius
calculation. These geometry differences are distinct from quadrature error.}
\label{fig:sacr-radius-convergence}\end{figure}
'''
    tex+=f'The straight-limit implementations differ by at most ${inf:.2g}$ V/m over the selected targets. '
    tex+=f'The largest recorded radius-sweep quadrature change is ${r["worst_recorded_quadrature_change_V_m"]:.2g}$ V/m. '
    tex+='The two checks support using SACR as the independent frozen-field reference for this tube; they do not validate beam tracking.\n'
    # Use readable scientific notation in LaTeX.
    import re
    tex=re.sub(r'\$([0-9.]+)e([+-][0-9]+)\$',lambda m:'$'+m.group(1)+r'\times10^{'+str(int(m.group(2)))+'}$',tex)
    (paper/'results/reference-extension.tex').write_text(tex)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--paper-dir',type=Path,default=DEFAULT_PAPER)
    a=parser.parse_args();paper=a.paper_dir.resolve()
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,'axes.titlesize':8,'axes.labelsize':7.5,
       'xtick.labelsize':7,'ytick.labelsize':7,'axes.spines.top':False,'axes.spines.right':False,
       'lines.linewidth':1.,'savefig.facecolor':'white'})
    volume_plot(paper);radius_plot(paper);result_tex(paper)

if __name__=='__main__':main()
