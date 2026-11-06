"""Combine synchronous Kokkos wall timers with non-overlapping stack leaves."""
from pathlib import Path
import re,json,hashlib
import numpy as np,pandas as pd,h5py
R=Path(__file__).resolve().parent;O=R/'dba-fftw-profile';k=O/'kernel';meta=json.loads((k/'manifest.json').read_text());assert meta['completed'];log=(k/'run.log').read_text();assert 'callback_errors=0 pending=0' in log
main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',log).group(1));kernels=pd.read_csv(k/'kernel-timings.csv');kernels['percent_of_native_wall']=100*kernels.exclusive_s/main;kernels.sort_values('exclusive_s',ascending=False).to_csv(O/'kernel-summary.csv',index=False)
# Parse the sample ASCII tree by indentation. A node's own weight is its
# inclusive count minus immediate children's counts. Each sample is counted once.
text=(O/'sample/cpu-sample.txt').read_text().split('Call graph:\n',1)[1].split('Total number in stack',1)[0];roots=[];stack=[]
for line in text.splitlines():
 m=re.match(r'^([ +!:|]*)(\d+) (.+)$',line)
 if not m:continue
 depth=len(m[1]);node=dict(depth=depth,count=int(m[2]),name=m[3],children=[])
 while stack and stack[-1]['depth']>=depth:stack.pop()
 if stack:stack[-1]['children'].append(node)
 else:roots.append(node)
 stack.append(node)
rows=[]
def visit(node,path,thread):
 path=path+[node['name']];own=node['count']-sum(c['count'] for c in node['children']);assert own>=0,(node['name'],own)
 if own:
  joined='\n'.join(path)
  if 'convertToFrenetSerret' in joined or 'preparePathGeometryAndProjections' in joined:category='Reference-path projection'
  elif any(s in joined for s in ['heffte::stock','heffte::plan_stock','heffte::compute_transform','heffte::internal::','heffte::plan_fftw','fftw_execute','fftw::','fftw_','dft_codelet','rdft_','apply_hc2','apply_rdft']):category='FFTW / heFFTe FFT math/reshapes'
  elif any(s in joined for s in ['FFT2D5Poisson::','FFT2D5Algorithm::solvePoissons','FFT<ippl::RCTransform','CopySliceFieldFunctor','PoissonCouplingFunctor']):category='Other slice-solver / FFT interface'
  elif any(s in joined for s in ['ScatterToGridFunctor','GatherFromGridFunctor']):category='Other deposition / gather'
  elif any(s in joined for s in ['__kmp','pthread_cond_wait','__psynch_cvwait','mach_msg']):category='Runtime / waiting / unclassified'
  else:category='Other tracking / host work'
  rows.append(dict(thread=thread,samples=own,category=category,leaf=node['name']))
 for child in node['children']:visit(child,path,thread)
for root in roots:
 if 'Thread_' in root['name']:visit(root,[],root['name'])
samples=pd.DataFrame(rows);samples.to_csv(O/'stack-leaves.csv',index=False);mainthread=next(r['name'] for r in roots if 'com.apple.main-thread' in r['name']);mt=samples[samples.thread==mainthread];assert mt.samples.sum()==next(r['count'] for r in roots if r['name']==mainthread)
s=mt.groupby('category').samples.sum().sort_values(ascending=False).rename_axis('category').reset_index();s['percent']=100*s.samples/mt.samples.sum();s.to_csv(O/'main-thread-sample-summary.csv',index=False)
# Exact blocking callback times; host FFT arithmetic is outside callbacks.
get=lambda name:float(kernels.loc[kernels.name==name,'exclusive_s'].sum())
groups=dict(particle_projection=get('for:FFT2D5::prepareParticleProjections'),geometry_preparation=get('for:FFT2D5::preparePathGeometry'),deposition_including_projection=get('for:Solve2d5::scatterToGrid::scatter'),gather_including_projection=get('for:Solver2d5::GatherFromGrid'),fft_pack_unpack=get('for:FFT_toTemp')+get('for:FFT_fromTemp'))
groups['other_kokkos_callbacks']=float(kernels.exclusive_s.sum())-sum(groups.values());groups['outside_kokkos_callbacks']=main-float(kernels.exclusive_s.sum());assert groups['outside_kokkos_callbacks']>=0
j=dict(binary_sha256=meta['binary_sha256'],native_wall_s=main,measured_wall_groups_s=groups,callback_sum_s=float(kernels.exclusive_s.sum()),kernel_profile_wall_s=meta['elapsed_seconds'],unprofiled_baseline_wall_s=json.loads((R/'dba-fftw-release/optimized-1/manifest.json').read_text())['elapsed_seconds'],runtime_change_vs_baseline_percent=100*(meta['elapsed_seconds']/json.loads((R/'dba-fftw-release/optimized-1/manifest.json').read_text())['elapsed_seconds']-1),main_thread_samples=int(mt.samples.sum()),sample_categories=s.to_dict(orient='records'),note='Kokkos callbacks are synchronous OpenMP blocking wall durations, exclusive of nested callbacks. CPU-stack percentages classify nonoverlapping main-thread sampled leaves; workers and MPI progress threads are excluded from wall estimates. FFTW host work is outside Kokkos callbacks. Separate runs/methods should not be added together.')
(O/'summary.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2));print('Top kernels\n',kernels.nlargest(10,'exclusive_s')[['name','count','exclusive_s','percent_of_native_wall']].to_string(index=False))

# Re-run endpoint audits against the unprofiled, identical-input SC pilot.
def endpoint(path):
 with h5py.File(path) as f:
  key=max(f,key=lambda x:int(x.split('#')[-1]));g=f[key];i=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][i],np.arange(100000));assert abs(float(g.attrs['TIME'][0])-3e-10)<1e-22;assert int(g.attrs['GlobalTrackStep'][0])==99
  r=np.column_stack([g[c][:][i] for c in 'xyz']);p=np.column_stack([g[c][:][i] for c in ['px','py','pz']]);assert np.isfinite(r).all() and np.isfinite(p).all();q=float(g['q'][:].sum());assert abs(q/5.602212333965894e-9-1)<1e-12
  ez=g.attrs['RefPartP']/np.linalg.norm(g.attrs['RefPartP']);ex=np.array([ez[2],0.,-ez[0]]);ey=np.array([0.,1.,0.]);rot=np.array([ex,ey,ez]);return r@rot+g.attrs['RefPartR'],p@rot
