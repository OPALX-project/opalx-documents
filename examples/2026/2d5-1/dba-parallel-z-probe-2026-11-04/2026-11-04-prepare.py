"""Bounded input-only probes of PARFFTZ support; preserves validated pilot input."""
from pathlib import Path
import json,hashlib
R=Path('/Users/adelmann/git/dba-lattice/comparison-20261104/unified-current');O=R/'dba-parallel-z-probe';O.mkdir(exist_ok=True);base=R/'dba-sc-feasibility/omp4-100steps';m=json.loads((base/'manifest.json').read_text());binary=Path(m['binary']);assert hashlib.sha256(binary.read_bytes()).hexdigest()==m['binary_sha256'];text=(base/'case.in').read_text();assert text.count('PARFFTZ=FALSE')==1;changed=text.replace('PARFFTZ=FALSE','PARFFTZ=TRUE')
for name,ranks,threads in [('mpi4-omp1',4,1),('mpi1-omp4',1,4)]:
 d=O/name;d.mkdir(exist_ok=False);(d/'case.in').write_text(changed);record=dict(binary=str(binary),binary_sha256=m['binary_sha256'],source_commit='40856f1a28246fb8d137864ca7541f2aede71a7b',base_input_sha256=m['input_sha256'],input_sha256=hashlib.sha256((d/'case.in').read_bytes()).hexdigest(),mpi_ranks=ranks,omp_threads=threads,parfftz=True,mesh=[64,64,512],particles=100000,charge_C=m['charge_C'],dt_s=m['dt_s'],max_steps=100,initial_state=str(R/'dba-sc-feasibility/initial-state.h5'),initial_state_sha256=m['initial_state_sha256'],scope='Only PARFFTZ changes; probe distributed-support validation before any claimed result comparison');(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print(O)
