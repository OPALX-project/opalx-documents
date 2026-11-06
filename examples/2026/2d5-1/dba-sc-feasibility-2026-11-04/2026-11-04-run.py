"""Bounded, timing-only charged DBA pilot; never launches a full turn campaign."""
from pathlib import Path
import os,sys,json,re,time,hashlib,shutil,subprocess,resource
import numpy as np,h5py
R=Path('/Users/adelmann/git/dba-lattice/comparison-20261104/unified-current');O=R/'dba-sc-feasibility';O.mkdir(exist_ok=True);B=Path('/Users/adelmann/git/opalx/build-omp/src/opalx');SHA='4fd718db8dea11088409158506cd61761eb35f7a0e6a15638fba235c433ba0eb'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B)==SHA
old=R.parent/'charged-kv/q5.602212nC';meta=json.loads((old/'source.json').read_text());src=np.load(old/'source.npz');n=meta['particle_count'];assert n==100000
shutil.copy2(old/'particles.txt',O/'particles.txt');shutil.copy2(old/'source.json',O/'source.json');shutil.copy2(old.parent/'reference-path.dat',O/'reference-path.dat');q=meta['charge_C']/n
seed=R/'dba-timesteps/checkpoint-schema/seed_checkpoint.h5';initial=O/'initial-state.h5'
if not initial.exists():
 shutil.copy2(seed,initial)
 with h5py.File(initial,'r+') as f:
  for k,v in [('GlobalTrackStep',0),('TIME',0.),('DT',3e-12),('StepSizeSegment',0),('StepsCompletedInSegment',0)]:f.attrs.modify(k,np.array([v],dtype=f.attrs[k].dtype))
  g=f['Step#0'];mass=float(g.attrs['MacroMass'][0])*q/float(g.attrs['MacroCharge'][0])
  for k,v in [('SPOS',0.),('AtSStop',0),('MacroCharge',q),('MacroMass',mass)]:g.attrs.modify(k,np.array([v],dtype=g.attrs[k].dtype))
  for k,v in [('RefPartR',np.zeros(3)),('RefPartP',np.array([0.,0.,meta['momentum_betagamma']])),('ToLabOrigin',np.zeros(3)),('ToLabQuaternion',np.array([1.,0.,0.,0.]))]:g.attrs.modify(k,v)
  values={**{c:src['positions_m'][:,j] for j,c in enumerate('xyz')},**{c:src['momenta_betagamma'][:,j] for j,c in enumerate(['px','py','pz'])},'q':np.full(n,q),'m':np.full(n,mass),'dt':np.full(n,3e-12),'id':np.arange(n,dtype=np.int64),'bin':np.zeros(n,dtype=np.int32)}
  for k,v in values.items():del g[k];g.create_dataset(k,data=v)
base=(R/'dba-timesteps/dt-3ps/case.in').read_text().split('DIST:DISTRIBUTION')[0];base=re.sub(r'PSDUMPFREQ=\d+', 'PSDUMPFREQ=100',base);base=re.sub(r'STATDUMPFREQ=\d+','STATDUMPFREQ=10',base);base=re.sub(r'STEPINFOFQ=\d+','STEPINFOFQ=10',base)
for threads,steps in [(int(sys.argv[i]),int(sys.argv[i+1])) for i in range(1,len(sys.argv),2)]:
 assert 1 <= steps <= 1000, 'This feasibility runner is limited to1000steps; no full campaign.'
 zero=os.environ.get('OPALX_PILOT_ZEROSC')=='1';d=O/(('zerosc-' if zero else '')+f'omp{threads}-{steps}steps');d.mkdir(exist_ok=False)
 text=base+f'''DIST:DISTRIBUTION,TYPE=FROMFILE,FNAME="{O/'particles.txt'}",NPARTDIST={n};
SOURCE:EMISSIONSOURCE,DISTRIBUTION=DIST;
SOURCES:EMISSIONSOURCELIST=(SOURCE);
FS:FIELDSOLVER,TYPE="FFT2D5",FFT2D5MODEL="ORIGINAL",PIPEMODE="NONE",CLOSEDRING=TRUE,REFPATHFNAME="{O/'reference-path.dat'}",NX=64,NY=64,NZ=512,PIPESIZEX=.064,PIPESIZEY=.064,BEAMR=.01,PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE;
BEAM1:BEAM,PARTICLE=PROTON,NALLOC={n},SOURCES=SOURCES,BCHARGE={meta['charge_C']:.17g},PC=.068539116182958951;
TRACK,LINE=LATTICE,BEAM=BEAM1,DT=3e-12,MAXSTEPS={steps};
RUN,METHOD="PARALLEL",FIELDSOLVER=FS,SCFIELDUPDATE="MIDPOINT";
ENDTRACK;
QUIT;
'''
 if zero:text=re.sub(r'FS:FIELDSOLVER[^;]*;', 'FS:FIELDSOLVER,TYPE=NONE,NX=64,NY=64,NZ=512;',text)
 (d/'case.in').write_text(text);assert sha(B)==SHA
 record=dict(binary=str(B),binary_sha256=SHA,initial_state_sha256=sha(initial),source_npz_sha256=sha(old/'source.npz'),source_text_sha256=sha(O/'particles.txt'),reference_path_sha256=sha(O/'reference-path.dat'),input_sha256=sha(d/'case.in'),charge_C=meta['charge_C'],dt_s=3e-12,steps=steps,omp_threads=threads,mpi_ranks=1,particles=n,mesh=[64,64,512],model='NONE' if zero else 'ORIGINAL',longitudinal='NONE: matched transverse-only coasting KV/PyORBIT comparison',space_charge=not zero,scope='timing pilot only; no full turn or tune validation')
 print('START',threads,steps,flush=True);t=time.monotonic()
 with (d/'run.log').open('w') as log:p=subprocess.run([str(B),'case.in','--restart',str(initial),'--info','1'],cwd=d,env=dict(os.environ,OMP_NUM_THREADS=str(threads),OMP_PROC_BIND='false',OPENBLAS_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT)
 record.update(elapsed_seconds=time.monotonic()-t,returncode=p.returncode,completed=p.returncode==0,peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss if sys.platform=='darwin' else resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024);(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print('DONE',json.dumps(record),flush=True)
 if p.returncode:break
