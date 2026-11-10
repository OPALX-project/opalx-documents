from pathlib import Path
import datetime,json,shlex,subprocess
out=Path('/Users/adelmann/git/opalx-master/tmp/pr637-audit-fixes-20261109/a100')
plan=json.loads((out/'submission-plan.json').read_text());remote=plan['remote_root']
log=out/'setup.log'
opts=['-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']
def run(label,args,timeout):
    print(label,datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
    result=subprocess.run(args,text=True,capture_output=True,timeout=timeout)
    with log.open('a') as f:f.write('\n'+label+'\n'+result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout[-4000:]+result.stderr[-4000:],flush=True)
        raise RuntimeError(label+' failed with status'+str(result.returncode))
    return result.stdout
run('create isolated root',['ssh',*opts,'merlin6',f'test ! -e {shlex.quote(remote)} && mkdir -p {shlex.quote(remote+"/evidence")}'],180)
run('upload exact source',['scp',*opts,plan['archive'],'merlin6:'+remote+'/source.tar.gz'],180)
run('upload setup scripts',['scp',*opts,*[str(out/name) for name in ['prepare_remote.py','run.sbatch','rank_gpu.py']],'merlin6:'+remote+'/'],180)
run('verify/extract and clone clean isolated dependencies',['ssh',*opts,'merlin6',f'python3 {shlex.quote(remote+"/prepare_remote.py")} > {shlex.quote(remote+"/evidence/prepare.log")} 2>&1 || {{ result=$?; tail -60 {shlex.quote(remote+"/evidence/prepare.log")}; exit "$result"; }}'],600)
submit='''from pathlib import Path
import datetime,json,subprocess
root=Path(REMOTE)
p=root/'evidence/submission.json'
assert not p.exists(),'Refusing duplicate job submission'
result=subprocess.check_output(['sbatch','--parsable','--chdir='+str(root),'--output='+str(root/'evidence/slurm-%j.out'),str(root/'run.sbatch')],cwd=root,text=True).strip()
parts=result.split(';');assert parts[0].isdigit(),result
record={'job_id':int(parts[0]),'cluster':parts[1] if len(parts)>1 else 'gmerlin6','submitted':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'source_id':SOURCE}
p.write_text(json.dumps(record,indent=2)+'\\n')
print(json.dumps(record),flush=True)
'''.replace('REMOTE',repr(remote)).replace('SOURCE',repr(plan['source_id']))
command="python3 - <<'SUBMIT'\n"+submit+"\nSUBMIT"
raw=run('submit one bounded A100 validation job',['ssh',*opts,'merlin6',command],180)
records=[]
for line in raw.splitlines():
    try:entry=json.loads(line)
    except json.JSONDecodeError:continue
    if isinstance(entry,dict) and 'job_id' in entry:records.append(entry)
assert len(records)==1,raw
record=records[0];record.update(archive_sha256=plan['archive_sha256'],source_files=plan['source_files'])
(out/'submission.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
