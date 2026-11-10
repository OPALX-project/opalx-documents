"""Nsight Systems interval accounting. Raw traces and particles remain external."""
from pathlib import Path
import os,sqlite3,json,re
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-profile-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/opalx-profile-cache')
import pandas as pd,numpy as np,h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=Path(__file__).resolve().parent
RAW=Path(os.environ.get('OPALX_PROFILE_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-06-publish-profile'))
SPECS=[('1 GPU',1,0,RAW/'nsys-1/trace-rank0.sqlite'),('2 GPUs, rank 0',2,0,RAW/'native/gpu-2-nsys/trace-rank0.sqlite'),('2 GPUs, rank 1',2,1,RAW/'native/gpu-2-nsys/trace-rank1.sqlite')]
def union(intervals):
 intervals=sorted((int(a),int(b)) for a,b in intervals if b>a)
 if not intervals:return 0
 a,b=intervals[0];total=0
 for x,y in intervals[1:]:
  if x>b:total+=b-a;a,b=x,y
  else:b=max(b,y)
 return total+b-a
def category(name):
 if 'SliceDensitySumFunctor' in name:return 'Slice density reductions'
 if 'preparePathGeometryAndProjections' in name:
  return 'Serial geometry / hierarchy' if '(instance 1)], Kokkos::RangePolicy' in name else 'Particle projection'
 if 'CoordinateSystemTrafo' in name:return 'Coordinate transforms'
 if 'DistributionMoments' in name:return 'Beam moments'
 if 'FFT2D5Poisson' in name:return 'Poisson staging / transposes'
 if 'Kokkos' not in name and 'fft' in name.lower():return 'FFT arithmetic'
 return 'Other'
summary=[];kernel_frames=[];api_frames=[];mpi_frames=[];shapes=[]
for label,n,rank,path in SPECS:
 c=sqlite3.connect(path)
 assert c.execute('pragma quick_check').fetchone()[0]=='ok'
 k=pd.read_sql_query('select k.*,s.value name from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName',c)
 k['category']=k.name.map(category)
 g=k[k.category=='Serial geometry / hierarchy'].sort_values('start');assert len(g)==100,(label,len(g))
 lo=int(g.start.iloc[1]);hi=int(k.end.max());duration=hi-lo
 # Precisely defined device-kernel window, not an unprofiled wall timer.
 q=k[(k.start>=lo)&(k.end<=hi)].copy();q['nanoseconds']=q.end-q.start
 ks=union(zip(q.start,q.end));dev=list(zip(q.start,q.end));copies=[]
 for table in ['CUPTI_ACTIVITY_KIND_MEMCPY','CUPTI_ACTIVITY_KIND_MEMSET']:
  z=pd.read_sql_query(f'select start,end from {table} where end>? and start<?',c,params=[lo,hi]);pairs=[(max(lo,a),min(hi,b)) for a,b in zip(z.start,z.end)];dev+=pairs;copies+=pairs
 all_active=union(dev)
 runtime=pd.read_sql_query('select a.*,s.value name from CUPTI_ACTIVITY_KIND_RUNTIME a join StringIds s on s.id=a.nameId where a.start>=? and a.end<=?',c,params=[lo,hi]);runtime['ns']=runtime.end-runtime.start
 apis=runtime.groupby('name').agg(calls=('name','size'),summed_elapsed_ns=('ns','sum')).reset_index();apis['configuration']=label;api_frames.append(apis)
 syncs=runtime.name.str.contains('cudaDeviceSynchronize|cudaStreamSynchronize|cuStreamSynchronize|cuCtxSynchronize',regex=True)
 row=dict(configuration=label,gpus=n,rank=rank,window_start_ns=lo,window_end_ns=hi,window_seconds=duration/1e9,steps=99,kernels=len(q),synchronization_calls=int(syncs.sum()),kernel_busy_percent=100*ks/duration,copy_memset_only_percent=100*(all_active-ks)/duration,no_device_activity_percent=100*(duration-all_active)/duration,gpu_kernel_ms_per_step=ks/1e6/99)
 # Whole-run counts are comparable to historical 100-step profiling counts.
 row['full_kernel_count']=len(k)
 row['full_density_kernels']=int((k.category=='Slice density reductions').sum())
 summary.append(row)
 group=q.groupby('category').agg(calls=('name','size'),total_ns=('nanoseconds','sum')).reset_index();group['gpu_ms_per_step']=group.total_ns/1e6/99;group['configuration']=label;kernel_frames.append(group)
 for table in ['MPI_COLLECTIVES_EVENTS','MPI_P2P_EVENTS','MPI_START_WAIT_EVENTS','MPI_OTHER_EVENTS']:
  if not c.execute('select 1 from sqlite_master where name=?',(table,)).fetchone():continue
  z=pd.read_sql_query(f'select a.*,s.value name from {table} a left join StringIds s on s.id=a.textId where a.start>=? and a.end<=?',c,params=[lo,hi]);z['ns']=z.end-z.start
  m=z.groupby('name').agg(calls=('name','size'),summed_elapsed_ns=('ns','sum')).reset_index();m['configuration']=label;m['table']=table;mpi_frames.append(m)
 for cat in ['Serial geometry / hierarchy','Slice density reductions','Particle projection']:
  z=q[q.category==cat];size=(z.gridX*z.gridY*z.gridZ);thread=(z.blockX*z.blockY*z.blockZ)
  shapes.append(dict(configuration=label,category=cat,blocks_min=int(size.min()),blocks_max=int(size.max()),threads_per_block_min=int(thread.min()),threads_per_block_max=int(thread.max()),registers_per_thread_max=int(z.registersPerThread.max()),local_bytes_per_thread_max=int(z.localMemoryPerThread.max()),mean_kernel_us=float(z.nanoseconds.mean()/1e3),sm_count=108))
 c.close()
