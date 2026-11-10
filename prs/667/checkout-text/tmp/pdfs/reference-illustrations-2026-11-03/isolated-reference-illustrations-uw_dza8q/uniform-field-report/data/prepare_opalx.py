"""Generate quiet ellipsoid source and reproducible native OPALX input cases."""
from pathlib import Path
import argparse,itertools,json,hashlib,os,subprocess,time
import numpy as np
from scipy.stats import qmc
from scipy.constants import c,e,proton_mass
import ellipsoid_model as model
ROOT=Path(__file__).resolve().parent;RUNS=ROOT/'opalx-runs';RUNS.mkdir(exist_ok=True)
BINARY=Path(os.environ.get('OPALX_BINARY') or ROOT.parents[3]/'build-omp/src/opalx')
PHASE=.2

def tag(value):
 return f'{value:.12g}'.replace('-','m').replace('.','p')

def source(power=11,radius=1.):
 if not np.isfinite(radius) or radius<=0:raise ValueError('Orbit radius must be positive')
 M=2**power;suffix='' if radius==1 else '-R'+tag(radius)
 name=ROOT/f'ellipsoid-{48*M}{suffix}.dist';meta=name.with_suffix('.npz')
 if name.exists():
  if not meta.exists():raise RuntimeError(f'Missing source provenance: {meta}')
  return name,meta,48*M
 uv=qmc.Sobol(d=2,scramble=True,seed=20261031).random_base2(power)
 rad=((np.arange(M)+.5)/M)**(1/3)
 z=2*uv[:,0]-1;phi=2*np.pi*uv[:,1]
 directions=np.c_[np.sqrt(1-z*z)*np.cos(phi),np.sqrt(1-z*z)*np.sin(phi),z]
 xyz=directions*rad[:,None]
 cloud=np.concatenate([xyz[:,perm]*np.array(sign) for perm in itertools.permutations(range(3)) for sign in itertools.product([-1,1],repeat=3)])
 # Midpoint radial quadrature slightly overestimates <r²>; a sub-unity scaling
 # gives exact target covariance and keeps all points inside the unit ball.
 cloud*=np.sqrt(.6/np.mean(np.sum(cloud*cloud,axis=1)))
 assert np.max(np.linalg.norm(cloud,axis=1))<1
 assert np.max(abs(cloud.T@cloud/len(cloud)-np.eye(3)/5))<1e-14
 C=np.array([radius,0.,0.]);r=C+cloud*model.AXES
 v=(model.OMEGA/radius)*(r@model.J.T)
 rot=np.array([[np.cos(PHASE),np.sin(PHASE),0],[-np.sin(PHASE),np.cos(PHASE),0],[0,0,1.]])
 r=r@rot.T;v=v@rot.T
 # Proper rotation (x,z,-y), then translate orbit center to(-radius,0,0).
 opal_r=np.c_[r[:,0]-radius,r[:,2],-r[:,1]]
 opal_v=np.c_[v[:,0],v[:,2],-v[:,1]]
 gamma=1/np.sqrt(1-np.sum(opal_v**2,axis=1)/c**2)
 opal_p=gamma[:,None]*opal_v/c
 values=np.column_stack([opal_r[:,0],opal_p[:,0],opal_r[:,1],opal_p[:,1],opal_r[:,2],opal_p[:,2]])
 with name.open('w') as f:f.write(f'{len(values)}\nx px y py z pz\n');np.savetxt(f,values,fmt='%.17e')
 np.savez(meta,unit_ball=cloud,positions=opal_r,momenta=opal_p,velocities=opal_v)
 return name,meta,len(values)

def reference_path(radius,path_limits,path_step):
 legacy=radius==1 and path_limits==(0.,4*np.pi/3) and path_step==.01
 ref=ROOT/('reference_path.dat' if legacy else f'reference-R{tag(radius)}-{tag(path_limits[0])}-{tag(path_limits[1])}-{tag(path_step)}.dat')
 if not ref.exists():
  count=421 if legacy else int(np.ceil((path_limits[1]-path_limits[0])/path_step))+1
  angle=np.linspace(*path_limits,count);vals=np.zeros((len(angle),15));vals[:,0]=(angle-angle[0])*radius
  vals[:,1]=radius*(np.cos(angle)-1);vals[:,3]=radius*np.sin(angle)
  vals[:,4]=-.01*np.sin(angle);vals[:,6]=.01*np.cos(angle)
  np.savetxt(ref,vals,header='s rx ry rz px py pz ex ey ez bx by bz ke time')
 return ref

