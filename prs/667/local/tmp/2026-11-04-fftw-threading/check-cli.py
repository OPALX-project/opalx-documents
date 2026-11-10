from pathlib import Path
import os,subprocess,json
r=Path('/Users/adelmann/git/opalx');o=r/'tmp/2026-11-04-fftw-threading';b=r/'build-omp/src/opalx';env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false');rows=[]
for option in ['--2D5BatchSize','--2D5FFTThreads']:
 for value in [[],['0'],['-1'],['8junk'],['1.5'],['2147483648']]:
  args=[str(b),option,*value];p=subprocess.run(args,cwd=o,env=env,text=True,capture_output=True);assert p.returncode!=0 and option+' requires a positive integer' in p.stdout+p.stderr,(args,p.returncode,p.stdout,p.stderr);rows.append(dict(args=args,returncode=p.returncode,check='invalid option rejected'))
for args in [['--help'],['-h'],['--2D5FFTThreads','4','--2D5BatchSize','8','--input','nonexistent.in'],['--input','nonexistent.in','--2D5BatchSize','8','--2D5FFTThreads','16'],['--restart','missing.h5','--2D5FFTThreads','4','--2D5BatchSize','8','--input','nonexistent.in']]:
 p=subprocess.run([str(b),*args,'--info','1'],cwd=o,env=env,text=True,capture_output=True);text=p.stdout+p.stderr
 if args[0] in ['--help','-h']:assert p.returncode==0 and '--2D5FFTThreads <n>' in text and '--2D5BatchSize <n>' in text
 else:assert p.returncode!=0 and "Input file 'nonexistent.in' doesn't exist!" in text
 rows.append(dict(args=args,returncode=p.returncode,check='help/placement/restart parsing'))
(o/'cli-checks.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),'CLI checks passed')
