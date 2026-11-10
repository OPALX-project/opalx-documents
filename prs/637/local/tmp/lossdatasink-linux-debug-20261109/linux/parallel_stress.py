from pathlib import Path
import json,subprocess,sys
build=Path(sys.argv[1]);out=Path(sys.argv[2]);runs=[]
for i in range(1,101):
 r=subprocess.run(['ctest','--test-dir',str(build),'-V','-j','2','--output-on-failure','-R','^TestLossDataSink(MPI)?$'],capture_output=True,text=True,timeout=60)
 text=r.stdout+r.stderr
 (out/('parallel-%03d.log'%i)).write_text(text)
 row={'iteration':i,'returncode':r.returncode,'expected_failure':'RewindH5RemovesCheckpointAndLaterStepsBeforeAppend' in text and '[  FAILED  ]' in text,'failure_lines':[x for x in text.splitlines() if 'FAILED' in x or 'Which is:' in x or 'tests passed' in x]}
 runs.append(row);print(json.dumps(row),flush=True)
 (out/'parallel-summary.json').write_text(json.dumps({'runs':runs,'failed_runs':sum(x['returncode']!=0 for x in runs)},indent=2)+'\n')
 if row['expected_failure']:
  break
