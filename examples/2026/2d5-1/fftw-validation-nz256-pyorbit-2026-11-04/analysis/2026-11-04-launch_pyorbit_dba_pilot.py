from pathlib import Path
import subprocess,os,time,json
R=Path(__file__).resolve().parent;P='/Users/adelmann/.venv-h6/bin/python'
assert (R/'pr-fftw-repeat/phase1-complete.json').exists()
assert len(json.loads((R/'dba-nz256/summary.json').read_text())['rows'])==2
O=R/'dba-pyorbit-pilot';O.mkdir(exist_ok=True)
for repeat in [1,2]:
 for nz in ([512,256] if repeat==1 else [256,512]):
  command=[P,str(R/'run_pyorbit_dba_pilot.py'),'--nz',str(nz),'--repeat',str(repeat)];start=time.monotonic()
  with (O/f'launch-{nz}-{repeat}.log').open('w') as f:proc=subprocess.run(command,env=dict(os.environ,PYTHONPATH='/Users/adelmann/git/OPALX-2D5/curved-study/triangle-pipe/pyorbit/native-package',OMP_NUM_THREADS='4',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
  result=dict(argv=command,returncode=proc.returncode,launch_wall_s=time.monotonic()-start);(O/f'launch-{nz}-{repeat}.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True);assert proc.returncode==0
