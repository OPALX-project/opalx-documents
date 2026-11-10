"""Reproducible 100-step MPI-z pilot audit, against the preserved serial executables.
Run using ~/.venv-h6/bin/python; reads CPU and downloaded GPU case.{h5,stat,out}.
All rank comparisons use sorted persistent particle IDs, never local array order.
"""
from pathlib import Path
import re,io,json,hashlib,os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/opalx-mpi-z-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/opalx-mpi-z-cache")
import numpy as np,pandas as pd,h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(os.environ.get("OPALX_MPI_Z_ROOT", str(Path(__file__).resolve().parent)))
OUT=Path('/Users/adelmann/git/opalx-documents/examples/2026/2d5-1/fft2d5-mpi-z-2026-11-06')
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.labelsize':11,'axes.titlesize':11,'figure.dpi':160,'savefig.dpi':300,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,'pdf.fonttype':42})
def stat(path):
 text=path.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',text,re.S)];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
def endpoint(path):
 with h5py.File(path) as h:
  assert len(h)==1;g=h[next(iter(h))];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(100000));a=np.column_stack([g[k][:] for k in ['x','y','z','px','py','pz','q']])[np.argsort(ids)];assert np.isfinite(a).all();assert abs(a[:,-1].sum()/5.602212333965894e-9-1)<1e-12;assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-22;assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99;return a
fields=['rms_x','rms_y','rms_s','emit_x','emit_y','emit_s']
series=[];timing=[];errors=[];particle=[]
base=stat(ROOT/'preserved/case.stat'); ref=endpoint(ROOT/'preserved/case.h5')
series.append(base.assign(code='CPU preserved',ranks=1,repeat=0))
for prefix,code in [('final-cpu-ranks-','CPU'),('gpu-ranks-','GPU')]:
 for path in sorted(ROOT.glob(prefix+'*-repeat-*')):
  if not (path/'run.json').exists():continue
  record=json.loads((path/'run.json').read_text());assert record['returncode']==0
  rank=int(path.name.split('ranks-')[1].split('-')[0]);repeat=int(path.name.split('repeat-')[1]);data=stat(path/'case.stat');assert len(data)==10
  assert np.allclose(data.t,base.t,rtol=0,atol=1e-14)
  series.append(data.assign(code=code,ranks=rank,repeat=repeat))
  a=endpoint(path/'case.h5');delta=a-ref
  particle.append(dict(code=code,ranks=rank,repeat=repeat,particles=len(a),charge_C=a[:,-1].sum(),max_position_difference_m=np.linalg.norm(delta[:,:3],axis=1).max(),max_momentum_difference_betagamma=np.linalg.norm(delta[:,3:6],axis=1).max()))
  log=(path/'case.out').read_text()
  def timer(name,key):
   return float(re.search(r'Timings(?:\{0\})?> '+re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
  main=timer('mainTimer','Wall tot');orbit=timer('OrbThreader','Wall max')
  timing.append(dict(code=code,ranks=rank,repeat=repeat,wall_s=record['wall_seconds'],main_s=main,orbit_s=orbit,tracking_s=main-orbit,binary_sha256=record['binary_sha256']))
  for f in fields:
   errors.append(dict(code=code,ranks=rank,repeat=repeat,field=f,max_relative_difference=float(abs(data[f]-base[f]).max()/abs(base[f]).max())))
series=pd.concat(series,ignore_index=True);timing=pd.DataFrame(timing);errors=pd.DataFrame(errors);particle=pd.DataFrame(particle)
series.to_csv(OUT/'series.csv',index=False);timing.to_csv(OUT/'timings.csv',index=False);errors.to_csv(OUT/'comparison.csv',index=False);particle.to_csv(OUT/'particle-audit.csv',index=False)
summary=timing.groupby(['code','ranks']).agg(tracking_s=('tracking_s','mean'),tracking_min_s=('tracking_s','min'),tracking_max_s=('tracking_s','max'),wall_s=('wall_s','mean'),orbit_s=('orbit_s','mean'),repetitions=('tracking_s','count')).reset_index()
summary['speedup']=summary.apply(lambda r:float(summary.loc[(summary.code==r.code)&(summary.ranks==1),'tracking_s'].iloc[0]/r.tracking_s),axis=1);summary.to_csv(OUT/'summary.csv',index=False)
fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
for ax,code,color in zip(axes,['CPU','GPU'],['#0072B2','#D55E00']):
 d=summary[summary.code==code]
 if len(d):
  ax.bar(d.ranks.astype(str),d.tracking_s,color=color,width=.6)
  for j,(_,r) in enumerate(d.iterrows()):ax.text(j,r.tracking_s*1.025,f'{r.tracking_s:.2f} s\n{r.speedup:.2f}×',ha='center',va='bottom',fontsize=9)
  ax.set_ylim(0,float(d.tracking_s.max())*1.3)
 ax.set_title('CPU: one thread per MPI rank' if code=='CPU' else 'A100: one GPU per MPI rank');ax.set_xlabel('MPI ranks');ax.set_ylabel('100-step tracking time [s]');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.suptitle('FFT2D5 z decomposition · 64×64×512 · 100,000 particles\nTracking time excludes reference-orbit construction',fontsize=11)
fig.savefig(OUT/'timing.png');fig.savefig(OUT/'timing.pdf');plt.close(fig)
colors={('CPU',1):'#0072B2',('CPU',2):'#56B4E9',('CPU',4):'#009E73',('GPU',1):'#D55E00',('GPU',2):'#CC79A7',('GPU',4):'#E69F00'}
fig,axes=plt.subplots(2,3,figsize=(11,6),layout='constrained')
for ax,f,label in zip(axes.flat,fields,[r'$\sigma_x$ [mm]',r'$\sigma_y$ [mm]',r'$\sigma_s$ [mm]',r'$\epsilon_{n,x}$ [mm mrad]',r'$\epsilon_{n,y}$ [mm mrad]',r'$\epsilon_{n,s}$ [mm mrad]']):
 scale=1000 if f.startswith('rms') else 1e6
 ax.plot(base.s,base[f]*scale,'k-',lw=2.4,label='Preserved serial CPU')
 for (code,n),d in series[(series.code.isin(['CPU','GPU']))&(series.repeat==1)].groupby(['code','ranks']):
  ax.plot(d.s,d[f]*scale,color=colors[(code,n)],ls='--' if code=='CPU' else ':',lw=1.3,marker='o' if code=='CPU' else 'x',ms=3,markevery=2,label=f'{code}, {n} rank'+('s' if n>1 else ''))
 ax.set_ylim(0,float(base[f].max())*scale*1.1);ax.set_xlabel('$s$ [m]');ax.set_ylabel(label);ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,4),useOffset=False);ax.grid(alpha=.2)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=4,fontsize=9)
