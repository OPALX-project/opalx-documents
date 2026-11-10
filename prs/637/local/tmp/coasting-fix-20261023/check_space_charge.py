from coast_data import *
import shutil,subprocess,os
repo=root.parents[1]
for name in ['Cyclotron-SC-Midpoint','Cyclotron-SC-Prestep']:
 src=Path('/Users/adelmann/git/regression-tests-x/RegressionTests')/name;dst=root/name;shutil.copytree(src,dst)
 with (dst/'run.log').open('w') as f:subprocess.run(['mpirun','-np','1',str(repo/'build_openmp/src/opalx'),name+'.in','--info','2'],cwd=dst,env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false'),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300)
 a=stat(dst/(name+'.stat')).iloc[-1];b=stat(src/'reference'/(name+'.stat')).iloc[-1]
 for line in (src/(name+'.rt')).read_text().splitlines()[1:]:
  match=re.fullmatch(r'stat "([^"]+)" last (\S+)',line)
  key,tol=match.groups();error=abs(a[key]-b[key]);assert error<=float(tol),(name,key,error,tol)
 print(name,'all 17 existing final-stat bounds passed',flush=True)