def field_map(radius,pipe_size):
 legacy=radius==1 and pipe_size[0]<=.04 and pipe_size[1]<=.064
 path=ROOT/('uniform-by.g4blmap' if legacy else f'uniform-by-R{tag(radius)}-{tag(pipe_size[0])}-{tag(pipe_size[1])}.g4blmap')
 if path.exists():return path
 margin=max(.2*radius,pipe_size[0]);vertical=max(.05,pipe_size[1]);zmargin=max(.1,pipe_size[0])
 lower=np.array([-2*radius-margin,-vertical,-.5*radius-zmargin])*1000
 upper=np.array([margin,vertical,1.3*radius+zmargin])*1000
 spacing=(upper-lower)/2;axes=[np.linspace(lower[i],upper[i],3) for i in range(3)]
 with path.open('w') as stream:
  stream.write('param normB=1 current=1\n')
  stream.write('grid '+ ' '.join(f'{k}={v:.17g}' for k,v in zip(['X0','Y0','Z0','dX','dY','dZ'],[*lower,*spacing]))+' nX=3 nY=3 nZ=3\ndata\n')
  for x,y,z in itertools.product(*axes):stream.write(f'{x:.17g} {y:.17g} {z:.17g} 0 {model.BZ/radius:.17g} 0\n')
 return path

