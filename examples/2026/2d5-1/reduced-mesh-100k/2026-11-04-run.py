"""Reproduce the requested reduced-mesh, 100k-particle 10pC ORIGINAL run."""
from pathlib import Path
import sys,importlib.util,json,hashlib,subprocess,os,time
import numpy as np
ROOT=Path(__file__).resolve().parent;TRACKING=ROOT.parent
SOURCE=ROOT/'source';RUN=ROOT/'run';SOURCE.mkdir(exist_ok=True);RUN.mkdir(exist_ok=True)
assert not (RUN/'manifest.json').exists(),'Use a fresh directory rather than overwrite a run'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
gen=TRACKING/'prepare_shared.py';spec=importlib.util.spec_from_file_location('shared_source',gen);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.NS,m.NR,m.NPHI=50,25,80
# Reuse the existing generator and geometry helpers without modifying originals.
original_root=m.ROOT;m.ROOT=ROOT
(ROOT/'sources').mkdir(exist_ok=True);m.main()
meta=json.loads((ROOT/'sources/bend-uniform-n100000.json').read_text());assert meta['source_particles']==100000
original=TRACKING/'bend-10m-100steps-local-original/opalx/runs/bend-10pC-10m-100steps-local-original/track.in'
s=original.read_text().replace('// Committed658 fd6ba8dc5 tracking. ZeroSC keeps identical charge and TYPE=NONE.','// Reduced-grid 10pC comparison; current ~/git/opalx OpenMP build, ORIGINAL model.')
s=s.replace('1048576','100000').replace('NX=512,NY=512,NZ=512','NX=32,NY=32,NZ=512')
s=s.replace(str(TRACKING/'sources/bend-uniform-n100000.dist'),meta['distribution'])
(RUN/'track.in').write_text(s)
binary=Path('/Users/adelmann/git/opalx/build-omp/src/opalx')
manifest=dict(binary=str(binary),binary_sha256=sha(binary),source=meta,mesh=[32,32,512],steps=100,charge_C=1e-11,fft2d5_model='ORIGINAL',omp_threads=1,mpi_ranks=1,box_xy_m=[.256,.320],dt_s=3.3356409519815204e-7,input_sha256=sha(RUN/'track.in'),driver_sha256=sha(__file__),source_generator_sha256=sha(gen),generator_parameters={'NS':50,'NR':25,'NPHI':80},note='Same physical source law, domain and integrator; new100k quiet realization. Current PR667 build differs from archived local a2 benchmark executable.')
env=dict(os.environ,OMP_NUM_THREADS='1',OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1');start=time.monotonic()
(RUN/'running.json').write_text(json.dumps(manifest,indent=2)+'\n')
with (RUN/'track.out').open('w') as f:result=subprocess.run([str(binary),'--info','4','track.in'],cwd=RUN,env=env,stdout=f,stderr=subprocess.STDOUT)
manifest.update(returncode=result.returncode,elapsed_seconds=time.monotonic()-start,completed=result.returncode==0)
(RUN/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2));sys.exit(result.returncode)
