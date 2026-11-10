from pathlib import Path
import subprocess,re,xml.etree.ElementTree as E,json
s=Path(__file__).resolve().parent;cache={};new=[];missing=[]
for f in (s/'doxygen/xml').glob('*.xml'):
 c=E.parse(f).find('compounddef')
 if c is None or c.get('kind')=='file':continue
 owner=c.findtext('compoundname','')
 for m in c.findall('.//memberdef[@kind="function"]'):
  loc=m.find('location');p=loc.get('file','') if loc is not None else ''
  if not p.startswith(('src/','unit_tests/')):continue
  if p not in cache:
   q=subprocess.run(['git','show','origin/master:'+p],capture_output=True,text=True);cache[p]=q.stdout if q.returncode==0 else ''
  name=m.findtext('name','');old=cache[p]
  if re.search(r'(?<![\w])'+re.escape(name)+r'\s*\(',old):continue
  documented=any(''.join(m.find(tag).itertext()).strip() for tag in ['briefdescription','detaileddescription'])
  row=dict(owner=owner,name=name,file=p,line=loc.get('line'),documented=documented);new.append(row)
  if not documented:missing.append(row)
(s/'doxygen-coverage.json').write_text(json.dumps(dict(new_functions=new,missing=missing,internal_docs=True),indent=2)+'\n')
print('New-function Doxygen entries:',len(new)-len(missing),'/',len(new));print(json.dumps(missing,indent=2));assert not missing
# Doxygen associates declarations with the actual definition spans, including inline methods.
import csv
sizes=[]
for f in (s/'doxygen/xml').glob('*.xml'):
 c=E.parse(f).find('compounddef')
 if c is None or c.get('kind')=='file':continue
 for m in c.findall('.//memberdef[@kind="function"]'):
  loc=m.find('location')
  if loc is None or 'bodystart' not in loc.attrib:continue
  a=int(loc.get('bodystart'));b=int(loc.get('bodyend'))
  if a<0 or b<a:continue
  sizes.append(dict(owner=c.findtext('compoundname'),name=m.findtext('name'),file=loc.get('bodyfile'),start=a,end=b,lines=b-a+1))
with (s/'function-sizes.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(sizes[0]));w.writeheader();w.writerows(sizes)
assert all(q['lines']<=60 for q in sizes if q['file'].startswith(('src/SpaceCharge/FFT2D5','unit_tests/SpaceCharge/Benchmark')))
print('All audited FFT2D5/benchmark definitions fit within 60 source lines')
