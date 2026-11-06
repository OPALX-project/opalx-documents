"""Native PyORBIT full-ring 100-kick timing pilot, preserving source phases.

Each physical particle starts at the same local KV coordinates and ring phase
as OPALX. TEAPOT body maps act in its current element, splitting hard-edge
crossings. All phases share one open transverse slice solve per 3 ps reference
flight. This is a common-s map; OPALX uses common time. No tunes are measured.
Python grouping/copy cost is measured separately from native SC and body maps.
"""
from pathlib import Path
import argparse,os,sys,time,json,hashlib
import numpy as np
import pandas as pd
from orbit.core.bunch import Bunch
from orbit.core import teapot_base as tp
from orbit.core.spacecharge import SpaceChargeCalcSliceBySlice2D
P=Path('/Users/adelmann/git/dba-lattice');R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--nz',type=int,choices=[256,512],required=True);p.add_argument('--repeat',type=int,default=1);a=p.parse_args()
O=R/'dba-pyorbit-pilot'/f'nz-{a.nz}-{a.repeat}';O.mkdir(parents=True,exist_ok=False)
total_start=time.perf_counter();source_dir=R.parent/'charged-kv/q5.602212nC';meta=json.loads((source_dir/'source.json').read_text());source=np.load(source_dir/'source.npz');N=meta['particle_count'];C=meta['circumference_m'];bg=meta['momentum_betagamma'];beta=meta['beta'];dt=3e-12;ds=beta*299792458.*dt;mass=.93827208816;q=meta['charge_C'];e=1.602176634e-19
assert N==100000 and hashlib.sha256((source_dir/'source.npz').read_bytes()).hexdigest()==meta['source_sha256']
machine=json.loads((P/'model/machine.json').read_text());elements=machine['elements'];starts=np.array([v['s_start_m'] for v in elements]);ends=np.array([v['s_start_m']+v['length_m'] for v in elements]);source_s=source['s_m'];trans=source['transverse'];x,xp,y,yp=trans.T;den=np.sqrt(1+xp*xp+yp*yp)
# z carries phase relative to the moving reference; TEAPOT adds path-length slip.
state=np.c_[x,xp/den,y,yp/den,source_s-C/2,np.zeros(N)]
def new_bunch():
 b=Bunch();b.mass(mass);b.charge(1.);b.macroSize(q/e/N);b.getSyncParticle().kinEnergy(mass*bg*bg/(np.sqrt(1+bg*bg)+1));return b
b=new_bunch();b.addPartAttr('macrosize');scratch=new_bunch()
for row in state:b.addParticle(*map(float,row));b.partAttrValue('macrosize',b.getSize()-1,0,q/e/N)
half=.032*(1-1/64);guards=np.array([[-half,0,-C/2],[half,0,C/2],[0,-half,-C/2],[0,half,C/2],[0,0,-C/2],[0,0,C/2]])
for x,y,z in guards:b.addParticle(float(x),0.,float(y),0.,float(z),0.);b.partAttrValue('macrosize',b.getSize()-1,0,0.)
solver=SpaceChargeCalcSliceBySlice2D(64,64,a.nz,1.);solver.longTracking(0)
access=['x','xp','y','yp','z','dE'];native_map_s=0.;grouping_s=0.;sc_s=0.;diagnostics_s=0.;crossings=0

def body(el,length):
 global native_map_s
 t=time.perf_counter()
 if el['type']=='sector_bend':
  theta=length*el['h_per_m'];tp.bend1(scratch,length/2,theta/2);tp.bend2(scratch,length/2);tp.bend3(scratch,theta/2);tp.bend4(scratch,theta/2);tp.bend4(scratch,theta/2);tp.bend3(scratch,theta/2);tp.bend2(scratch,length/2);tp.bend1(scratch,length/2,theta/2)
 elif el['type']=='quadrupole':tp.quad1(scratch,length/2,el['kx_m2'],1);tp.quad2(scratch,length);tp.quad1(scratch,length/2,el['kx_m2'],1)
 else:tp.drift(scratch,length)
 native_map_s+=time.perf_counter()-t

def map_group(indices,el,length):
 scratch.deleteAllParticles()
 for i in indices:scratch.addParticle(*map(float,state[i]))
 body(el,length)
 for j,i in enumerate(indices):
  for k,name in enumerate(access):state[i,k]=getattr(scratch,name)(j)

