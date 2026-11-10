from pathlib import Path
import json,subprocess
out=Path(__file__).resolve().parent;submission=json.loads((out/'submission.json').read_text())
opts=['-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ForwardX11=no','-o','HostName=129.129.185.171','-o','HostKeyAlias=merlin-l-001.psi.ch','-o','StrictHostKeyChecking=yes']
code=r"""from pathlib import Path
import json,subprocess
p=Path(TASK)
result={'accounting':subprocess.check_output(['sacct','-M','gmerlin6','-j',JOB,'-n','-P','-o','JobIDRaw,State,ExitCode,Elapsed,Start,End,NodeList'],text=True)}
for name in ['progress','gaussian-variants','full-suite-result','terminal']:
 path=p/'after'/(name+'.json')
 if path.exists():result[name]=json.loads(path.read_text())
for name in ['build','job','distribution','full-suite']:
 path=p/'after'/(name+'.log')
 if path.exists():
  text=path.read_text(errors='replace');result[name+'-tail']=text.splitlines()[-12:]
  result[name+'-failures']=[x for x in text.splitlines()if '***Failed'in x or '[  FAILED  ]'in x or '***Timeout'in x or 'Traceback (most recent call last)'in x]
print(json.dumps(result))
""".replace('TASK',repr(submission['task_root'])).replace('JOB',repr(str(submission['job_id'])))
r=subprocess.run(['ssh',*opts,'merlin6',"python3 - <<'REMOTE'\n"+code+'\nREMOTE'],capture_output=True,text=True,timeout=180);(out/'status.log').write_text(r.stdout+r.stderr);r.check_returncode();rows=[json.loads(x)for x in r.stdout.splitlines()if x.startswith('{')];assert len(rows)==1;j=rows[0];(out/'status.json').write_text(json.dumps(j,indent=2)+'\n')
if j.get('progress'):j['progress']=j['progress'][-1]
summary={'accounting':j['accounting'],'phase':j.get('progress'),'gaussian_variants_passed':len(j.get('gaussian-variants',[])),'full_suite':j.get('full-suite-result'),'terminal':j.get('terminal'),'full_suite_tail':j.get('full-suite-tail'),'failure_markers':{k:v for k,v in j.items()if k.endswith('-failures')and v}}
print(json.dumps(summary,indent=2))
