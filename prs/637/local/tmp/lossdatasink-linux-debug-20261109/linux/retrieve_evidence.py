from pathlib import Path
import hashlib,json,subprocess,tarfile
out=Path(__file__).resolve().parent;remote=json.loads((out/'baseline-plan.json').read_text())['remote_root']
opts=['-o','BatchMode=yes','-o','ConnectTimeout=10','-o','ForwardX11=no']
code=r"""from pathlib import Path
import hashlib,json,subprocess,tarfile
root=Path(REMOTE_ROOT)
rows=subprocess.check_output(['sacct','-M','gmerlin6','-j','355089,355090,355091,355092,355093','-n','-P','-o','JobIDRaw,State,ExitCode,Elapsed,Start,End,NodeList'],text=True)
main={x.split('|')[0]:x.split('|') for x in rows.splitlines() if x.split('|')[0].isdigit()}
assert main['355093'][1]=='COMPLETED' and main['355093'][2]=='0:0',main
queue=subprocess.check_output(['squeue','-M','gmerlin6','-j','355089,355090,355091,355092,355093','-h','-o','%i %T'],text=True)
assert not queue.strip(),queue
(root/'job-accounting.txt').write_text(rows)
(root/'task-jobs-terminal.json').write_text(json.dumps({'accounting':main,'queue_empty':True},indent=2)+'\n')
assert (root/'evidence-stress/terminal-verification.json').is_file()
archive=root/'validation-evidence.tgz'
if not archive.exists():
 with tarfile.open(archive,'w:gz') as tar:
  files=[]
  for dirname in ['evidence','evidence-after','evidence-final','evidence-stress']:
   for path in (root/dirname).rglob('*'):
    if path.is_file() and not path.name.startswith('baseline-TestLossDataSink'):files.append(path)
  for path in root.iterdir():
   if path.is_file() and (path.suffix in ['.sbatch','.py','.json'] or path.name in ['fixed-TestLossDataSink.cpp','job-accounting.txt']):files.append(path)
  for relative in ['build/CMakeCache.txt','build/CTestTestfile.cmake','build/unit_tests/Structure/CTestTestfile.cmake','build/unit_tests/Distribution/CTestTestfile.cmake','build/unit_tests/Algorithms/CTestTestfile.cmake','build/unit_tests/Structure/CMakeFiles/TestLossDataSink.dir/flags.make','build/unit_tests/Structure/CMakeFiles/TestLossDataSinkMPI.dir/flags.make','build/unit_tests/Structure/CMakeFiles/TestLossDataSink.dir/link.txt','build/unit_tests/Structure/CMakeFiles/TestLossDataSinkMPI.dir/link.txt']:
   path=root/relative
   if path.is_file():files.append(path)
  for path in sorted(set(files)):tar.add(path,arcname=str(path.relative_to(root)),recursive=False)
record={'path':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'size_bytes':archive.stat().st_size,'final_job':355093,'all_task_jobs_terminal':True}
(root/'validation-evidence.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
""".replace('REMOTE_ROOT',repr(remote))
r=subprocess.run(['ssh',*opts,'merlin6',"python3 - <<'REMOTE'\n"+code+'\nREMOTE'],capture_output=True,text=True,timeout=180)
(out/'retrieve-remote.log').write_text(r.stdout+r.stderr);r.check_returncode()
rows=[json.loads(x) for x in r.stdout.splitlines() if x.startswith('{')];assert len(rows)==1,r.stdout;record=rows[0]
archive=out/'validation-evidence.tgz'
r=subprocess.run(['scp',*opts,'merlin6:'+record['path'],str(archive)],capture_output=True,text=True,timeout=300)
(out/'retrieve-local.log').write_text(r.stdout+r.stderr);r.check_returncode()
assert hashlib.sha256(archive.read_bytes()).hexdigest()==record['sha256']
raw=out/'remote-evidence';assert not raw.exists(),'Refusing to overlay previous extracted evidence';raw.mkdir()
with tarfile.open(archive) as tar:
 for member in tar.getmembers():
  p=Path(member.name);assert not p.is_absolute() and '..' not in p.parts;assert member.isfile() or member.isdir()
 tar.extractall(raw)
(out/'validation-evidence.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
