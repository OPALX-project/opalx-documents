from pathlib import Path
import subprocess,json,time,hashlib,tarfile,xml.etree.ElementTree as ET
root=Path('/data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643')
job='355069'
submitted=root/'evidence/submission-school.json'
for attempt in range(120):
    query=subprocess.run(['sacct','-M','gmerlin6','-j',job,'-n','-P','--format=JobID,State,ExitCode,Elapsed,NodeList'],text=True,capture_output=True,timeout=20)
    rows=[line.split('|') for line in query.stdout.splitlines() if line.startswith(job+'|')]
    if not rows:
        print(json.dumps({'job':job,'state':'accounting-pending'}),flush=True);time.sleep(60);continue
    row=rows[0];state=row[1]
    statusfile=root/('gpu-school/status.tsv' if job!='355069' else 'evidence/status.tsv')
    phase=statusfile.read_text().strip().splitlines()[-2:] if statusfile.exists() else []
    logfile=root/('gpu-school/job.log' if job!='355069' else 'evidence/build.log')
    tail=logfile.read_text(errors='replace').strip().splitlines()[-1:] if logfile.exists() else []
    print(json.dumps({'job':job,'state':state,'exit':row[2],'elapsed':row[3],'phase':phase,'last':tail}),flush=True)
    if state=='COMPLETED' and row[2]=='0:0' and job=='355069':
        junit=root/'evidence/junit.xml';tree=ET.parse(junit)
        failed=[case.attrib for case in tree.iter('testcase') if list(case.iter('failure')) or list(case.iter('error'))]
        assert not failed,failed
        verified=json.loads((root/'evidence/source-verification.json').read_text())
        assert verified['files_verified']==1072
        if submitted.exists():
            record=json.loads(submitted.read_text());job=record['output'].split(';')[0]
            print('Following existing school job '+job,flush=True);continue
        result=subprocess.run(['sbatch','--parsable','--chdir='+str(root),'--output='+str(root/'evidence/slurm-school-%j.out'),str(root/'run-school.sbatch')],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        record={'returncode':result.returncode,'output':result.stdout.strip(),'after_successful_build_job':355069,'source_id':verified['source_id'],'script_sha256':hashlib.sha256((root/'run-school.sbatch').read_bytes()).hexdigest()}
        submitted.write_text(json.dumps(record,indent=2)+'\n')
        assert result.returncode==0,record
        job=record['output'].split(';')[0]
        print('Submitted school integration '+json.dumps(record),flush=True);continue
    if state in ['COMPLETED','FAILED','CANCELLED','TIMEOUT','OUT_OF_MEMORY','NODE_FAIL','PREEMPTED','BOOT_FAIL','DEADLINE']:
        terminal={'job':job,'state':state,'exit':row[2],'elapsed':row[3]}
        (root/'evidence/terminal-monitor.json').write_text(json.dumps(terminal,indent=2)+'\n')
        break
    time.sleep(60)
else:
    raise SystemExit('Monitor time limit reached; existing job was not restarted or cancelled')
# Preserve diagnostics and immutable provenance, without binaries or dependency build trees.
report={}
for name in ['ippl','kokkos','heffte','gtest','h5hut']:
    path=root/'deps'/(name+'-src')
    report[name]={'sha':subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip(),'status':subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True).strip()}
original=Path('/data/user/adelmann/opalx-dev/opalx-probe-615')
report['original_checkout']={'sha':subprocess.check_output(['git','-C',str(original),'rev-parse','HEAD'],text=True).strip(),'status':subprocess.check_output(['git','-C',str(original),'status','--short','--branch'],text=True).strip()}
(root/'evidence/post-run-repositories.json').write_text(json.dumps(report,indent=2)+'\n')
archive=root/'validation-evidence.tgz'
with tarfile.open(archive,'w:gz') as tar:
    for name in ['evidence','gpu-school','run.sbatch','run-attempt3.sbatch','run-school.sbatch','ffa-school-gpu-fixture-790abac19643.json','build/CMakeCache.txt']:
        path=root/name
        if path.exists():tar.add(path,arcname=name)
summary={'terminal':terminal,'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
print(json.dumps(summary,indent=2),flush=True)
