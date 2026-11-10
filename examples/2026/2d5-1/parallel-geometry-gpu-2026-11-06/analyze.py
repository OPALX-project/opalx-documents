"""Matched-executable CUDA geometry comparison; snapshots/traces stay native."""
from pathlib import Path
import os,re,io,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-gpu-geometry-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-gpu-geometry-cache')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
RAW=Path(os.environ.get('OPALX_GPU_GEOMETRY_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-06-gpu-parallel-geometry'))
def stat(p):
 t=p.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',t,re.S)];lines=[x.strip() for x in re.split(r'&data\b.*?&end',t,maxsplit=1,flags=re.S)[1].splitlines() if x.strip() and not x.lstrip().startswith('!')][len(re.findall(r'&parameter\b',t)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
rows=[];kernels=[];audits=[]
for n in [1,2,3]:
 for profiled in [False,True]:
  runs={}
  for mode in ['before','after']:
   d=RAW/f'gpu-{n}-{mode}{"-profile" if profiled else ""}'
   if not (d/'run.json').exists():continue
   meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0
   log=(d/'case.out').read_text();timer=lambda name,key='Wall max':float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
   q=stat(d/'case.stat');assert (q.numParticles==100000).all();runs[mode]=q
   if not profiled:rows.append(dict(gpus=n,mode=mode,steady_sc_ms=1000*timer('2D5 Solve')/99,geometry_phase_ms=10*timer('2D5 Geometry'),first_sc_ms=1000*timer('2D5 First Solve'),main_s=timer('mainTimer','Wall tot'),orbit_s=timer('OrbThreader'),main_minus_orbit_s=timer('mainTimer','Wall tot')-timer('OrbThreader'),process_s=meta['wall_seconds'],binary_sha256=meta['binary_sha256']))
   if profiled:
    for rank in json.loads((d/'geometry-kernels.json').read_text()):
     ordered=rank['kernels'];stages=['serial build','projection'] if mode=='before' else ['segments/leaves','prefix/hierarchy','projection']
     assert len(ordered)==len(stages)
     for stage,k in zip(stages,ordered):kernels.append(dict(gpus=n,rank=rank['rank'],mode=mode,stage=stage,**k))
  if len(runs)==2:
   a=runs['after'];b=runs['before'];cols=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s'];rel={c:float(abs(a[c]-b[c]).max()/abs(b[c]).max()) for c in cols};assert max(rel.values())<1e-9
   audits.append(dict(gpus=n,profiled=profiled,max_stat_relative=max(rel.values()),**rel))
s=pd.DataFrame(rows);k=pd.DataFrame(kernels);s.to_csv(OUT/'timings.csv',index=False);k.to_csv(OUT/'geometry-kernels.csv',index=False);pd.DataFrame(audits).to_csv(OUT/'stat-audit.csv',index=False)
if not len(s):raise SystemExit('No completed runs available')
plt.rcParams.update({'font.family':'serif','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':240})
fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained');ns=sorted(s.gpus.unique());x=np.arange(len(ns))
for j,mode in enumerate(['before','after']):
 q=s[s['mode']==mode].set_index('gpus').reindex(ns)
 for ax,col in zip(axes[1:],['steady_sc_ms','main_minus_orbit_s']):
  bars=ax.bar(x+(j-.5)*.36,q[col],.34,label=mode.capitalize());ax.bar_label(bars,fmt='%.2f',fontsize=8,padding=10 if j==0 else 2)
 if len(k):
  build=k[(k['mode']==mode)&(k.stage!='projection')].groupby(['gpus','rank']).average_ms.sum().groupby('gpus').max().reindex(ns)
  bars=axes[0].bar(x+(j-.5)*.36,build,.34,label=mode.capitalize());axes[0].bar_label(bars,fmt='%.3f',fontsize=8,padding=3)
for ax,title,ylabel in zip(axes,['Geometry/hierarchy kernels','Steady physical SC solves','Tracking without OrbitThreader'],['GPU execution [ms/step]','Wall time [ms/call]','Wall time [s / 100 steps]']):
 ax.set(xticks=x,xticklabels=[str(n) for n in ns],xlabel='A100s / MPI ranks',title=title,ylabel=ylabel);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.set_ylim(0,ax.get_ylim()[1]*1.12)
axes[0].legend();fig.savefig(OUT/'timings.png');fig.savefig(OUT/'timings.pdf');plt.close(fig)
print(s.to_string(index=False));print(k.drop(columns=['name'],errors='ignore').to_string(index=False));print(pd.DataFrame(audits).to_string(index=False))

# Rank scaling also preserves the tracking curves.
cross=[]
for mode in ['before','after']:
 ref=stat(RAW/f'gpu-1-{mode}/case.stat')
 for n in [2,3]:
  d=RAW/f'gpu-{n}-{mode}'
  if not (d/'run.json').exists():continue
  a=stat(d/'case.stat');cols=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s'];rel={c:float(abs(a[c]-ref[c]).max()/abs(ref[c]).max()) for c in cols};assert max(rel.values())<1e-8
  cross.append(dict(mode=mode,gpus=n,reference_gpus=1,max_stat_relative=max(rel.values()),**rel))
pd.DataFrame(cross).to_csv(OUT/'cross-rank-stat-audit.csv',index=False);print('CROSS RANK',cross)
# Update the earlier 100/1000-step whole-tracking calibration using the measured
# steady SC saving. This is a modelled estimate, not a new calibration pair.
cal=pd.read_csv(OUT.parent/'longitudinal-density-batch-2026-11-06/turn-estimates.csv')
est=[]
for n in sorted(s.gpus.unique()):
 q=s[s.gpus==n].set_index('mode')
 if not {'before','after'}.issubset(q.index):continue
 old=float(cal[(cal.gpus==n)&(cal['mode']=='after')].whole_step_ms.iloc[0]);saving=q.loc['before','steady_sc_ms']-q.loc['after','steady_sc_ms'];new=old-saving
 est.append(dict(gpus=int(n),previous_complete_step_ms=old,steady_sc_saving_ms=saving,estimated_complete_step_ms=new,steps_per_turn=393240,dt_s=3e-12,estimated_minutes_per_turn=new*393240/60000,method='Prior unprofiled 100/1000-step complete-step calibration minus measured 99-solve steady SC saving; assumes non-SC tracking time unchanged; not a fresh calibration'))
pd.DataFrame(est).to_csv(OUT/'turn-estimates.csv',index=False);print('UPDATED TURN ESTIMATES',est)
