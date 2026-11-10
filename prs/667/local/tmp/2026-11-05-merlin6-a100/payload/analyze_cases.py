"""Audit native A100 outputs and compare with the exact published PR data."""
from pathlib import Path
import json,re,io
import numpy as np,pandas as pd,h5py
import emittance_reference as h
import analytic_zero_sc as analytic
O=Path(__file__).resolve().parent;FIELDS=['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV'];rows=[];audit=[];errors=[]
summary=json.loads((O/'run-summary.json').read_text())
for mode in ['ZeroSC','10pC']:
 d=O/'runs'/('bend-'+mode);m=json.loads((d/'manifest.json').read_text())
 if not m.get('completed'):continue
 p0=.001/np.sqrt(1-.001**2)
 def record(step,r,p,time):
  phase=step*.1/2;theta=np.arctan2(r[:,2],r[:,0]+2);u=np.hypot(r[:,0]+2,r[:,2])-2;s=2*np.arctan2(np.sin(theta-phase),np.cos(theta-phase));values=dict(sigma_u_m=np.std(u),sigma_y_m=np.std(r[:,1]),sigma_s_m=np.std(s),**h.particle_emittances(r,p,phase,p0,938272088.16));assert all(np.isfinite(v) for v in values.values());rows.append(dict(code='A100 OPALX',mode=mode,step=step,s_m=step*.1,time_s=time,**values))
 with np.load(O/'assets/bend-source.npz') as src:record(0,src['cartesian_m'],src['momenta_betagamma'],0)
 with h5py.File(d/'case.h5') as f:
  keys=sorted(f,key=lambda k:int(k.split('#')[-1]));assert len(keys)==100
  for step,key in enumerate(keys,1):
   g=f[key];assert np.array_equal(np.sort(g['id'][:]),np.arange(1048576));q=float(g['q'][:].sum());assert abs(q/1e-11-1)<1e-10;t=float(np.asarray(g.attrs['TIME']).flat[0]);assert abs(t-step*m['dt_s'])<1e-16;r,p=h.global_snapshot(g);assert np.isfinite(r).all() and np.isfinite(p).all();record(step,r,p,t);audit.append(dict(case=m['case'],step=step,particles=1048576,charge_C=q,time_s=t))
 print('AUDITED',mode,flush=True)
gpu=pd.DataFrame(rows,columns=['code','mode','step','s_m','time_s',*FIELDS]);gpu.to_csv(O/'gpu-series.csv',index=False,float_format='%.17g');published=pd.read_csv(O/'published-series.csv',float_precision='round_trip');combined=pd.concat([published,gpu],ignore_index=True);combined.to_csv(O/'overlay-series.csv',index=False,float_format='%.17g')
for mode in ['ZeroSC','10pC']:
 a=gpu[gpu['mode']==mode].set_index('step');b=published[(published['mode']==mode)&(published.code=='Local original')].set_index('step')
 if len(a)!=101:continue
 for field in FIELDS:
  delta=a[field]-b[field];scale=abs(b[field]).max();relative=abs(delta)/abs(b[field]).replace(0,np.nan);errors.append(dict(mode=mode,field=field,max_absolute_difference=float(abs(delta).max()),max_difference_over_published_peak=float(abs(delta).max()/scale) if scale else None,max_pointwise_percent=float(relative.max()*100) if relative.notna().any() else None,endpoint_a100=float(a[field].iloc[-1]),endpoint_published=float(b[field].iloc[-1])))
pd.DataFrame(errors).to_csv(O/'bend-vs-published.csv',index=False)
zero=gpu[gpu['mode']=='ZeroSC'].sort_values('step');analytic_check={}
if len(zero)==101:
 ref=analytic.evaluate(zero.s_m.to_numpy());analytic_check=dict(convention='common time',endpoint_radial_emittance_error_percent=float(100*(zero.emit_n_u_m.iloc[-1]/ref.emit_n_u_m.iloc[-1]-1)),max_absolute_error_percent_analytic_peak=float(100*np.max(abs(zero.emit_n_u_m.to_numpy()-ref.emit_n_u_m))/ref.emit_n_u_m.max()))
def stat(path):
 text=path.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',text,re.S)];data=re.split(r'&data\b.*?&end',text,maxsplit=1,flags=re.S)[1];lines=[x.strip() for x in data.splitlines() if x.strip() and not x.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',text)):];v=np.loadtxt(io.StringIO('\n'.join(lines)));assert v.shape[1]==len(names);return pd.DataFrame(v,columns=names)
def endpoint(path):
 with h5py.File(path) as f:
  assert len(f)==1;g=f[next(iter(f))];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(100000));order=np.argsort(ids);r,p=h.global_snapshot(g);r=r[order];p=p[order];assert np.isfinite(r).all() and np.isfinite(p).all();assert abs(float(g['q'][:].sum())/5.602212333965894e-9-1)<1e-12;assert abs(float(np.asarray(g.attrs['TIME']).flat[0])-3e-10)<1e-22;assert int(np.asarray(g.attrs['GlobalTrackStep']).flat[0])==99;return r,p
br,bp=endpoint(O/'published-dba-endpoint.h5');_,zp=endpoint(O/'published-dba-zero-sc.h5');kick=float(np.linalg.norm(bp-zp,axis=1).max());bs=stat(O/'published-dba.stat');dba=[];metrics=[]
for m in summary:
 if m['kind']!='dba' or not m.get('completed'):continue
 d=O/'runs'/m['case'];r,p=endpoint(d/'case.h5');s=stat(d/'case.stat');assert len(s)==len(bs)==10;assert np.allclose(s.t,bs.t,rtol=0,atol=1e-14)
 for field in s:
  if field.startswith(('rms_','emit_')):metrics.append(dict(case=m['case'],field=field,max_relative_difference=float(abs(s[field]-bs[field]).max()/abs(bs[field]).max()) if abs(bs[field]).max() else None))
 log=(d/'run.log').read_text();main=float(re.search(r'Timings> mainTimer\.+ Wall tot =\s*([\d.eE+-]+)',log)[1]);orbit=float(re.search(r'Timings> OrbThreader\.+ Wall max =\s*([\d.eE+-]+)',log)[1]);dba.append(dict(case=m['case'],wall_s=m['elapsed_seconds'],steady_s_per_step=(main-orbit)/100,max_position_difference_m=float(np.linalg.norm(r-br,axis=1).max()),max_momentum_difference_betagamma=float(np.linalg.norm(p-bp,axis=1).max()),max_momentum_difference_percent_peak_sc_kick=float(100*np.linalg.norm(p-bp,axis=1).max()/kick)))
pd.DataFrame(dba).to_csv(O/'dba-vs-published.csv',index=False);pd.DataFrame(metrics).to_csv(O/'dba-stat-comparison.csv',index=False);pd.DataFrame(audit).to_csv(O/'snapshot-audit.csv',index=False)
result=dict(identity=json.loads((O/'run-identity.json').read_text()),audited_bend_snapshots=len(audit),bend_comparison=errors,analytic_zero_sc=analytic_check,dba_comparison=dba,unsupported_batches=[m['case'] for m in summary if m.get('unsupported')],failed_cases=[m['case'] for m in summary if not m.get('completed') and not m.get('unsupported')],scope='Published physical cases and current serial-slice DBA repeated on1A100/1rank. Earlier CPU implementations/timings are historical references. Batching guard retained, no GPU batching result.')
(O/'analysis-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
