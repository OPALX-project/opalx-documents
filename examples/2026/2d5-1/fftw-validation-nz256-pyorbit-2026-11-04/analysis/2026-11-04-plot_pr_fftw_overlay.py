"""Same published six-panel plots, adding the verified current-build curves."""
from pathlib import Path
import os,json,hashlib,shutil
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-original-model-plots')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent/'pr-fftw-repeat';PUBLISHED=Path('/Users/adelmann/git/opalx-documents/examples/2026/2d5-1')
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(PUBLISHED))
import analytic_zero_sc as analytic_model
current=pd.read_csv(ROOT/'series.csv',float_precision='round_trip');current=current[current.code=='Current OPALX'];assert len(current)==202
published=pd.read_csv(PUBLISHED/'series.csv',float_precision='round_trip');assert len(published)==606
published.code=published.code.replace({'Committed 658':'PR: committed 658','Local original':'PR: local ORIGINAL','PyORBIT':'PR: PyORBIT'})
data=pd.concat([published,current],ignore_index=True);data.to_csv(ROOT/'overlay-series.csv',index=False,float_format='%.17g')
analytic=analytic_model.evaluate(np.linspace(0,10,1001));station=analytic_model.evaluate(analytic.s_m,convention='station')
assert max(abs(analytic.emit_n_u_m-analytic_model.evaluate(analytic.s_m,128).emit_n_u_m))<1e-20
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','pdf.fonttype':42})
styles=[('PR: committed 658','#0072B2','o','-'),('PR: PyORBIT','#D55E00','s','-'),('PR: local ORIGINAL','#009E73','x','--'),('Current OPALX','black','D','-')]
for kind,fields,factors,units,titles in [
 ('rms',[f'sigma_{c}_m' for c in ['u','y','s']],[1e3,1e3,1],['mm','mm','m'],[r'$\sigma_u$',r'$\sigma_y$',r'$\sigma_s$']),
 ('emittance',['emit_n_u_m','emit_n_y_m','emit_sE_m_eV'],[1e6,1e6,1e3],['mm mrad','mm mrad','mm eV'],[r'$\epsilon_{n,u}$',r'$\epsilon_{n,y}$',r'$\epsilon_{s,E}$'])]:
 fig,axes=plt.subplots(2,3,figsize=(7.3,4.3));fig.subplots_adjust(left=.11,right=.99,top=.88,bottom=.28,wspace=.43,hspace=.35)
 for i,mode in enumerate(['ZeroSC','10pC']):
  for j,(field,factor,unit,title) in enumerate(zip(fields,factors,units,titles)):
   ax=axes[i,j]
   for code,color,marker,ls in styles:
    q=data[(data.code==code)&(data['mode']==mode)].sort_values('step');assert len(q)==101;values=q[field]*factor
    if kind=='emittance' and i==0 and j==2:values=values.where(values>0)
    ax.plot(q.s_m,values,color=color,marker=marker,markevery=10,ms=2.6 if code=='Current OPALX' else 3,mfc='white',lw=1.0,ls=ls,label=code)
   if kind=='emittance' and i==0 and j==0:
    ax.plot(analytic.s_m,analytic.emit_n_u_m*1e6,'k:',lw=1.5,label='Analytic: common time');ax.plot(station.s_m,station.emit_n_u_m*1e6,color='#CC79A7',ls=':',lw=1.5,label='Analytic: common station')
   maximum=float(data.loc[data['mode']==mode,field].max())*factor
   if maximum==0:maximum=float(data[field].max())*factor
   if kind=='emittance' and i==0 and j==0:maximum=max(maximum,float(analytic.emit_n_u_m.max())*1e6)
   ax.set_xlim(0,10);ax.grid(alpha=.16);ax.set_ylim(0,1.05*maximum if maximum>0 else 1)
   ax.set_ylabel((mode.replace('10pC','10 pC')+'\n' if j==0 else '')+('RMS size' if kind=='rms' else 'RMS emittance')+f' ({unit})')
   if i==0:ax.set_title(title)
   if i==1:ax.set_xlabel(r'$s$ (m)')
   if kind=='emittance' and i==0 and j==2:
    positive=data.loc[(data['mode']=='ZeroSC')&(data[field]>0),field]*factor;ax.set_yscale('log');ax.set_ylim(positive.min()*.5,positive.max()*2);ax.text(.5,.07,'Zero values omitted',transform=ax.transAxes,ha='center',fontsize=6)
 handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.015),ncol=2,frameon=False,fontsize=7)
 fig.suptitle('Current build versus published PR: 100 steps, 10 m, $R=2$ m',fontsize=10)
 for ext in ['png','pdf']:fig.savefig(ROOT/f'{kind}-current-vs-pr.{ext}',dpi=300,bbox_inches='tight')
 plt.close(fig)
errors=[]
for mode in ['ZeroSC','10pC']:
 a=data[(data.code=='Current OPALX')&(data['mode']==mode)].set_index('step');b=data[(data.code=='PR: local ORIGINAL')&(data['mode']==mode)].set_index('step')
 for field in ['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV']:
  delta=a[field]-b[field];relative=100*delta/b[field].replace(0,np.nan)
  if mode=='ZeroSC' and field=='emit_sE_m_eV':relative[:]=np.nan
  errors.append(dict(mode=mode,field=field,current_endpoint=a[field].iloc[-1],published_endpoint=b[field].iloc[-1],endpoint_difference=delta.iloc[-1],endpoint_percent=relative.iloc[-1],max_absolute_difference=float(abs(delta).max()),max_absolute_percent=float(abs(relative).max()) if relative.notna().any() else None))
pd.DataFrame(errors).to_csv(ROOT/'current-vs-published.csv',index=False,float_format='%.17g');print(pd.DataFrame(errors).to_string(index=False))
