from pathlib import Path
import argparse,hashlib,json,re,tarfile,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--checkout',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();r=args.evidence
m=json.loads((r/'manifest.json').read_text());stage=json.loads((r/'stage.json').read_text());before=json.loads((r/'before/inventory.json').read_text());terminal=json.loads((r/'after/terminal.json').read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert len(m['files'])==30 and len(m['targets'])==29
assert len(stage['expected_source_sha256'])==1073
assert set(stage['expected_source_sha256'])==set(before['source_sha256'])|{'unit_tests/TemporaryDirectory.h'}
changed={name for name,h in stage['expected_source_sha256'].items()if before['source_sha256'].get(name)!=h};assert changed==set(m['files']),changed
for name,h in stage['expected_source_sha256'].items():assert digest(args.checkout/name)==h,name
for name,h in m['prior_files_unchanged'].items():assert digest(args.checkout/name)==h,name
assert all(name.startswith('unit_tests/')and Path(name).suffix in ['.cpp','.h']for name in changed)
cache=(r/'build/CMakeCache.txt').read_text();assert re.search(r'^CMAKE_BUILD_TYPE:[^=]+=Debug$',cache,re.M);assert re.search(r'^PLATFORMS:[^=]+=OPENMP$',cache,re.M)
assert digest(r/'source-update.tgz')==json.loads((r/'source-update.json').read_text())['archive_sha256']
with tarfile.open(r/'source-update.tgz')as archive:
 for name,h in m['files'].items():assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==h,name

def junit(path,n):
 e=ET.parse(path).getroot();cases=list(e.iter('testcase'));assert len(cases)==n,(path,len(cases));bad=[c.attrib['name']for c in cases if c.find('failure')is not None or c.find('error')is not None];return cases,bad
_,bad=junit(r/'before/isolated.xml',2);assert not bad
old=(r/'before/parallel-001.log').read_text();old_failed=set(re.findall(r'\[  FAILED  \]\s+([A-Za-z_]\w*\.\w+)',old));assert len(old_failed)==10,old_failed
assert 'filesystem error: cannot remove: Directory not empty [/tmp/opalx_fm2d_test]'in old
_,bad=junit(r/'after/affected.xml',29);assert not bad
proof=json.loads((r/'after/binary-proof.json').read_text());assert set(proof)==set(m['targets'])
compiled=set(re.findall(r'Building CXX object unit_tests/[^\n]+/CMakeFiles/(\w+)\.dir/',(r/'after/build.log').read_text()));assert compiled==set(m['targets']),(compiled,set(m['targets'])-compiled)
for name,row in proof.items():
 assert row['sha256']!=row['baseline_sha256']==stage['baseline_binary_sha256'][name],name
 assert row['source_mtime_ns']<=row['object_mtime_ns']<=row['binary_mtime_ns'],name
 source_name=next(n for n in m['files'] if n.endswith('/'+name+'.cpp'))
 assert row['source_sha256']==m['files'][source_name],name
field_rows=json.loads((r/'after/fm2d-summary.json').read_text());assert len(field_rows)==20 and all(x['returncode']==0 for x in field_rows)
for i in range(1,21):
 text=(r/('after/fm2d-%03d.log'%i)).read_text();assert '100% tests passed'in text and '[  FAILED  ]'not in text
 assert text.count('[       OK ]')==42,(i,text.count('[       OK ]'));assert '[  SKIPPED ]'not in text
manual=json.loads((r/'after/manual-mpi.json').read_text());assert len(manual)==5
counts={'checkpoint-r2':4,'multicontainer-rewind-r2':2,'orb-updater-r2':2,'orb-load-balancing-r4':8,'fft2d5-reject-r2':2}
for row in manual:
 text=(r/'after'/(row['name']+'.log')).read_text();n=counts[row['name']]
 assert row['returncode']==0 and row['run_cases']==row['passed_cases']==n and row['skipped_cases']==0,row
 assert text.count('[       OK ]')==n and '[  FAILED  ]'not in text and '[  SKIPPED ]'not in text,row
full,bad=junit(r/'after/full-suite.xml',137);assert bad==['TestGaussian'],bad
fulltext=(r/'after/full-suite.log').read_text();assert '5.5717775960503042'in fulltext and '[  FAILED  ] GaussianTest.largeCutoffDisablesTruncation'in fulltext
assert terminal['source_files_verified']==1073 and terminal['changed_files']==30 and terminal['affected_targets_passed']==29
assert terminal['production_library_unchanged']and terminal['source_and_test_binaries_unchanged_during_checks']and terminal['prior_archive_unchanged']
assert stage['production_library_sha256']==before['binary_sha256']['src/libopalx.so']
accounting=json.loads((r/'task-jobs-terminal.json').read_text());assert accounting['queue_empty'];assert all(accounting['accounting'][str(j)][1:3]==['COMPLETED','0:0']for j in[355094,355096])
result={'status':'ownership fixes and all affected checks passed; full suite retains known Gaussian failure','before':{'isolated_targets_passed':2,'first_concurrent_pair_failed':True,'failed_native_cases':sorted(old_failed),'direct_error':'Directory not empty [/tmp/opalx_fm2d_test]'},'after':{'job':355096,'job_terminal':'COMPLETED0:0','source_files_verified_against_current_checkout':1073,'changed_files':30,'prior7files_unchanged':True,'affected_targets_passed':29,'freshly_compiled_and_relinked_target_count':len(proof),'fm2d_pairs_passed':20,'fm2d_native_case_executions':840,'fm2d_skips':0,'manual_mpi':manual,'manual_native_case_executions':sum(counts.values()),'manual_skips':0,'full_suite_passed':136,'full_suite_total':137,'full_suite_failed':bad,'gaussian_concrete_failure':'5.5717775960503042 exceeds5.5 maximum; unchanged','production_library_sha256_unchanged':stage['production_library_sha256'],'prior_archive_sha256_unchanged':stage['prior_archive_sha256']},'scope':['All30intended files are unit-test C++ sources/header only; production and CMake source hashes unchanged','Existing seven audit/loss files unchanged','Default load-balancing target skips without4ranks; explicit4rankrun executes its8native case instances','No Gaussian source/seed/tolerance change or additional Gaussian rerun','No commit or push; task jobs355094and355096terminal'],'environment':['Linux kernel5.14el9_8 onmerlin-g-100, GCC14.3/OpenMPI5/CMake4.4, CPU Debug/OpenMP,4OMPthreads','SSHloginRHEL8.10 is not used to infer compute-node userland','Kokkos5.2.2 differs from CI5.2.0; not exact GitHubUbuntu image']}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
