#!/usr/bin/env python3
"""Generate the short-deck production comparison from validated LUMI results."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'data/production-f8ac63538915/comparison-summary.json').read_text())
assert s['status']=='PASS' and s['source_head']=='f8ac635389152f906f0df022978e6a834e671ba0'
rows=[]
for e in (50,70,90):
 x=next(x for x in s['comparison'] if x['emittance_pi_mm_mrad']==e)
 d=next(x for x in s['diagnostics'] if x['emittance']==e)
 assert d['integration_steps']==182825 and d['input_macroparticles']==d['final_particles']==131072
 rows.append(f"{e} & {x['paper_delta_Qx']:.4f} & {x['delta_Qx_maximum_depression']:.4f} & {x['delta_Qy_maximum_depression']:.4f} & $\\simeq${x['wall_s_per_turn']:.0f} \\\\")
(R/'generated/short-production-paper.tex').write_text(r'''\begin{tabular}{rrrrr}
\toprule
$\epsilon$ & Paper PIC $\Delta Q_x$ & OPALX $\Delta Q_x$ & OPALX $\Delta Q_y$ & s/turn \\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}
''')
print('Generated maximum-depression comparison for three validated production cases.')
