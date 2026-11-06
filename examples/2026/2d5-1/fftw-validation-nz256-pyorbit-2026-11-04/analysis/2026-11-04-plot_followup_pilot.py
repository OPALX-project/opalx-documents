from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-pilot-mpl')
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;O=R/'dba-pyorbit-pilot';d=pd.read_csv(O/'timing-comparison.csv');v=pd.read_csv(O/'local-moment-comparison.csv');nz=pd.read_csv(R/'dba-nz256/comparison.csv')
plt.rcParams.update({'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(8,3.9));fig.subplots_adjust(left=.08,right=.98,top=.85,bottom=.28,wspace=.35)
keys=[('OPALX',512),('OPALX',256),('PyORBIT',512),('PyORBIT',256)];colors=['#0072B2','#56B4E9','#D55E00','#E69F00']
for i,(code,z) in enumerate(keys):
 q=d[(d.code==code)&(d.nz==z)].launch_wall_s;mean=q.mean();axes[0].bar(i,mean,color=colors[i],width=.65);axes[0].errorbar(i,mean,yerr=[[mean-q.min()],[q.max()-mean]],fmt='none',color='black',capsize=3);axes[0].text(i,mean+.5,f'{mean:.2f}',ha='center',fontsize=7)
axes[0].set(xticks=range(4),xticklabels=['OPALX\n512','OPALX\n256','PyORBIT\n512','PyORBIT\n256'],ylabel='Launch-to-completion time (s)',ylim=(0,d.launch_wall_s.max()*1.18),title='Whole pilot: two unprofiled repeats')
py=d[d.code=='PyORBIT'];bottom=np.zeros(2);labels=['Native space charge','Native body maps','Python phase grouping / copies','Setup, diagnostics, output'];cols=['#0072B2','#009E73','#E69F00','#BBBBBB'];means=py.groupby('nz').mean(numeric_only=True).loc[[512,256]]
parts=[means.native_sc_s.to_numpy(),means.native_body_maps_s.to_numpy(),means.python_grouping_copy_s.to_numpy()];parts.append(means.launch_wall_s.to_numpy()-sum(parts))
for values,label,color in zip(parts,labels,cols):axes[1].bar([0,1],values,bottom=bottom,label=label,color=color,width=.6);bottom+=values
axes[1].set(xticks=[0,1],xticklabels=['512','256'],xlabel='$N_z$ in PyORBIT',ylabel='Time (s)',ylim=(0,max(bottom)*1.15),title='PyORBIT: native work and driver overhead')
for ax in axes:ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
fig.legend(*axes[1].get_legend_handles_labels(),loc='lower center',bbox_to_anchor=(.5,.045),ncol=2,frameon=False,fontsize=7)
fig.suptitle('DBA pilot: 100,000 KV particles, 5.602 nC, 100 × 3 ps, $64^2$ transverse grid',fontsize=9)
fig.text(.5,.005,'OPALX: batch 8, FFTW 1, OpenMP 4. PyORBIT: native serial kernels; OpenMP environment 4.\nSame distributed ring source and reference flight. Total times include each driver; no intrinsic code speed ratio is inferred.',ha='center',fontsize=6.5)
for ext in ['png','pdf']:fig.savefig(O/f'runtime-comparison.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(7.4,5.1));fig.subplots_adjust(left=.13,right=.98,top=.87,bottom=.18,wspace=.42,hspace=.44)
fields=['sigma_x_m','sigma_y_m','emit_n_x_m','emit_n_y_m'];titles=[r'$\sigma_x$',r'$\sigma_y$',r'$\epsilon_{n,x}$',r'$\epsilon_{n,y}$'];base=v[(v.code=='OPALX')&(v.nz==512)].iloc[0]
for ax,field,title in zip(axes.flat,fields,titles):
 values=[]
 for code,z in keys[1:]:
  q=v[(v.code==code)&(v.nz==z)][field];values.append(100*(q.mean()/base[field]-1))
 ax.bar(range(3),values,color=colors[1:],width=.6);ax.axhline(0,color='black',lw=.7);span=max(abs(np.array(values)));ax.set_ylim(-span*1.3,span*1.3);ax.set(xticks=range(3),xticklabels=['OPALX\n256','PyORBIT\n512','PyORBIT\n256'],ylabel='Difference from OPALX 512 (%)',title=title);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.ticklabel_format(axis='y',style='sci',scilimits=(-2,2))
fig.suptitle('End-of-pilot local transverse moments',fontsize=9)
fig.text(.5,.025,'100 steps span only 6.55 mm of reference flight. OPALX 256 versus 512: SC momentum difference 7.10% RMS.\nPyORBIT uses NGP slices / TSC transverse shapes and common-s maps; OPALX uses CIC and common-time tracking.',ha='center',fontsize=7)
for ext in ['png','pdf']:fig.savefig(O/f'pilot-comparison.{ext}',dpi=300,bbox_inches='tight')
