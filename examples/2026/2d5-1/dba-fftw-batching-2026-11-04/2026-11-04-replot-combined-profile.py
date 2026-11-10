"""Measured blocking wall-time groups, and separate CPU-stack evidence."""
from pathlib import Path
import json, os, tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir())/"opalx-fftw-mpl"))
import numpy as np
import pandas as pd
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'dba-fftw-profile'
j=json.loads((O/'summary.json').read_text());old=json.loads((R/'dba-projection-cache-retiming/summary.json').read_text())
k=pd.read_csv(R/'dba-exact-search/optimized-profile/kernel-timings.csv')
get=lambda name:float(k.loc[k.name==name,'exclusive_s'].sum())
main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',(R/'dba-exact-search/optimized-profile/run.log').read_text())[1])
g=dict(particle_projection=get('for:FFT2D5::prepareParticleProjections'),geometry_preparation=get('for:FFT2D5::preparePathGeometry'),fft_pack_unpack=get('for:FFT_toTemp')+get('for:FFT_fromTemp'),deposition_including_projection=get('for:Solve2d5::scatterToGrid::scatter'),gather_including_projection=get('for:Solver2d5::GatherFromGrid'))
g['other_kokkos_callbacks']=float(k.exclusive_s.sum())-sum(g.values());g['outside_kokkos_callbacks']=main-float(k.exclusive_s.sum())
latest=dict(measured_wall_groups_s=g)
batched=json.loads((R/'dba-fftw-batching/summary.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':220})
fig,axes=plt.subplots(1,2,figsize=(13.2,6.2),gridspec_kw={'width_ratios':[1,1.15]})
labels=['Projection','FFT copies / batch packing','Scatter / gather','Other kernels','Host work outside timers']
colors=['#0072B2','#E69F00','#009E73','#8C8C8C','#CC79A7']
for i,d in enumerate([old,j,latest,batched]):
 g=d['measured_wall_groups_s'];v=[g['particle_projection']+g['geometry_preparation'],g['fft_pack_unpack'],g['deposition_including_projection']+g['gather_including_projection'],g['other_kokkos_callbacks'],g['outside_kokkos_callbacks']]
 left=0
 for value,label,color in zip(v,labels,colors):
  axes[0].barh(i,value,left=left,color=color,label=label if i==0 else None,height=.52)
  if value>3:axes[0].text(left+value/2,i,f'{value:.1f}',ha='center',va='center',color='white' if color in ['#0072B2','#8C8C8C'] else 'black',fontsize=9)
  left+=value
 axes[0].text(left+.5,i,f'{left:.2f} s',va='center',fontsize=10)
axes[0].set(yticks=[0,1,2,3],yticklabels=['Stock FFT','FFTW','FFTW + hierarchy','FFTW + hierarchy\n+ batch 8'],xlim=(0,60),xlabel='Wall time for 100 steps [s]',title='Blocking timer measurements')
axes[0].invert_yaxis();axes[0].set_ylim(3.95,-.5)
axes[0].annotate('Projection: 0.40 s',xy=(.20,2.18),xytext=(2.0,2.58),fontsize=8,color='#0072B2',arrowprops=dict(arrowstyle='-',color='#0072B2',lw=.8))
axes[0].annotate('Batch packing: 0.50 s',xy=(.65,3.18),xytext=(2.0,3.67),fontsize=8,color='#9b6500',arrowprops=dict(arrowstyle='-',color='#9b6500',lw=.8))
axes[0].legend(loc='upper left',bbox_to_anchor=(0,-.2),frameon=False,ncol=2,fontsize=8)
keys=['Reference-path projection','Other slice-solver / FFT interface','FFTW / heFFTe FFT math/reshapes','Runtime / waiting / unclassified','Other deposition / gather','Other tracking / host work']
cpu=json.loads((R/'dba-fftw-batching/summary.json').read_text())
s={x['category']:x['percent'] for x in cpu['sample_categories']};values=[s.get(k,0) for k in keys]
short=['Particle projection','Slice solver / FFT interface','FFTW / heFFTe arithmetic','Runtime / waiting','Deposition / gathering','Other host work']
axes[1].barh(np.arange(len(keys)),values,color=['#0072B2','#E69F00','#CC79A7','#8C8C8C','#009E73','#999999'],height=.62)
for i,v in enumerate(values):axes[1].text(v+.6,i,f'{v:.1f}%',va='center',fontsize=9)
axes[1].set(yticks=np.arange(len(keys)),yticklabels=short,xlim=(0,max(45,max(values)*1.15+2)),xlabel='Main-thread stack samples [%]',title='New CPU sample: FFTW + hierarchy + batch 8');axes[1].invert_yaxis()
for ax in axes:ax.set_axisbelow(True);ax.grid(axis='x',alpha=.2)
fig.suptitle('DBA FFT2D5 pilot · 100 steps · 100k particles · 64 × 64 × 512 · 4 OpenMP threads',fontsize=11)
fig.subplots_adjust(left=.16,right=.97,top=.83,bottom=.32,wspace=.64)
fig.text(.16,.025,'Left: blocking wall timers. Right: fresh batch-8 CPU sample (7 s, during tracking); sample fractions are separate from wall-timer groups.',fontsize=8,color='#555555')
for ext in ['png','pdf']:fig.savefig(R/'dba-fftw-batching'/f'fftw-profile-with-batch8.{ext}')
