"""Measured blocking wall-time groups, and separate CPU-stack evidence."""
from pathlib import Path
import json, os, tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir())/"opalx-fftw-mpl"))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'dba-fftw-profile'
j=json.loads((O/'summary.json').read_text());old=json.loads((R/'dba-projection-cache-retiming/summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':220})
fig,axes=plt.subplots(1,2,figsize=(11.4,5.3),gridspec_kw={'width_ratios':[1,1.15]})
labels=['Projection','FFT buffer copies','Scatter / gather','Other kernels','Host work outside timers']
colors=['#0072B2','#E69F00','#009E73','#8C8C8C','#CC79A7']
for i,d in enumerate([old,j]):
 g=d['measured_wall_groups_s'];v=[g['particle_projection']+g['geometry_preparation'],g['fft_pack_unpack'],g['deposition_including_projection']+g['gather_including_projection'],g['other_kokkos_callbacks'],g['outside_kokkos_callbacks']]
 left=0
 for value,label,color in zip(v,labels,colors):
  axes[0].barh(i,value,left=left,color=color,label=label if i==0 else None,height=.52)
  if value>3:axes[0].text(left+value/2,i,f'{value:.1f}',ha='center',va='center',color='white' if color in ['#0072B2','#8C8C8C'] else 'black',fontsize=9)
  left+=value
 axes[0].text(left+.5,i,f'{left:.2f} s',va='center',fontsize=10)
axes[0].set(yticks=[0,1],yticklabels=['Stock FFT','FFTW'],xlim=(0,60),xlabel='Wall time for 100 steps [s]',title='Blocking timer measurements')
axes[0].invert_yaxis();axes[0].legend(loc='upper left',bbox_to_anchor=(0,-.2),frameon=False,ncol=2,fontsize=8)
keys=['Reference-path projection','Other slice-solver / FFT interface','FFTW / heFFTe FFT math/reshapes','Runtime / waiting / unclassified','Other deposition / gather','Other tracking / host work']
s={x['category']:x['percent'] for x in j['sample_categories']};values=[s.get(k,0) for k in keys]
short=['Particle projection','Slice solver / FFT interface','FFTW / heFFTe arithmetic','Runtime / waiting','Deposition / gathering','Other host work']
axes[1].barh(np.arange(len(keys)),values,color=['#0072B2','#E69F00','#CC79A7','#8C8C8C','#009E73','#999999'],height=.62)
for i,v in enumerate(values):axes[1].text(v+.6,i,f'{v:.1f}%',va='center',fontsize=9)
axes[1].set(yticks=np.arange(len(keys)),yticklabels=short,xlim=(0,45),xlabel='Main-thread stack samples [%]',title='Independent CPU sample (FFTW)');axes[1].invert_yaxis()
for ax in axes:ax.set_axisbelow(True);ax.grid(axis='x',alpha=.2)
fig.suptitle('DBA FFT2D5 pilot · 100 steps · 100k particles · 64 × 64 × 512 · 4 OpenMP threads',fontsize=12)
fig.subplots_adjust(left=.08,right=.96,top=.83,bottom=.32,wspace=.64)
fig.text(.08,.025,'Host work includes FFT arithmetic and initialization. CPU samples are a separate measurement; do not add them to timer groups.',fontsize=8,color='#555555')
for ext in ['png','pdf']:fig.savefig(O/f'fftw-profile.{ext}')
