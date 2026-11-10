from pathlib import Path
import re,hashlib
root=Path('/Users/adelmann/git/opalx-documents');o=root/'examples/2026/2d5-1/longitudinal-density-batch-2026-11-06'
p=o/'readme.md';s=p.read_text().replace('New code and these results remain uncommitted pending review.','The implementation is committed as `a8ce134af` in OPALX. A requested four-GPU pilot was cancelled while queued because of the account GPU limit; it produced no results.');s+='\n![Before/after GPU RMS and emittance agreement](rms-emittance.png)\n';p.write_text(s)
p=o/'analyze.py';s=p.read_text();s+='''
# Matched-source tracking curves; all cases are numerically coincident.
fig,axes=plt.subplots(2,3,figsize=(10,5.7),layout='constrained')
for n,color in zip([1,2,3],['#0072B2','#D55E00','#009E73']):
 for mode,ls in [('before','-'),('after','--')]:
  q=runs[('gpu',n,mode,100)];x=(q.s-q.s.iloc[0])*1000
  for row,prefix,factor,unit in [(0,'rms',1000,'mm'),(1,'emit',1e6,'mm mrad')]:
   for col,coord in enumerate(['x','y','s']):
    ax=axes[row,col];ax.plot(x,q[f'{prefix}_{coord}']*factor,color=color,ls=ls,lw=1.2,label=f'{n} A100: {mode}')
    ax.set(xlabel='s − s₀ [mm]',ylabel=f'{prefix} '+('z' if coord=='s' else coord)+f' [{unit}]');ax.grid(alpha=.2);ax.set_ylim(bottom=0)
    ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,3),useOffset=False)
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=3,fontsize=8)
fig.savefig(OUT/'rms-emittance.png');fig.savefig(OUT/'rms-emittance.pdf');plt.close(fig)
''';p.write_text(s)
