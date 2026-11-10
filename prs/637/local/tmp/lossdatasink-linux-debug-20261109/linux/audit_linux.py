from pathlib import Path
import argparse,hashlib,json,re,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--checkout',type=Path);args=p.parse_args()
r=args.evidence;before=r/'evidence';final=r/'evidence-final';stress=r/'evidence-stress'
cache=(r/'build/CMakeCache.txt').read_text();assert re.search(r'^CMAKE_BUILD_TYPE:[^=]+=Debug$',cache,re.M);assert re.search(r'^PLATFORMS:[^=]+=OPENMP$',cache,re.M)
manifest=json.loads((before/'source-manifest.json').read_text())
if args.checkout:
 for name,digest in manifest['files'].items():
  expected='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6' if name=='unit_tests/Structure/TestLossDataSink.cpp' else digest
  assert hashlib.sha256((args.checkout/name).read_bytes()).hexdigest()==expected,name
beforelog=(before/'parallel-001.log').read_text()
exact='[  FAILED  ] LossDataSinkTest.RewindH5RemovesCheckpointAndLaterStepsBeforeAppend'
assert exact in beforelog
assert 'Could not open HDF5 file test_monitor_checkpoint_keep_all.h5' in beforelog
isolated=(before/'isolated.log').read_text();assert '100% tests passed' in isolated and '17 tests.' in isolated
junit=ET.parse(final/'full-suite.xml').getroot();cases=list(junit.iter('testcase'));assert len(cases)==137,len(cases)
failed_cases=[x for x in cases if x.find('failure') is not None or x.find('error') is not None]
assert [x.attrib.get('name') for x in failed_cases]==['TestGaussian'],[x.attrib for x in failed_cases]
full_log=(final/'full-suite.log').read_text();assert 'GaussianTest.largeCutoffDisablesTruncation' in full_log and '5.5717775960503042' in full_log
related=ET.parse(stress/'related.xml').getroot();related_cases=list(related.iter('testcase'));assert len(related_cases)==5
assert not list(related.iter('failure')) and not list(related.iter('error'))
assert {x.attrib.get('name') for x in related_cases}=={'TestLossDataSink','TestLossDataSinkMPI','TestCheckpointFile','TestCyclotronProbe','TestCyclotronProbeMPI'}
gaussian=ET.parse(stress/'gaussian-isolated.xml').getroot();gaussian_failed=bool(list(gaussian.iter('failure')) or list(gaussian.iter('error')))
terminal=json.loads((stress/'terminal-verification.json').read_text());assert terminal['pair_iterations']==100 and terminal['pair_failures']==0 and terminal['source_files_verified']==1072
summary=json.loads((stress/'parallel-summary.json').read_text());assert len(summary['runs'])==100 and summary['failed_runs']==0
for i in range(1,101):
 text=(stress/('parallel-%03d.log'%i)).read_text()
 assert '100% tests passed' in text,(i,'CTest')
 assert text.count('[  FAILED  ]')==0,i
 assert '[  PASSED  ] 17 tests.' in text,(i,'17cases')
 assert text.count('[  PASSED  ] 4 tests.')==2,(i,'twoMPIprocesses')
binaries=json.loads((final/'binary-verification.json').read_text())
for name,row in binaries.items():
 assert row['sha256']!=row['baseline_sha256'],name
 assert row['object_mtime']>=row['source_mtime'] and row['binary_mtime']>=row['object_mtime'],name
 assert row['old_fixed_names_absent'] and row['new_owned_directory_label_present'],name
source=json.loads((final/'source-verification.json').read_text());assert source['files_verified']==1072 and source['other_verified_files']==1071
assert source['after_sha256']=='c5f55848a0a2435d5256c9a12bbf7cd3bb09a2dafaf8eb983965bb1a8b8145b6'
basehash=(before/'binaries-corrected.sha256').read_text().splitlines()[0].split()[0]
assert basehash==(final/'library-before.sha256').read_text().strip()
assert basehash==json.loads((stress/'input-metadata.json').read_text())['library_sha256']
assert terminal['library_unchanged'] and terminal['gaussian_binary_unchanged']
leaves=['test_monitor_checkpoint_rewind.h5','test_monitor_checkpoint_keep_all.h5','test_monitor_checkpoint_missing_step.h5','test_monitor_checkpoint_compaction.h5']
traces={};creators={name:[] for name in leaves}
for path in sorted(before.glob('before-strace.*')):
 text=path.read_text(errors='replace');pid=path.name.rsplit('.',1)[-1];calls=[]
 for line in text.splitlines():
  for name in leaves:
   if '"'+name+'"' not in line:continue
   if line.startswith('openat(') and 'O_CREAT' in line:
    creators[name].append(pid);calls.append({'file':name,'operation':'create','line':line})
   if line.startswith('unlink(') or line.startswith('unlinkat('):calls.append({'file':name,'operation':'unlink','success':line.rstrip().endswith('= 0'),'line':line})
 if calls:traces[pid]=calls
cross=[]
for pid,calls in traces.items():
 for row in calls:
  if row['operation']=='unlink' and creators[row['file']] and pid not in creators[row['file']]:cross.append({'pid':pid,**row,'creator_pids':creators[row['file']]})
result={'status':'relevant-tests-passed; full-suite has one unrelated Gaussian failure','baseline':{'isolated_ctest_targets':2,'parallel_pair_iteration':1,'exact_rewind_case_failed':True,'missing_keep_all_file':True,'literal_CI_values_reproduced':False},'final':{'full_suite_targets':len(cases),'full_suite_passed':136,'full_suite_failed':['TestGaussian'],'gaussian_first_failure':'largeCutoffDisablesTruncation:5.5717775960503042 exceeds5.5','gaussian_isolated_passed':not gaussian_failed,'related_targets_passed':len(related_cases),'actual_CMake_build_type':'Debug','actual_platform':'OPENMP','local_checkout_verified':str(args.checkout) if args.checkout else None,'concurrent_pair_iterations':100,'concurrent_ctest_targets':200,'single_rank_case_executions':1700,'two_rank_subset_case_executions':800,'source':source,'binary_proof':binaries,'production_library_sha256_unchanged':basehash},'strace':{'traced_pair_ctest_exit':0,'creator_pids':creators,'cross_process_unlink_attempts':cross,'successful_cross_process_unlinks':sum(x['success'] for x in cross),'traces_with_relevant_calls':traces},'limitations':['Linux Debug/OpenMP on RHEL8/gcc14.3/Kokkos5.2.2, not exact CI Ubuntu26/gcc15.2/Kokkos5.2.0 image','Full local source snapshot registers137targets vs138 at CI synthetic merge; testedLossDataSinksource matchesexactCIfile','MPI target covers four rank/collective fixture contracts; it does not run the seventeen single-rank HDF5 cases','Baseline job terminal1 was a post-test fingerprint-path harness mistake; stale-binary validation was cancelled and replaced; raw history is retained']}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='strace'},indent=2));print('Cross-process unlink attempts:',len(cross),'successful:',sum(x['success'] for x in cross))
