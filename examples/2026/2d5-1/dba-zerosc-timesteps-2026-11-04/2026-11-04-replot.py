"""Replot the saved DBA ZeroSC table; no simulations are launched."""
from pathlib import Path
import sys,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-dba-mpl')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator,ScalarFormatter
root=Path(__file__).resolve().parent
source=Path(sys.argv[1]) if len(sys.argv)>1 else root/'2026-11-04-timestep-summary.csv'
out=Path(sys.argv[2]) if len(sys.argv)>2 else root/'2026-11-04-dba-zerosc-timestep-study'
s=pd.read_csv(source)
if len(sys.argv)>3:s=s[s.dt_ps<=float(sys.argv[3])]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelsize':11,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
fig,axes=plt.subplots(2,2,figsize=(10,6.6),layout='constrained')
for j,(axis,color,ref) in enumerate([('x','#0072B2',.7701075691328534),('y','#D55E00',1.689536397020211)]):
 complete=s[s[f'{axis}_count']==64];bad=s[s[f'{axis}_count']<64]
 a=axes[0,j];a.axhline(ref,color='black',ls='--',lw=1.2,label=f'Analytic: {ref:.6f}');a.fill_between(s.dt_ps,ref*.99,ref*1.01,color='gray',alpha=.12,label='±1% of analytic');a.plot(complete.dt_ps,complete[f'Q{axis}_median'],'o-',color=color,label='KV median (all 64 tracks)');a.fill_between(complete.dt_ps,complete[f'Q{axis}_05'],complete[f'Q{axis}_95'],color=color,alpha=.2,label='5–95% particle range');
 if not bad.empty:a.scatter(bad.dt_ps,bad[f'Q{axis}_median'],marker='x',color='crimson',label='Incomplete station records')
 a.set_ylabel('$Q_'+axis+'$');a.set_title('Radial' if axis=='x' else 'Vertical');a.legend(fontsize=8)
 a=axes[1,j];a.axhspan(-1,1,color='gray',alpha=.12);a.axhline(0,color='black',lw=.8);a.plot(complete.dt_ps,complete[f'{axis}_median_error_percent'],'o-',color=color);a.fill_between(complete.dt_ps,100*(complete[f'Q{axis}_05']/ref-1),100*(complete[f'Q{axis}_95']/ref-1),color=color,alpha=.2);a.scatter(bad.dt_ps,bad[f'{axis}_median_error_percent'],marker='x',color='crimson');a.set_ylabel('Difference from analytic (%)');a.set_xlabel('Fixed Boris timestep (ps)')
 for a in axes[:,j]:
  a.set_xscale('log',base=2);a.xaxis.set_major_locator(FixedLocator([v for v in [2,3,4,8,16,31,62,125,250,500,915] if s.dt_ps.min()<=v<=s.dt_ps.max()]));a.xaxis.set_major_formatter(ScalarFormatter());a.tick_params(axis='x',labelsize=8);a.grid(alpha=.2)
fig.suptitle('DBA ZeroSC · 2.5 MeV protons · 16 turns · current build-omp',fontsize=12)
for ext in ['png','pdf']:fig.savefig(out.with_suffix('.'+ext),dpi=300)
