from pathlib import Path
import subprocess,re,json,os,time
R=Path('/Users/adelmann/git/opalx');O=Path(__file__).resolve().parent;log=(O/'build-keep-going.log').read_text();failed=sorted(set(re.findall(r'make\[2\]: \*\*\* \[unit_tests/[^\n]*?/CMakeFiles/([^/]+)\.dir/',log)));assert failed
(O/'build-failures.json').write_text(json.dumps(dict(targets=failed,compiler_errors=re.findall(r'^.*error:.*$',log,re.M)),indent=2)+'\n');print('Not runnable (compile failures):',failed,flush=True)
rows=[]
for n in [1,4]:
 command=['ctest','--test-dir',str(R/'build-omp'),'-L','unit','-E','^('+'|'.join(failed)+')$','--output-on-failure','--parallel','1','--output-junit',str(O/f'ctest-omp{n}.xml')];start=time.monotonic()
 with (O/f'ctest-omp{n}.log').open('w') as f:p=subprocess.run(command,cwd=R,env=dict(os.environ,OMP_NUM_THREADS=str(n),OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
 rows.append(dict(omp_threads=n,mpi_ranks=1,argv=command,returncode=p.returncode,elapsed_s=time.monotonic()-start));(O/'ctest-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
