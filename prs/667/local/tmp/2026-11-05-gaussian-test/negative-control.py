from pathlib import Path
import subprocess,os,re,json
R=Path('/Users/adelmann/git/opalx');O=Path(__file__).resolve().parent;source=R/'unit_tests/Distribution/TestGaussian.cpp';correct=source.read_bytes();pattern=rb'(const double noCut\s*=\s*)std::numeric_limits<double>::max\(\)';bad,n=re.subn(pattern,rb'\g<1>3.0',correct);assert n==1
result={}
try:
 source.write_bytes(bad)
 with (O/'negative-build.log').open('w') as f:subprocess.run(['cmake','--build',str(R/'build-omp'),'--target','TestGaussian','-j','4'],stdout=f,stderr=subprocess.STDOUT,check=True)
 with (O/'negative-control.log').open('w') as f:p=subprocess.run([str(R/'build-omp/unit_tests/Distribution/TestGaussian'),'--gtest_filter=GaussianTest.largeCutoffDisablesTruncation'],env=dict(os.environ,OMP_NUM_THREADS='4',OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT)
 text=(O/'negative-control.log').read_text();result=dict(returncode=p.returncode,clipped_tails_rejected=p.returncode!=0 and 'phase-space component' in text);assert result['clipped_tails_rejected']
finally:
 source.write_bytes(correct)
 (R/'build-omp/unit_tests/Distribution/CMakeFiles/TestGaussian.dir/TestGaussian.cpp.o').unlink(missing_ok=True)
 with (O/'restored-build.log').open('w') as f:subprocess.run(['cmake','--build',str(R/'build-omp'),'--target','TestGaussian','-j','4'],stdout=f,stderr=subprocess.STDOUT,check=True)
(O/'negative-control.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
