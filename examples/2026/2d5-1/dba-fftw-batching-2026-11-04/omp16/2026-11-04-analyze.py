"""Compare the unchanged100-step charged pilot before/after caching."""
from pathlib import Path
import json,re,io
import numpy as np,pandas as pd,h5py
R=Path(__file__).resolve().parent;O=R/'dba-fftw-batching-omp16'
def endpoint(path):
 with h5py.File(path) as f:
  assert len(f)==1;g=f[next(iter(f))];i=np.argsort(g['id'][:]);assert np.array_equal(g['id'][:][i],np.arange(100000));assert abs(float(g.attrs['TIME'][0])-3e-10)<1e-22;assert int(g.attrs['GlobalTrackStep'][0])==99;r=np.column_stack([g[c][:][i] for c in 'xyz']);p=np.column_stack([g[c][:][i] for c in ['px','py','pz']]);assert np.isfinite(r).all() and np.isfinite(p).all();q=float(g['q'][:].sum());assert abs(q/5.602212333965894e-9-1)<1e-12
  ez=g.attrs['RefPartP']/np.linalg.norm(g.attrs['RefPartP']);ex=np.array([ez[2],0.,-ez[0]]);ey=np.array([0.,1.,0.]);rot=np.array([ex,ey,ez]);return r@rot+g.attrs['RefPartR'],p@rot,q
def stat(path):
 text=path.read_text();blocks=re.findall(r'&column\b(.*?)&end',text,re.S);names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in blocks];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];values=np.loadtxt(io.StringIO('\n'.join(lines)));assert values.shape[1]==len(names);return pd.DataFrame(values,columns=names)

baseline=R/'dba-fftw-batching/batch-0-1';bm=json.loads((baseline/'manifest.json').read_text());assert bm['completed']
br,bp,q=endpoint(baseline/'case.h5');bs=stat(baseline/'case.stat')
_,zp,_=endpoint(R/'dba-sc-feasibility/zerosc-omp4-100steps/case.h5');kick_scale=float(np.linalg.norm(bp-zp,axis=1).max())
build=json.loads(Path('/Users/adelmann/git/opalx/tmp/2026-11-04-fft2d5-batching/build-final.json').read_text());rows=[];metrics=[]
for d in sorted(O.glob('batch-*')):
 if not (d/'manifest.json').exists():continue
 m=json.loads((d/'manifest.json').read_text())
 if not m.get('completed'):continue
 assert m['returncode']==0 and m['binary_sha256']==build['binary_sha256'] and m['source_diff_sha256']==build['source_diff_sha256']
 assert m['input_sha256']==bm['input_sha256'] and m['initial_state_sha256']==bm['initial_state_sha256']
 rr,pp,q=endpoint(d/'case.h5');ss=stat(d/'case.stat');assert ss.shape==bs.shape and len(ss)==10 and np.allclose(ss.t,bs.t,rtol=0,atol=1e-14)
 dr=float(np.linalg.norm(rr-br,axis=1).max());dp=float(np.linalg.norm(pp-bp,axis=1).max());assert dr<1e-9 and dp<1e-10 and dp/kick_scale<.001
 for c in [c for c in ss if c.startswith(('rms_','emit_'))]:
  absolute=float(np.max(abs(ss[c]-bs[c])));scale=float(np.max(abs(bs[c])));relative=absolute/scale if scale else 0.
  assert relative<1e-8
  metrics.append(dict(case=m['case'],column=c,max_absolute_difference=absolute,max_relative_difference=relative))
 log=(d/'run.log').read_text();main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',log)[1]);orbit=float(re.search(r'Timings> OrbThreader\.+ Wall max =\s*([\d.eE+-]+)',log)[1])
 if m['profile']:assert 'callback_errors=0 pending=0' in log
 rows.append(dict(case=m['case'],omp_threads=m['omp_threads'],batch_size=m['batch_size'],repeat=m['repeat'],profile=m['profile'],wall_s=m['elapsed_seconds'],steady_s_per_step=(main-orbit)/100,speedup=bm['elapsed_seconds']/m['elapsed_seconds'],max_lab_position_difference_m=dr,max_lab_momentum_difference_betagamma=dp,momentum_difference_percent_sc_kick=100*dp/kick_scale,charge_C=q,particles=100000))
summary=pd.DataFrame(rows);summary.to_csv(O/'comparison.csv',index=False);pd.DataFrame(metrics).to_csv(O/'stat-comparison.csv',index=False)
(O/'comparison.json').write_text(json.dumps(dict(build=build,baseline=bm,reference_sc_kick_scale=kick_scale,rows=rows,qa='All100kIDs/charge/finitearrays,100steps300ps/globalstep99; endpointbounds1e-9m,1e-10beta-gamma,0.1%SCkick;statbound1e-8relative. No physics tolerance changed.'),indent=2)+'\n')
print(summary.to_string(index=False));print('RMS/emit:',pd.DataFrame(metrics).groupby('case').max_relative_difference.max().to_dict())
