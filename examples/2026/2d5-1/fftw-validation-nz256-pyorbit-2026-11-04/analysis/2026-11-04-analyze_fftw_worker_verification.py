from pathlib import Path
import re,json,io
import numpy as np,pandas as pd,h5py
R=Path(__file__).resolve().parent;O=R/'dba-fftw-threads'
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

def endpoint(path):
 with h5py.File(path) as f:
  key=max(f,key=lambda x:int(x.split('#')[-1]));g=f[key];i=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][i],np.arange(100000));assert abs(float(g.attrs['TIME'][0])-3e-10)<1e-22;assert int(g.attrs['GlobalTrackStep'][0])==99
  r=np.column_stack([g[c][:][i] for c in 'xyz']);p=np.column_stack([g[c][:][i] for c in ['px','py','pz']]);assert np.isfinite(r).all() and np.isfinite(p).all();q=float(g['q'][:].sum());assert abs(q/5.602212333965894e-9-1)<1e-12
  ez=g.attrs['RefPartP']/np.linalg.norm(g.attrs['RefPartP']);ex=np.array([ez[2],0.,-ez[0]]);ey=np.array([0.,1.,0.]);rot=np.array([ex,ey,ez]);return r@rot+g.attrs['RefPartR'],p@rot
def contains(node,needle):return needle in node['name'] or any(contains(c,needle) for c in node['children'])
def stat(path):
 text=path.read_text();blocks=re.findall(r'&column\b(.*?)&end',text,re.S);names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in blocks];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];values=np.loadtxt(io.StringIO('\n'.join(lines)));assert values.shape[1]==len(names);return pd.DataFrame(values,columns=names)
worker_names=[r['name'] for r in roots if contains(r,'__kmp_launch_thread') and 'com.apple.main-thread' not in r['name']]
w=samples[samples.thread.isin(worker_names)]
summary=w.groupby('category').samples.sum().rename_axis('category').reset_index();summary['percent']=100*summary.samples/summary.samples.sum();summary.to_csv(O/'worker-sample-summary.csv',index=False)
math=w[w.leaf.str.contains(r'in libfftw3\.3',regex=True)]
assert math.samples.sum()>0
base=endpoint(O/'fftw-1-1/case.h5');current=endpoint(O/'sample/case.h5');dr=float(np.linalg.norm(current[0]-base[0],axis=1).max());dp=float(np.linalg.norm(current[1]-base[1],axis=1).max());assert dr<1e-9 and dp<1e-10
bs=stat(O/'fftw-1-1/case.stat');ss=stat(O/'sample/case.stat');assert bs.shape==ss.shape and len(ss)==10 and np.allclose(bs.t,ss.t,rtol=0,atol=1e-14)
relative=max(float(np.max(abs(ss[c]-bs[c])))/float(np.max(abs(bs[c]))) for c in ss if c.startswith(('rms_','emit_')) and float(np.max(abs(bs[c])))>0);assert relative<1e-8
j=dict(worker_threads=len(worker_names),worker_fft_arithmetic_leaf_samples=int(math.samples.sum()),worker_fft_arithmetic_threads=int(math.thread.nunique()),max_lab_position_difference_m=dr,max_lab_momentum_difference_betagamma=dp,max_relative_rms_emittance_difference=relative,note='Separate FFTW16 maximum/Kokkos4 diagnostic: actual FFTW arithmetic codelets observed on worker threads; excluded from timing means.')
(O/'worker-verification.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2))
