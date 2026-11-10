"""Replot classified steady-state main-thread sample fractions."""
from pathlib import Path
import os,sys
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-profile-mpl')
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;source=Path(sys.argv[1]) if len(sys.argv)>1 else R/'2026-11-04-main-thread-sample-summary.csv';out=Path(sys.argv[2]) if len(sys.argv)>2 else R/'2026-11-04-profile';d=pd.read_csv(source).set_index('category').percent
names=['Reference-path projection','heFFTe stock FFT math/reshapes','Other slice-solver / FFT interface'];values=[d[n] for n in names];values.append(100-sum(values));labels=['Particle projection onto reference path','Stock CPU FFT calculations / reshapes','FFT transfers and other slice-solver work','Tracking, runtime and remaining work'];colors=['#0072B2','#D55E00','#009E73','#777777']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
fig,ax=plt.subplots(figsize=(9,3.6),layout='constrained');bars=ax.barh(labels,values,color=colors,height=.6);ax.invert_yaxis();ax.set_xlim(0,55);ax.set_xlabel('Share of steady-state main-thread stack samples (%)');ax.set_title('DBA FFT2D5 pilot · 100,000 particles · 64×64×512 · 4 threads',pad=13);ax.xaxis.grid(alpha=.2);ax.set_axisbelow(True)
for bar,value in zip(bars,values):ax.text(value+.6,bar.get_y()+bar.get_height()/2,f'{value:.1f}%',va='center')
for ext in ['png','pdf']:fig.savefig(out.with_suffix('.'+ext),dpi=300)
