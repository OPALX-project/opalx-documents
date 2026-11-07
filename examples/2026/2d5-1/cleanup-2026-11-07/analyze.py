"""FFT2D5 cleanup: matched one/two-rank before/after pilot audit."""
from pathlib import Path
import os,re,json,io
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-geometry-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-geometry-cache')
import numpy as np,pandas as pd,h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
RAW=Path(os.environ.get('OPALX_GEOMETRY_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-07-fft2d5-cleanup'))
def stat(p):
 t=p.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',t,re.S)];lines=[x.strip() for x in re.split(r'&data\b.*?&end',t,maxsplit=1,flags=re.S)[1].splitlines() if x.strip() and not x.lstrip().startswith('!')][len(re.findall(r'&parameter\b',t)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
def endpoint(p):
 with h5py.File(p) as f:
  for g in f.values():
   assert np.array_equal(np.sort(g['id'][:]),np.arange(100000))
   assert abs(g['q'][:].sum()/5.602212333965894e-9-1)<1e-12
  g=max(f.values(),key=lambda a:float(np.asarray(a.attrs['TIME']).flat[0]));assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-100*3e-12)<1e-21
  assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99
  a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(g['id'][:])];assert np.isfinite(a).all();return a
rows=[];audits=[]
for ranks in [1,2]:
 for threads in [1]:
  pair={}
  for mode in ['before','after']:
   d=RAW/f'cpu-{ranks}-{mode}'
   if not (d/'run.json').exists():continue
   meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0
   log=(d/'case.out').read_text()
   def t(name,key='Wall max'):return float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
   rows.append(dict(ranks=ranks,threads=threads,mode=mode,geometry_ms=10*t('2D5 Geometry'),steady_sc_ms=1000*t('2D5 Solve')/99,main_minus_orbit_s=t('mainTimer','Wall tot')-t('OrbThreader'),process_s=meta['wall_seconds'],binary_sha256=meta['binary_sha256']))
   q=stat(d/'case.stat');assert (q.numParticles==100000).all();pair[mode]=(q,endpoint(d/'case.h5'))
  if len(pair)!=2:continue
  a,x=pair['after'];b,y=pair['before'];cols=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s'];rel={c:float(abs(a[c]-b[c]).max()/abs(b[c]).max()) for c in cols}
  e=dict(ranks=ranks,threads=threads,all_particles_exact=bool(np.array_equal(x,y)),max_position_m=float(np.linalg.norm(x[:,:3]-y[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(x[:,3:6]-y[:,3:6],axis=1).max()),max_stat_relative=max(rel.values()),**rel)
  assert e['max_stat_relative']<1e-10 and e['max_position_m']<1e-9 and e['max_momentum']<1e-10,e
  audits.append(e)
s=pd.DataFrame(rows);s.to_csv(OUT/'timings.csv',index=False);pd.DataFrame(audits).to_csv(OUT/'physics-audit.csv',index=False)
plt.rcParams.update({'font.family':'serif','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':240})
fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained');labels=[f'{n} rank'+('s' if n>1 else '')+f' / {t} OMP' for n in [1,2] for t in [1]];x=np.arange(len(labels))
for j,mode in enumerate(['before','after']):
 q=s[s['mode']==mode].set_index(['ranks','threads']).reindex([(n,t) for n in [1,2] for t in [1]])
 for ax,col in zip(axes,['geometry_ms','steady_sc_ms']):ax.bar(x+(j-.5)*.36,q[col],.34,label=mode.capitalize())
for ax,title in zip(axes,['Geometry build + particle projections','Steady physical space-charge solves']):
 ax.set(xticks=x,xticklabels=labels,ylabel='Time [ms/call]',title=title);ax.tick_params(axis='x',labelrotation=35);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.set_ylim(bottom=0)
axes[0].legend();fig.savefig(OUT/'timings.png');fig.savefig(OUT/'timings.pdf');plt.close(fig)
print(s.to_string(index=False));print(pd.DataFrame(audits).to_string(index=False))
