from pathlib import Path
import datetime,hashlib,json,math,os,re,shutil,signal,subprocess,sys,time
root=Path('/data/user/adelmann/opalx-dev/pr637-audit-fixes-20261109/3320cf6fc490')
work=root/'gpu-integration-final';fixture=work/'fixture';runroot=work/'runs';runroot.mkdir(exist_ok=False)
manifest=json.loads((fixture/'fixture-manifest.json').read_text())
for name,sha in manifest['files'].items():assert hashlib.sha256((fixture/name).read_bytes()).hexdigest()==sha,name
binary=root/'build/bin/opalx';binary_sha=hashlib.sha256(binary.read_bytes()).hexdigest()
records=[]
for case in ['valid','failure']:
    for ranks in [1,2]:
        run=runroot/(case+'-r'+str(ranks));shutil.copytree(fixture/case,run)
        mappings=run/'gpu-mapping';mappings.mkdir()
        env=dict(os.environ,AUDIT_GPU_MAP_DIR=str(mappings),OMP_NUM_THREADS='1',IPPL_OPENMP_THREADS='1')
        command=['mpiexec','-n',str(ranks),'--bind-to','none',sys.executable,str(root/'rank_gpu_runtime_attempt2.py'),str(binary),'Cyclotron-RF-Stop.in','--info','2']
        start=time.monotonic();timed_out=False
        with (run/'run.log').open('w') as log:
            process=subprocess.Popen(command,cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=process.wait(timeout=90)
            except subprocess.TimeoutExpired:
                timed_out=True;os.killpg(process.pid,signal.SIGTERM)
                try:code=process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);code=process.wait(timeout=5)
        log=(run/'run.log').read_text(errors='replace').replace('\x00','')
        for name,sha in manifest['files'].items():
            if name.startswith(case+'/'):assert hashlib.sha256((run/name.split('/',1)[1]).read_bytes()).hexdigest()==sha,name
        mapping=[json.loads(path.read_text()) for rank in range(ranks)
                 if (path:=mappings/('opalx-rank'+str(rank)+'.json')).is_file()]
        mapping_ok=(len(mapping)==ranks and len({r['gpu_uuid'] for r in mapping})==ranks
                    and all(r['runtime_device_count']==1 and r['cuda_runtime_library']==r['probe_cuda_runtime_library'] for r in mapping))
        captured=[line for line in log.splitlines() if 'SINGLEGAP failure rank=' in line]
        passed=not timed_out and mapping_ok and ((case=='valid' and code==0 and 'Done executing ParallelTracker' in log) or (case=='failure' and code!=0 and 'SINGLEGAP particle transport failed' in log and bool(captured)))
        if case=='failure':
            for line in captured:
                assert 'cause=field-support' in line,line
                match=re.search(r'id=(\d+).*Rlab\[m\]=\(\s*([^,]+),\s*([^,]+),\s*([^\)]+)\).*Plab\[beta\*gamma\]=\(\s*([^,]+),\s*([^,]+),\s*([^\)]+)\)',line)
                assert match,line
                assert 0<=int(match.group(1))<256,line
                values=[float(x) for x in match.groups()[1:]]
                assert all(math.isfinite(x) for x in values),line
                assert abs(values[1])>1,line
        record=dict(case=case,ranks=ranks,returncode=code,timeout=timed_out,elapsed_s=time.monotonic()-start,passed=passed,command=command,binary_sha256=binary_sha,gpu_mapping=mapping,mapping_ok=mapping_ok,captured_failures=captured,failed_log_tail=log.splitlines()[-20:] if not passed else [],input_sha256=manifest['files'][case+'/Cyclotron-RF-Stop.in'],particle_sha256=manifest['files'][case+'/bunch.dat'])
        (run/'launch.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
        (work/'run-report.json').write_text(json.dumps({'source_id':manifest['source_id'],'runs':records},indent=2)+'\n')
        print(json.dumps({'case':case,'ranks':ranks,'returncode':code,'timeout':timed_out,'passed':passed,'elapsed_s':record['elapsed_s']}),flush=True)
        assert passed,record
assert hashlib.sha256(binary.read_bytes()).hexdigest()==binary_sha
print('All4actualtrackerGPUcheckscompleted; HDF5physicalstatecomparison follows locally.',flush=True)
