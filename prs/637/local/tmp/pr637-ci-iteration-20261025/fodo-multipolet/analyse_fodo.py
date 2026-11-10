"""Manual regression diagnosis only; no CTest or unit-test dependency."""
from pathlib import Path
import re
import math
import pandas as pd
import numpy as np

study = Path(__file__).resolve().parent
fixture = Path('/Users/adelmann/git/regression-tests-x/RegressionTests/FodoCell-multipoleT-fromfile')
name = 'FodoCell-multipoleT-fromfile'

def read_stat(path):
    text = path.read_text()
    columns = re.findall(r'&column\s+.*?name=([^,\s]+).*?&end', text, re.S)
    rows = []
    for line in text.splitlines():
        items = line.split()
        if len(items) != len(columns):
            continue
        try:
            rows.append([float(x) for x in items])
        except ValueError:
            continue
    return pd.DataFrame(rows, columns=columns)

reference = read_stat(fixture/'reference'/f'{name}.stat')
current = read_stat(study/'head-23f04f6'/f'{name}.stat')
assert len(reference) == len(current), (len(reference), len(current))
records=[]
for field in ['t','s','numParticles','rms_x','rms_y','rms_s','emit_x','emit_y','emit_s','energy','ref_px','ref_py','ref_pz']:
    diff = current[field] - reference[field]
    significant = np.flatnonzero(abs(diff.to_numpy()) > 1e-12)
    records.append(dict(field=field, count=len(diff), nightly_avg=math.sqrt(sum(float(x*x) for x in diff))/len(diff),
                        max_abs=float(abs(diff).max()), first_row_gt_1e_12=int(significant[0]) if len(significant) else None,
                        first_ref=float(reference[field].iloc[0]), first_current=float(current[field].iloc[0]),
                        last_ref=float(reference[field].iloc[-1]), last_current=float(current[field].iloc[-1])))
summary=pd.DataFrame(records)
summary.to_csv(study/'comparison-summary.csv',index=False)
combined=pd.concat([reference.add_prefix('reference_'),current.add_prefix('current_')],axis=1)
for field in ['rms_x','rms_y','emit_x','emit_y','energy','numParticles']:
    combined[f'delta_{field}']=current[field]-reference[field]
combined.to_csv(study/'full-row-comparison.csv',index=False)
print(summary.to_string(index=False))
print('\nSelected early rows:')
print(combined[['current_s','reference_numParticles','current_numParticles','reference_rms_x','current_rms_x','reference_emit_y','current_emit_y']].iloc[[0,1,2,5,10,20,30,50,100,500,1000,2000]].to_string(index=True))

# Publication-quality manual diagnostic figure; not consumed by tests.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
clipped=read_stat(study/'body-clipped-diagnostic'/f'{name}.stat')
plt.rcParams.update({'font.size':10,'axes.labelsize':11,'legend.fontsize':9,'lines.linewidth':1.5,'savefig.dpi':220})
fig, axes=plt.subplots(2,1,figsize=(7.1,5.6),sharex=True,constrained_layout=True)
for frame,label,color,style in [(reference,'July reference 72dd380','#222222','-'),(current,'Current 23f04f6','#1769aa','-'),(clipped,'Body-only diagnostic (changed input)','#b45f06','--')]:
    axes[0].plot(frame.s,1e3*frame.rms_x,label=label,color=color,linestyle=style)
    axes[1].plot(frame.s,1e6*frame.emit_y,label=label,color=color,linestyle=style)
axes[0].set_ylabel(r'$\sigma_x$ [mm]')
axes[1].set_ylabel(r'$\epsilon_{n,y}$ [mm mrad]')
axes[1].set_xlabel('Reference path length [m]')
for ax in axes: ax.grid(alpha=.24);ax.tick_params(direction='in',top=True,right=True)
axes[0].legend(loc='upper center',ncol=1,frameon=False)
fig.savefig(study/'fodo-comparison.png');fig.savefig(study/'fodo-comparison.pdf')
plt.close(fig)
