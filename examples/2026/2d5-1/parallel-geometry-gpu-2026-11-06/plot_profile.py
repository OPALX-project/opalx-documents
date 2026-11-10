"""Current one-A100 runtime breakdown from existing trace summaries."""
from pathlib import Path
import os,json,shutil
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-gpu-geometry-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-gpu-geometry-cache')
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent;RAW=Path(os.environ.get('OPALX_GPU_GEOMETRY_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-06-gpu-parallel-geometry'))/'gpu-1-after-profile'
a=json.loads((RAW/'runtime-breakdown.json').read_text());k=pd.read_csv(RAW/'kernel-groups.csv');k['category']=k.category.replace({'Poisson staging / transposes':'Poisson grid kernels'});k['kernel_time_percent']=100*k.ms_per_step/k.ms_per_step.sum();k.to_csv(OUT/'runtime-kernel-groups.csv',index=False);shutil.copy2(RAW/'cuda-api.csv',OUT/'runtime-cuda-api.csv');shutil.copy2(RAW/'runtime-breakdown.json',OUT/'runtime-breakdown.json')
plt.rcParams.update({'font.family':'serif','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':240})
fig,axes=plt.subplots(1,2,figsize=(11,4.5),layout='constrained',gridspec_kw={'width_ratios':[1.5,1]})
z=k.sort_values('ms_per_step');ax=axes[0];bars=ax.barh(z.category,z.ms_per_step,color='#0072B2');ax.bar_label(bars,labels=[f'{v:.3f} ms  ({p:.1f}%)' for v,p in zip(z.ms_per_step,z.kernel_time_percent)],fontsize=8,padding=3);ax.set(xlabel='GPU kernel execution per step [ms]',title='One A100: current kernel-time distribution',xlim=(0,3.15));ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
ax=axes[1];left=0
for label,value,color in [('Kernels',a['kernel_busy_percent'],'#0072B2'),('Copy/memset only',a['copy_memset_only_percent'],'#E69F00'),('No device activity',a['no_device_activity_percent'],'#CCCCCC')]:
 ax.barh(0,value,left=left,label=f'{label}: {value:.2f}%',color=color);left+=value
ax.set(xlim=(0,100),ylim=(-.8,.8),yticks=[],xlabel='Profiled device window [%]',title='Temporal activity — not SM occupancy')
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.17),frameon=False,fontsize=9)
ax.text(.02,.94,f"{a['profiled_window_ms_per_step']:.2f} ms/step profiled window\n{a['kernel_execution_ms_per_step']:.2f} ms/step kernel-active",transform=ax.transAxes,va='top',fontsize=10)
ax.text(.02,.07,f"{a['kernel_count_per_step']:.0f} kernel launches/step\n{a['synchronization_calls']/a['steps']:.0f} synchronizations/step",transform=ax.transAxes,va='bottom',fontsize=10)
fig.savefig(OUT/'runtime-breakdown.png');fig.savefig(OUT/'runtime-breakdown.pdf');plt.close(fig)
print(k.to_string(index=False));print(a)
