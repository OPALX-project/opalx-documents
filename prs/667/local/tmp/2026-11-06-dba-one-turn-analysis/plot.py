"""Publication-quality one-turn rms and geometric-emittance comparison figures."""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-dba-one-turn-mpl')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;a=pd.read_csv(P/'evolution.csv');profiles=pd.read_csv(P/'profiles.csv');model=pd.read_csv(P/'analytic-envelope-cell.csv');summary=json.loads((P/'summary.json').read_text());C=summary['run']['circumference_m'];L=C/6
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
colors=['#0072B2','#D55E00'];symbols=['o','s']
def decorate(ax,xlabel,ylabel):
 ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.grid(alpha=.16);ax.set_axisbelow(True)
def save(fig,name):
 for ext in ['png','pdf']:fig.savefig(P/(name+'.'+ext),dpi=300,bbox_inches='tight')
 plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(8,5.9));fig.subplots_adjust(left=.1,right=.98,top=.88,bottom=.12,hspace=.48,wspace=.3)
for j,axis in enumerate(['x','y']):
 ax=axes[0,j]
 for cell in range(6):ax.plot(model.s_cell_m+cell*L,model['sigma_'+axis+'_m']*1e3,'k-',lw=1.4,label='Matched KV' if cell==0 else None)
 for step,label,color,marker in [(0,'Initial source','#999999','x'),(int(a.step.iloc[-1]),'OPALX: one turn',colors[j],symbols[j])]:
  b=profiles[(profiles.step==step)&(profiles.axis==axis)]
  ax.plot(b.s_m,b.sigma_m*1e3,ls='none',marker=marker,ms=3.2,mfc='white',mew=.8,color=color,label=label)
 ax.set_xlim(0,C);ax.set_ylim(0,float(model['sigma_'+axis+'_m'].max())*1e3*1.12);ax.set_title(r'$\sigma_'+axis+'$ around the ring');decorate(ax,r'Lattice position $s$ (m)','Local RMS size (mm)')
 ax=axes[1,j];v=a['sigma_'+axis+'_error_percent'];ax.plot(a.reference_s_m,v,color=colors[j],marker=symbols[j],ms=2.8,lw=1.2);ax.axhline(0,color='k',lw=1,ls='--');span=max(abs(v).max()*1.2,.02);ax.set_ylim(-span,span);ax.set_xlim(0,C);decorate(ax,r'Reference flight $s_{\rm ref}$ (m)','Difference from KV (%)');ax.set_title('Section-equivalent RMS evolution')
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.955),ncol=3,frameon=False,fontsize=8)
fig.suptitle('One-turn DBA: 5.602 nC, 100k particles, 64×64×512, batch 64',y=1.005,fontsize=11)
fig.text(.5,.005,'Top: 96 spatial bins; each snapshot fills the ring. Bottom: fixed analytic Twiss map removes lattice-phase mixing; no fit to tracking.',ha='center',fontsize=7)
save(fig,'rms-vs-matched-kv')
fig,axes=plt.subplots(2,2,figsize=(8,5.4));fig.subplots_adjust(left=.11,right=.98,top=.84,bottom=.12,hspace=.38,wspace=.32)
for j,axis in enumerate(['x','y']):
 ax=axes[0,j];v=a['emit_equivalent_'+axis+'_m_rad']*1e6;target=summary['model']['geometric_rms_emittances_m_rad'][j]*1e6
 ax.axhline(target,color='k',lw=1.3,ls='--',label='Matched KV');ax.plot(a.reference_s_m,v,color=colors[j],marker=symbols[j],ms=3,mfc='white',lw=1.2,label='OPALX');ax.set_xlim(0,C);ax.set_ylim(0,max(v.max(),target)*1.08);ax.set_title(r'$\epsilon_'+axis+'$');decorate(ax,r'Reference flight $s_{\rm ref}$ (m)','Geometric RMS emittance\n(mm mrad)')
 ax=axes[1,j];v=a['emit_'+axis+'_error_percent'];ax.axhline(0,color='k',lw=1,ls='--');ax.plot(a.reference_s_m,v,color=colors[j],marker=symbols[j],ms=2.8,lw=1.2);span=max(abs(v).max()*1.2,.02);ax.set_ylim(-span,span);ax.set_xlim(0,C);decorate(ax,r'Reference flight $s_{\rm ref}$ (m)','Difference from KV (%)')
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.94),ncol=2,frameon=False,fontsize=8)
fig.suptitle('One-turn DBA: emittance after removing periodic Twiss variation',y=.99,fontsize=11)
fig.text(.5,.005,'Section-equivalent, population-centred moments of all 100k particles; fixed model map at each particle’s local lattice position.',ha='center',fontsize=7)
save(fig,'emittance-vs-matched-kv')
