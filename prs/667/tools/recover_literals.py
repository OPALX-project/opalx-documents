from pathlib import Path
import ast,json,re,hashlib,subprocess
OUT=Path('/Users/adelmann/git/opalx-documents/prs/667');rows=json.loads((OUT/'inventory.json').read_text());missing=[x for x in rows if x['disposition']=='repository-copy' and not (OUT/x['archive']).is_file()];need={x['sha256']:x for x in missing};found={};cmds=[]
def offer(v,where):
 if not isinstance(v,str):return
 for b in [v.encode(),(v+'\n').encode(),v.replace('\\n','\n').encode()]:
  h=hashlib.sha256(b).hexdigest()
  if h in need:found[h]=(b,where)
for log in [next(Path('/Users/adelmann/.codex/sessions/2026/10/29').glob('*01a18862*')),next(Path('/Users/adelmann/.codex/sessions/2026/11/07').glob('*01a1b54b*'))]:
 for line in log.open():
  q=json.loads(line).get('payload',{});s=q.get('input','') or q.get('arguments','')
  if not isinstance(s,str) or q.get('type') not in ['custom_tool_call','function_call']:continue
  for m in re.finditer(r'cmd\s*:\s*("(?:\\.|[^"\\])*")',s,re.S):
   try:cmd=json.loads(m[1])
   except Exception:continue
   cmds.append(cmd)
   # Shell here documents and Python literals contain exact original file bodies.
   for m in re.finditer(r"<<\s*['\"]?(\w+)['\"]?[^\n]*\n(.*?)\n\1(?:\n|$)",cmd,re.S):
    block=m[2];offer(block+'\n','journal-heredoc')
    try:tree=ast.parse(block)
    except SyntaxError:continue
    for n in ast.walk(tree):
     if isinstance(n,ast.Constant):offer(n.value,'journal-literal')
     elif isinstance(n,ast.BinOp) and isinstance(n.op,ast.Add):
      try:offer(ast.literal_eval(n),'journal-literal-expression')
      except Exception:pass
# Look for exact historical blobs with matching sizes; no checkout or mutation.
sizes={x['size'] for x in missing}
for repo in ['/Users/adelmann/git/opalx','/Users/adelmann/git/opalx-documents']:
 text=subprocess.check_output(['git','cat-file','--batch-all-objects','--batch-check=%(objectname) %(objecttype) %(objectsize)'],cwd=repo,text=True)
 candidates=[s.split()[0] for s in text.splitlines() if s.split()[1]=='blob' and int(s.split()[2]) in sizes]
 p=subprocess.Popen(['git','cat-file','--batch'],cwd=repo,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 for oid in candidates:
  p.stdin.write((oid+'\n').encode());p.stdin.flush();hdr=p.stdout.readline().split();size=int(hdr[2]);b=p.stdout.read(size);p.stdout.read(1);h=hashlib.sha256(b).hexdigest()
  if h in need:found[h]=(b,'git-blob:'+oid)
 p.stdin.close();p.wait()
recovery=[]
for h,(b,where) in found.items():
 for x in missing:
  if x['sha256']==h:
   p=OUT/x['archive'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);recovery.append({'original':x['original'],'method':where,'sha256':h})
(OUT/'recovery-exact.json').write_text(json.dumps(recovery,indent=2)+'\n');Path('/tmp/pr667-journal-commands.json').write_text(json.dumps(cmds))
print('Exact hash-verified recovery:',len(recovery),'of',len(missing))
