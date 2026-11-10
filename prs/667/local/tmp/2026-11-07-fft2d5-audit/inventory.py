"""Lexical length inventory for qualified FFT2D5 method definitions (not an AST)."""
from pathlib import Path
import re,csv,subprocess
out=Path(__file__).resolve().parent
rows=[]
# Blank comments and literals while retaining line positions and brace offsets.
token=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
def blank(m):return ''.join('\n' if c=='\n' else ' ' for c in m[0])
for p in sorted(Path('src/SpaceCharge/FFT2D5').glob('*')):
 if p.suffix not in ['.cpp','.hpp']:continue
 t=p.read_text();z=token.sub(blank,t)
 for m in re.finditer(r'(?P<name>(?:[A-Za-z_]\w*::)+[A-Za-z_~]\w*)\s*\(',z):
  start=m.start();line=z.count('\n',0,start)+1
  # Calls have non-whitespace expression prefixes on their source line.
  prefix=z[z.rfind('\n',0,start)+1:start]
  if re.search(r'[=;{}]|return|throw|\.',prefix):continue
  par=z.find('(',start);depth=1;i=par+1
  while i<len(z) and depth:
   depth+=(z[i]=='(')-(z[i]==')');i+=1
  j=i
  while j<len(z) and z[j] not in '{};':j+=1
  if j>=len(z) or z[j]!='{':continue
  # Exclude call expressions within another method by signature prefix shape.
  if ')' in prefix:continue
  depth=1;k=j+1
  while k<len(z) and depth:
   depth+=(z[k]=='{')-(z[k]=='}');k+=1
  end=z.count('\n',0,k)+1
  name=m['name'];rows.append(dict(file=str(p),name=name,start=line,end=end,lines=end-line+1))
# Deduplicate and retain real out-of-line signatures; manually review inventory.
rows=[dict(zip(['file','name','start','end','lines'],x)) for x in dict.fromkeys(tuple(q.values()) for q in rows)]
with (out/'method-lengths.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['file','name','start','end','lines']);w.writeheader();w.writerows(rows)
for q in sorted(rows,key=lambda x:x['lines'],reverse=True):
 if q['lines']>=45:print(q)
