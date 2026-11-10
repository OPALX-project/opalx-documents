from pathlib import Path
from io import StringIO
import re,json
import numpy as np,pandas as pd,h5py
root=Path('/Users/adelmann/git/opalx-master/tmp/coasting-fix-20261023')
def stat(p):
 h,b=re.split(r'&data\b.*?&end',p.read_text(),maxsplit=1,flags=re.S)
 names=[re.search(r'\bname\s*=\s*([^,\s]+)',c).group(1) for c in re.findall(r'&column\b(.*?)&end',h,re.S)]
 lines=[l for l in b.splitlines() if l.strip() and not l.lstrip().startswith('!')]
 return pd.read_csv(StringIO('\n'.join(lines[len(re.findall('&parameter',h)):])),sep=r'\s+',names=names)
