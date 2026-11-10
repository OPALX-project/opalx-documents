from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time,xml.etree.ElementTree as ET
root=Path(sys.argv[1]);task=Path(sys.argv[2]);source=root/'src';build=root/'build';out=task/'after';out.mkdir(exist_ok=True)
manifest=json.loads((task/'manifest.json').read_text());stage=json.loads((task/'stage.json').read_text());targets=manifest['targets'];phase_rows=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phase(name,**extra):
 row={'phase':name,'utc_epoch':time.time(),**extra};phase_rows.append(row);(out/'progress.json').write_text(json.dumps(phase_rows,indent=2));print(json.dumps(row),flush=True)
def verify_sources():
 for name,h in stage['expected_source_sha256'].items():assert digest(source/name)==h,name
 assert digest(root/'validation-evidence.tgz')==stage['prior_archive_sha256']
 assert digest(build/'src/libopalx.so')==stage['production_library_sha256']
verify_sources();phase('source-verified',source_files=len(stage['expected_source_sha256']))
for name in manifest['files']:os.utime(source/name,None)
listing=json.loads(subprocess.check_output(['ctest','--test-dir',str(build),'--show-only=json-v1'],text=True));entries={x['name']:x for x in listing['tests']}
cpp_by_target={Path(n).stem:n for n in manifest['files'] if n.endswith('.cpp')}
paths={}
for name in targets:
 entry=entries[name];matches=[Path(x) for x in entry['command'] if Path(x).name==name];assert len(matches)==1,(name,matches)
 binary=matches[0];src=source/cpp_by_target[name];obj=binary.parent/'CMakeFiles'/(name+'.dir')/(src.name+'.o')
 paths[name]={'binary':binary,'source':src,'object':obj}
def execute(command,path,timeout,cwd=None):
 with path.open('w') as stream:
  result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,text=True,cwd=cwd,timeout=timeout)
 return result.returncode
phase('build',target_count=len(targets))
code=execute(['cmake','--build',str(build),'--parallel','32','--target',*targets],out/'build.log',1800)
assert code==0,('build',code)
proof={}
for name,p in paths.items():
 binary=p['binary'];src=p['source'];obj=p['object'];h=digest(binary)
 row={'sha256':h,'baseline_sha256':stage['baseline_binary_sha256'][name],'binary':str(binary),'object':str(obj),'source':str(src),'source_sha256':digest(src),'source_mtime_ns':src.stat().st_mtime_ns,'object_mtime_ns':obj.stat().st_mtime_ns,'binary_mtime_ns':binary.stat().st_mtime_ns}
 assert row['object_mtime_ns']>=row['source_mtime_ns'],row
 assert row['binary_mtime_ns']>=row['object_mtime_ns'],row
 assert h!=row['baseline_sha256'],row
 proof[name]=row
verify_sources();(out/'binary-proof.json').write_text(json.dumps(proof,indent=2));phase('binaries-verified',count=len(proof))
regex='^('+'|'.join(re.escape(n) for n in targets)+')$'
phase('affected-targets')
code=execute(['ctest','--test-dir',str(build),'-V','-j4','--output-on-failure','--output-junit',str(out/'affected.xml'),'-R',regex],out/'affected.log',1200)
assert code==0,('affected targets',code)
phase('fm2d-stress')
rows=[]
for iteration in range(1,21):
 code=execute(['ctest','--test-dir',str(build),'-V','-j2','--output-on-failure','-R','^TestFM2D(Dynamic|MagnetoStatic)$'],out/('fm2d-%03d.log'%iteration),90)
 rows.append({'iteration':iteration,'returncode':code});(out/'fm2d-summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[-1]),flush=True)
 assert code==0,('FM2D stress',iteration,code)
phase('manual-mpi')
manual=[('checkpoint-r2','TestCheckpointFile',2,None),('multicontainer-rewind-r2','TestMultiContainerPartBunch',2,'MultiContainerPartBunchTest.DataSink_RewindToCheckpointAppendsDiagnosticH5InPlace'),('orb-updater-r2','TestCartesianDomainUpdaterORB',2,None),('orb-load-balancing-r4','TestCartesianDomainLoadBalancing',4,None),('fft2d5-reject-r2','TestFFT2D5Numerics',2,'TestSolve2d5.Configuration_MultipleRanksRejected')]
manual_rows=[]
for label,name,ranks,select in manual:
 binary=paths[name]['binary'];command=['mpiexec','--bind-to','none','-n',str(ranks),str(binary)]
 if select:command.append('--gtest_filter='+select)
 code=execute(command,out/(label+'.log'),180,cwd=binary.parent)
 text=(out/(label+'.log')).read_text()
 row={'name':label,'target':name,'ranks':ranks,'filter':select,'returncode':code,'run_cases':len(re.findall(r'\[ RUN      \]',text)),'passed_cases':len(re.findall(r'\[       OK \]',text)),'skipped_cases':len(re.findall(r'\[  SKIPPED \]',text))}
 manual_rows.append(row);(out/'manual-mpi.json').write_text(json.dumps(manual_rows,indent=2));print(json.dumps(row),flush=True)
 assert code==0 and row['run_cases']>0 and row['run_cases']==row['passed_cases'] and row['skipped_cases']==0,row
phase('full-suite')
code=execute(['ctest','--test-dir',str(build),'-j4','--output-on-failure','--output-junit',str(out/'full-suite.xml')],out/'full-suite.log',1200)
junit=ET.parse(out/'full-suite.xml').getroot();cases=list(junit.iter('testcase'));bad=[c.attrib['name'] for c in cases if c.find('failure') is not None or c.find('error') is not None]
assert len(cases)==137,len(cases)
assert bad in ([],['TestGaussian']),bad
if bad:
 text=(out/'full-suite.log').read_text();failed=set(re.findall(r'\[  FAILED  \]\s+([A-Za-z_]\w*\.\w+)',text));assert failed=={'GaussianTest.largeCutoffDisablesTruncation'},failed
full={'returncode':code,'targets':len(cases),'passed':len(cases)-len(bad),'failed':bad,'known_gaussian_failure_retained':bool(bad)}
(out/'full-suite-result.json').write_text(json.dumps(full,indent=2));print(json.dumps(full),flush=True)
verify_sources()
for name,p in paths.items():assert digest(p['binary'])==proof[name]['sha256'],name
terminal={'source_files_verified':len(stage['expected_source_sha256']),'changed_files':len(manifest['files']),'affected_targets_passed':len(targets),'fm2d_concurrent_pairs_passed':len(rows),'manual_mpi_cases':manual_rows,'full_suite':full,'production_library_unchanged':True,'source_and_test_binaries_unchanged_during_checks':True,'prior_archive_unchanged':True}
(out/'terminal.json').write_text(json.dumps(terminal,indent=2));phase('complete',**terminal)
