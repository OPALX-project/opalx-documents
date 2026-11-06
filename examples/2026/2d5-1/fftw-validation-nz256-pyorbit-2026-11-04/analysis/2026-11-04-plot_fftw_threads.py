from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-pilot-mpl')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent/'dba-fftw-threads';d=pd.read_csv(R/'comparison.csv');g=d.groupby('fftw_threads').wall_s.agg(['mean','min','max'])
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
f,ax=plt.subplots(figsize=(5.4,3.8));f.subplots_adjust(left=.14,right=.98,top=.88,bottom=.26);x=np.arange(3);ax.bar(x,g['mean'],color=['#0072B2','#56B4E9','#E69F00'],width=.6);ax.errorbar(x,g['mean'],yerr=[g['mean']-g['min'],g['max']-g['mean']],fmt='none',ecolor='black',capsize=4)
for i,v in enumerate(g['mean']):ax.text(i,v+.6,f'{v:.2f} s',ha='center')
ax.set(xticks=x,xticklabels=['1','4','16'],xlabel='FFTW maximum threads',ylabel='100-step wall time (s)',ylim=(0,27),title='DBA pilot: batch 8, Kokkos/OpenMP 4, MPI 1');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
f.text(.5,.01,'64 × 64 × 512 · 100,000 KV particles · 5.602 nC\nTwo unprofiled repeats; bars show means and observed ranges.',ha='center',fontsize=7)
for ext in ['png','pdf']:f.savefig(R/f'runtime.{ext}',dpi=300,bbox_inches='tight')
print(g)
