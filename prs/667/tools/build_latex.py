"""Stage archived text/figure dependencies and compile all standalone TeX sources.

Usage: ~/.venv-h6/bin/python tools/build_latex.py --output /tmp/pr667-latex
No tracking runs or plot/data regeneration are performed. PDFs and auxiliaries
are written only to the chosen output directory, never into the text archive.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,re,shutil,subprocess,time
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
archive=Path(__file__).resolve().parents[1];repo=archive.parents[1];index=json.loads((archive/'latex-inventory.json').read_text());rows=[r for name in index['parts'] for r in json.loads((archive/name).read_text())];stage=a.output/'staged-checkout';stage.mkdir(parents=True,exist_ok=True)
for x in rows:
 if x['disposition'] not in ['text-source','figure-asset']:continue
 src=repo/x['archive'];assert hashlib.sha256(src.read_bytes()).hexdigest()==x['sha256'],src
 dst=stage/x['original'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 if dst.suffix in ['.tex','.tikz']:
  dst.write_text(dst.read_text().replace('/Users/adelmann/git/opalx/',str(stage.resolve())+'/'))
roots=[]
for x in rows:
 if x['disposition']=='text-source' and Path(x['original']).suffix=='.tex':
  src=stage/x['original']
  if re.search(r'\\documentclass\b',src.read_text()):roots.append(src)

def build(src):
 key=src.relative_to(stage).as_posix().replace('/','--');out=a.output/'builds'/key;out.mkdir(parents=True,exist_ok=True)
 cwd=src.parent.parent if src.parent.name=='.build' else src.parent
 cmd=['latexmk','-pdf','-halt-on-error','-interaction=nonstopmode','-file-line-error','-recorder','-outdir='+str(out),str(src.relative_to(cwd))]
 start=time.monotonic()
 with (out/'command.log').open('w') as f:r=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT)
 log=(out/(src.stem+'.log'));text=log.read_text(errors='replace') if log.exists() else (out/'command.log').read_text(errors='replace')
 pdf=out/(src.stem+'.pdf')
 row=dict(source=src.relative_to(stage).as_posix(),returncode=r.returncode,pdf=str(pdf) if pdf.exists() else None,elapsed_seconds=time.monotonic()-start,log=str(out/'command.log'),missing_references=bool(re.search('There were undefined references|There were undefined citations',text)))
 print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(build,roots))
(a.output/'compile-results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(x['returncode']==0 for x in results),'LaTeX build failures; see compile-results.json'
print('Compiled',len(results),'standalone documents.')
