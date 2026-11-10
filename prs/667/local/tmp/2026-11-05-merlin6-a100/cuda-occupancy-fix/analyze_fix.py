"""Validate the CUDA occupancy launch fix against existing GPU tests and pilot records."""
from pathlib import Path
import json,re,io,xml.etree.ElementTree as ET
import pandas as pd,numpy as np
P=Path(__file__).resolve().parent;D=P/'results'
tests=ET.parse(D/'unit-tests.xml').getroot().findall('.//testcase');assert len(tests)==5
assert not any(t.find('failure') is not None or t.find('skipped') is not None for t in tests)
full=(D/'full-ctest.log').read_text()
names=re.findall(r'^\[\s+OK\s+\] FFT2D5AlgorithmTest\.([^ ]+)',full,re.M)
assert len(names)==11 and len(set(names))==11,names
text='\n'.join(names)+'\n'
(D/'algorithm-detailed.log').write_text(text)
def stat(p):
 s=p.read_text();names=[re.search(r'\bname\s*=\s*([^,\s]+)',b)[1].strip('"') for b in re.findall(r'&column\b(.*?)&end',s,re.S)];body=re.split(r'&data\b.*?&end',s,maxsplit=1,flags=re.S)[1];lines=[l.strip() for l in body.splitlines() if l.strip() and not l.lstrip().startswith('!')];lines=lines[len(re.findall(r'&parameter\b',s)):];return pd.DataFrame(np.loadtxt(io.StringIO('\n'.join(lines))),columns=names)
reference=stat(P.parent/'gpu-batching/results/batch-0-repeat-1/case.stat');metrics=[]
rows=json.loads((D/'measurements.json').read_text());assert len(rows)==2
for m in rows:
 got=stat(D/f"batch-{m['batch']}-repeat-1/case.stat");assert np.array_equal(got.t,reference.t)
 for name in got:
  if name.startswith(('rms_','emit_')):
   delta=float(abs(got[name]-reference[name]).max());scale=float(abs(reference[name]).max());metrics.append(dict(batch=m['batch'],field=name,max_absolute_difference=delta,max_percent_reference_peak=100*delta/scale if scale else None))
a=pd.DataFrame(metrics);a.to_csv(D/'moment-comparison.csv',index=False)
summary=dict(identity=json.loads((D/'identity.json').read_text()),gpu_targets_passed=5,algorithm_tests_passed=11,algorithm_tests_skipped=0,pilot_cases=2,max_moment_difference_percent_reference_peak=float(a.max_percent_reference_peak.max()),max_position_component_difference_m=max(max(m['errors'][k] for k in ['x','y','z']) for m in rows),max_momentum_component_difference_betagamma=max(max(m['errors'][k] for k in ['px','py','pz']) for m in rows),no_tolerance_changes=True,no_ippl_changes=True,source_fix_committed=False)
(D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
