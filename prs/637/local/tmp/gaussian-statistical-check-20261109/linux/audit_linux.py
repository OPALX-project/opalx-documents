from pathlib import Path
import argparse,hashlib,json,re,xml.etree.ElementTree as ET
parser=argparse.ArgumentParser();parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--checkout',type=Path);args=parser.parse_args();e=args.evidence;a=e/'after';b=e/'before'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stage=json.loads((e/'stage.json').read_text());inputs=stage['inputs'];assert inputs['cpp_path']=='unit_tests/Distribution/TestGaussian.cpp'
assert inputs['before_sha256']=='0dc5c3c23ca4921838e4a6a771ae6d3ba3cdc4e6765d52f56d33d5a925449477'
assert inputs['after_sha256']=='6569cabdd647bd40dcbbeb280819aca92ea724b5f06b30972975b5bf830fa4ce'
assert len(stage['expected_source_sha256'])==1073
if args.checkout:
 for name,h in stage['expected_source_sha256'].items():assert digest(args.checkout/name)==h,name
cache=(e/'build/CMakeCache.txt').read_text();assert re.search(r'^CMAKE_BUILD_TYPE:[^=]+=Debug$',cache,re.M) and re.search(r'^PLATFORMS:[^=]+=OPENMP$',cache,re.M)
assert digest(b/'original-TestGaussian.cpp')==inputs['before_sha256']
old=(b/'prior-full-suite.log').read_text();assert '5.5717775960503042' in old and 'GaussianTest.largeCutoffDisablesTruncation' in old
proof=json.loads((a/'binary-proof.json').read_text());assert proof['source_sha256']==inputs['after_sha256'];assert proof['source_mtime_ns']<=proof['object_mtime_ns']<=proof['binary_mtime_ns'];assert proof['binary_sha256']!=proof['before_binary_sha256'];assert proof['production_library_sha256']==stage['before']['production_library_sha256']
variants=json.loads((a/'gaussian-variants.json').read_text());assert len(variants)==4 and {(x['ranks'],x['threads'])for x in variants}=={(1,1),(1,4),(2,1),(2,4)}
passed=0
for row in variants:
 text=(a/(row['label']+'.log')).read_text();n=text.count('[       OK ]');assert row['returncode']==0 and n==row['native_cases_run']==row['native_cases_passed']==8*row['ranks'];assert row['native_cases_skipped']==0 and '[  SKIPPED ]'not in text
 assert row['KOKKOS_NUM_THREADS']==row['OMP_NUM_THREADS']==str(row['threads']);assert 'GaussianTest.largeCutoffDisablesTruncation'in text;passed+=n
assert passed==48
related=ET.parse(a/'distribution.xml').getroot();rc=list(related.iter('testcase'));assert len(rc)==7 and not list(related.iter('failure')) and not list(related.iter('error'))
assert {x.attrib['name']for x in rc}=={'TestGaussian','TestMultiVariateGaussian','TestFlatTop','TestOpalFlatTop','TestFromFile','TestEmittedFromFile','TestUniform'}
full=ET.parse(a/'full-suite.xml').getroot();fc=list(full.iter('testcase'));assert len(fc)==137 and not list(full.iter('failure')) and not list(full.iter('error')) and not list(full.iter('skipped'))
terminal=json.loads((a/'terminal.json').read_text());assert terminal['source_files_verified']==1073 and terminal['distribution_targets_passed']==7 and terminal['full_suite']['passed']==137 and terminal['full_suite']['returncode']==0 and not terminal['full_suite']['failed']
assert terminal['production_library_unchanged'] and terminal['both_prior_archives_unchanged'] and terminal['test_binary_unchanged_during_checks']
job=json.loads((e/'submission.json').read_text());account=(e/'job-accounting.txt').read_text();assert re.search('^'+str(job['job_id'])+r'\|COMPLETED\|0:0\|',account,re.M)
result={'status':'all Gaussian and related Linux checks passed','job_id':job['job_id'],'job_terminal':'COMPLETED0:0','source_files_verified_against_checkout':1073 if args.checkout else None,'sole_source_change':inputs['cpp_path'],'before_source_sha256':inputs['before_sha256'],'after_source_sha256':inputs['after_sha256'],'source_and_binary_rebuilt_proof':proof,'gaussian_variants':variants,'gaussian_native_case_executions':48,'gaussian_skips':0,'distribution_targets_passed':7,'full_suite_targets_passed':137,'full_suite_failures':0,'production_library_unchanged_sha256':stage['before']['production_library_sha256'],'both_prior_archives_unchanged':True,'limits':['CPU Debug/OpenMP on Merlin6, GCC14.3/OpenMPI5/CMake4.4; not an exact GitHub Ubuntu image','Same default seed and N100000; no retry-until-pass or production changes','Default one-rank ORB cases in full suite can internally skip; their explicit MPI coverage was validated in prior frozen ownership task']}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
