from pathlib import Path
import subprocess,os,json
r=Path('/Users/adelmann/git/opalx');o=r/'tmp/2026-11-04-fft2d5-batching';b=r/'build-omp/src/opalx';env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false');records=[]
for args in [[],['0'],['-1'],['1.5'],['8junk'],['2147483648']]:
 p=subprocess.run([str(b),'--2D5BatchSize',*args],cwd=o,env=env,text=True,capture_output=True);assert p.returncode!=0 and '--2D5BatchSize requires a positive integer' in p.stdout+p.stderr,(args,p.returncode,p.stdout,p.stderr);records.append(dict(args=args,returncode=p.returncode,check='invalid size rejected'))
for args in [['--help'],['-h'],['--2D5BatchSize','8','--input','nonexistent.in'],['--input','nonexistent.in','--2D5BatchSize','64']]:
 p=subprocess.run([str(b),*args,*([] if args[0] in ['--help','-h'] else ['--info','1'])],cwd=o,env=env,text=True,capture_output=True);out=p.stdout+p.stderr
 if args[0] in ['--help','-h']:assert p.returncode==0 and '--2D5BatchSize <n>' in out
 else:assert p.returncode!=0 and "Input file 'nonexistent.in' doesn't exist!" in out
 records.append(dict(args=args,returncode=p.returncode,check='OPALX help/argument placement accepted'))
(o/'cli-checks.json').write_text(json.dumps(records,indent=2)+'\n');print('10 CLI checks passed')
