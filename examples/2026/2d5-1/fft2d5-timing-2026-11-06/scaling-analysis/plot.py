"""Compare inclusive GPU phase totals; do not stack overlapping timers."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-mpi-z-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-mpi-z-cache')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;data=ROOT.parent
t=pd.read_csv(data/'timers.csv');g=t[t.code=='GPU'].pivot(index='timer',columns='ranks',values='wall_max_s');s=pd.read_csv(data/'summary.csv').query("code=='GPU'").set_index('ranks')
rows=[('Forward FFT','2D5 FFT Rho'),('Inverse FFT','2D5 FFT Back'),('Geometry / projections','2D5 Geometry'),('Particle migration¹','2D5 Migration'),('Density halo²','2D5 Rho Halo'),('Field halo²','2D5 E Halo')]
report=pd.DataFrame([dict(phase=label,gpu1_s=g.loc[name,1],gpu2_s=g.loc[name,2]) for label,name in rows]);report.to_csv(ROOT/'phase-breakdown.csv',index=False)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':300})
fig,axes=plt.subplots(1,2,figsize=(11,4.8),gridspec_kw={'width_ratios':[1.65,1]},layout='constrained');ax=axes[0];y=np.arange(len(rows))
for offset,n,color in [(-.18,1,'#0072B2'),(.18,2,'#D55E00')]:
 vals=[g.loc[name,n] for _,name in rows];bars=ax.barh(y+offset,vals,height=.33,label=f'{n} GPU'+('s' if n>1 else ''),color=color)
 ax.bar_label(bars,labels=[f'{x:.3f}' if x else '—' for x in vals],padding=3,fontsize=9)
ax.set_yticks(y,[x[0] for x in rows]);ax.invert_yaxis();ax.set_xlim(0,4.15);ax.set_xlabel('Maximum rank time [s], all 100 physical calls');ax.set_title('Inclusive phase totals, including the first call');ax.legend(loc='lower right');ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
ax=axes[1];vals=[s.loc[n,'steady_solve_ms'] for n in [1,2]];bars=ax.bar(['1 GPU','2 GPUs'],vals,color=['#0072B2','#D55E00'],width=.55);ax.bar_label(bars,labels=[f'{x:.2f} ms' for x in vals],padding=4);ideal=vals[0]/2
ax.hlines(ideal,.6,1.4,colors='black',linestyles='--');ax.text(1.43,ideal,f'Ideal 2-GPU\n{ideal:.2f} ms',va='center',fontsize=9);ax.set_xlim(-.6,2);ax.set_ylim(0,90);ax.set_ylabel('Complete FFT2D5 solve [ms/call]');ax.set_title('Steady state: 99 physical calls');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.suptitle('FFT2D5: FFT work halves; geometry and communication limit scaling',fontsize=12)
fig.supxlabel('¹ Migration includes the second projection pass.  ² Halo totals include startup and synchronization.\nParent and child timers overlap; totals must not be added.',fontsize=9)
fig.savefig(ROOT/'gpu-breakdown.png');fig.savefig(ROOT/'gpu-breakdown.pdf');plt.close(fig)
a,b=vals
print(f'speedup={a/b:.6f}; efficiency={a/(2*b):.6f}; ideal={a/2:.6f}ms; gap={b-a/2:.6f}ms')
print(report.to_string(index=False))
