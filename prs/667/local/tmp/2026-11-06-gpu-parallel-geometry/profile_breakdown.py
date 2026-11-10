"""Summarize existing one-A100 CUDA trace without moving raw trace databases."""
from pathlib import Path
import sqlite3,json,csv,collections
s=Path(__file__).resolve().parent;d=s/'gpu-1-after-profile';c=sqlite3.connect(d/'trace-rank0.sqlite')
assert c.execute('pragma quick_check').fetchone()[0]=='ok'
g=json.loads((d/'geometry-kernels.json').read_text())[0]['kernels'];geom={k['name']:label for k,label in zip(g,['Segment geometry','Prefix / hierarchy','Particle projection'])}
rows=c.execute('select k.start,k.end,s.value from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName order by k.start').fetchall()
starts=[a for a,b,name in rows if name==g[0]['name']];assert len(starts)==100
lo=starts[1];hi=max(b for a,b,name in rows);duration=hi-lo;window=[(a,b,name) for a,b,name in rows if a>=lo and b<=hi]
def union(pairs):
 pairs=sorted((int(a),int(b)) for a,b in pairs if b>a)
 if not pairs:return 0
 a,b=pairs[0];total=0
 for x,y in pairs[1:]:
  if x>b:total+=b-a;a,b=x,y
  else:b=max(b,y)
 return total+b-a

def category(name):
 if name in geom:return geom[name]
 if 'SliceDensitySumFunctor' in name:return 'Line density'
 if 'CoordinateSystemTrafo' in name:return 'Coordinate transforms'
 if 'DistributionMoments' in name:return 'Beam moments'
 if 'FFT2D5Poisson' in name:return 'Poisson grid kernels'
 if 'Kokkos' not in name and 'fft' in name.lower():return 'FFT arithmetic'
 return 'Other'
groups=collections.defaultdict(lambda:[0,0]);names=collections.defaultdict(lambda:[0,0])
for a,b,name in window:
 for dic,key in [(groups,category(name)),(names,name)]:dic[key][0]+=1;dic[key][1]+=b-a
copies=[]
for table in ['CUPTI_ACTIVITY_KIND_MEMCPY','CUPTI_ACTIVITY_KIND_MEMSET']:
 copies.extend((max(lo,a),min(hi,b)) for a,b in c.execute(f'select start,end from {table} where end>? and start<?',(lo,hi)))
kernel_ns=union((a,b) for a,b,name in window);active_ns=union([(a,b) for a,b,name in window]+copies)
runtime=c.execute('select a.start,a.end,s.value from CUPTI_ACTIVITY_KIND_RUNTIME a join StringIds s on s.id=a.nameId where a.start>=? and a.end<=?',(lo,hi)).fetchall();apis=collections.defaultdict(lambda:[0,0])
for a,b,name in runtime:apis[name][0]+=1;apis[name][1]+=b-a
summary=dict(steps=99,window_start_ns=lo,window_end_ns=hi,window_s=duration/1e9,profiled_window_ms_per_step=duration/1e6/99,kernel_count=len(window),kernel_count_per_step=len(window)/99,kernel_busy_percent=100*kernel_ns/duration,copy_memset_only_percent=100*(active_ns-kernel_ns)/duration,no_device_activity_percent=100*(duration-active_ns)/duration,kernel_execution_ms_per_step=kernel_ns/1e6/99,synchronization_calls=sum(v[0] for k,v in apis.items() if any(x in k for x in ['cudaDeviceSynchronize','cudaStreamSynchronize','cuStreamSynchronize','cuCtxSynchronize'])),scope='Second segment-build kernel start through last GPU kernel; first physical solve and OrbitThreader excluded. CUDA API durations overlap GPU work; percentages measure temporal device activity, not SM occupancy.')
(d/'runtime-breakdown.json').write_text(json.dumps(summary,indent=2)+'\n')
for filename,data,keyname in [('kernel-groups.csv',groups,'category'),('kernel-names.csv',names,'name'),('cuda-api.csv',apis,'name')]:
 with (d/filename).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=[keyname,'calls','total_ms','ms_per_step']);w.writeheader()
  for key,(count,total) in sorted(data.items(),key=lambda z:z[1][1],reverse=True):w.writerow({keyname:key,'calls':count,'total_ms':total/1e6,'ms_per_step':total/1e6/99})
print(json.dumps(summary,indent=2));print('KERNEL GROUPS',dict(groups));print('TOP KERNELS',sorted(names.items(),key=lambda x:x[1][1],reverse=True)[:15])