baseline=endpoint(R/'dba-fftw-release/optimized-1/case.h5');audits=[]
for mode in ['kernel','sample']:
 d=O/mode;m=json.loads((d/'manifest.json').read_text());assert m['completed'] and m['returncode']==0;assert m['input_sha256']==m['pilot_manifest']['input_sha256'];assert hashlib.sha256(Path(m['binary']).read_bytes()).hexdigest()==m['binary_sha256'];r,p=endpoint(d/'case.h5');a=dict(mode=mode,wall_s=m['elapsed_seconds'],max_lab_position_difference_m=float(np.max(np.linalg.norm(r-baseline[0],axis=1))),max_lab_momentum_difference_betagamma=float(np.max(np.linalg.norm(p-baseline[1],axis=1))),particle_count=100000,charge_C=5.602212333965894e-9,all_finite=True);assert a['max_lab_position_difference_m']<1e-9 and a['max_lab_momentum_difference_betagamma']<1e-10;audits.append(a)
(O/'endpoint-audit.json').write_text(json.dumps(audits,indent=2)+'\n');print('Audits',audits)
# Worker samples are supplementary CPU utilization evidence, not wall estimates.
def contains(node,needle):return needle in node['name'] or any(contains(c,needle) for c in node['children'])
worker_names=[r['name'] for r in roots if contains(r,'__kmp_launch_thread') and 'com.apple.main-thread' not in r['name']]
w=samples[samples.thread.isin(worker_names)].groupby('category').samples.sum().rename_axis('category').reset_index();w['percent']=100*w.samples/w.samples.sum();w.to_csv(O/'openmp-worker-sample-summary.csv',index=False);print('Workers',len(worker_names),w.to_dict(orient='records'))

import io
def stat(path):
 text=path.read_text();blocks=re.findall(r'&column\b(.*?)&end',text,re.S);names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in blocks];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];values=np.loadtxt(io.StringIO('\n'.join(lines)));assert values.shape[1]==len(names);return pd.DataFrame(values,columns=names)
bs=stat(R/'dba-fftw-release/optimized-1/case.stat');metrics=[]
for mode in ['kernel','sample']:
 ss=stat(O/mode/'case.stat');assert ss.shape==bs.shape and len(ss)==10
 assert np.allclose(ss.t,bs.t,rtol=0,atol=1e-14)
 for c in [c for c in ss if c.startswith(('rms_','emit_'))]:
  diff=float(np.max(abs(ss[c]-bs[c])));scale=float(np.max(abs(bs[c])));relative=diff/scale if scale else 0.
  assert relative<1e-8
  metrics.append(dict(mode=mode,column=c,max_absolute_difference=diff,max_relative_difference=relative))
pd.DataFrame(metrics).to_csv(O/'stat-audit.csv',index=False)
print('RMS/emittance maxrelative',pd.DataFrame(metrics).groupby('mode').max_relative_difference.max().to_dict())
