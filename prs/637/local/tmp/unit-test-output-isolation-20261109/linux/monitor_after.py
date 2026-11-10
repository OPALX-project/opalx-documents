from pathlib import Path
import json,subprocess
out=Path(__file__).resolve().parent;p=json.loads((out/'after-submission.json').read_text());opts=['-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ForwardX11=no','-o','HostName=129.129.185.171','-o','HostKeyAlias=merlin-l-001.psi.ch','-o','StrictHostKeyChecking=yes']
code=r"""from pathlib import Path
import json,re,subprocess
p=Path(EVIDENCE)
acct=subprocess.check_output(['sacct','-M','gmerlin6','-j',JOB,'-n','-P','-o','JobIDRaw,State,ExitCode,Elapsed,Start,End,NodeList'],text=True)
result={'accounting':acct}
for rel,key in [('after/progress.json','progress'),('after/fm2d-summary.json','fm2d'),('after/manual-mpi.json','manual_mpi'),('after/full-suite-result.json','full_suite'),('after/terminal.json','terminal')]:
 q=p/rel
 if q.is_file():result[key]=json.loads(q.read_text())
for rel,key in [('after/build.log','build_tail'),('after/job.log','job_tail'),('after/affected.log','affected_tail'),('after/full-suite.log','full_suite_tail')]:
 q=p/rel
 if q.is_file():result[key]=q.read_text(errors='replace').splitlines()[-8:]
print(json.dumps(result))
""".replace('EVIDENCE',repr(p['evidence_root'])).replace('JOB',repr(str(p['job_id'])))
r=subprocess.run(['ssh',*opts,'merlin6',"python3 - <<'REMOTE'\n"+code+'\nREMOTE'],capture_output=True,text=True,timeout=180);(out/'after-status.log').write_text(r.stdout+r.stderr);r.check_returncode();rows=[json.loads(x)for x in r.stdout.splitlines()if x.startswith('{')];assert len(rows)==1
j=rows[0];(out/'after-status.json').write_text(json.dumps(j,indent=2)+'\n')
summary={'accounting':j['accounting'],'current_phase':j.get('progress',[{}])[-1],'fm2d_pairs':len(j.get('fm2d',[])),'manual_mpi':j.get('manual_mpi'),'full_suite':j.get('full_suite'),'terminal':j.get('terminal'),'build_tail':j.get('build_tail'),'job_tail':j.get('job_tail'),'affected_tail':j.get('affected_tail'),'full_suite_tail':j.get('full_suite_tail')}
print(json.dumps(summary,indent=2))
