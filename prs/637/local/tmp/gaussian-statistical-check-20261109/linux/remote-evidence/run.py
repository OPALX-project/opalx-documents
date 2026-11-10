from pathlib import Path
import hashlib,json,os,re,subprocess,time,xml.etree.ElementTree as ET
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');task=root/'gaussian-statistical-20261109';source=root/'src';build=root/'build';out=task/'after';out.mkdir(exist_ok=True)
stage=json.loads((task/'stage.json').read_text());before=stage['before'];inputs=stage['inputs'];cpp=source/inputs['cpp_path'];binary=build/'unit_tests/Distribution/TestGaussian';obj=binary.parent/'CMakeFiles/TestGaussian.dir/TestGaussian.cpp.o';rows=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def phase(name,**other):
 row={'phase':name,'utc_epoch':time.time(),**other};rows.append(row);(out/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
def verify_sources():
 for name,h in stage['expected_source_sha256'].items():assert digest(source/name)==h,name
 assert digest(build/'src/libopalx.so')==before['production_library_sha256']
 assert digest(root/'validation-evidence.tgz')==before['frozen_loss_archive_sha256']
 assert digest(root/'ownership-20261109/validation-evidence.tgz')==before['frozen_ownership_archive_sha256']
def run(command,path,timeout,cwd=None,env=None):
 with path.open('w') as stream:result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,text=True,timeout=timeout,cwd=cwd,env=env)
 return result.returncode
verify_sources();phase('source-verified',source_files=len(stage['expected_source_sha256']))
os.utime(cpp,None)
phase('build-gaussian')
code=run(['cmake','--build',str(build),'--parallel','8','--target','TestGaussian'],out/'build.log',900);assert code==0,('build',code)
proof={'source_sha256':digest(cpp),'source_mtime_ns':cpp.stat().st_mtime_ns,'object_mtime_ns':obj.stat().st_mtime_ns,'binary_mtime_ns':binary.stat().st_mtime_ns,'binary_sha256':digest(binary),'before_binary_sha256':before['gaussian_binary_sha256'],'production_library_sha256':digest(build/'src/libopalx.so')}
assert proof['source_mtime_ns']<=proof['object_mtime_ns']<=proof['binary_mtime_ns'],proof
assert proof['binary_sha256']!=proof['before_binary_sha256'],proof
assert proof['production_library_sha256']==before['production_library_sha256'],proof
(out/'binary-proof.json').write_text(json.dumps(proof,indent=2)+'\n');verify_sources();phase('binary-verified',**proof)
variants=[]
for ranks,threads in [(1,1),(1,4),(2,1),(2,4)]:
 label=f'gaussian-r{ranks}-t{threads}';env=dict(os.environ,OMP_NUM_THREADS=str(threads),IPPL_OPENMP_THREADS=str(threads),KOKKOS_NUM_THREADS=str(threads),OMP_PROC_BIND='false');phase(label)
 code=run(['mpiexec','--bind-to','none','-n',str(ranks),str(binary)],out/(label+'.log'),180,cwd=binary.parent,env=env)
 text=(out/(label+'.log')).read_text();nr=text.count('[ RUN      ]');np=text.count('[       OK ]');nskip=text.count('[  SKIPPED ]')
 row={'label':label,'ranks':ranks,'threads':threads,'returncode':code,'native_cases_run':nr,'native_cases_passed':np,'native_cases_skipped':nskip,'OMP_NUM_THREADS':env['OMP_NUM_THREADS'],'IPPL_OPENMP_THREADS':env['IPPL_OPENMP_THREADS'],'KOKKOS_NUM_THREADS':env['KOKKOS_NUM_THREADS']};variants.append(row);(out/'gaussian-variants.json').write_text(json.dumps(variants,indent=2)+'\n');print(json.dumps(row),flush=True)
 assert code==0 and nr==8*ranks and nr==np and nskip==0,row
phase('distribution-group')
regex='^Test(Gaussian|MultiVariateGaussian|FlatTop|OpalFlatTop|FromFile|EmittedFromFile|Uniform)$'
code=run(['ctest','--test-dir',str(build),'-V','-j4','--output-on-failure','--output-junit',str(out/'distribution.xml'),'-R',regex],out/'distribution.log',600)
assert code==0,('distribution group',code)
group=ET.parse(out/'distribution.xml').getroot();gc=list(group.iter('testcase'));assert len(gc)==7 and not list(group.iter('failure'))and not list(group.iter('error'))
phase('full-suite')
code=run(['ctest','--test-dir',str(build),'-j4','--output-on-failure','--output-junit',str(out/'full-suite.xml')],out/'full-suite.log',1200)
full=ET.parse(out/'full-suite.xml').getroot();cases=list(full.iter('testcase'));bad=[x.attrib['name']for x in cases if x.find('failure')is not None or x.find('error')is not None]
fullrow={'returncode':code,'targets':len(cases),'passed':len(cases)-len(bad),'failed':bad};(out/'full-suite-result.json').write_text(json.dumps(fullrow,indent=2)+'\n');print(json.dumps(fullrow),flush=True)
assert code==0 and len(cases)==137 and not bad,fullrow
verify_sources();assert digest(binary)==proof['binary_sha256']
terminal={'source_files_verified':len(stage['expected_source_sha256']),'changed_file':inputs['cpp_path'],'new_source_sha256':inputs['after_sha256'],'production_library_unchanged':True,'both_prior_archives_unchanged':True,'test_binary_unchanged_during_checks':True,'gaussian_variants':variants,'distribution_targets_passed':len(gc),'full_suite':fullrow}
(out/'terminal.json').write_text(json.dumps(terminal,indent=2)+'\n');phase('complete',**terminal)
