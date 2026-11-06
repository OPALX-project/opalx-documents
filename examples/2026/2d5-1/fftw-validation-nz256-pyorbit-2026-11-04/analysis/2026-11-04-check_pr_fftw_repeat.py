from pathlib import Path
import json,numpy as np,pandas as pd
R=Path(__file__).resolve().parent;O=R/'pr-fftw-repeat';data=pd.read_csv(O/'overlay-series.csv');rows=[]
for mode in ['ZeroSC','10pC']:
 a=data[(data.code=='Current OPALX')&(data['mode']==mode)].sort_values('step');b=data[(data.code=='PR: local ORIGINAL')&(data['mode']==mode)].sort_values('step');assert len(a)==len(b)==101
 for col in ['sigma_u_m','sigma_y_m','sigma_s_m','emit_n_u_m','emit_n_y_m','emit_sE_m_eV']:
  delta=float(np.max(abs(a[col].to_numpy()-b[col].to_numpy())));scale=float(abs(b[col]).max());relative=delta/scale if scale else None
  # ZeroSC longitudinal energy spread is roundoff-sized; compare absolute values.
  if mode=='ZeroSC' and col=='emit_sE_m_eV':assert delta<1e-12
  else:assert relative is None or relative<1e-8
  rows.append(dict(mode=mode,field=col,max_absolute_difference=delta,max_difference_relative_to_published_peak=relative))
analytic=pd.read_csv('/Users/adelmann/git/opalx-documents/examples/2026/2d5-1/analytic_reference.csv') if Path('/Users/adelmann/git/opalx-documents/examples/2026/2d5-1/analytic_reference.csv').exists() else None
pd.DataFrame(rows).to_csv(O/'published-retention.csv',index=False);(O/'published-retention.json').write_text(json.dumps(dict(passed=True,criterion='Each RMS/emittance absolute curve difference <1e-8 of its published peak; ZeroSC longitudinal roundoff uses absolute1e-12m eV',rows=rows,scope='Repeated local ORIGINAL curves; committed658 and PyORBIT remain unchanged historical references. Historical implementation timing bars are not rerun using different executables.'),indent=2)+'\n');print(pd.DataFrame(rows).to_string(index=False))
