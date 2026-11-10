"""Compare fixed-source transverse meshes and the saved fine-grid reference."""
from pathlib import Path
import json,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;TRACKING=ROOT.parent
FIELDS=['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV']
FACTORS=[1e3,1e3,1,1e6,1e6,1e3]
LABELS=['RMS radial (mm)','RMS vertical (mm)','RMS longitudinal (m)','Normalized radial emittance (mm mrad)','Normalized vertical emittance (mm mrad)','Longitudinal emittance (mm eV)']
BLOCKS=[];timings=[];selections=[]
for n in [32,64,128]:
 d=TRACKING/f'bend-10m-100steps-{n}x{n}x512-n100000-same-exe';m=json.loads((d/'run/manifest.json').read_text());v=pd.read_csv(d/'series.csv');audit=json.loads((d/'results.json').read_text())
 assert m['completed'] and audit['checks_passed'] and m['mesh']==[n,n,512] and m['source']['source_particles']==100000 and m['omp_threads']==4
 assert m['binary_sha256']=='a2c87276106782554324753c889db203629f1b7f645d35e2f1bd30b00e32fa9e'
 assert v.step.tolist()==list(range(101))
 BLOCKS.append(v.assign(mesh=n,particles=100000,label=f'{n}×{n}×512; 100,000 particles'))
 timings.append(dict(mesh=n,particles=100000,wall_seconds=m['elapsed_seconds'],omp_threads=4))
 selections.append(dict(mesh=n,manifest=str(d/'run/manifest.json'),sha256=hashlib.sha256((d/'run/manifest.json').read_bytes()).hexdigest(),binary_sha256=m['binary_sha256'],source_sha256=m['source']['npz_sha256']))
assert len({s['source_sha256'] for s in selections})==1
d=TRACKING/'bend-10m-100steps-64x64x512-n200000-same-exe'
m=json.loads((d/'run/manifest.json').read_text());v=pd.read_csv(d/'series.csv');audit=json.loads((d/'results.json').read_text())
assert m['completed'] and audit['checks_passed'] and m['mesh']==[64,64,512] and m['source']['source_particles']==200000 and m['omp_threads']==4
assert m['binary_sha256']==selections[0]['binary_sha256'] and v.step.tolist()==list(range(101))
BLOCKS.append(v.assign(mesh=64,particles=200000,label='64×64×512; 200,000 particles'))
timings.append(dict(mesh=64,particles=200000,wall_seconds=m['elapsed_seconds'],omp_threads=4))
selections.append(dict(mesh=64,particles=200000,manifest=str(d/'run/manifest.json'),sha256=hashlib.sha256((d/'run/manifest.json').read_bytes()).hexdigest(),binary_sha256=m['binary_sha256'],source_sha256=m['source']['npz_sha256']))
fine=TRACKING/'bend-10m-100steps-local-original'
v=pd.read_csv(fine/'analysis/series.csv');v=v[(v.code=='Local original')&(v['mode']=='10pC')&(v.steps==100)].sort_values('step');assert len(v)==101
BLOCKS.append(v[['step','s_m','time_s']+FIELDS].assign(mesh=512,particles=1048576,label='512×512×512; 1,048,576 particles'))
m=json.loads((fine/'opalx/runs/bend-10pC-10m-100steps-local-original/manifest.json').read_text());timings.append(dict(mesh=512,particles=1048576,wall_seconds=m['elapsed_s'],omp_threads=m['omp_threads']));assert m['binary_sha256']==selections[0]['binary_sha256'] and m['omp_threads']==4
data=pd.concat(BLOCKS,ignore_index=True);data.to_csv(ROOT/'series.csv',index=False,float_format='%.17g')
runtimes=pd.DataFrame(timings).sort_values(['mesh','particles']).reset_index(drop=True);runtimes['speedup_vs_fine']=runtimes.wall_seconds.iloc[-1]/runtimes.wall_seconds;runtimes.to_csv(ROOT/'runtimes.csv',index=False,float_format='%.17g')
ends=data[data.step==100].copy();ends=ends.merge(runtimes,on=['mesh','particles'],validate='one_to_one');ends.to_csv(ROOT/'endpoints.csv',index=False,float_format='%.17g')
ref=BLOCKS[-1].set_index('step');errors=[]
for n,count in [(32,100000),(64,100000),(64,200000),(128,100000)]:
 q=data[(data.mesh==n)&(data.particles==count)].set_index('step')
 for field in FIELDS:
  delta=q[field]-ref[field]
  errors.append(dict(mesh=n,particles=count,field=field,endpoint_percent=100*delta.iloc[-1]/ref[field].iloc[-1],max_abs_difference=float(abs(delta).max()),max_abs_difference_over_reference_peak_percent=100*abs(delta).max()/ref[field].max()))
pd.DataFrame(errors).to_csv(ROOT/'errors.csv',index=False,float_format='%.17g')
pyorbit=pd.read_csv(ROOT/'pyorbit-series.csv')
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
for ext in ['png','pdf']:fig.savefig(ROOT/f'mesh-comparison.{ext}',dpi=300)
fig,ax=plt.subplots(figsize=(6.5,3.5),layout='constrained');ax.bar([f'{int(row.mesh)}²\n{int(row.particles):,}' for row in runtimes.itertuples()],runtimes.wall_seconds,color='#0072B2');ax.set(xlabel='Transverse mesh / particle count (Nz=512)',ylabel='Wall time (s)',title='100 steps; identical executable; four OpenMP threads');ax.grid(axis='y',alpha=.2)
for i,r in runtimes.iterrows():ax.text(i,r.wall_seconds+15,f'{r.wall_seconds:.1f} s',ha='center',fontsize=9)
ax.set_ylim(0,runtimes.wall_seconds.max()*1.15)
for ext in ['png','pdf']:fig.savefig(ROOT/f'runtimes.{ext}',dpi=300)
summary=dict(completed=True,selected_runs=selections,fine_reference_manifest=str(fine/'opalx/runs/bend-10pC-10m-100steps-local-original/manifest.json'),comparison_scope='32/64/128 use same100k source and change only transverse grid. Fine512reference has1048576particles. All OPALX cases use same executable/4OMPthreads/1MPIrank. Added64-grid200k source doubles longitudinal strata with same transverse quiet disk rule. Timings are end-to-end, sequential new runs; fine runtime historical.',errors=errors,runtimes=timings)
(ROOT/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(ends[['mesh','particles','wall_seconds']+FIELDS].to_string(index=False));print(pd.DataFrame(errors).to_string(index=False))