fig.suptitle('100-step DBA pilot: rms sizes and normalized emittances\nGlobal Cartesian statistics of the full coasting ring',fontsize=12)
fig.savefig(OUT/'rms-emittance.png');fig.savefig(OUT/'rms-emittance.pdf');plt.close(fig)
print(summary.to_string(index=False));print('Max relative rms/emittance discrepancy',errors.max_relative_difference.max());print(particle.to_string(index=False))

fig,axes=plt.subplots(2,3,figsize=(11,6),layout='constrained')
for ax,f in zip(axes.flat,fields):
 ax.axhline(0,color='k',lw=.8)
 bound=0.
 for (code,n),d in series[(series.code.isin(['CPU','GPU']))&(series.repeat==1)].groupby(['code','ranks']):
  residual=100*(d[f].to_numpy()-base[f].to_numpy())/abs(base[f]).max()
  bound=max(bound,float(abs(residual).max()))
  ax.plot(d.s,residual,color=colors[(code,n)],ls='--' if code=='CPU' else ':',lw=1.3,marker='o' if code=='CPU' else 'x',ms=3,label=f'{code}, {n} rank'+('s' if n>1 else ''))
 ax.set_ylim(-max(bound*1.2,1.e-13),max(bound*1.2,1.e-13));ax.set_xlabel('$s$ [m]');ax.set_ylabel(f'{f}: difference [%]');ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useOffset=False);ax.grid(alpha=.2)
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=9)
fig.suptitle('Difference from preserved serial CPU result\nNormalized by the peak value of each statistic',fontsize=12)
fig.savefig(OUT/'differences.png');fig.savefig(OUT/'differences.pdf');plt.close(fig)

if (ROOT/'gpu-preserved/case.h5').exists():
 gpu_reference=endpoint(ROOT/'gpu-preserved/case.h5')
 gpu_stat=stat(ROOT/'gpu-preserved/case.stat')
 checks=[]
 for path in sorted(ROOT.glob('gpu-ranks-*-repeat-*')):
  if not (path/'run.json').exists():continue
  data=stat(path/'case.stat');a=endpoint(path/'case.h5')
  checks.append(dict(case=path.name,max_position_difference_m=float(np.linalg.norm(a[:,:3]-gpu_reference[:,:3],axis=1).max()),max_momentum_difference_betagamma=float(np.linalg.norm(a[:,3:6]-gpu_reference[:,3:6],axis=1).max()),max_stat_relative_difference=max(float(abs(data[f]-gpu_stat[f]).max()/abs(gpu_stat[f]).max()) for f in fields)))
 pd.DataFrame(checks).to_csv(OUT/'gpu-vs-preserved.csv',index=False)
 print('GPU vs preserved A100:');print(pd.DataFrame(checks).to_string(index=False))
