from pathlib import Path
import hashlib,json,shlex,subprocess,time
out=Path('/Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100')
submission=json.loads((out/'submission-tracker.json').read_text());root=submission['root'];job=submission['job_id']
opts=['-x','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']
remote='''from pathlib import Path
import datetime,json,subprocess
root=Path(ROOT)
def call(args):
 p=subprocess.run(args,text=True,capture_output=True,timeout=25)
 return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
q=call(['squeue','-M','gmerlin6','-j',JOB,'-h','-o','%T|%M|%R'])
info={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queue':q}
if not q['stdout'].strip():info['accounting']=call(['sacct','-M','gmerlin6','-j',JOB,'--format=JobIDRaw,State,ExitCode,Elapsed','--noheader','--parsable2'])
for name in ['status.tsv','job.log','run-report.json']:
 p=root/'gpu-integration'/name
 if p.exists():
  if name.endswith('.json'):info[name]=json.loads(p.read_text())
  else:info[name]=p.read_text(errors='replace').splitlines()[-20:]
print(json.dumps(info),flush=True)
'''.replace('ROOT',repr(root)).replace('JOB',repr(str(job)))
command="python3 - <<'POLL'\n"+remote+"\nPOLL"
failures=0
while True:
 try:p=subprocess.run(['ssh',*opts,'merlin6',command],text=True,capture_output=True,timeout=120)
 except subprocess.TimeoutExpired:
  failures+=1;print('Tracker status SSH timed out; no job action taken.',flush=True)
  if failures>=3:raise
  time.sleep(30);continue
 records=[]
 for line in p.stdout.splitlines():
  try:r=json.loads(line)
  except json.JSONDecodeError:continue
  if isinstance(r,dict) and 'queue' in r:records.append(r)
 if p.returncode or len(records)!=1:
  failures+=1;(out/'tracker-monitor-error.log').write_text(p.stdout+p.stderr)
  if failures>=3:raise RuntimeError(p.stdout+p.stderr)
  time.sleep(30);continue
 failures=0;info=records[0]
 (out/'tracker-latest-status.json').write_text(json.dumps(info,indent=2)+'\n')
 with (out/'tracker-status-history.jsonl').open('a') as f:f.write(json.dumps(info)+'\n')
 q=info['queue']['stdout'].strip().splitlines()
 accounting=info.get('accounting',{}).get('stdout','').splitlines()
 main=[line.split('|') for line in accounting if line.split('|')[0]==str(job)]
 state=q[0].split('|')[0] if q else main[0][1] if main else 'UNKNOWN'
 elapsed=q[0].split('|')[1] if q else main[0][3] if main else '?'
 cases=info.get('run-report.json',{}).get('runs',[])
 print(json.dumps({'time':info['time'],'job':job,'state':state,'elapsed':elapsed,'completed_cases':[{k:r[k] for k in ['case','ranks','passed','returncode','timeout']} for r in cases],'status':info.get('status.tsv',[])}),flush=True)
 if state not in ['RUNNING','PENDING','CONFIGURING','COMPLETING','UNKNOWN']:break
 time.sleep(30)
archive_command='cd '+shlex.quote(root)+' && tar -czf tracker-validation-evidence.tgz gpu-integration run-tracker.sbatch run_tracker_gpu.py rank_gpu_runtime.py evidence/binaries.sha256 evidence/submission-tracker.json && sha256sum tracker-validation-evidence.tgz'
p=subprocess.run(['ssh',*opts,'merlin6',archive_command],text=True,capture_output=True,timeout=180)
(out/'tracker-archive-remote.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
subprocess.run(['scp',*opts,'merlin6:'+root+'/tracker-validation-evidence.tgz',str(out/'tracker-validation-evidence.tgz')],check=True,timeout=180)
sha=hashlib.sha256((out/'tracker-validation-evidence.tgz').read_bytes()).hexdigest()
assert any(line.startswith(sha+' ') for line in p.stdout.splitlines())
terminal={'job_id':job,'state':state,'accounting':accounting,'source_id':submission['source_id'],'archive_sha256':sha}
(out/'tracker-terminal.json').write_text(json.dumps(terminal,indent=2)+'\n')
print('TERMINAL '+json.dumps(terminal),flush=True)
