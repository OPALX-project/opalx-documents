"""Compare unprofiled batch timings, moments and Nsight kernel/API counts."""
from pathlib import Path
import io,json,re,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-gpu-batch-mpl')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;D=P/'results'
ms=pd.DataFrame(json.loads((D/'measurements.json').read_text()))
def stat(p):
 s=p.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',s,re.S)];body=re.split(r'&data\b.*?&end',s,maxsplit=1,flags=re.S)[1];lines=[l.strip() for l in body.splitlines() if l.strip() and not l.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',s)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
reference=stat(D/'batch-0-repeat-1/case.stat');moments=[]
for m in ms.to_dict('records'):
 name=f"batch-{m['batch']}-"+('profile' if m['profile'] else f"repeat-{m['repeat']}")
 got=stat(D/name/'case.stat');assert np.array_equal(got.t,reference.t)
 for field in got:
  if field.startswith(('rms_','emit_')):
   delta=float(abs(got[field]-reference[field]).max());scale=float(abs(reference[field]).max());moments.append(dict(case=name,field=field,max_absolute_difference=delta,max_difference_percent_peak=100*delta/scale if scale else None))
pd.DataFrame(moments).to_csv(D/'moment-comparison.csv',index=False)
runtime=ms[~ms.profile].groupby('batch').agg(wall_mean_s=('elapsed_s','mean'),wall_min_s=('elapsed_s','min'),wall_max_s=('elapsed_s','max'),tracking_mean_s=('tracking_s','mean'),tracking_min_s=('tracking_s','min'),tracking_max_s=('tracking_s','max'),orbit_mean_s=('orbit_s','mean'))
counts=[]
for b in [0,1,8,32,64]:
 folder=P.parent/'gpu-proof' if b==0 else D/f'batch-{b}-profile'
 k=pd.read_csv(folder/'stats_cuda_gpu_kern_sum.csv');a=pd.read_csv(folder/'stats_cuda_api_sum.csv')
 def calls(name):return int(a.loc[a.Name==name,'Num Calls'].sum())
 counts.append(dict(batch=b,kernel_launches=int(k.Instances.sum()),kernel_duration_s=float(k['Total Time (ns)'].sum()/1e9),device_synchronizations=calls('cudaDeviceSynchronize'),stream_synchronizations=calls('cudaStreamSynchronize'),synchronizations=calls('cudaDeviceSynchronize')+calls('cudaStreamSynchronize')))
counts=pd.DataFrame(counts).set_index('batch');table=runtime.join(counts);table['tracking_speedup']=table.loc[0,'tracking_mean_s']/table.tracking_mean_s;table['kernel_reduction_percent']=100*(1-table.kernel_launches/table.loc[0,'kernel_launches']);table['sync_reduction_percent']=100*(1-table.device_synchronizations/table.loc[0,'device_synchronizations']);table.to_csv(D/'comparison.csv');print(table.to_string())
plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
x=np.arange(5);labels=['Serial','1','8','32','64'];colors=['#777777','#0072B2','#009E73','#E69F00','#CC79A7']
fig,ax=plt.subplots(1,3,figsize=(11,3.3));fig.subplots_adjust(left=.07,right=.99,bottom=.22,top=.82,wspace=.35)
for i,(col,title,ylabel,fac) in enumerate([('tracking_mean_s','Tracking time','Seconds / 100 steps',1),('kernel_launches','CUDA kernel launches','Millions',1e-6),('device_synchronizations','Device synchronizations','Thousands',1e-3)]):
 values=table[col].to_numpy()*fac;ax[i].bar(x,values,color=colors,width=.65)
 if i==0:
  lo=(table.tracking_mean_s-table.tracking_min_s).to_numpy();hi=(table.tracking_max_s-table.tracking_mean_s).to_numpy();ax[i].errorbar(x,values,yerr=[lo,hi],fmt='none',ecolor='black',capsize=3)
 for xx,v in zip(x,values):ax[i].text(xx,v+max(values)*.025,f'{v:.2f}' if i==0 else f'{v:.3f}',ha='center',fontsize=8)
 ax[i].set_xticks(x,labels);ax[i].set_xlabel('Batch size');ax[i].set_ylabel(ylabel);ax[i].set_title(title);ax[i].set_ylim(0,max(values)*1.2);ax[i].grid(axis='y',alpha=.15);ax[i].set_axisbelow(True)
fig.suptitle('FFT2D5 on one A100: DBA pilot, 100k particles, 64×64×512, 100 steps',fontsize=11)
fig.text(.5,.02,'Time: mean/range of two unprofiled runs, excluding OrbitThreader. Counts: separate Nsight traces; serial trace uses preserved executable.',ha='center',fontsize=7)
for ext in ['png','pdf']:fig.savefig(D/f'gpu-batching-comparison.{ext}',dpi=300,bbox_inches='tight')
