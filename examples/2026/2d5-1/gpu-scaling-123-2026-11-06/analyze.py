"""Identical-executable one/two/three-A100 pilot and full-step calibration."""
from pathlib import Path
import os,re,io,json,hashlib,shutil
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-gpu3-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-gpu3-cache')
import numpy as np,pandas as pd,h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
RAW=Path(os.environ.get('OPALX_GPU3_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-06-gpu3-analysis/native'))
OLD=OUT.parent/'r2c-row-integration-2026-11-06/provenance'
NATIVE_OLD=Path('/Users/adelmann/git/opalx/tmp/2026-11-06-r2c-integration')
EXE='a21ab5e66c046f089d907ff14eb7b5c932a234336d49efc6b082431a8f1dd32a'
def stat(path):
 text=path.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',text,re.S)];lines=[x.strip() for x in re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1].splitlines() if x.strip() and not x.lstrip().startswith('!')][len(re.findall(r'&parameter\b',text)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
def endpoint(path,steps=100):
 with h5py.File(path) as f:
  for group in f.values():
   assert np.array_equal(np.sort(group['id'][:]),np.arange(100000));assert abs(group['q'][:].sum()/5.602212333965894e-9-1)<1e-12
  g=max(f.values(),key=lambda a:float(np.asarray(a.attrs['TIME']).flat[0]));assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-steps*3e-12)<1e-21;assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==steps-1
  a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(g['id'][:])];assert np.isfinite(a).all();return a
rows=[];phases=[];runs={};audits=[]
for n in [1,2,3]:
 d=OLD/f'gpu-{n}-rows' if n<3 else RAW/'gpu-3-rows'
 meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0 and meta['binary_sha256']==EXE
 assert 'PIPEMODE="OPEN"' in (d/'case.in').read_text()
 log=(d/'case.out').read_text();values={name:float(v) for name,v in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Wall max =\s*([\d.eE+-]+)',log)};counts={name:int(v) for name,v in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Count =\s*(\d+)',log)}
 assert counts['2D5 Solve']==99 and counts['2D5 Poisson']==counts['2D5 Line density']==100
 def t(name,key='Wall max'):return float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
 rows.append(dict(gpus=n,steady_sc_ms=1000*values['2D5 Solve']/99,first_sc_ms=1000*values['2D5 First Solve'],warmup_ms=1000*values['2D5 Warmup'],initialize_ms=1000*values['2D5 Initialize'],main_minus_orbit_s=t('mainTimer','Wall tot')-t('OrbThreader'),process_wall_s=meta['wall_seconds']))
 for name,v in values.items():phases.append(dict(gpus=n,phase=name,total_s=v,calls=counts[name],ms_per_physical_solve=10*v))
 s=stat(d/'case.stat');assert len(s)==10 and (s.numParticles==100000).all()
 a=endpoint((NATIVE_OLD/f'gpu-{n}-rows/case.h5') if n<3 else d/'case.h5');runs[n]=(s,a)
