"""Native checkpoint benchmark with physical cell-charge quadrature.

One macro particle at each occupied source-grid cell centre carries the
analytic physical charge of that cell. This is an independent initialization
quadrature for the same specified physical density, not a field reference.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

import h5py
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import c,proton_mass,e
import run_study as base
import run_weighted_study as weighted

ROOT=base.ROOT


def cross_cell_charges(nx,ny,box,nquad):
    """Integrate (1+u/R) over exact ellipse/rectangular-cell intersections."""
    dx,dy=box[0]/nx,box[1]/ny
    gx,gw=leggauss(nquad)
    cross=[];weights=[]
    for i in range(nx):
        ulo,uhi=-box[0]/2+i*dx,-box[0]/2+(i+1)*dx
        if ulo>=base.A or uhi<=-base.A:
            continue
        for j in range(ny):
            ylo,yhi=max(-base.C,-box[1]/2+j*dy),min(base.C,-box[1]/2+(j+1)*dy)
            if yhi<=ylo:
                continue
            breaks=[ylo,yhi]
            for edge in [ulo,uhi]:
                if abs(edge)<base.A:
                    yy=base.C*np.sqrt(1-(edge/base.A)**2)
                    breaks.extend([sgn*yy for sgn in [-1.,1.] if ylo<sgn*yy<yhi])
            breaks=sorted(set(breaks));area=0.
            for lo,hi in zip(breaks[:-1],breaks[1:]):
                yy=(lo+hi)/2+(hi-lo)/2*gx
                width=base.A*np.sqrt(np.maximum(0.,1-(yy/base.C)**2))
                low=np.maximum(ulo,-width);high=np.minimum(uhi,width)
                integrand=np.where(high>low,high-low+(high*high-low*low)/(2*base.R),0.)
                area+=float(np.sum(gw*integrand)*(hi-lo)/2)
            if area>0:
                cross.append([(ulo+uhi)/2,-box[1]/2+(j+.5)*dy]);weights.append(area)
    return np.asarray(cross),np.asarray(weights)


def longitudinal_cells(nz,profile):
    dz=base.PATH_LENGTH/nz
    edges=np.linspace(-base.PATH_LENGTH/2,base.PATH_LENGTH/2,nz+1)
    lo=np.maximum(edges[:-1],-base.L/2);hi=np.minimum(edges[1:],base.L/2)
    if profile=='uniform':
        weight=np.maximum(0.,hi-lo)
    else:
        primitive=lambda ss:ss-ss*abs(ss)/(base.L)
        weight=np.where(hi>lo,primitive(hi)-primitive(lo),0.)
    keep=weight>0
    return (edges[:-1][keep]+edges[1:][keep])/2,weight[keep]


def write_checkpoint(path,n,blocks):
    hashes={key:hashlib.sha256() for key in ['q','m']};sumq=0.;mass_per_charge=(proton_mass*c*c/e/1e9)/e
    with h5py.File(path,'w') as handle:
        for key,value in dict(OPALXCheckpointFormat=1,GlobalTrackStep=0,NumContainers=1,
                              StepSizeSegment=0,StepsCompletedInSegment=0,NumCavityPhases=0).items():
            handle.attrs[key]=np.array([value],dtype=np.int64)
        for key,value in dict(TIME=0.,DT=base.DT).items():
            handle.attrs[key]=np.array([value],dtype=np.float64)
        step=handle.create_group('Step#0')
        for key,value in dict(ContainerIndex=0,Species=5,QMStorageMode=1,SpinEnabled=0,AtSStop=0).items():
            step.attrs[key]=np.array([value],dtype=np.int64)
        for key,value in dict(SPOS=0.,MacroCharge=0.,MacroMass=0.).items():
            step.attrs[key]=np.array([value],dtype=np.float64)
        for key,value in dict(RefPartR=[0.,0.,0.],RefPartP=[0.,0.,base.BETA/np.sqrt(1-base.BETA**2)],
                              ToLabOrigin=[0.,0.,0.],ToLabQuaternion=[1.,0.,0.,0.]).items():
            step.attrs[key]=np.array(value,dtype=np.float64)
        for key in ['x','px','y','py','z','pz','dt','q','m']:
            step.create_dataset(key,shape=(n,),dtype=np.float64)
        step.create_dataset('id',shape=(n,),dtype=np.int64);step.create_dataset('bin',shape=(n,),dtype=np.int32)
        offset=0
        for local,charge in blocks():
            count=len(local);sl=slice(offset,offset+count);data=base.global_values(local);mass=charge*mass_per_charge
            for j,key in enumerate(['x','px','y','py','z','pz']):
                step[key][sl]=data[:,j]
            step['q'][sl]=charge;step['m'][sl]=mass;step['dt'][sl]=base.DT
            step['id'][sl]=np.arange(offset,offset+count,dtype=np.int64);step['bin'][sl]=0
            hashes['q'].update(charge.tobytes());hashes['m'].update(mass.tobytes())
            sumq+=float(charge.sum());offset+=count
        if offset!=n:
            raise ValueError('Source count mismatch')
    return {key:value.hexdigest() for key,value in hashes.items()},sumq


def source(profile,mesh,box,nquad):
    nx,ny,nz=mesh
    directory=ROOT/'sources';directory.mkdir(exist_ok=True)
    name=f'cell-{profile}-{nx}x{ny}x{nz}-box{box[0]:g}x{box[1]:g}-q{nquad}'
    meta=directory/(name+'.json')
    if meta.exists():
        saved=json.loads(meta.read_text())
        for key in ['path','probe_checkpoint']:
            if base.sha(saved[key])!=saved[key+'_sha256']:
                raise ValueError('Preserved cell source hash mismatch')
        return saved
    cross,area=cross_cell_charges(nx,ny,box,nquad)
    ss,longweight=longitudinal_cells(nz,profile)
    nc=len(cross);nsource=nc*len(ss);probes=base.points()[['u_m','y_m','s_m']].to_numpy();nprobe=len(probes)
    norm=base.Q/(float(area.sum())*float(longweight.sum()));qprobe=base.Q/nsource
    paths={False:directory/(name+'.h5'),True:directory/(name+'-probes.h5')};digests={};totals={}
    for probe_only,path in paths.items():
        def blocks():
            if not probe_only:
                for start in range(0,len(ss),32):
                    times=ss[start:start+32];ww=longweight[start:start+32]
                    yield np.c_[np.tile(cross,(len(times),1)),np.repeat(times,nc)],(norm*ww[:,None]*area).ravel()
            yield probes,np.full(nprobe,qprobe,dtype=np.float64)
        digests[probe_only],totals[probe_only]=write_checkpoint(path,nprobe if probe_only else nsource+nprobe,blocks)
    sourceq=totals[False]-totals[True]
    if abs(sourceq/base.Q-1)>5e-13:
        raise ValueError('Cell source total charge mismatch')
    snapshots={}
    for label,script in [('cell',Path(__file__)),('weighted',Path(weighted.__file__)),('base',Path(base.__file__))]:
        digest=base.sha(script);snapshot=directory/'generators'/(digest+'.py');snapshot.parent.mkdir(exist_ok=True)
        if not snapshot.exists():
            shutil.copy2(script,snapshot)
        snapshots[label]=str(snapshot)
    result=dict(profile=profile,path=str(paths[False]),probe_checkpoint=str(paths[True]),
        path_sha256=base.sha(paths[False]),probe_checkpoint_sha256=base.sha(paths[True]),sha256=base.sha(paths[False]),
        ns=len(ss),nrad=nx,nphi=ny,ncross=nc,source_particles=nsource,probe_particles=nprobe,total_particles=nsource+nprobe,
        nominal_charge_C=base.Q,source_charge_C=sourceq,macrocharge_C=qprobe,full_charge_C=totals[False],probe_charge_C=totals[True],
        q_dataset_sha256=digests[False]['q'],m_dataset_sha256=digests[False]['m'],
        probe_q_dataset_sha256=digests[True]['q'],probe_m_dataset_sha256=digests[True]['m'],
        source_mesh=list(mesh),source_box_m=list(box),cell_area_gauss_order=nquad,
        integrated_cross_J_m2=float(area.sum()),exact_cross_J_m2=np.pi*base.A*base.C,
        cross_area_relative_error=float(area.sum()/(np.pi*base.A*base.C)-1),
        profile_long_integral_m=float(longweight.sum()),normalization_density_C_m3=norm,
        layout='physical-cell-charge',longitudinal_stagger=False,
        physical_density='q_i=normalization times exact profile integral ds times ellipse-cell integral (1+u/R) du dy',
        quadrature='occupied physical source-grid cell centres; no field fitting; partial ellipse boundary cell masses integrated',
        mass_policy='m_i=q_i/e times proton mass[GeV], preserving physical proton q/m',
        initialization='existing native checkpoint QM_MODE=ATTRIBUTES',
        generator_sha256=base.sha(__file__),generator_snapshots=snapshots,
        points_sha256=base.sha(ROOT/'reference/points_extended.csv'))
    meta.write_text(json.dumps(result,indent=2)+'\n');return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name');parser.add_argument('--profile',choices=['uniform','triangle'],required=True)
    parser.add_argument('--mesh',type=int,nargs=3,required=True)
    parser.add_argument('--source-mesh',type=int,nargs=3,help='fixed source quadrature; defaults to solve mesh')
    parser.add_argument('--box',type=float,nargs=2,default=[.012,.0015])
    parser.add_argument('--cell-quadrature',type=int,default=16)
    parser.add_argument('--path-step',type=float,default=.02);parser.add_argument('--mpi-ranks',type=int,default=1)
    parser.add_argument('--audit-checkpoint',action='store_true');parser.add_argument('--run',action='store_true')
    args=parser.parse_args();base.BOX=tuple(args.box)
    src=source(args.profile,args.source_mesh or args.mesh,args.box,args.cell_quadrature)
    for probe_only in [False,True]:
        directory,manifest=weighted.make(args.name+('-probes' if probe_only else ''),args.mesh,src,args.path_step,
                                          probe_only,args.mpi_ranks,args.audit_checkpoint)
        manifest['cell_source_generator_sha256']=base.sha(__file__)
        (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if args.run:
            weighted.run(directory,manifest)
        else:
            print(directory/'tube.in')


if __name__=='__main__':
    main()
