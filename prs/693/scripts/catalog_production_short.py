#!/usr/bin/env python3
"""Catalog only updated production short-deck assets; preserve unrelated records."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1];repo=R.parent.parent
owned=['xxx-short.tex','xxx-short.pdf','xxx-short-readme.md','beamer-handoff.md','generated/short-production-paper.tex','scripts/update_short_production.py','scripts/catalog_production_short.py','data/short-presentation-qa.json']
owned += [f'figures/opalx-production-f8-{e}.pdf' for e in (50,70,90)]
owned += [str(p.relative_to(R)) for p in sorted((R/'data/production-f8ac63538915').iterdir()) if p.is_file() and p.name!='sha256sums.txt']
owned += ['data/zhou-fig6-digitized-hulls.csv','data/zhou-fig6-hull-provenance.json']
owned += ['drafts/before-production-f8ac63538915/'+n for n in ['xxx-short.tex','xxx-short.pdf','xxx-short-readme.md']]
checksum_path=R/'data/production-f8ac63538915/sha256sums.txt'
checksum_path.write_text('\n'.join(hashlib.sha256((R/rel).read_bytes()).hexdigest()+'  '+rel for rel in owned)+'\n')
owned += ['data/production-f8ac63538915/sha256sums.txt']
manifest=repo/'manifest.yml';text=manifest.read_text();checks=[]
for rel in owned:
 p=R/rel;assert p.is_file(),rel
 digest=hashlib.sha256(p.read_bytes()).hexdigest();checks.append(digest+'  '+rel)
 destination=str(p.relative_to(repo));q=json.dumps(destination)
 if rel.startswith('scripts/'):
  # Repository infrastructure scripts are checksum-covered, not manifest assets.
  at=text.find('    destination: '+q+'\n')
  if at>=0:
   start=text.rfind('\n  - title:',0,at)+1;end=text.find('\n  - title:',at);end=len(text) if end<0 else end+1
   text=text[:start]+text[end:]
  continue
 values={'title':'OPALX and paper production comparison - '+rel,'date':None,'category':'prs','source':'Completed LUMI sourcef8ac63538915, production24039424/24039425/24039426, analysis24039716; Zhou et al DOI10.1103/q1xb-z29j.','destination':destination,'description':'Six-slide OPALX and paper comparison: maximum accepted central tune depression, native runtime per turn, and new KV footprints. Verified lattice parameter MAXYPOWER=5; header comment2stale.','status':'experimental','sha256':digest}
 if '    destination: '+q+'\n' in text:
  # Replace just the associated record, preserving all neighboring records.
  pattern=r'(?m)^  - title:.*\n(?:(?!  - title:)[\s\S])*?    destination: '+re.escape(q)+r'\n(?:(?!  - title:)[\s\S])*?(?=^  - title:|\Z)'
  match=re.search(pattern,text)
  # Bound the start at the last preceding record rather than earlier entries.
  at=text.index('    destination: '+q+'\n');start=text.rfind('\n  - title:',0,at)+1;end=text.find('\n  - title:',at);end=len(text) if end<0 else end+1
  assert start>0 and text[start:at].startswith('  - title:')
  block='\n'.join(('  - ' if i==0 else '    ')+key+': '+json.dumps(value,ensure_ascii=False) for i,(key,value) in enumerate(values.items()))+'\n\n'
  text=text[:start]+block+text[end:]
 else:
  block='\n'.join(('  - ' if i==0 else '    ')+key+': '+json.dumps(value,ensure_ascii=False) for i,(key,value) in enumerate(values.items()))
  text=text.rstrip()+'\n\n'+block+'\n'
manifest.write_text(text.rstrip()+"\n")

print(f'Cataloged {len(owned)} production short-deck assets.')
