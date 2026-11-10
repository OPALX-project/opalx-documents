from pathlib import Path
import json,subprocess,hashlib,shutil
ROOT=Path('/Users/adelmann/git/opalx');R=Path(__file__).resolve().parent
binary=ROOT/'build-omp/src/opalx'
if binary.exists():
 digest=hashlib.sha256(binary.read_bytes()).hexdigest();backup=ROOT/'build-omp/previous'/('opalx-'+digest[:12]);
 if not backup.exists():shutil.copy2(binary,backup)
(R/'committed-TestSpaceChargeConfig.cpp').write_bytes(subprocess.check_output(['git','show','HEAD:unit_tests/SpaceCharge/TestSpaceChargeConfig.cpp'],cwd=ROOT))
(R/'validation-target.cmake').write_text('''function(add_unified_validation_target)
 add_executable(UnifiedValidationSpaceChargeConfig "'''+str(R/'committed-TestSpaceChargeConfig.cpp')+'''")
 target_link_libraries(UnifiedValidationSpaceChargeConfig PRIVATE opalx GTest::gtest_main)
 target_include_directories(UnifiedValidationSpaceChargeConfig PRIVATE "'''+str(ROOT/'unit_tests')+'''")
endfunction()
cmake_language(DEFER DIRECTORY "${CMAKE_SOURCE_DIR}" CALL add_unified_validation_target)
''')
args=json.loads(Path('/Users/adelmann/git/opalx-build-667-record/configure-commands.json').read_text())['build-omp'];args=[a for a in args if not a.startswith('-DOPALX_ENABLE_UNIT_TESTS=')];args+=['-DOPALX_ENABLE_UNIT_TESTS=ON','-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES='+str(R/'validation-target.cmake')]
(R/'configure-command.json').write_text(json.dumps(args,indent=2)+'\n')
with (R/'configure.log').open('w') as f:subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
with (R/'build.log').open('w') as f:subprocess.run(['cmake','--build',str(ROOT/'build-omp'),'--target','opalx_exe','UnifiedValidationSpaceChargeConfig','--parallel','4'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
meta=dict(branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),src_diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','src'],cwd=ROOT)).hexdigest(),source_note='Build only ~/git/opalx/build-omp; untouched local experimental tests preserved; configuration test compiled from current committed PR source via supplemental CMake target.')
(R/'build-provenance.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
