from pathlib import Path
import datetime,hashlib,json,shlex,subprocess,time
out=Path('/Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100')
submission=json.loads((out/'submission.json').read_text());root=submission['root'];job=submission['job_id']
opts=['-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']
remote='''from pathlib import Path
import datetime,json,subprocess
root=Path(ROOT)
def call(args):
    p=subprocess.run(args,text=True,capture_output=True,timeout=30)
    return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
info={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'queue':call(['squeue','-M','gmerlin6','-j',JOB,'-h','-o','%T|%M|%R']),'accounting':call(['sacct','-M','gmerlin6','-j',JOB,'--format=JobIDRaw,State,ExitCode,Elapsed','--noheader','--parsable2'])}
for name in ['status.tsv','configure.log','build.log','tests.log','job.log']:
    p=root/'evidence'/name
    if p.exists():
        lines=p.read_text(errors='replace').splitlines()
        info[name]={'tail':lines[-7:]}
        if name in ['build.log','configure.log','tests.log']:
            errors=[line for line in lines if 'error:' in line.lower() or 'fatal error' in line.lower() or 'FAILED' in line or 'failed out of' in line]
            info[name]['errors']=errors[:12]
print(json.dumps(info),flush=True)
'''.replace('ROOT',repr(root)).replace('JOB',repr(str(job)))
command="python3 - <<'POLL'\n"+remote+"\nPOLL"
failures=0
while True:
    queried=subprocess.run(['ssh',*opts,'merlin6',command],text=True,capture_output=True,timeout=150)
    records=[]
    for line in queried.stdout.splitlines():
        try:record=json.loads(line)
        except json.JSONDecodeError:continue
        if isinstance(record,dict) and 'accounting' in record:records.append(record)
    if queried.returncode or len(records)!=1:
        failures+=1
        print('Monitor query failure '+str(failures)+': '+queried.stderr[-800:],flush=True)
        with (out/'monitor-errors.log').open('a') as f:f.write(queried.stdout+queried.stderr+'\n')
        if failures>=3:raise RuntimeError('Three status-query failures; job not cancelled or resubmitted')
        time.sleep(45);continue
    failures=0;info=records[0]
    (out/'latest-status.json').write_text(json.dumps(info,indent=2)+'\n')
    with (out/'status-history.jsonl').open('a') as f:f.write(json.dumps(info)+'\n')
    accounting=info['accounting']['stdout'].splitlines()
    main=[line.split('|') for line in accounting if line.split('|')[0]==str(job)]
    state=main[0][1] if main else 'UNKNOWN';elapsed=main[0][3] if main else '?'
    phase=info.get('status.tsv',{}).get('tail',[])
    tail=info.get('build.log',info.get('configure.log',{})).get('tail',[])
    errors=sum([info.get(n,{}).get('errors',[]) for n in ['configure.log','build.log','tests.log']],[])
    print(json.dumps({'time':info['time'],'job':job,'state':state,'elapsed':elapsed,'phase':phase,'progress':tail[-2:],'errors':errors[:3]}),flush=True)
    if state not in ['RUNNING','PENDING','CONFIGURING','COMPLETING','UNKNOWN']:
        break
    time.sleep(45)
# Collect terminal evidence without modifying any source/build products.
archive_command='cd '+shlex.quote(root)+' && tar -czf validation-evidence.tgz evidence run.sbatch rank_gpu.py prepare_remote.py src/source-manifest.json && sha256sum validation-evidence.tgz'
archived=subprocess.run(['ssh',*opts,'merlin6',archive_command],text=True,capture_output=True,timeout=180)
(out/'archive-remote.log').write_text(archived.stdout+archived.stderr)
assert archived.returncode==0,archived.stderr
subprocess.run(['scp',*opts,'merlin6:'+root+'/validation-evidence.tgz',str(out/'validation-evidence.tgz')],check=True,timeout=180)
sha=hashlib.sha256((out/'validation-evidence.tgz').read_bytes()).hexdigest()
assert any(line.startswith(sha+' ') for line in archived.stdout.splitlines()),'Archive hash mismatch'
(out/'terminal.json').write_text(json.dumps({'job_id':job,'state':state,'accounting':accounting,'archive_sha256':sha,'source_id':submission['source_id']},indent=2)+'\n')
print('TERMINAL '+json.dumps({'job_id':job,'state':state,'archive_sha256':sha,'source_id':submission['source_id']}),flush=True)
