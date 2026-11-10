from pathlib import Path
import subprocess,json,os,time
R=Path('/Users/adelmann/git/opalx');O=R/'tmp/2026-11-05-all-unit-tests';P='/Users/adelmann/.venv-h6/bin/python'
directories=['tools','tools/toOPALX','tools/toOPALX/opal2opalx','tools/toOPALX/astra2opalx','tools/toOPALX/astra2opalx/dev_tests','tools/toOPALX/elegant2opalx','tools/toOPALX/elegant2opalx/dev_tests'];rows=[]
for i,relative in enumerate(directories):
 d=R/relative;name=f'python-{i}';args=[P,'-m','unittest','discover','-s',str(d),'-p','test*.py','-v'];started=time.monotonic();env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MPLCONFIGDIR='/tmp/opalx-unit-mpl')
 with (O/(name+'.log')).open('w') as log:p=subprocess.run(args,cwd=d,env=env,stdout=log,stderr=subprocess.STDOUT)
 rows.append(dict(directory=relative,argv=args,returncode=p.returncode,elapsed_s=time.monotonic()-started,log=str(O/(name+'.log'))));(O/'python-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
raise SystemExit(any(r['returncode'] for r in rows))
