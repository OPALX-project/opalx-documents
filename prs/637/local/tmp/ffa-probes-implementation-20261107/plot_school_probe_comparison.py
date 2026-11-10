#!/usr/bin/env python3
"""Plot matched raw FFA probe crossings; this is integration analysis, not a unit test."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs',nargs='+',type=Path)
    parser.add_argument('--output-prefix',required=True,type=Path)
    parser.add_argument('--observable',choices=['radial','vertical'],default='radial')
    args=parser.parse_args()
    plt.rcParams.update({'font.size':10,'axes.labelsize':11,'axes.titlesize':11,
                         'legend.fontsize':9,'font.family':'DejaVu Sans',
                         'axes.spines.top':False,'axes.spines.right':False,
                         'savefig.dpi':300,'pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(10.2,7.0),sharex='col',
                          gridspec_kw={'height_ratios':[1.8,1]})
    frames=[]; reports=[]
    colors=['#1261a0','#b34520','#31854f','#754ca0']
    for index,path in enumerate(args.runs):
        manifest=json.loads((path/'manifest.json').read_text())
        analysis=json.loads((path/'analysis.json').read_text())
        data=pd.read_csv(path/'crossing-comparison.csv').sort_values('time_native')
        label=('OPALX' if len(args.runs)==1 else f'OPALX, dt={manifest["dt_s"]*1e12:.3g} ps')
        oldlabel=('OPAL 2022.1' if len(args.runs)==1 else f'OPAL, dt={manifest["dt_s"]*1e12:.3g} ps')
        if args.observable=='radial':
            for suffix in ['old','native']:
                data['position_'+suffix]=np.hypot(data['x_'+suffix],data['y_'+suffix])
                data['momentum_'+suffix]=(data['x_'+suffix]*data['px_'+suffix]
                                         +data['y_'+suffix]*data['py_'+suffix])/data['position_'+suffix]
            position_label='Radius (mm)'; momentum_label=r'Radial momentum $p_r/(mc)$'
            residual_position_label=r'$r_{\mathrm{OPALX}}-r_{\mathrm{OPAL}}$ (mm)'
            residual_momentum_label=r'$\Delta p_r/(mc)$'
        else:
            for suffix in ['old','native']:
                data['position_'+suffix]=data['z_'+suffix]
                data['momentum_'+suffix]=data['pz_'+suffix]
            position_label='Vertical position (mm)'; momentum_label=r'Vertical momentum $p_z/(mc)$'
            residual_position_label=r'$z_{\mathrm{OPALX}}-z_{\mathrm{OPAL}}$ (mm)'
            residual_momentum_label=r'$\Delta p_z/(mc)$'
        color=colors[index%len(colors)]
        axes[0,0].plot(data.time_old*1e6,data.position_old*1e3,'o',ms=4,mfc='none',
                       mec=color,alpha=.75,label=oldlabel)
        axes[0,0].plot(data.time_native*1e6,data.position_native*1e3,'-',lw=1.1,
                       color=color,label=label)
        axes[0,1].plot(data.time_old*1e6,data.momentum_old,'o',ms=4,mfc='none',mec=color,alpha=.75)
        axes[0,1].plot(data.time_native*1e6,data.momentum_native,'-',lw=1.1,color=color)
        data['position_delta']=data.position_native-data.position_old
        data['momentum_delta']=data.momentum_native-data.momentum_old
        axes[1,0].plot(data.time_native*1e6,data.position_delta*1e3,'o-',ms=3,lw=.8,color=color)
        axes[1,1].plot(data.time_native*1e6,data.momentum_delta,'o-',ms=3,lw=.8,color=color)
        reports.append(dict(directory=str(path.resolve()),dt_s=manifest['dt_s'],
                            matched_crossings=len(data),
                            max_abs_position_delta_m=float(data.position_delta.abs().max()),
                            rms_position_delta_m=float(np.sqrt(np.mean(data.position_delta**2))),
                            max_abs_momentum_delta_mc=float(data.momentum_delta.abs().max()),
                            old_initial_hits_excluded=analysis['old_initial_hits_excluded'],
                            unmatched_old=analysis['unmatched_old'],unmatched_native=analysis['unmatched_native']))
        data['native_run']=str(path.resolve());frames.append(data)
    axes[0,0].set_ylabel(position_label);axes[0,1].set_ylabel(momentum_label)
    axes[1,0].set_ylabel(residual_position_label);axes[1,1].set_ylabel(residual_momentum_label)
    for ax in axes.flat:
        ax.grid(color='#d4d8dc',lw=.6,alpha=.65)
        ax.tick_params(direction='out')
    for ax in axes[1]:
        ax.axhline(0,color='#777777',lw=.7,zorder=0)
        ax.set_xlabel('Crossing time (µs)')
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.94),ncol=2,frameon=False)
    for ax in [axes[0,1],axes[1,1]]:
        ax.ticklabel_format(axis='y',style='sci',scilimits=(-2,2),useMathText=True)
    title_case=json.loads((args.runs[0]/'manifest.json').read_text())['case']
    fig.suptitle(f'{title_case} FFA school: raw probe crossing comparison',fontsize=13,y=.98)
    fig.text(.5,.03,'Matched station / particle ID / chronological passage; initial-plane legacy rows excluded.\n'
             'Native reference launch-plane counts and legacy RF-budget labels are retained separately.\n'
             'Shown dt values are nominal; native boundary stepping may subdivide them.',
             ha='center',va='bottom',fontsize=8.5,color='#42474c')
    fig.tight_layout(rect=(0,.12,1,.86),h_pad=1.2,w_pad=2.)
    prefix=args.output_prefix;prefix.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(prefix.with_suffix('.png'));fig.savefig(prefix.with_suffix('.pdf'));plt.close(fig)
    pd.concat(frames,ignore_index=True).to_csv(prefix.with_suffix('.csv'),index=False)
    prefix.with_suffix('.json').write_text(json.dumps(dict(observable=args.observable,runs=reports),indent=2)+'\n')
    print(json.dumps(reports,indent=2))

if __name__=='__main__':main()
