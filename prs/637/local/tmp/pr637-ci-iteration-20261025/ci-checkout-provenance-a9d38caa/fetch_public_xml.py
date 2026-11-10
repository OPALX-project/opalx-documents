#!/Users/adelmann/.venv-h6/bin/python
"""Read public terminal-job artifacts once; never authenticate or rerun CI."""
import argparse, collections, datetime, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET

EXPECTED_SOURCE = 'a9d38caa4f88433a5de1508b3d5c7d01bdfea95a'
BRANCH = 'pr-637_Implement_cyclotron_PROBE_and_accelerating_space-charge_tracking'
JOBS = {
 'openmp': ('694321096757983', '17451990959', 'cpu-zen2-openmp'),
 'gh200': ('694321096757981', '17451990424', 'gpu-cuda-gh200'),
 'mi300': ('694321096757982', '17451990683', 'gpu-rocm-mi300'),
}

class Links(HTMLParser):
 def __init__(self): super().__init__(); self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a': self.links.append(a.get('href',''))

def get(url):
 with urlopen(Request(url,headers={'User-Agent':'OPALX-provenance-readonly'}),timeout=25) as r:
  if '/users/sign_in' in r.url: raise RuntimeError('Access requires sign-in; stopped.')
  return r.read(), r.url

def collect(name, dest):
 mirror,job,arch=JOBS[name]
 root=f'https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/{mirror}/-/jobs/{job}/artifacts/'
 relative=f'regression-results-{arch}/regressionTests/{BRANCH}/{arch}/'
 report={'backend_job':name,'job_id':job,'architecture_from_job_path':arch,'expected_source':EXPECTED_SOURCE,'queried_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  body,browse=get(root+'browse/'+relative)
  p=Links();p.feed(body.decode())
  urls=sorted({urljoin(browse,u).split('?')[0] for u in p.links if '/artifacts/raw/' in u and re.search(r'/results_\d{4}-\d\d-\d\d_\d\d-\d\d\.xml(?:\?|$)',u)})
  report['browser_url']=browse
  if not urls: raise RuntimeError('No timestamped result XML in public artifact directory.')
  url=urls[-1]; data,actual=get(url); xml=ET.fromstring(data)
  report.update(xml_url=actual,xml_sha256=hashlib.sha256(data).hexdigest(),xml_bytes=len(data),date_start=xml.findtext('Date/start'),revisions={e.tag:(e.text or '').strip() for e in xml.find('Revisions')},run_metadata={e.tag:(e.text or '').strip() for e in xml.find('RunMetadata')},comparison_counts=dict(collections.Counter(e.findtext('state') for e in xml.findall('Simulation/Test'))))
  report['source_matches']=report['revisions'].get('code_full')==EXPECTED_SOURCE
  report['date_matches']=str(report['date_start']).startswith('2026-10-25T')
  report['failures']=[{'simulation':s.get('name'),**t.attrib,'state':t.findtext('state'),'eps':t.findtext('eps'),'delta':t.findtext('delta')} for s in xml.findall('Simulation') for t in s.findall('Test') if t.findtext('state')!='passed']
  if not report['source_matches'] or not report['date_matches']: raise RuntimeError('Stale/different-source XML: not accepted as current a9 evidence.')
  (dest/f'{name}-results.xml').write_bytes(data)
  report['accepted_current_result']=True
 except (HTTPError,URLError,RuntimeError,ET.ParseError) as e:
  report.update(accepted_current_result=False,error=str(e))
 (dest/f'{name}-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('backend',choices=JOBS);p.add_argument('--dest',type=Path,default=Path('/tmp/pr637-a9-xml-provenance'));a=p.parse_args();a.dest.mkdir(parents=True,exist_ok=True);collect(a.backend,a.dest)
