from pathlib import Path
from collections import Counter
import hashlib,json,re,tarfile,xml.etree.ElementTree as ET
root=Path('/Users/adelmann/git/opalx-master');out=root/'tmp/pr637-audit-fixes-20261109/a100'
terminal=json.loads((out/'terminal.json').read_text());assert terminal['state']=='COMPLETED'
archive=out/'validation-evidence.tgz';assert hashlib.sha256(archive.read_bytes()).hexdigest()==terminal['archive_sha256']
remote=out/'remote-native';remote.mkdir(exist_ok=False)
with tarfile.open(archive) as tar:
 for member in tar.getmembers():
  path=Path(member.name);assert not path.is_absolute() and '..' not in path.parts
  assert member.isfile() or member.isdir(),member.name
 tar.extractall(remote)
e=remote/'evidence';tree=ET.parse(e/'junit.xml').getroot()
assert int(tree.attrib['tests'])==6 and int(tree.attrib.get('failures',0))==0 and int(tree.attrib.get('skipped',0))==0,tree.attrib
log=(e/'tests.log').read_text(errors='replace')
runs=Counter(re.findall(r'\[\s*RUN\s*\]\s+([\w.]+)',log))
oks=Counter(re.findall(r'\[\s*OK\s*\]\s+([\w.]+)',log))
assert sum(runs.values())==111,(sum(runs.values()),runs)
assert runs==oks,(runs-oks,oks-runs)
assert '[  SKIPPED ]' not in log and '[  FAILED  ]' not in log
new='RFEventStepTest.ConcurrentFailuresKeepOneCoherentRecordAndAllowResetAndReuse'
sector='CyclotronTest.DeviceParticleFieldMatchesHostIncludingTrim'
assert runs[new]==3 and oks[new]==3,(runs[new],oks[new])
assert runs[sector]==3 and oks[sector]==3
manifest=json.loads((e/'source-manifest.json').read_text());verified=json.loads((e/'source-verification.json').read_text())
assert manifest['source_id']==terminal['source_id']==verified['source_id']
assert verified['files_verified']==len(manifest['files'])==1072
intended=json.loads((root/'tmp/pr637-audit-fixes-20261109/intended-files.json').read_text())
for name,digest in intended['files'].items():
 assert manifest['files'][name]==digest==hashlib.sha256((root/name).read_bytes()).hexdigest(),name
mapping={}
for name in ['TestRFEventStep','TestCyclotronSector','TestCyclotronProbe']:
 for count,suffix in [(1,''),(2,'MPI')]:
  key=name+suffix
  records=[json.loads((e/'gpu-mapping'/(key+'-rank'+str(i)+'.json')).read_text()) for i in range(count)]
  assert len({r['selected_cuda_visible_device'] for r in records})==count,key
  assert len({r['gpu_uuid'] for r in records})==count,key
  mapping[key]=records
build=(e/'build.log').read_text(errors='replace')
assert not re.search(r'(?:fatal\s+)?error\s*:',build,re.I)
report={'job_id':355081,'state':terminal['state'],'accounting':terminal['accounting'],'source_id':manifest['source_id'],'base_head':manifest['base_head'],'source_files_verified':1072,'current_intended_files_verified':6,'ctest':tree.attrib,'gtest_run_executions':sum(runs.values()),'gtest_ok_executions':sum(oks.values()),'gtest_skipped':0,'new_failure_capture_run_ok':runs[new],'extended_sector_test_run_ok':runs[sector],'per_case_executions':dict(runs),'mapping':mapping,'mapping_qualification':'Native job selected distinct CUDA_VISIBLE_DEVICES ordinal tokens per rank and recorded NVML UUIDs via nvidia-smi; runtime UUID API was not queried in this native launcher. The follow-on tracker launcher uses the executable CUDA runtime for stronger physical UUID confirmation.','archive_sha256':terminal['archive_sha256'],'binary_hashes':(e/'binaries.sha256').read_text(),'build_warnings':re.findall(r'^.*warning\s*:.*$',build,re.M|re.I)}
(out/'native-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({key:report[key] for key in ['job_id','state','source_id','source_files_verified','current_intended_files_verified','ctest','gtest_run_executions','gtest_ok_executions','gtest_skipped','new_failure_capture_run_ok','extended_sector_test_run_ok','archive_sha256']},indent=2))
