from pathlib import Path
import json,hashlib,importlib.util,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-round-paper-mpl')
import numpy as np
import pandas as pd
import h5py
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;TRACK=Path('/Users/adelmann/git/OPALX-2D5/curved-study/straight-round-paper/tracking')
helper=TRACK/'bend-10m-100steps-658-committed/provenance/emittance_reference-f2687a55cea723923a642af5bbc0a444f0d3d61b2758e1f4db5ac4e6d3f3dba5.py';spec=importlib.util.spec_from_file_location('native_emittance',helper);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
FIELDS=['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV'];rows=[];checks=[]
for mode in ['ZeroSC','10pC']:
 d=ROOT/'pr-bend'/mode;m=json.loads((d/'manifest.json').read_text());assert m['completed'];p0=m['source']['momentum_betagamma']
 def record(step,r,p,time):
  phi=step*.1/2;theta=np.arctan2(r[:,2],r[:,0]+2);u=np.hypot(r[:,0]+2,r[:,2])-2;s=2*np.arctan2(np.sin(theta-phi),np.cos(theta-phi));rows.append(dict(code='Current OPALX',mode=mode,step=step,s_m=step*.1,time_s=time,sigma_u_m=np.std(u),sigma_y_m=np.std(r[:,1]),sigma_s_m=np.std(s),**h.particle_emittances(r,p,phi,p0,938272088.16)))
 with np.load(m['source']['npz']) as source:record(0,source['cartesian_m'],source['momenta_betagamma'],0)
 with h5py.File(d/'track.h5') as f:
  keys=sorted(f,key=lambda k:int(k.split('#')[-1]));assert len(keys)==100
  for i,key in enumerate(keys,1):
   g=f[key];ids=g['id'][:];assert np.array_equal(np.sort(ids),np.arange(1048576));q=float(g['q'][:].sum());assert np.isclose(q,1e-11,rtol=1e-10,atol=0);time=float(np.asarray(g.attrs['TIME']).flat[0]);assert abs(time-i*m['dt_s'])<1e-16
   r,p=h.global_snapshot(g);assert np.isfinite(r).all() and np.isfinite(p).all();record(i,r,p,time);checks.append(dict(mode=mode,step=i,particles=len(ids),charge_C=q,time_s=time))
old=pd.read_csv(TRACK/'bend-10m-100steps-local-original/analysis/series.csv');old=old[old.steps==100];reference=old[old.code=='Local original'].copy();reference.code='Published OPALX';py=old[old.code=='PyORBIT'].copy();data=pd.concat([pd.DataFrame(rows),reference,py],ignore_index=True);data.to_csv(ROOT/'pr-bend/series.csv',index=False,float_format='%.17g')
# Exact common-time and common-station references, continuous moments over physical volume.
x,w=np.polynomial.legendre.leggauss(256);a=.02*np.cos((x+1)*np.pi/2);weights=w*np.sin((x+1)*np.pi/2)**2*(1+a/2);weights/=weights.sum();analytic=[];p0=.001/np.sqrt(1-.001**2)
for dist in np.linspace(0,10,1001):
 phi=dist/2;r=np.sqrt(4+4*a*np.cos(phi)+a*a);u=(4*a*np.cos(phi)+a*a)/(r+2);q=-p0*a*np.sin(phi)/r
 def area(u,p):
  u=u-np.sum(weights*u);p=p-np.sum(weights*p);v=np.sum(weights*u*u);res=p-np.sum(weights*u*p)/v*u if v else p;return np.sqrt(v*np.sum(weights*res*res))
 us=a*np.cos(phi)-a*a*np.sin(phi)**2/(2+np.sqrt(4-a*a*np.sin(phi)**2));ps=-p0*a*np.sin(phi)/2
 analytic.append((dist,area(u,q),area(us,ps)))
analytic=pd.DataFrame(analytic,columns=['s_m','time','station']);analytic.to_csv(ROOT/'pr-bend/analytic.csv',index=False,float_format='%.17g')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
for name,fields,factors,units in [('rms',FIELDS[:3],[1e3,1e3,1],['mm','mm','m']),('emittance',FIELDS[3:],[1e6,1e6,1e3],['mm mrad','mm mrad','mm eV'])]:
 fig,axes=plt.subplots(2,3,figsize=(10,6),layout='constrained')
 for i,mode in enumerate(['ZeroSC','10pC']):
  for j,(field,factor,unit) in enumerate(zip(fields,factors,units)):
   ax=axes[i,j]
   for code,color,ls in [('Current OPALX','#0072B2','-'),('Published OPALX','#999999',':'),('PyORBIT','#D55E00','--')]:
    q=data[(data.code==code)&(data['mode']==mode)];values=q[field]*factor
    if name=='emittance' and i==0 and j==2:values=values.where(values>0)
    ax.plot(q.s_m,values,color=color,ls=ls,lw=1.5,label=code)
   if name=='emittance' and i==0 and j==0:
    ax.plot(analytic.s_m,analytic.time*1e6,'k:',label='Analytic common time');ax.plot(analytic.s_m,analytic.station*1e6,color='#CC79A7',ls=':',label='Analytic common station')
   ax.set(xlabel='$s$ (m)',ylabel=mode+' '+field.replace('_m','')+' ('+unit+')',xlim=(0,10));ax.grid(alpha=.2)
   if name=='emittance' and i==0 and j==2:ax.set_yscale('log')
   else:ax.set_ylim(bottom=0)
 handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,fontsize=8);fig.suptitle('PR benchmark repeated: ~/git/opalx/build-omp, 100 steps, 1,048,576 particles')
 for ext in ['png','pdf']:fig.savefig(ROOT/f'pr-bend/{name}.{ext}',dpi=300)
end=data[data.step==100];end.to_csv(ROOT/'pr-bend/endpoints.csv',index=False,float_format='%.17g');audit=dict(passed=True,checks=checks,build=json.loads((ROOT/'pr-bend/10pC/manifest.json').read_text())['build']);(ROOT/'pr-bend/audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(end[['code','mode']+FIELDS].to_string(index=False))