def make(name,solver='none',Q=0.,steps=128,mesh=(32,32,64),power=11,*,radius=1.,pipe_size=(.024,.012),path_limits=(0.,4*np.pi/3),path_step=.01,dump_every=None):
 if steps<1 or min(mesh)<1 or min(pipe_size)<=0:raise ValueError('Positive steps, grid and pipe dimensions required')
 if path_limits[1]<=path_limits[0] or path_step<=0:raise ValueError('Reference-path interval and angular spacing must be positive')
 path,meta,N=source(power,radius);d=RUNS/name
 if d.exists() and (d/'uniform-b.h5').exists():raise RuntimeError(f'Preserving results: {d}')
 d.mkdir(exist_ok=True)
 assigned=Q if Q else 1e-13
 omega=model.OMEGA/radius;magnetic_field=model.BZ/radius
 P0=magnetic_field*radius*.299792458
 dump_every=steps if dump_every is None else dump_every
 if dump_every<1:raise ValueError('Snapshot interval must be positive')
 lines=['// Uniform Bz thin-ellipsoid benchmark; axes rotated to OPALX x-z / By.',
  '// Zero self-field uses TYPE=NONE and nominal charge to retain finite macro q/m.',
  'OPTION, VERSION=10900;',f'OPTION, PSDUMPFREQ={dump_every};',
  'OPTION, STATDUMPFREQ=1;','OPTION, EBDUMP=TRUE;','OPTION, MINBINEMITTED=0;',
  f'REAL P0={P0:.17g};',
  f'DIST1: DISTRIBUTION, TYPE=FROMFILE, NPARTDIST={N}, FNAME="{path}";',
  'E1: EMISSIONSOURCE, DISTRIBUTION=DIST1, R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0, ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;',
  'ELIST1: EMISSIONSOURCELIST=(E1);']
 nx,ny,nz=mesh
 if solver=='none':lines+=['FS: FIELDSOLVER,TYPE=NONE,NX=8,NY=8,NZ=8,PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE;']
 elif solver=='open':lines+=[f'FS: FIELDSOLVER,TYPE=OPEN,NX={nx},NY={ny},NZ={nz},GREENSF=INTEGRATED,BBOXINCR=5,PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,BCFFTX=OPEN,BCFFTY=OPEN,BCFFTZ=OPEN;']
 elif solver=='fft2d5':
  ref=reference_path(radius,path_limits,path_step)
  pipes='PIPESIZEX=.024,PIPESIZEY=.012' if pipe_size==(.024,.012) else f'PIPESIZEX={pipe_size[0]:.17g},PIPESIZEY={pipe_size[1]:.17g}'
  lines+=[f'FS: FIELDSOLVER,TYPE="FFT2D5",NX={nx},NY={ny},NZ={nz},PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE=OPEN,REFPATHFNAME="{ref}",BEAMR=.005,CLOSEDRING=FALSE,{pipes},SCATTERLONGITUDINALLY=TRUE;']
 else:raise ValueError(solver)
 lines+=[f'B1: BEAM,PARTICLE=PROTON,NALLOC={N},BCHARGE={assigned:.17g},SOURCES="ELIST1";']
 fieldmap=field_map(radius,pipe_size)
 lines += [f'UB: FIELDMAP,FMAPFN="{fieldmap}",BSCALE=1,ESCALE=0,X=0,Y=0,Z=0,THETA=0,PHI=0,PSI=0;']
 lines+=['L1: LINE=(UB);',f'TRACK,BEAM=B1,LINE=L1,MAXSTEPS={steps},ZSTOP={{{6*max(1,radius):g}}},DT={{{np.pi/omega/steps:.17g}}};','RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1;','ENDTRACK;']
 (d/'uniform-b.in').write_text('\n'.join(lines)+'\n')
 m=dict(name=name,solver=solver,charge_C=Q,assigned_charge_C=assigned,steps=steps,mesh=list(mesh),expected_particles=N,
  initial_phase_rad=PHASE,orbit_radius_m=radius,orbit_center_opal_m=[-radius,0.,0.],omega_rad_per_s=omega,Bz_T=magnetic_field,distribution=str(path),source_npz=str(meta),
  directory=str(d),h5=str(d/'uniform-b.h5'),dt_s=np.pi/omega/steps,pipe_size_m=list(pipe_size),reference_path_limits_rad=list(path_limits),snapshot_interval_steps=dump_every,
  field_geometry='one uniform Cartesian map',fieldmap=str(fieldmap),fieldmap_sha256=hashlib.sha256(fieldmap.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),input_sha256=hashlib.sha256((d/'uniform-b.in').read_bytes()).hexdigest(),
  binary_sha256=hashlib.sha256(BINARY.read_bytes()).hexdigest(),binary=str(BINARY))
 if solver=='fft2d5':m.update(reference_path=str(ref),reference_path_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(),reference_path_points=int(np.loadtxt(ref).shape[0]))
 (d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');return d,m

def run(d,m):
 env=os.environ.copy();env.update(OMP_NUM_THREADS='4',OMP_PROC_BIND='false');start=time.monotonic()
 with (d/'uniform-b.out').open('w') as f:
  p=subprocess.run([str(BINARY),'uniform-b.in','--info','4'],cwd=d,env=env,stdout=f,stderr=subprocess.STDOUT)
 m['returncode']=p.returncode;m['elapsed_s']=time.monotonic()-start
 (d/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({k:m[k] for k in ['name','returncode','elapsed_s']}),flush=True)
 return p.returncode
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--solver',default='none',choices=['none','open','fft2d5']);p.add_argument('--charge-pc',type=float,default=0.);p.add_argument('--steps',type=int,default=128);p.add_argument('--mesh',type=int,nargs=3,default=[32,32,64]);p.add_argument('--power',type=int,default=11);p.add_argument('--radius-m',type=float,default=1.);p.add_argument('--pipe-size',type=float,nargs=2,default=[.024,.012]);p.add_argument('--path-limits',type=float,nargs=2,default=[0.,4*np.pi/3]);p.add_argument('--path-step-rad',type=float,default=.01);p.add_argument('--dump-every',type=int);p.add_argument('--run',action='store_true');a=p.parse_args()
 d,m=make(a.name,a.solver,a.charge_pc*1e-12,a.steps,tuple(a.mesh),a.power,radius=a.radius_m,pipe_size=tuple(a.pipe_size),path_limits=tuple(a.path_limits),path_step=a.path_step_rad,dump_every=a.dump_every)
 if a.run:raise SystemExit(run(d,m))
 print(d/'uniform-b.in')
