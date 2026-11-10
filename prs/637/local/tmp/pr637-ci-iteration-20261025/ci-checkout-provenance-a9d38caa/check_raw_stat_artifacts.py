from urllib.request import Request,urlopen
from html.parser import HTMLParser
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from urllib.parse import urljoin,urlparse
import json,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument("--only",choices=["root","arch","plots"]);args=parser.parse_args()
base='https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/'
out=Path('/tmp/pr637-a9-xml-provenance');jobs=[]
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'artifacts/' in a.get('href',''):self.links.append(a['href'])
for name,mirror,job,arch in [('openmp','694321096757983','17451990959','cpu-zen2-openmp'),('mi300','694321096757982','17451990683','gpu-rocm-mi300')]:
 meta=json.loads((out/f'{name}-provenance.json').read_text());xml=meta['xml_url']
 import xml.etree.ElementTree as ET
 doc=ET.fromstring((out/f'{name}-results.xml').read_bytes())
 plot=next(e.text for e in doc.findall('Simulation/Test/plot') if e.text).split('/')[0]
 directory=xml.rsplit('/',1)[0].replace('/artifacts/raw/','/artifacts/browse/')
 root=f'{base}{mirror}/-/jobs/{job}/artifacts/browse/regression-results-{arch}/'
 for label,url in [('root',root),('arch',directory+'/'),('plots',directory+'/'+plot+'/')]:
  if args.only is None or args.only==label:jobs.append((name,label,url))
def inspect(job):
 name,label,url=job
 with urlopen(Request(url,headers={'User-Agent':'OPALX-provenance-readonly'}),timeout=25) as r:
  if '/users/sign_in' in r.url:raise RuntimeError('Sign-in required; stopped')
  b=r.read();p=Links();p.feed(b.decode());links=sorted(set(urljoin(r.url,x).split('?')[0] for x in p.links))
  files=[x for x in links if '/artifacts/raw/' in x]; dirs=[x for x in links if '/artifacts/browse/' in x]
  result={'backend':name,'listing':label,'url':r.url,'html_sha256':hashlib.sha256(b).hexdigest(),'raw_file_count':len(files),'raw_file_extensions':dict(Counter(Path(urlparse(x).path).suffix for x in files)),'raw_stat_links':[x for x in files if urlparse(x).path.endswith(('.stat','.smb','.csv','.dat'))],'raw_files':files,'directory_links':dirs}
  (out/f'{name}-{label}-artifact-listing.html').write_bytes(b)
  (out/f'{name}-{label}-artifact-listing.json').write_text(json.dumps(result,indent=2)+'\n')
  print(json.dumps({k:v for k,v in result.items() if k not in ['raw_files','directory_links']},indent=2))
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(inspect,jobs))
