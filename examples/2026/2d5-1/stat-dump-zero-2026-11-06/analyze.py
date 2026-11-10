"""Same-executable STATDUMPFREQ 10/0 pilot timings and moment work."""
from pathlib import Path
import os,json,re
import pandas as pd
OUT=Path(__file__).resolve().parent;RAW=Path(os.environ.get('OPALX_STAT0_ROOT','/Users/adelmann/git/opalx/tmp/2026-11-06-stat0'))
rows=[]
for name in ['stat10','stat0','stat0-profile']:
 d=RAW/name;meta=json.loads((d/'run.json').read_text());assert meta['returncode']==0 and meta['binary_sha256']=='981ce971edc5485c78f48525e517d8242ddbfd456e8e18ea5cf5f51ca1126c43'
 log=(d/'case.out').read_text()
 def timer(key,kind='Wall max'):
  m=re.search(re.escape(key)+r'\.+ '+kind+r' =\s*([\d.eE+-]+)',log);return float(m[1]) if m else 0.
 rows.append(dict(run=name,profiled=meta['profiled'],stat_dump_frequency=meta['stat_dump_frequency'],process_s=meta['wall_seconds'],main_minus_orbit_s=timer('mainTimer','Wall tot')-timer('OrbThreader'),steady_sc_ms=1000*timer('2D5 Solve')/99,moments_count=int(timer('computeMoments','Count')),moments_ms=timer('computeMoments')*10,stat_write_count=int(timer('Write Stat','Count')),stat_write_s=timer('Write Stat')))
s=pd.DataFrame(rows);s.to_csv(OUT/'timings.csv',index=False)
old=pd.read_csv(OUT.parent/'parallel-geometry-gpu-2026-11-06/runtime-kernel-groups.csv');new=pd.read_csv(OUT/'runtime-kernel-groups.csv');comparison=old[['category','calls','ms_per_step']].merge(new[['category','calls','ms_per_step']],on='category',suffixes=('_stat10','_stat0'));comparison.to_csv(OUT/'profile-comparison.csv',index=False)
a=json.loads((RAW/'particle-audit.json').read_text());assert all(row['moment_count']==601 for row in a);(OUT/'particle-audit.json').write_text(json.dumps(a,indent=2)+'\n');print(s.to_string(index=False));print(comparison.to_string(index=False))