def external(length,travel):
 global grouping_s,crossings
 t=time.perf_counter();previous=native_map_s
 phase=np.remainder(state[:,4]+C/2+travel,C);which=np.searchsorted(starts,phase,side='right')-1;remaining=ends[which]-phase;cross=remaining<length
 for j,el in enumerate(elements):
  ids=np.flatnonzero((which==j)&~cross)
  if len(ids):map_group(ids,el,length)
 for i in np.flatnonzero(cross):
  j=which[i];map_group([i],elements[j],float(remaining[i]));map_group([i],elements[(j+1)%len(elements)],float(length-remaining[i]));crossings+=1
 grouping_s+=time.perf_counter()-t-(native_map_s-previous)

def record(step):
 t=time.perf_counter();rows=[]
 for k in [0,2]:
  xx=state[:,k]-state[:,k].mean();pp=state[:,k+1]-state[:,k+1].mean();v=np.mean(xx*xx);res=pp-np.mean(xx*pp)/v*xx;rows.extend([np.sqrt(v),bg*np.sqrt(v*np.mean(res*res))])
 moments.append(dict(step=step,time_s=step*dt,s_m=step*ds,sigma_x_m=rows[0],emit_n_x_m=rows[1],sigma_y_m=rows[2],emit_n_y_m=rows[3]));return time.perf_counter()-t
moments=[];diagnostics_s+=record(0);setup_s=time.perf_counter()-total_start;track_start=time.perf_counter()
for step in range(100):
 external(ds/2,step*ds)
 t=time.perf_counter()
 for k,name in enumerate(access):
  fn=getattr(b,name)
  for i in range(N):fn(i,float(state[i,k]))
 for j,(x,y,z) in enumerate(guards):
  i=N+j;b.x(i,float(x));b.xp(i,0.);b.y(i,float(y));b.yp(i,0.);b.z(i,float(z));b.dE(i,0.)
 grouping_s+=time.perf_counter()-t
 t=time.perf_counter();solver.trackBunch(b,ds);sc_s+=time.perf_counter()-t
 if step==0:
  grid=solver.getRhoGrid();bounds=[grid.getMinX(),grid.getMaxX(),grid.getMinY(),grid.getMaxY(),grid.getMinZ()/meta['gamma'],grid.getMaxZ()/meta['gamma']];assert np.max(abs(np.array(bounds)-[-half,half,-half,half,-C/2,C/2]))<1e-10
 t=time.perf_counter()
 for k,name in enumerate(access):state[:,k]=[getattr(b,name)(i) for i in range(N)]
 grouping_s+=time.perf_counter()-t
 external(ds/2,(step+.5)*ds)
 assert np.isfinite(state).all() and b.getSize()==N+6
 if (step+1)%10==0:
  diagnostics_s+=record(step+1);print('STEP',step+1,'tracking_s',time.perf_counter()-track_start,flush=True)
tracking_s=time.perf_counter()-track_start
np.savez_compressed(O/'endpoint.npz',id=np.arange(N),state=state,phase_s=np.remainder(state[:,4]+C/2+100*ds,C));pd.DataFrame(moments).to_csv(O/'moments.csv',index=False)
record=dict(completed=True,code='PyORBIT',steps=100,dt_s=dt,reference_flight_m=100*ds,particles=N,charge_C=q,mesh=[64,64,a.nz],mpi_ranks=1,omp_threads=int(os.environ['OMP_NUM_THREADS']),setup_s=setup_s,tracking_s=tracking_s,native_sc_s=sc_s,native_body_maps_s=native_map_s,python_grouping_copy_s=grouping_s,diagnostics_s=diagnostics_s,elapsed_seconds=time.perf_counter()-total_start,hard_edge_crossing_particles=crossings,source_sha256=meta['source_sha256'],driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),native_library=str(tp.__file__),native_library_sha256=hashlib.sha256(Path(tp.__file__).read_bytes()).hexdigest(),longitudinal_SC=False,transverse_boundary='open',longitudinal='coasting phase labels, periodic native Grid3D, zero-charge extent guards; NGP slice deposition and TSC transverse deposition versus OPALX CIC',sampling='common reference s, distributed ring phases and local matched envelope; OPALX common time',scope='100-step timing pilot; no turns or tunes; Python grouping is separately reported, native code unchanged')
(O/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2),flush=True)