s=pd.DataFrame(summary);kg=pd.concat(kernel_frames,ignore_index=True);api=pd.concat(api_frames,ignore_index=True);mpi=pd.concat(mpi_frames,ignore_index=True);shape=pd.DataFrame(shapes)
for name,d in [('gpu-activity',s),('kernel-groups',kg),('cuda-api',api),('mpi-api',mpi),('launch-shapes',shape)]:d.to_csv(OUT/(name+'.csv'),index=False)
# Independent endpoint audit; snapshots are only in the external native/cache directory.
def endpoint(p):
 with h5py.File(p) as f:
  g=f[next(iter(f))];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(100000));a=np.column_stack([g[n][:] for n in ['x','y','z','px','py','pz','q']])[np.argsort(ids)];assert np.isfinite(a).all();assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-22;return a
baseline=Path('/Users/adelmann/git/opalx/tmp/2026-11-06-r2c-integration')
audits=[]
for n in [1,2]:
 a=endpoint(RAW/f'native/gpu-{n}-nsys/case.h5');b=endpoint(baseline/f'gpu-{n}-rows/case.h5')
 e=dict(gpus=n,max_position_m=float(np.linalg.norm(a[:,:3]-b[:,:3],axis=1).max()),max_momentum=float(np.linalg.norm(a[:,3:6]-b[:,3:6],axis=1).max()),particles=len(a),charge_C=float(a[:,-1].sum()))
 assert e['max_position_m']<1e-9 and e['max_momentum']<1e-10,e
 audits.append(e)
pd.DataFrame(audits).to_csv(OUT/'profile-physics-audit.csv',index=False)
# Incremental unprofiled full-tracker calibration, removing fixed startup and orbit work.
calibration=[]
for steps in [100,1000]:
 d=RAW/'native'/f'calibrate-{steps}'
 log=(d/'case.out').read_text();meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0
 def timer(name,key='Wall max'):
  return float(re.search(re.escape(name)+r'\.+ '+key+r' =\s*([\d.eE+-]+)',log)[1])
 with h5py.File(d/'case.h5') as f:
  # Longer calibration writes multiple snapshots; audit every ID/charge set, then select latest.
  for key in f:
   group=f[key];assert np.array_equal(np.sort(group['id'][:]),np.arange(100000));assert abs(group['q'][:].sum()/5.602212333965894e-9-1)<1e-12
  group=max(f.values(),key=lambda g:float(np.asarray(g.attrs['TIME']).flat[0]))
  assert abs(float(np.asarray(group.attrs['TIME']).flat[0])-steps*3e-12)<1e-21
  assert int(np.asarray(group.attrs['GlobalTrackStep']).flat[0])==steps-1
  for name in ['x','y','z','px','py','pz']:assert np.isfinite(group[name][:]).all()
  snapshot_count=len(f)
 calibration.append(dict(steps=steps,main_s=timer('mainTimer','Wall tot'),orbit_s=timer('OrbThreader'),main_minus_orbit_s=timer('mainTimer','Wall tot')-timer('OrbThreader'),steady_sc_s=timer('2D5 Solve'),steady_sc_ms=timer('2D5 Solve')/(steps-1)*1000,process_wall_s=meta['wall_seconds'],particles=100000,snapshots=snapshot_count))
