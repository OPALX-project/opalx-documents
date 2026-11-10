"""Safely reconstruct recorded literal writes in memory; execute no journal code."""
import ast,json,re,hashlib
from pathlib import Path
OUT=Path('/Users/adelmann/git/opalx-documents/prs/667');ROOT=Path('/Users/adelmann/git/opalx');rows=json.loads((OUT/'inventory.json').read_text());missing=[x for x in rows if x['disposition']=='repository-copy' and not (OUT/x['archive']).is_file()];need={x['sha256']:x for x in missing};virtual={};recovered=[]
class Unknown:pass
U=Unknown()
def offer(v,where):
 if not isinstance(v,(str,bytes)):return
 b=v.encode() if isinstance(v,str) else v;h=hashlib.sha256(b).hexdigest()
 if h in need:
  for x in missing:
   if x['sha256']==h and not (OUT/x['archive']).exists():
    p=OUT/x['archive'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);recovered.append(dict(original=x['original'],sha256=h,method=where))
def read(p):
 p=str(p)
 if p in virtual:return virtual[p]
 try:
  q=Path(p)
  rel=q.relative_to(ROOT).as_posix() if q.is_absolute() else q.as_posix()
  x=next(x for x in rows if x['original']==rel and x.get('archive'))
  if (OUT/x['archive']).is_file():return (OUT/x['archive']).read_text()
 except Exception:pass
 return U

def ev(n,e):
 try:
  if isinstance(n,ast.Constant):return n.value
  if isinstance(n,ast.Name):return e.get(n.id,U)
  if isinstance(n,(ast.List,ast.Tuple)):return [ev(x,e) for x in n.elts]
  if isinstance(n,ast.BinOp):
   a,b=ev(n.left,e),ev(n.right,e)
   if isinstance(n.op,ast.Div) and isinstance(a,(str,Path)) and isinstance(b,str):return Path(a)/b
   if isinstance(n.op,ast.Add):return a+b
  if isinstance(n,ast.JoinedStr):return ''.join(str(ev(x.value,e)) if isinstance(x,ast.FormattedValue) else x.value for x in n.values)
  if isinstance(n,ast.Call):
   a=[ev(v,e) for v in n.args]
   if isinstance(n.func,ast.Name):
    if n.func.id=='Path' and isinstance(a[0],str):return Path(a[0])
    if n.func.id=='str' and not isinstance(a[0],Unknown):return str(a[0])
   if isinstance(n.func,ast.Attribute):
    obj=ev(n.func.value,e);name=n.func.attr
    if isinstance(obj,(Path,str)) and name in ['write_text','write_bytes'] and a and isinstance(a[0],(str,bytes)):
     virtual[str(obj)]=a[0];offer(a[0],'journal-write-replay');return len(a[0])
    if isinstance(obj,(Path,str)) and name=='read_text':return read(obj)
    if isinstance(obj,str) and name in ['replace','strip','rstrip','lstrip','format','join']:return getattr(obj,name)(*a)
    if isinstance(obj,Path) and name=='resolve':return obj
    if isinstance(obj,Path) and name=='open':return ('file',obj,a[0] if a else 'r')
    if isinstance(obj,tuple) and obj[0]=='file' and name=='write' and isinstance(a[0],str):
     p=str(obj[1]);base=virtual.get(p,read(p)) if 'a' in obj[2] else ''
     if isinstance(base,str):virtual[p]=base+a[0];offer(virtual[p],'journal-append-replay')
  if isinstance(n,ast.Attribute):
   obj=ev(n.value,e)
   if isinstance(obj,Path) and n.attr=='parent':return obj.parent
 except Exception:pass
 return U

def run(body,e):
 for n in body:
  if isinstance(n,ast.Assign):
   v=ev(n.value,e)
   for t in n.targets:
    if isinstance(t,ast.Name):e[t.id]=v
  elif isinstance(n,ast.Expr):ev(n.value,e)
  elif isinstance(n,ast.With):
   for item in n.items:
    if isinstance(item.optional_vars,ast.Name):e[item.optional_vars.id]=ev(item.context_expr,e)
   run(n.body,e)
  elif isinstance(n,ast.For):
   values=ev(n.iter,e)
   if isinstance(values,list) and len(values)<1000:
    for v in values:
     if isinstance(n.target,ast.Name):e[n.target.id]=v
     run(n.body,e)
  elif isinstance(n,(ast.If,ast.Try)):
   run(n.body,e);run(n.orelse,e)

for cmd in json.loads(Path('/tmp/pr667-journal-commands.json').read_text()):
 for m in re.finditer(r"<<\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\1(?:\n|$)",cmd,re.S):
  block=m[2]
  try:run(ast.parse(block).body,{})
  except Exception:pass
 for m in re.finditer(r"cat\s*(>>?)\s*([^\s]+)\s*<<\s*['\"]?(\w+)['\"]?\n(.*?)\n\3(?:\n|$)",cmd,re.S):
  p=m[2].strip('"\'');p=str(ROOT/p) if not p.startswith('/') else p
  b=m[4]+'\n';base=virtual.get(p,read(p)) if m[1]=='>>' else ''
  if isinstance(base,str):virtual[p]=base+b;offer(virtual[p],'journal-shell-replay')
(OUT/'recovery-replay.json').write_text(json.dumps(recovered,indent=2)+'\n');print('Replayed exact recovered',len(recovered),'of',len(missing),'files')
