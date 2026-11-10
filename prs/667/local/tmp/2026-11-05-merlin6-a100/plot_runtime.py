from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-a100-pr-mpl')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent;R=O/'results';cpu=pd.read_csv(O/'payload/published-dba-timings.csv');gpu=pd.read_csv(R/'dba-vs-published.csv');cpu=cpu[~cpu.profile]
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(6.2,3.9));fig.subplots_adjust(left=.14,right=.98,top=.86,bottom=.3)
groups=[cpu[cpu.batch_size==0].wall_s,cpu[cpu.batch_size==8].wall_s,gpu.wall_s];colors=['#777777','#0072B2','#009E73'];labels=['Published CPU\nserial slices','Published CPU\nbatch 8','A100 GPU\nserial slices']
for i,(d,c) in enumerate(zip(groups,colors)):
 v=d.mean();ax.bar(i,v,color=c,width=.6);ax.errorbar(i,v,yerr=[[v-d.min()],[d.max()-v]],fmt='none',color='black',capsize=4);ax.text(i,v+.025*max(x.max() for x in groups),f'{v:.2f} s',ha='center',fontsize=9)
ax.set(xticks=[0,1,2],xticklabels=labels,ylabel='Wall time for 100 steps (s)',ylim=(0,max(x.max() for x in groups)*1.2),title='PR667 DBA pilot: 100,000 KV particles, $64^2$ × 512');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.text(.5,.035,'One MPI rank; 3 ps steps; 5.602 nC. CPU: published M5/OpenMP 4/FFTW.\nGPU: Gwendolen A100/CUDA/cuFFT. GPU batching is unsupported by this branch.\nBars show means and observed repeat ranges; full application runtimes include startup and I/O.',ha='center',fontsize=7)
for ext in ['png','pdf']:fig.savefig(R/f'dba-runtime-a100.{ext}',dpi=300,bbox_inches='tight')
