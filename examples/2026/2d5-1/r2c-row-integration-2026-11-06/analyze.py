"""Compare frozen/public-plan and integrated/row-executor DBA pilots."""
from pathlib import Path
import os,re,io,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-r2c-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-r2c-cache')
import pandas as pd,numpy as np,h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;DATA=ROOT/'provenance'
def stat(path):
 text=path.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',text,re.S)]
 lines=[x.strip() for x in re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1].splitlines() if x.strip() and not x.lstrip().startswith('!')][len(re.findall(r'&parameter\b',text)):]
 return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
def endpoint(path):
 if not path.exists():
  locations=json.loads((ROOT/'snapshot-locations.json').read_text())
  external=Path(os.environ.get('OPALX_SNAPSHOT_ROOT',str(Path(locations[path.parent.name]['local']).parent.parent)))/path.parent.name/path.name
  if not external.exists():
   raise FileNotFoundError(f"External particle snapshot required: {external}; set OPALX_SNAPSHOT_ROOT. Published plots/CSVs need no snapshots.")
  assert __import__('hashlib').sha256(external.read_bytes()).hexdigest()==locations[path.parent.name]['sha256']
  path=external
 with h5py.File(path) as f:
  assert len(f)==1;g=f[next(iter(f))];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(100000))
  a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(ids)]
  assert np.isfinite(a).all();assert abs(a[:,-1].sum()/5.602212333965894e-9-1)<1e-12
  assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-22
  assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99
  return a
runs={};timers=[];summary=[];audit=[]
for d in sorted(DATA.glob('*-*-*')):
 if not (d/'run.json').exists():continue
 backend,n,version=d.name.split('-');n=int(n);meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0
 assert 'PIPEMODE="OPEN"' in (d/'case.in').read_text()
 log=(d/'case.out').read_text();values={k:float(v) for k,v in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Wall max =\s*([\d.eE+-]+)',log)}
 counts={k:int(v) for k,v in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Count =\s*(\d+)',log)}
 assert counts['2D5 Solve']==99 and counts['2D5 Poisson']==100 and counts['2D5 Line density']==100
 assert values['2D5 Line density']>0
 for name,v in values.items():timers.append(dict(backend=backend,ranks=n,version=version,timer=name,seconds=v,count=counts[name]))
 def timer(name,key):return float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
 summary.append(dict(backend=backend,ranks=n,version=version,steady_ms=1000*values['2D5 Solve']/99,poisson_ms=10*values['2D5 Poisson'],line_density_ms=10*values['2D5 Line density'],initialize_s=values['2D5 Initialize'],warmup_s=values['2D5 Warmup'],first_solve_s=values['2D5 First Solve'],main_minus_orbit_s=timer('mainTimer','Wall tot')-timer('OrbThreader','Wall max'),wall_s=meta['wall_seconds'],exe_sha256=meta['binary_sha256']))
 s=stat(d/'case.stat');assert len(s)==10 and (s.numParticles==100000).all();runs[(backend,n,version)]=(s,endpoint(d/'case.h5'))
refstat,ref= runs[('cpu',1,'before')]
for key,(s,a) in runs.items():
 b,n,v=key;base_s,base=runs[(b,n,'before')]
 columns=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s']
 relative={c:float(abs(s[c]-base_s[c]).max()/max(abs(base_s[c]).max(),1e-30)) for c in columns}
 cross=max(float(abs(s[c]-refstat[c]).max()/max(abs(refstat[c]).max(),1e-30)) for c in columns)
 e=dict(backend=b,ranks=n,version=v,max_stat_relative=max(relative.values()),max_position_difference_m=float(np.linalg.norm(a[:,:3]-base[:,:3],axis=1).max()),max_momentum_difference_betagamma=float(np.linalg.norm(a[:,3:6]-base[:,3:6],axis=1).max()),cross_cpu1_stat_relative=cross,cross_cpu1_position_m=float(np.linalg.norm(a[:,:3]-ref[:,:3],axis=1).max()),cross_cpu1_momentum=float(np.linalg.norm(a[:,3:6]-ref[:,3:6],axis=1).max()),particles=len(a),charge_C=a[:,-1].sum(),**{f'{c}_relative':v for c,v in relative.items()})
 assert e['max_position_difference_m']<1e-8 and e['max_momentum_difference_betagamma']<1e-9 and e['max_stat_relative']<1e-8,e
 audit.append(e)
pd.DataFrame(summary).to_csv(ROOT/'summary.csv',index=False);pd.DataFrame(timers).to_csv(ROOT/'timers.csv',index=False);pd.DataFrame(audit).to_csv(ROOT/'physics-audit.csv',index=False)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':240})
fig,axes=plt.subplots(2,3,figsize=(11,6),layout='constrained')
for backend,n,color,name in [('cpu',1,'#0072B2','CPU'),('gpu',1,'#D55E00','1 A100'),('gpu',2,'#009E73','2 A100s')]:
 for version,style in [('before','--'),('rows','-')]:
  if (backend,n,version) not in runs:continue
  s,_=runs[(backend,n,version)];x=1000*(s.s-refstat.s.iloc[0])
  for row,quantity,unit in [(0,'rms','mm'),(1,'emit','mm mrad')]:
   for col,direction in enumerate(['x','y','s']):
    axes[row,col].plot(x,s[f'{quantity}_{direction}']*(1e3 if row==0 else 1e6),style,color=color,lw=1.5,label=f'{name}: '+('previous' if version=='before' else 'R2C rows'))
    axes[row,col].set(xlabel='s − s₀ [mm]',ylabel=f'{quantity} '+('z' if direction=='s' else direction)+f' [{unit}]');axes[row,col].grid(alpha=.2);axes[row,col].ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useOffset=False);axes[row,col].set_ylim(0,max(line.get_ydata().max() for line in axes[row,col].lines)*1.08)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=3,fontsize=9)
fig.savefig(ROOT/'rms-emittance.png');fig.savefig(ROOT/'rms-emittance.pdf');plt.close(fig)
s=pd.DataFrame(summary);cases=[('cpu',1),('cpu',2),('gpu',1),('gpu',2)];cases=[k for k in cases if ((s.backend==k[0])&(s.ranks==k[1])).any()]
fig,axes=plt.subplots(1,2,figsize=(9,3.8),layout='constrained');x=np.arange(len(cases))
for ax,column,title in zip(axes,['steady_ms','poisson_ms'],['Space charge: steady 99 solves','Transverse Poisson: 100 solves']):
 for version,offset,color,label in [('before',-.18,'#888888','Previous'),('rows',.18,'#0072B2','R2C rows')]:
  y=[s[(s.backend==b)&(s.ranks==n)&(s.version==version)][column].iloc[0] for b,n in cases]
  bars=ax.bar(x+offset,y,width=.34,color=color,label=label)
  ax.bar_label(bars,fmt='%.1f',fontsize=8,padding=3)
 ax.set(xticks=x,xticklabels=[f'{n} CPU rank'+('s' if n>1 else '') if b=='cpu' else f'{n} A100'+('s' if n>1 else '') for b,n in cases],ylabel='Time per call [ms]',title=title);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.set_ylim(0,ax.get_ylim()[1]*1.15)
axes[0].legend();fig.savefig(ROOT/'timing-comparison.png');fig.savefig(ROOT/'timing-comparison.pdf');plt.close(fig)
print(s.to_string(index=False));print(pd.DataFrame(audit).to_string(index=False))
