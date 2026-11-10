"""Frozen native OPALX study using existing Q/M-attribute checkpoint import.

Uniform spatial quadrature with analytic longitudinal density in q_i gives
well-resolved triangular tails. This changes only benchmark initialization;
the ordinary existing native FFT2D5 scatter, solve and gather are exercised.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import resource
import shutil
import subprocess
import time

import h5py
import numpy as np
from scipy.constants import c,proton_mass,e
from scipy.optimize import brentq
import run_study as base

ROOT=base.ROOT


def area_cartesian(nu,ny):
    """Exact ellipse area CDF in y and conditional physical-J CDF in u."""
    if nu%2 or ny%2:
        raise ValueError('Both area-Cartesian node counts must be even')
    cumulative=(np.arange(ny)+.5)/ny
    angle=np.array([brentq(lambda th: (th+.5*np.sin(2*th)+np.pi/2)/np.pi-pp,
                             -np.pi/2,np.pi/2,xtol=2e-15) for pp in cumulative])
    yy=base.C*np.sin(angle)
    width=base.A*np.cos(angle)
    midpoint=(2*(np.arange(nu)+.5)/nu-1)
    u0=width[:,None]*midpoint
    radicand=base.R**2+2*base.R*u0+width[:,None]**2
    uu=(2*base.R*u0+width[:,None]**2)/(np.sqrt(radicand)+base.R)
    cross=np.c_[uu.ravel(),np.repeat(yy,nu)]
    iy=np.minimum(np.arange(ny),ny-1-np.arange(ny))
    iu=np.minimum(np.arange(nu),nu-1-np.arange(nu))
    group=(iy[:,None]*(nu//2)+iu).ravel();ngroup=nu*ny//4
    order=np.argsort(np.mod(np.arange(ngroup)*((np.sqrt(5)-1)/2),1.))
    rank=np.empty(ngroup,dtype=int);rank[order]=np.arange(ngroup)
    return cross,(rank[group]+.5)/ngroup


def source(profile,ns,nrad,nphi,layout='polar'):
    if ns<2 or ns%2:
        raise ValueError('ns must be positive and even')
    directory=ROOT/'sources';directory.mkdir(exist_ok=True)
    name=f'weighted-{profile}-{layout}-ns{ns}-nr{nrad}-np{nphi}'
    meta=directory/(name+'.json')
    if meta.exists():
        result=json.loads(meta.read_text())
        for key in ['path','probe_checkpoint']:
            if base.sha(result[key])!=result[key+'_sha256']:
                raise ValueError('Checkpoint source integrity mismatch')
        return result
    cross,phase=(base.cross_section(nrad,nphi) if layout=='polar' else area_cartesian(nrad,nphi))
    points=base.points();probes=points[['u_m','y_m','s_m']].to_numpy()
    nc=len(cross);nsource=ns*nc;nprobe=len(probes);qprobe=base.Q/nsource
    mass_per_charge=(proton_mass*c*c/e/1e9)/e
    paths={False:directory/(name+'.h5'),True:directory/(name+'-probes.h5')}
    dataset_hashes={}
    source_sumq=0.;source_qs2=0.
    for probe_only,path in paths.items():
        n=nprobe if probe_only else nsource+nprobe
        hashes={key:hashlib.sha256() for key in ['q','m']}
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
            for key,value in dict(RefPartR=[0.,0.,0.],
                RefPartP=[0.,0.,base.BETA/np.sqrt(1-base.BETA**2)],ToLabOrigin=[0.,0.,0.],
                ToLabQuaternion=[1.,0.,0.,0.]).items():
                step.attrs[key]=np.array(value,dtype=np.float64)
            for key in ['x','px','y','py','z','pz','dt','q','m']:
                step.create_dataset(key,shape=(n,),dtype=np.float64)
            step.create_dataset('id',shape=(n,),dtype=np.int64)
            step.create_dataset('bin',shape=(n,),dtype=np.int32)
            offset=0
            def emit(local,weights):
                nonlocal offset,source_sumq,source_qs2
                count=len(local);sl=slice(offset,offset+count)
                data=base.global_values(local)
                for j,key in enumerate(['x','px','y','py','z','pz']):
                    step[key][sl]=data[:,j]
                masses=weights*mass_per_charge
                step['q'][sl]=weights;step['m'][sl]=masses;step['dt'][sl]=base.DT
                step['id'][sl]=np.arange(offset,offset+count,dtype=np.int64);step['bin'][sl]=0
                hashes['q'].update(np.asarray(weights,dtype=np.float64).tobytes())
                hashes['m'].update(np.asarray(masses,dtype=np.float64).tobytes())
                offset+=count
            if not probe_only:
                for start in range(0,ns//2,16):
                    sp=base.longitudinal_positions('uniform',ns,phase,start,min(start+16,ns//2),True)
                    for sign in [-1.,1.]:
                        local=np.c_[np.tile(cross,(len(sp),1)),sign*sp.ravel()]
                        ww=np.ones(len(local)) if profile=='uniform' else 2*(1-abs(local[:,2])/(base.L/2))
                        qq=qprobe*ww
                        source_sumq+=float(np.sum(qq));source_qs2+=float(np.sum(qq*local[:,2]**2))
                        emit(local,qq)
            emit(probes,np.full(nprobe,qprobe))
            assert offset==n
        dataset_hashes[probe_only]={key:value.hexdigest() for key,value in hashes.items()}
    if abs(source_sumq/base.Q-1)>2e-13:
        raise ValueError('Analytic profile quadrature charge normalization failed')
    generator_snapshots={}
    for label,script in [('weighted',Path(__file__)),('base',Path(base.__file__))]:
        digest=base.sha(script);snapshot=directory/'generators'/(digest+'.py')
        snapshot.parent.mkdir(exist_ok=True)
        if not snapshot.exists():
            shutil.copy2(script,snapshot)
        generator_snapshots[label]=str(snapshot)
    result=dict(profile=profile,path=str(paths[False]),probe_checkpoint=str(paths[True]),
        path_sha256=base.sha(paths[False]),probe_checkpoint_sha256=base.sha(paths[True]),
        sha256=base.sha(paths[False]),ns=ns,nrad=nrad,nphi=nphi,ncross=nc,source_particles=nsource,
        probe_particles=nprobe,total_particles=nsource+nprobe,nominal_charge_C=base.Q,
        source_charge_C=source_sumq,macrocharge_C=qprobe,source_mean_s_squared_m2=source_qs2/source_sumq,
        expected_source_mean_s_squared_m2=(base.L/2)**2/(3 if profile=='uniform' else 6),
        full_charge_C=source_sumq+nprobe*qprobe,probe_charge_C=nprobe*qprobe,
        q_dataset_sha256=dataset_hashes[False]['q'],m_dataset_sha256=dataset_hashes[False]['m'],
        probe_q_dataset_sha256=dataset_hashes[True]['q'],probe_m_dataset_sha256=dataset_hashes[True]['m'],
        mean_u_m=float(cross[:,0].mean()),expected_mean_u_m=base.A**2/(4*base.R),
        mean_y_m=float(cross[:,1].mean()),layout=layout,longitudinal_stagger=True,
        physical_density='uniform physical ellipse; physical-J weighted coordinates; q_i proportional to rho(s_i)',
        mass_policy='m_i=q_i/e times proton mass in GeV, constant physical proton q/m including probes',
        initialization='existing native --restart OPALXCheckpointFormat1 with QM_MODE=ATTRIBUTES',
        weighted_generator_sha256=base.sha(__file__),base_generator_sha256=base.sha(base.__file__),
        generator_snapshots=generator_snapshots,
        points_sha256=base.sha(ROOT/'reference/points_extended.csv'))
    meta.write_text(json.dumps(result,indent=2)+'\n');return result


def make(name,mesh,src,pathstep,probe_only=False,mpi_ranks=1,audit_checkpoint=False):
    directory=ROOT/'runs'/name;directory.mkdir(parents=True,exist_ok=True)
    manifest_path=directory/'manifest.json'
    if manifest_path.exists():
        old=json.loads(manifest_path.read_text())
        if old.get('returncode')==0:
            if base.sha(directory/'tube.in')!=old['input_sha256'] or base.sha(base.BINARY)!=old['binary_sha256']:
                raise ValueError('Preserved run differs; use a fresh case name')
            return directory,old
    checkpoint=Path(src['probe_checkpoint' if probe_only else 'path'])
    n=src['probe_particles' if probe_only else 'total_particles']
    charge=src['probe_charge_C' if probe_only else 'full_charge_C']
    reference=base.reference(pathstep);nx,ny,nz=mesh
    text=f'''// Checkpoint is the sole particle source; parser distribution is not sampled.
OPTION,VERSION=10900;
OPTION,QM_MODE="ATTRIBUTES";
OPTION,PSDUMPFREQ=1;
OPTION,STATDUMPFREQ=1;
OPTION,EBDUMP=TRUE;
OPTION,MINBINEMITTED=0;
OPTION,CHECKPOINTFREQ={1 if audit_checkpoint else 0};
DIST1:DISTRIBUTION,TYPE=UNIFORM,NPARTDIST={n},SIGMAX={base.A},SIGMAY={base.C},SIGMAZ={base.L/2};
E1:EMISSIONSOURCE,DISTRIBUTION=DIST1,R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0,ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;
ELIST1:EMISSIONSOURCELIST=(E1);
FS:FIELDSOLVER,TYPE="FFT2D5",NX={nx},NY={ny},NZ={nz},PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE=OPEN,REFPATHFNAME="{reference}",BEAMR={base.A},CLOSEDRING=FALSE,PIPESIZEX={base.BOX[0]},PIPESIZEY={base.BOX[1]},SCATTERLONGITUDINALLY=TRUE;
B1:BEAM,PARTICLE=PROTON,NALLOC={n},BCHARGE={charge:.17g},SOURCES="ELIST1";
D1:DRIFT,L=1,ELEMEDGE=1000;
L1:LINE=(D1);
TRACK,BEAM=B1,LINE=L1,MAXSTEPS=1,ZSTOP={{100}},DT={{{base.DT:.17g}}};
RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1;
ENDTRACK;
'''
    inp=directory/'tube.in';inp.write_text(text)
    digest=base.sha(base.BINARY);snapshot=ROOT/'sources/binaries'/digest/'opalx'
    snapshot.parent.mkdir(parents=True,exist_ok=True)
    if not snapshot.exists():
        shutil.copy2(base.BINARY,snapshot)
    manifest=dict(name=name,directory=str(directory),profile=src['profile'],mesh=list(mesh),
        pipe_size_m=list(base.BOX),radius_m=base.R,full_length_m=base.L,
        radial_semiaxis_m=base.A,vertical_semiaxis_m=base.C,beta=base.BETA,dt_s=base.DT,
        probe_only=probe_only,weighted_source=True,charge_C=charge,source=src,reference_path=str(reference),
        reference_path_sha256=base.sha(reference),path_step_m=pathstep,reference_path_points=len(np.loadtxt(reference)),
        h5=str(directory/'tube.h5'),expected_particles=n,distribution=str(checkpoint),
        distribution_sha256=base.sha(checkpoint),binary=str(base.BINARY),binary_sha256=digest,binary_snapshot=str(snapshot),
        input_sha256=base.sha(inp),generator_sha256=base.sha(__file__),mpi_ranks=mpi_ranks,
        points_sha256=base.sha(ROOT/'reference/points_extended.csv'),
        reference_fields_sha256=base.sha(ROOT/f'reference/{src["profile"]}_fields_reference.csv'),
        expected_q_dataset_sha256=src['probe_q_dataset_sha256' if probe_only else 'q_dataset_sha256'],
        expected_m_dataset_sha256=src['probe_m_dataset_sha256' if probe_only else 'm_dataset_sha256'],
        external_fields='none; frozen geometry only',audit_output_checkpoint=audit_checkpoint,
        command=[str(base.BINARY),'tube.in','--info','4','--restart',str(checkpoint)])
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');return directory,manifest


def run(directory,manifest):
    if manifest.get('returncode')==0:
        return
    if base.sha(base.BINARY)!=manifest['binary_sha256']:
        raise ValueError('Executable changed after manifest preparation')
    env=os.environ.copy();env.update(OMP_NUM_THREADS='4',OMP_PROC_BIND='false')
    command=manifest['command']
    if manifest['mpi_ranks']>1:
        command=['mpiexec','-n',str(manifest['mpi_ranks'])]+command
    start=time.monotonic()
    with (directory/'tube.out').open('w') as stream:
        result=subprocess.run(command,cwd=directory,env=env,stdout=stream,stderr=subprocess.STDOUT)
    manifest.update(returncode=result.returncode,elapsed_s=time.monotonic()-start,
                    driver_children_max_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({key:manifest[key] for key in ['name','profile','mesh','returncode','elapsed_s','driver_children_max_rss_bytes']}),flush=True)
    if result.returncode:
        raise RuntimeError('Weighted native run failed; see '+str(directory/'tube.out'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name');parser.add_argument('--profile',choices=['uniform','triangle'],required=True)
    parser.add_argument('--mesh',type=int,nargs=3,required=True)
    parser.add_argument('--ns',type=int,default=1280);parser.add_argument('--nrad',type=int,default=16)
    parser.add_argument('--nphi',type=int,default=64);parser.add_argument('--path-step',type=float,default=.02)
    parser.add_argument('--cross-layout',choices=['polar','area-cartesian'],default='polar')
    parser.add_argument('--box',type=float,nargs=2,default=list(base.BOX),help='Free-space transverse mesh box widths in metres')
    parser.add_argument('--mpi-ranks',type=int,default=1);parser.add_argument('--audit-checkpoint',action='store_true')
    parser.add_argument('--run',action='store_true');args=parser.parse_args()
    if args.box[0]<=2*base.A or args.box[1]<=2*base.C:
        raise ValueError('Box must contain the full charged ellipse with a CIC margin')
    base.BOX=tuple(args.box)
    src=source(args.profile,args.ns,args.nrad,args.nphi,args.cross_layout)
    for probe_only in [False,True]:
        directory,manifest=make(args.name+('-probes' if probe_only else ''),args.mesh,src,args.path_step,
                                probe_only,args.mpi_ranks,args.audit_checkpoint)
        if args.run:
            run(directory,manifest)
        else:
            print(directory/'tube.in')


if __name__=='__main__':
    main()
