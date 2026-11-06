"""Package small provenance/results files, leaving native HDF5 and Nsight databases remote."""
from pathlib import Path
import tarfile
p=Path('/psi/home/adelmann/opalx-dev/dba/validation-a100-20261105/gpu-batching')
with tarfile.open(p/'results.tar.gz','w:gz') as archive:
 for f in sorted(p.rglob('*')):
  if f.is_file() and f.suffix in ['.csv','.json','.log','.out','.err','.sha256','.patch','.stat','.in','.exit','.txt']:
   archive.add(f,arcname=str(f.relative_to(p)))
