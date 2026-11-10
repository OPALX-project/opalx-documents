from pathlib import Path
import json,subprocess,sys
build=Path(sys.argv[1]);out=Path(sys.argv[2]);rows=[]
for i in range(1,21):
 r=subprocess.run(['ctest','--test-dir',str(build),'-V','-j2','--output-on-failure','-R','^TestFM2D(Dynamic|MagnetoStatic)$'],capture_output=True,text=True,timeout=60)
 text=r.stdout+r.stderr
 (out/('parallel-%03d.log'%i)).write_text(text)
 row={'iteration':i,'returncode':r.returncode,'failed_case_lines':[x for x in text.splitlines() if '[  FAILED  ]' in x or 'exception' in x or 'Could not open' in x or 'Cannot open' in x]}
 rows.append(row)
 (out/'parallel-summary.json').write_text(json.dumps({'runs':rows,'failed_runs':sum(x['returncode']!=0 for x in rows)},indent=2))
 print(json.dumps(row),flush=True)
 if r.returncode:break