pd.DataFrame(calibration).to_csv(OUT/'calibration.csv',index=False)
step_seconds=(calibration[1]['main_minus_orbit_s']-calibration[0]['main_minus_orbit_s'])/900
estimate=dict(steps_per_turn=393240,dt_s=3e-12,incremental_seconds_per_step=step_seconds,estimated_hours_per_turn=step_seconds*393240/3600,one_hour_seconds_per_step=3600/393240,required_speedup=step_seconds*393240/3600,method='Difference of unprofiled 1000- and 100-step main-minus-OrbitThreader times / 900; one allocation; no repeat uncertainty measured',job='355043')
(OUT/'turn-estimate.json').write_text(json.dumps(estimate,indent=2)+'\n')
print('CALIBRATION',calibration);print('TURN ESTIMATE',estimate)
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.dpi':240})
fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
ax=axes[0,0];left=np.zeros(len(s));colors=['#0072B2','#E69F00','#CCCCCC']
for col,label,color in zip(['kernel_busy_percent','copy_memset_only_percent','no_device_activity_percent'],['Kernel executing','Copy/memset only','No device activity'],colors):
 ax.barh(s.configuration,s[col],left=left,label=label,color=color);left+=s[col].to_numpy()
ax.set(xlim=(0,100),xlabel='Fraction of profiled device window [%]',title='Device activity: not SM occupancy');ax.legend(fontsize=8,loc='lower left',bbox_to_anchor=(0,1.01),ncol=3);ax.set_title('Device activity: not SM occupancy',pad=32)
z=kg[kg.configuration=='2 GPUs, rank 0'].sort_values('gpu_ms_per_step');ax=axes[0,1];ax.barh(z.category,z.gpu_ms_per_step,color='#0072B2');ax.set(xlabel='GPU kernel time / step [ms]',title='Two GPUs: rank 0');ax.grid(axis='x',alpha=.2)
ax=axes[1,0];a=kg.pivot(index='category',columns='configuration',values='calls').fillna(0);a['total']=a.sum(axis=1);a=a.nlargest(5,'total').drop(columns='total')
y=np.arange(len(a))
for j,label in enumerate(['1 GPU','2 GPUs, rank 0']):ax.barh(y+(j-.5)*.32,a[label]/99,height=.3,label=label,color=['#0072B2','#D55E00'][j])
ax.set(yticks=y,yticklabels=a.index,xlabel='Kernel launches per step',title='Launch count');ax.legend(fontsize=8);ax.grid(axis='x',alpha=.2)
ax=axes[1,1];z=shape[shape.configuration=='2 GPUs, rank 0'];ax.barh(z.category,z.blocks_max,color='#0072B2');ax.axvline(108,color='#333333',ls='--',label='108 SMs');ax.set(xscale='log',xlabel='Blocks per launch (log scale)',title='Blocks exposed to GPU');ax.legend(fontsize=8);ax.grid(axis='x',alpha=.2)
fig.suptitle('Current row-batched FFT2D5 · 100-step pilot · Nsight Systems',fontsize=12);fig.savefig(OUT/'gpu-profile.png');fig.savefig(OUT/'gpu-profile.pdf');plt.close(fig)
print(s.to_string(index=False));print(kg[kg.configuration=='2 GPUs, rank 0'].to_string(index=False));print(shape.to_string(index=False));print(pd.DataFrame(audits).to_string(index=False))

# Complete-step budget from incremental, unprofiled measurements.
sc_increment=(calibration[1]['steady_sc_s']-calibration[0]['steady_sc_s'])/900*1000
step_ms=1000*step_seconds;other_ms=step_ms-sc_increment;budget_ms=1000*3600/393240
fig,ax=plt.subplots(figsize=(9,3),layout='constrained')
ax.barh([0],[sc_increment],color='#0072B2',height=.36,label='Space charge')
ax.barh([0],[other_ms],left=[sc_increment],color='#BBBBBB',height=.36,label='Other tracker work')
ax.text(sc_increment/3,0,f'Space charge: {sc_increment:.2f} ms',ha='center',va='center',color='white')
ax.text(sc_increment+other_ms/2,0,f'Other: {other_ms:.2f} ms',ha='center',va='center')
ax.axvline(budget_ms,color='#D55E00',ls='--');ax.text(budget_ms,.32,f'1 h target: {budget_ms:.2f} ms',ha='center',color='#D55E00')
ax.set(xlim=(0,24),ylim=(-.5,.65),yticks=[],xlabel='Complete tracking time per step [ms]',title='Two A100s · incremental unprofiled 100 / 1,000-step calibration')
ax.secondary_xaxis('top',functions=(lambda ms:ms*393240/3600000,lambda h:h*3600000/393240)).set_xlabel('Projected hours per turn at 3 ps')
ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
fig.savefig(OUT/'one-hour-budget.png');fig.savefig(OUT/'one-hour-budget.pdf');plt.close(fig)
