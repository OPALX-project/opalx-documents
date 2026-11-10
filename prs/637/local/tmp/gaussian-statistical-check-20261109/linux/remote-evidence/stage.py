from pathlib import Path
import hashlib,json,os
root=Path('/data/user/adelmann/opalx-dev/lossdatasink-linux-debug-20261109/baseline-3320cf6fc490');task=root/'gaussian-statistical-20261109';source=root/'src';build=root/'build'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((task/'before/inventory.json').read_text());inputs=json.loads((task/'input.json').read_text())
assert inputs['cpp_path']=='unit_tests/Distribution/TestGaussian.cpp'
assert inputs['before_sha256']==before['gaussian_cpp_sha256']
for name,h in before['source_sha256'].items():assert digest(source/name)==h,name
assert digest(build/'src/libopalx.so')==before['production_library_sha256']
assert digest(build/'unit_tests/Distribution/TestGaussian')==before['gaussian_binary_sha256']
assert digest(root/'validation-evidence.tgz')==before['frozen_loss_archive_sha256']
assert digest(root/'ownership-20261109/validation-evidence.tgz')==before['frozen_ownership_archive_sha256']
fixed=task/'fixed-TestGaussian.cpp';assert digest(fixed)==inputs['after_sha256']
path=source/inputs['cpp_path'];path.write_bytes(fixed.read_bytes());os.utime(path,None);assert digest(path)==inputs['after_sha256']
expected=dict(before['source_sha256']);expected[inputs['cpp_path']]=inputs['after_sha256']
for name,h in expected.items():assert digest(source/name)==h,name
record={'inputs':inputs,'expected_source_sha256':expected,'before':{k:v for k,v in before.items()if k!='source_sha256'},'source_files_verified':len(expected),'source_write_method':'write_bytes+utime; no preserved staging timestamps'}
(task/'stage.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items()if k!='expected_source_sha256'}))
