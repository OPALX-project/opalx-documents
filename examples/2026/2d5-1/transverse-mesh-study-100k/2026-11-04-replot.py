from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
FIELDS=['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV']
FACTORS=[1e3,1e3,1,1e6,1e6,1e3]
LABELS=['RMS radial (mm)','RMS vertical (mm)','RMS longitudinal (m)','Normalized radial emittance (mm mrad)','Normalized vertical emittance (mm mrad)','Longitudinal emittance (mm eV)']
data=pd.read_csv(ROOT/'2026-11-04-series.csv')
runtimes=pd.read_csv(ROOT/'2026-11-04-runtimes.csv')
pyorbit=pd.read_csv(ROOT/'2026-11-04-pyorbit-series.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
styles=[(32,100000,'#D55E00',':'),(64,100000,'#009E73','--'),(64,200000,'#006644','-'),(128,100000,'#CC79A7','-.'),(512,1048576,'#0072B2','-')]
fig,axes=plt.subplots(2,3,figsize=(11,6.2),layout='constrained')
for ax,field,factor,label in zip(axes.flat,FIELDS,FACTORS,LABELS):
 for n,count,color,ls in styles:
  q=data[(data.mesh==n)&(data.particles==count)];ax.plot(q.s_m,q[field]*factor,color=color,ls=ls,lw=1.5,marker='o' if count==200000 else None,markevery=10,ms=2.5,label=f'{n}×{n}×512 ({count:,} particles)')
 ax.plot(pyorbit.s_m,pyorbit[field]*factor,color='black',ls='--',lw=1.6,label='PyORBIT 512×512×512 (1,048,576 particles)')
 ax.set(xlabel='$s$ (m)',ylabel=label,xlim=(0,10),ylim=(0,None));ax.grid(alpha=.2)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=2,fontsize=9)
fig.suptitle('10 pC, R=2 m, 10 m / 100 steps: OPALX mesh study and PyORBIT')
for ext in ['png','pdf']:fig.savefig(ROOT/f'2026-11-04-mesh-comparison.{ext}',dpi=300)
fig,ax=plt.subplots(figsize=(6.5,3.5),layout='constrained');ax.bar([f'{int(row.mesh)}²\n{int(row.particles):,}' for row in runtimes.itertuples()],runtimes.wall_seconds,color='#0072B2');ax.set(xlabel='Transverse mesh / particle count (Nz=512)',ylabel='Wall time (s)',title='100 steps; identical executable; four OpenMP threads');ax.grid(axis='y',alpha=.2)
for i,r in runtimes.iterrows():ax.text(i,r.wall_seconds+15,f'{r.wall_seconds:.1f} s',ha='center',fontsize=9)
ax.set_ylim(0,runtimes.wall_seconds.max()*1.15)
for ext in ['png','pdf']:fig.savefig(ROOT/f'2026-11-04-runtimes.{ext}',dpi=300)