for n,(s,a) in runs.items():
 for ref in [1,2]:
  q,b=runs[ref];cols=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s'];rel={c:float(abs(s[c]-q[c]).max()/abs(q[c]).max()) for c in cols}
  e=dict(gpus=n,reference_gpus=ref,max_stat_relative=max(rel.values()),max_position_m=float(np.linalg.norm(a[:,:3]-b[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(a[:,3:6]-b[:,3:6],axis=1).max()),particles=len(a),charge_C=float(a[:,-1].sum()),**{c+'_relative':v for c,v in rel.items()})
  assert e['max_stat_relative']<1e-8 and e['max_position_m']<1e-9 and e['max_momentum']<1e-10,e;audits.append(e)
s=pd.DataFrame(rows);p=pd.DataFrame(phases);s['sc_speedup_vs_1']=s.steady_sc_ms.iloc[0]/s.steady_sc_ms;s['parallel_efficiency_vs_1']=s.sc_speedup_vs_1/s.gpus
s.to_csv(OUT/'summary.csv',index=False);p.to_csv(OUT/'phases.csv',index=False);pd.DataFrame(audits).to_csv(OUT/'physics-audit.csv',index=False)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':240})
fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained');axes[0].bar(s.gpus.astype(str),s.steady_sc_ms,color='#0072B2');axes[0].bar_label(axes[0].containers[0],fmt='%.2f',padding=3);axes[0].set(xlabel='A100s / MPI ranks',ylabel='Space-charge time [ms/call]',title='Steady 99 physical solves',ylim=(0,22));axes[0].grid(axis='y',alpha=.2);axes[0].set_axisbelow(True)
names=['2D5 Geometry','2D5 Line density','2D5 Poisson','2D5 Migration','2D5 Rho Halo','2D5 E Halo']
x=np.arange(len(names))
for j,n in enumerate([1,2,3]):
 y=p[(p.gpus==n)&p.phase.isin(names)].set_index('phase').loc[names].ms_per_physical_solve
 axes[1].bar(x+(j-1)*.25,y,width=.23,label=f'{n} GPU'+('s' if n>1 else ''))
axes[1].set(xticks=x,xticklabels=['Geometry','Line\ndensity','Poisson','Migration','Charge\nhalo','Field\nhalo'],ylabel='Phase total / 100 physical solves [ms]',title='Inclusive timers; first physical call included');axes[1].legend(fontsize=8);axes[1].grid(axis='y',alpha=.2);axes[1].set_axisbelow(True)
fig.savefig(OUT/'timing-123.png');fig.savefig(OUT/'timing-123.pdf');plt.close(fig)
fig,axes=plt.subplots(2,3,figsize=(10,5.6),layout='constrained')
for n,color in zip([1,2,3],['#0072B2','#D55E00','#009E73']):
 q,_=runs[n];x=(q.s-q.s.iloc[0])*1000
 for row,prefix,factor,unit in [(0,'rms',1000,'mm'),(1,'emit',1e6,'mm mrad')]:
  for col,coord in enumerate(['x','y','s']):
   ax=axes[row,col];ax.plot(x,q[f'{prefix}_{coord}']*factor,color=color,label=f'{n} GPU'+('s' if n>1 else ''),ls=['-','--',':'][n-1]);ax.set(xlabel='s − s₀ [mm]',ylabel=f'{prefix} '+('z' if coord=='s' else coord)+f' [{unit}]');ax.set_ylim(0,max(line.get_ydata().max() for line in ax.lines)*1.08);ax.grid(alpha=.2);ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useOffset=False)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=3);fig.savefig(OUT/'rms-emittance-123.png');fig.savefig(OUT/'rms-emittance-123.pdf');plt.close(fig)
print(s.to_string(index=False));print(pd.DataFrame(audits).to_string(index=False));print(p.pivot(index='phase',columns='gpus',values='ms_per_physical_solve').to_string())
# Same-allocation three-GPU 100/1000-step calibration, independent of later density changes.
cal=[]
for steps in [100,1000]:
 d=RAW.parent/'calibration'/f'calibrate3-{steps}';meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0 and meta['binary_sha256']==EXE
 endpoint(d/'case.h5',steps)
 log=(d/'case.out').read_text();timer=lambda name,key:float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
 cal.append(dict(gpus=3,steps=steps,main_s=timer('mainTimer','Wall tot'),orbit_s=timer('OrbThreader','Wall max'),main_minus_orbit_s=timer('mainTimer','Wall tot')-timer('OrbThreader','Wall max'),steady_sc_s=timer('2D5 Solve','Wall max'),process_wall_s=meta['wall_seconds']))
pd.DataFrame(cal).to_csv(OUT/'calibration3.csv',index=False)
step_seconds=(cal[1]['main_minus_orbit_s']-cal[0]['main_minus_orbit_s'])/900
estimate=dict(gpus=3,steps_per_turn=393240,dt_s=3e-12,seconds_per_complete_step=step_seconds,estimated_hours_per_turn=step_seconds*393240/3600,required_speedup_for_one_hour=step_seconds*393240/3600,calibration_job='355045',method='Difference of unprofiled main-minus-OrbitThreader time, 1000 vs100 steps, /900; one allocation, no repeat uncertainty measured')
(OUT/'turn-estimate.json').write_text(json.dumps(estimate,indent=2)+'\n');print('CALIBRATION',cal,estimate)
