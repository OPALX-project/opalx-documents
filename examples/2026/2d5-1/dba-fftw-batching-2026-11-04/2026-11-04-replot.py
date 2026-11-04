"""Publication-quality runtime comparison; means and observed repeat ranges."""
from pathlib import Path
import os,tempfile,json
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'opalx-fftw-mpl'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parent;O=R/'dba-fftw-batching'
d=pd.read_csv(O/'comparison.csv');d=d[~d.profile]
g=d.groupby('batch_size').wall_s.agg(['count','mean','min','max']).reindex([0,1,8,32,64]);g['speedup']=g.loc[0,'mean']/g['mean'];g.to_csv(O/'runtime-summary.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':220})
fig,ax=plt.subplots(figsize=(8.6,4.8));y=np.arange(len(g));means=g['mean'].to_numpy();lower=means-g['min'].to_numpy();upper=g['max'].to_numpy()-means
ax.barh(y,means,xerr=np.array([lower,upper]),height=.61,color=['#8C8C8C','#56B4E9','#009E73','#0072B2','#0072B2'],error_kw=dict(ecolor='#222222',capsize=4,lw=1.3))
for i,(mean,speed) in enumerate(zip(means,g.speedup)):
 ax.text(g.iloc[i]['max']+.4,i,f'{mean:.2f} s'+(f'  ({speed:.2f}×)' if i else ''),va='center')
ax.set(yticks=y,yticklabels=['Serial (no option)','Batch 1','Batch 8','Batch 32','Batch 64'],xlim=(0,26.5),xlabel='Elapsed wall time for 100 steps [s]',title='OPALX FFT2D5 batching · Release / FFTW · 4 OpenMP threads');ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
fig.subplots_adjust(left=.23,right=.96,top=.82,bottom=.21)
fig.text(.23,.91,'Same source: 100k particles · 5.602 nC · 64 × 64 × 512 · Δt = 3 ps',fontsize=10)
fig.text(.23,.085,'Bars: mean of two runs; whiskers: observed range. Serial: one fresh run.',fontsize=9,color='#555555')
fig.text(.23,.04,'All cases retain 100k particles; maximum relative RMS/emittance difference: 2.16 × 10⁻¹⁴.',fontsize=9,color='#555555')
for ext in ['png','pdf']:fig.savefig(O/f'batch-runtime.{ext}')
