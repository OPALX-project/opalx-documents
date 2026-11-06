"""Matched-source density batching timings; raw particles stay in native runs."""
from pathlib import Path
import os,re,io,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-density-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-density-cache')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
RAW=Path(os.environ.get('OPALX_DENSITY_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-06-longitudinal-batch'))
def stat(p):
 t=p.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',t,re.S)];lines=[x.strip() for x in re.split(r'&data\b.*?&end',t,maxsplit=1,flags=re.S)[1].splitlines() if x.strip() and not x.lstrip().startswith('!')][len(re.findall(r'&parameter\b',t)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
rows=[];phases=[];audits=[];runs={}
for backend,ranks in [('cpu',[1,2]),('gpu',[1,2,3])]:
 for n in ranks:
  for mode in ['before','after']:
   for steps in ([100] if backend=='cpu' else [100,1000]):
    d=RAW/f'{backend}-{n}-{mode}{"" if steps==100 else str(steps)}'
    if not (d/'run.json').exists():continue
    meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0
    log=(d/'case.out').read_text()
    def t(name,key='Wall max'):return float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
    rows.append(dict(backend=backend,ranks=n,mode=mode,steps=steps,density_ms=1000*t('2D5 Line density')/steps,steady_sc_ms=1000*t('2D5 Solve')/(steps-1),main_minus_orbit_s=t('mainTimer','Wall tot')-t('OrbThreader'),binary_sha256=meta['binary_sha256']))
    for name,value in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Wall max =\s*([\d.eE+-]+)',log):phases.append(dict(backend=backend,ranks=n,mode=mode,steps=steps,phase=name,ms_per_step=1000*float(value)/steps))
    q=stat(d/'case.stat');assert (q.numParticles==100000).all();runs[(backend,n,mode,steps)]=q
  for steps in ([100] if backend=='cpu' else [100,1000]):
   if (backend,n,'after',steps) not in runs:continue
   a=runs[(backend,n,'after',steps)];b=runs[(backend,n,'before',steps)]
   cols=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s'];rel={c:float(abs(a[c]-b[c]).max()/abs(b[c]).max()) for c in cols}
   assert len(a)==len(b) and max(rel.values())<1e-8
   audits.append(dict(backend=backend,ranks=n,steps=steps,**rel))
s=pd.DataFrame(rows);s.to_csv(OUT/'timings.csv',index=False);pd.DataFrame(phases).to_csv(OUT/'phases.csv',index=False);pd.DataFrame(audits).to_csv(OUT/'stat-audit.csv',index=False)
cal=[]
for n in [1,2,3]:
 for mode in ['before','after']:
  q=s[(s.backend=='gpu')&(s.ranks==n)&(s['mode']==mode)].set_index('steps')
  if len(q)!=2:continue
  sec=(q.loc[1000,'main_minus_orbit_s']-q.loc[100,'main_minus_orbit_s'])/900
  cal.append(dict(gpus=n,mode=mode,whole_step_ms=sec*1000,estimated_hours_per_turn=sec*393240/3600))
pd.DataFrame(cal).to_csv(OUT/'turn-estimates.csv',index=False)
plt.rcParams.update({'font.family':'serif','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':240})
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
q=s[s.steps==100].copy();q['label']=q.backend.str.upper()+' '+q.ranks.astype(str);labels=q.label.unique();x=np.arange(len(labels))
for j,mode in enumerate(['before','after']):
 z=q[q['mode']==mode].set_index('label').reindex(labels)
 for ax,col in zip(axes,['density_ms','steady_sc_ms']):
  bars=ax.bar(x+(j-.5)*.36,z[col],.34,label=mode.capitalize());ax.bar_label(bars,fmt='%.2f',fontsize=8,padding=12 if j==0 else 2)
for ax,title in zip(axes,['Longitudinal density: all physical calls','Space charge: steady physical calls']):
 ax.set(xticks=x,xticklabels=labels,ylabel='Time [ms/call]',title=title);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.set_ylim(0,ax.get_ylim()[1]*1.12)
axes[0].legend();fig.savefig(OUT/'density-timing.png');fig.savefig(OUT/'density-timing.pdf');plt.close(fig)
print(s.to_string(index=False));print(pd.DataFrame(cal).to_string(index=False));print('Max stat relative differences:',pd.DataFrame(audits).to_string(index=False))

# Matched-source tracking curves; all cases are numerically coincident.
fig,axes=plt.subplots(2,3,figsize=(10,5.7),layout='constrained')
for n,color in zip([1,2,3],['#0072B2','#D55E00','#009E73']):
 for mode,ls in [('before','-'),('after','--')]:
  q=runs[('gpu',n,mode,100)];x=(q.s-q.s.iloc[0])*1000
  for row,prefix,factor,unit in [(0,'rms',1000,'mm'),(1,'emit',1e6,'mm mrad')]:
   for col,coord in enumerate(['x','y','s']):
    ax=axes[row,col];ax.plot(x,q[f'{prefix}_{coord}']*factor,color=color,ls=ls,lw=1.2,label=f'{n} A100: {mode}')
    ax.set(xlabel='s − s₀ [mm]',ylabel=f'{prefix} '+('z' if coord=='s' else coord)+f' [{unit}]');ax.grid(alpha=.2);ax.set_ylim(0,1.08*max(line.get_ydata().max() for line in ax.lines))
    ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useOffset=False)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=3,fontsize=8)
fig.savefig(OUT/'rms-emittance.png');fig.savefig(OUT/'rms-emittance.pdf');plt.close(fig)
