from pathlib import Path
import json,subprocess
out=Path('/Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100')
if (out/'terminal.json').exists():
 terminal=json.loads((out/'terminal.json').read_text());assert terminal['state']=='COMPLETED',terminal
else:
 latest=json.loads((out/'latest-status.json').read_text())
 main=[line.split('|') for line in latest['accounting']['stdout'].splitlines() if line.split('|')[0]=='355081']
 assert len(main)==1 and main[0][1]=='COMPLETED' and main[0][2]=='0:0',main
submission=json.loads((out/'submission.json').read_text());remote=submission['root']
script='''from pathlib import Path
import datetime,json,subprocess
root=Path(ROOT)
status=(root/'evidence/status.tsv').read_text()
assert 'ctest\\t0' in status and 'phase\\tcomplete' in status and 'exit\\t0' in status,status
verified=json.loads((root/'evidence/source-verification.json').read_text())
assert verified['source_id']==SOURCE
p=root/'evidence/submission-tracker-attempt2.json';assert not p.exists(),'Refusing duplicate integration submission'
raw=subprocess.check_output(['sbatch','--parsable','--chdir='+str(root),'--output='+str(root/'evidence/slurm-tracker-attempt2-%j.out'),str(root/'run-tracker-attempt2.sbatch')],cwd=root,text=True).strip()
parts=raw.split(';');assert parts[0].isdigit(),raw
record={'job_id':int(parts[0]),'cluster':parts[1] if len(parts)>1 else 'gmerlin6','submitted':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'source_id':SOURCE,'native_job_id':355081}
p.write_text(json.dumps(record,indent=2)+'\\n');print(json.dumps(record),flush=True)
'''.replace('ROOT',repr(remote)).replace('SOURCE',repr(submission['source_id']))
command="python3 - <<'SUBMIT'\n"+script+"\nSUBMIT"
result=subprocess.run(['ssh','-x','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2','merlin6',command],text=True,capture_output=True,timeout=180)
(out/'tracker-attempt2-submission.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,result.stdout+result.stderr
records=[]
for line in result.stdout.splitlines():
 try:entry=json.loads(line)
 except json.JSONDecodeError:continue
 if isinstance(entry,dict) and 'job_id' in entry:records.append(entry)
assert len(records)==1,result.stdout
(out/'submission-tracker-attempt2.json').write_text(json.dumps(records[0],indent=2)+'\n')
print(json.dumps(records[0],indent=2),flush=True)
