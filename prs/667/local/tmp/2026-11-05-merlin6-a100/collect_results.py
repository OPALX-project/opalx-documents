from pathlib import Path
import json,re,xml.etree.ElementTree as ET
import pandas as pd
O=Path(__file__).resolve().parent;R=O/'results'
a=json.loads((R/'analysis-summary.json').read_text());unit=ET.parse(R/'unit-tests.xml').getroot();units=[]
for t in unit.findall('testcase'):
 output=t.findtext('system-out') or '';units.append(dict(name=t.attrib['name'],status=t.attrib.get('status'),failure=t.find('failure') is not None,failed_cases=list(dict.fromkeys(re.findall(r'\[  FAILED  \] ([A-Za-z0-9_]+\.[A-Za-z0-9_]+)',output))),skipped_cases=list(dict.fromkeys(re.findall(r'\[  SKIPPED \] ([A-Za-z0-9_]+\.[A-Za-z0-9_]+)',output)))))
runs=json.loads((R/'run-summary.json').read_text());dba=pd.read_csv(R/'dba-vs-published.csv');bd=pd.read_csv(R/'bend-vs-published.csv');stats=pd.read_csv(R/'dba-stat-comparison.csv');result=dict(analysis=a,unit=units,runs=runs,dba_mean_wall_s=float(dba.wall_s.mean()) if len(dba) else None,max_dba_stat_relative=float(stats.max_relative_difference.max()) if len(stats) else None,charged_max_rms_peak_relative=float(bd[(bd['mode']=='10pC')&bd.field.str.startswith('sigma')].max_difference_over_published_peak.max()),charged_max_emittance_peak_relative=float(bd[(bd['mode']=='10pC')&bd.field.str.startswith('emit')].max_difference_over_published_peak.max()))
(R/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
