"""Audit physical equivalence and synchronized FFT2D5 timers; warmup/first/steady separate."""
from pathlib import Path
import re,io,json,os,hashlib
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-mpi-z-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-mpi-z-cache')
import pandas as pd,numpy as np,h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=Path('/Users/adelmann/git/opalx-documents/examples/2026/2d5-1/fft2d5-timing-2026-11-06');OUT.mkdir(parents=True,exist_ok=True)
OLD=ROOT.parent/'2026-11-06-fft2d5-mpi-z'
def stat(path):
 s=path.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',s,re.S)];data=re.split(r'&data\b.*?&end',s,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')][len(re.findall(r'&parameter\b',s)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
def endpoint(path):
 with h5py.File(path) as f:
  assert len(f)==1;g=f[next(iter(f))];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(100000));a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(ids)];assert np.isfinite(a).all();assert abs(a[:,-1].sum()/5.602212333965894e-9-1)<1e-12;assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-22;assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99;return a
ref=endpoint(OLD/'preserved/case.h5');refstat=stat(OLD/'preserved/case.stat');summary=[];phases=[];errors=[]
for code,pattern in [('CPU','cpu-ranks-*'),('GPU','gpu-*')]:
 for d in sorted(ROOT.glob(pattern)):
  if not d.is_dir() or not (d/'run.json').exists():continue
  n=int(d.name.split('-')[-1]);m=json.loads((d/'run.json').read_text());assert m['returncode']==0
  log=(d/'case.out').read_text();raw=(d/'timing.dat').read_text();values={};counts={}
  for name,value in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Wall max =\s*([\d.eE+-]+)',log):values[name]=float(value)
  for name,value in re.findall(r'Timings(?:\{0\})?> (2D5 [^\n]*?)\.+ Count =\s*(\d+)',log):counts[name]=int(value)
  assert counts['2D5 Initialize']==counts['2D5 Warmup']==counts['2D5 First Solve']==1
  assert counts['2D5 Solve']==99 and counts['2D5 Poisson']==100
  assert counts['2D5 FFT Rho']==counts['2D5 FFT Back']==100*(512//n//64)
  for name,v in values.items():
   assert name in raw
   phases.append(dict(code=code,ranks=n,timer=name,wall_max_s=v,count=counts[name]))
  def full_timer(name,key):return float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
  summary.append(dict(code=code,ranks=n,initialize_s=values['2D5 Initialize'],warmup_s=values['2D5 Warmup'],first_solve_s=values['2D5 First Solve'],steady_solve_99_s=values['2D5 Solve'],steady_solve_ms=1000*values['2D5 Solve']/99,poisson_100_s=values['2D5 Poisson'],main_minus_orbit_s=full_timer('mainTimer','Wall tot')-full_timer('OrbThreader','Wall max'),process_wall_s=m['wall_seconds'],binary_sha256=m['binary_sha256']))
  a=endpoint(d/'case.h5');s=stat(d/'case.stat');assert len(s)==10
  e=max(float(abs(s[c]-refstat[c]).max()/abs(refstat[c]).max()) for c in s if c.startswith(('rms_','emit_')))
  errors.append(dict(code=code,ranks=n,max_stat_relative_difference=e,max_position_difference_m=float(np.linalg.norm(a[:,:3]-ref[:,:3],axis=1).max()),max_momentum_difference_betagamma=float(np.linalg.norm(a[:,3:6]-ref[:,3:6],axis=1).max()),particles=len(a),charge_C=a[:,-1].sum()))
summary=pd.DataFrame(summary);phases=pd.DataFrame(phases);errors=pd.DataFrame(errors)
summary.to_csv(OUT/'summary.csv',index=False);phases.to_csv(OUT/'timers.csv',index=False);errors.to_csv(OUT/'physics-audit.csv',index=False)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':300})
fig,axes=plt.subplots(1,2,figsize=(9,3.6),layout='constrained')
for ax,code,color in zip(axes,['CPU','GPU'],['#0072B2','#D55E00']):
 s=summary[summary.code==code];ax.bar(s.ranks.astype(str),s.steady_solve_ms,color=color,width=.6)
 for i,(_,r) in enumerate(s.iterrows()):ax.text(i,r.steady_solve_ms*1.02,f'{r.steady_solve_ms:.2f}',ha='center')
 ax.set_ylim(0,s.steady_solve_ms.max()*1.18);ax.set_xlabel('MPI ranks');ax.set_ylabel('FFT2D5 solve time [ms/call]');ax.set_title('CPU: one thread per rank' if code=='CPU' else 'A100: one GPU per rank');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.suptitle('Direct FFT2D5 timer · 99 calls after the first physical solve\n64×64×512 · 100,000 particles · batch size 64',fontsize=11)
fig.savefig(OUT/'steady-solver.png');fig.savefig(OUT/'steady-solver.pdf');plt.close(fig)
print(summary.to_string(index=False));print(errors.to_string(index=False))
