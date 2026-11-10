"""Publication figure from saved pilot timings; launches no simulations."""
from pathlib import Path
import os,sys
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-projection-mpl')
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;data=Path(sys.argv[1]) if len(sys.argv)>1 else R/'2026-11-04-comparison.csv';kernels=Path(sys.argv[2]) if len(sys.argv)>2 else R/'2026-11-04-kernel-comparison.csv';out=Path(sys.argv[3]) if len(sys.argv)>3 else R/'2026-11-04-runtime';d=pd.read_csv(data).set_index('case');k=pd.read_csv(kernels).set_index('kernel');plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
f,axs=plt.subplots(1,2,figsize=(9.5,4),layout='constrained');ax=axs[0];v=[d.loc[n,'wall_seconds'] for n in ['baseline','optimized-1','optimized-2']];bars=ax.bar(['Before','After 1','After 2'],v,color=['#777777','#0072B2','#0072B2'],width=.6)
for b,x in zip(bars,v):ax.text(b.get_x()+b.get_width()/2,x+.8,f'{x:.2f} s',ha='center')
ax.set_ylim(0,85);ax.set_ylabel('Wall time (s)');ax.set_title('Identical 100-step pilot');ax.yaxis.grid(alpha=.2);ax.set_axisbelow(True)
ax=axs[1];bottom=[0.,0.]
for names,label,color in [(['for:FFT2D5::preparePathGeometry','for:FFT2D5::prepareParticleProjections'],'Preparation','#009E73'),(['for:Solve2d5::scatterToGrid::scatter'],'Deposition','#0072B2'),(['for:Solver2d5::GatherFromGrid'],'Gather','#D55E00')]:
 vals=[sum(k.loc[n,c] for n in names) for c in ['old_seconds','new_seconds']];ax.bar(['Before','After'],vals,bottom=bottom,label=label,color=color,width=.6);bottom=[b+x for b,x in zip(bottom,vals)]
for i,x in enumerate(bottom):ax.text(i,x+.6,f'{x:.2f} s',ha='center')
ax.set_ylim(0,40);ax.set_ylabel('Kernel wall time per 100 steps (s)');ax.set_title('Profiled geometry, deposition and gather');ax.legend(loc='upper right',fontsize=8);ax.yaxis.grid(alpha=.2);ax.set_axisbelow(True)
f.suptitle('FFT2D5 geometry preparation and projection reuse\n100,000 particles · 64×64×512 · 4 OpenMP threads · 3 ps',fontsize=12)
for ext in ['png','pdf']:f.savefig(out.with_suffix('.'+ext),dpi=300)
