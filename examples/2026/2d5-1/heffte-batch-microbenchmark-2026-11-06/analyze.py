from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
frames=[]
for backend in ['cpu','gpu']:
    f=root/backend/'samples.csv'
    if not f.exists(): continue
    d=pd.read_csv(f)
    s=d.groupby(['nz','batch','method']).seconds_per_solve.agg(['median','min','max']).reset_index()
    baseline=s[s.method=='current_solveBatched'][['nz','batch','median']].rename(columns={'median':'baseline'})
    s=s.merge(baseline,on=['nz','batch'])
    s['speedup']=s.baseline/s['median']
    s['milliseconds']=s['median']*1000
    s['backend']=backend
    frames.append(s)
summary=pd.concat(frames,ignore_index=True)
summary.to_csv(root/'summary.csv',index=False)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220})
fig,axs=plt.subplots(len(frames),2,figsize=(10,3.4*len(frames)),squeeze=False,layout='constrained')
labels={'current_solveBatched':'Current R2C','public_reorder_scale_fused':'Public R2C, fused scale','executor_r2c_rows_transpose':'Batched R2C rows','executor_c2c_merged_xy':'Batched 2D C2C'}
for row,frame in enumerate(frames):
    for ax,nz in zip(axs[row],[256,512]):
        for method,label in labels.items():
            d=frame[(frame.nz==nz)&(frame.method==method)].sort_values('batch')
            ax.plot(d.batch,d.milliseconds,'o-',label=label,linewidth=1.6,markersize=4)
        ax.set(xscale='log',yscale='log',xticks=[1,8,32,64],xlabel='Slices per batch',ylabel='Time per solve [ms]',title=f'{frame.backend.iloc[0].upper()}: 64 × 64 × {nz}')
        ax.set_xticklabels(['1','8','32','64'])
        ax.grid(alpha=.2)
axs[0,0].legend(fontsize=8)
fig.savefig(root/'heffte-batch-timing.png')
fig.savefig(root/'heffte-batch-timing.pdf')
print(summary[['backend','nz','batch','method','milliseconds','speedup']].to_string(index=False))
