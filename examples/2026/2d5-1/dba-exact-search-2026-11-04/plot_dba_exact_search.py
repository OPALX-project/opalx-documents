"""Reproduce runtime and projection-cost comparisons for the exact search."""
from pathlib import Path
import json,os,tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'opalx-fftw-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
R=Path(__file__).resolve().parent;O=R/'dba-exact-search'
s=json.loads((O/'comparison.json').read_text());old=json.loads((R/'dba-fftw-profile/summary.json').read_text());k=pd.read_csv(O/'optimized-profile/kernel-timings.csv')
projection=float(k.loc[k.name=='for:FFT2D5::prepareParticleProjections','exclusive_s'].sum())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
fig,axes=plt.subplots(1,2,figsize=(10.2,4.3))
values=[s['stock_manifest']['elapsed_seconds']]+[r['wall_s'] for r in s['rows'] if r['case']!='optimized-profile']
labels=['Exhaustive','Hierarchy 1','Hierarchy 2']
axes[0].barh(labels,values,color=['#8C8C8C','#0072B2','#0072B2'],height=.6)
for i,v in enumerate(values):axes[0].text(v+.35,i,f'{v:.2f} s',va='center')
axes[0].set(xlabel='Elapsed wall time [s]',xlim=(0,39),title='Same 100-step pilot, unprofiled');axes[0].invert_yaxis()
vs=[old['measured_wall_groups_s']['particle_projection'],projection]
axes[1].barh(['Exhaustive','Hierarchy'],vs,color=['#8C8C8C','#0072B2'],height=.5)
for i,v in enumerate(vs):axes[1].text(v+.15,i,f'{v:.3f} s',va='center')
axes[1].set(xlabel='Projection kernel time over 100 solves [s]',xlim=(0,13),title=f'Projection: {vs[0]/vs[1]:.1f}× faster');axes[1].invert_yaxis()
for ax in axes:ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
fig.suptitle('Exact nearest-segment hierarchy · FFTW Release · 100k particles · 64 × 64 × 512 · 4 threads',fontsize=11)
fig.subplots_adjust(left=.11,right=.97,top=.80,bottom=.20,wspace=.45)
fig.text(.11,.045,'Search oracle: exact indices and coordinates. Tracking differences remain at floating-point roundoff.',fontsize=9,color='#555555')
for ext in ['png','pdf']:fig.savefig(O/f'exact-search-comparison.{ext}')
