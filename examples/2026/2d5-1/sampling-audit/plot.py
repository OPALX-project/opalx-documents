from pathlib import Path
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/opalx-2d5-1-plots")
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
ref=pd.read_csv(root/'references.csv')
data=pd.read_csv(root.parent/'series.csv')
fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
for code,color in [('Local original','#0072B2'),('PyORBIT','#D55E00')]:
 d=data[(data.code==code)&(data['mode']=='ZeroSC')]
 ax.plot(d.s_m,d.emit_n_u_m*1e6,color=color,label=code+' (100 steps)')
ax.plot(ref.s_m,ref.exact_time,'k:',lw=2,label='Exact: common time (OPALX convention)')
ax.plot(ref.s_m,ref.exact_station,'--',color='#009E73',label='Exact: common station (PyORBIT convention)')
ax.set(xlabel='$s$ (m)',ylabel=r'$\epsilon_{n,u}$ (mm mrad)',xlim=(0,10),ylim=(0,None),title='Zero space charge: different sampling conventions')
ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.grid(alpha=.2);ax.legend(fontsize=9)
fig.savefig(root/'zero-sc-conventions.png',dpi=300)
