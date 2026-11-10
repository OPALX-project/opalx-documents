"""Native frozen FFT2D5 free-space comparison with physical-profile SACR.

Generate by default; pass --run explicitly after the new binary is ready.
The full distribution and identical-macrocharge probe-only companion permit
linear subtraction of the diagnostic particles' own charge.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time

import numpy as np
import pandas as pd
from scipy.constants import c, proton_mass, e

ROOT=Path(__file__).resolve().parent
BINARY=Path('/Users/adelmann/git/opalx/build-omp/src/opalx')
R,A,C,L,Q,BETA,DT=2.,.005,.0005,5.,1e-11,.001,1e-17
BOX=(.016,.004)
PATH_LENGTH=8.


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def points():
    return pd.read_csv(ROOT/'reference/points_extended.csv',float_precision='round_trip')


def global_values(local):
    u,y,s=np.asarray(local).T
    theta=s/R;co,si=np.cos(theta),np.sin(theta)
    position=np.c_[u*co-2*R*np.sin(theta/2)**2,y,(R+u)*si]
    bg=BETA/np.sqrt(1-BETA**2)
    momentum=bg*np.c_[-si,np.zeros_like(si),co]
    return np.column_stack([position[:,0],momentum[:,0],position[:,1],momentum[:,1],position[:,2],momentum[:,2]])


def cross_section(nrad,nphi):
    """Equal-area polar quiet source, physical curved-volume density J.

    The angular CDF is phi+(a*r/R)sin(phi). Its inverse weights J exactly.
    Longitudinal phases are shared by each reflection quartet of the
    pre-inversion angular rule, preserving exact vertical reflection.
    """
    if nphi%4:
        raise ValueError('nphi must be divisible by four for quiet quartets')
    radii=np.sqrt((np.arange(nrad)+.5)/nrad)
    base=2*np.pi*(np.arange(nphi)+.5)/nphi
    rr,pp=np.meshgrid(radii,base,indexing='ij')
    rr=rr.ravel();pp=pp.ravel();phi=pp.copy()
    for _ in range(6):
        phi-=(phi+A*rr/R*np.sin(phi)-pp)/(1+A*rr/R*np.cos(phi))
    cross=np.c_[A*rr*np.cos(phi),C*rr*np.sin(phi)]
    nquad=nphi//4
    # Explicit quartet mapping avoids ambiguity at opposite quadrant edges.
    groups=np.empty(nphi,dtype=int)
    for j in range(nquad):
        groups[[j,nphi//2-1-j,nphi//2+j,nphi-1-j]]=j
    index=np.repeat(np.arange(nrad),nphi)*nquad+np.tile(groups,nrad)
    ngroup=nrad*nquad
    # Low discrepancy permutation of the phase ranks across radius and angle.
    order=np.argsort(np.mod(np.arange(ngroup)*((np.sqrt(5)-1)/2),1.))
    ranks=np.empty(ngroup,dtype=int);ranks[order]=np.arange(ngroup)
    phase=(ranks[index]+.5)/ngroup
    return cross,phase


def longitudinal_positions(profile,ns,phase,start,stop,stagger=True):
    """Positive |s|, each duplicated with exactly reflected negative s.

    Staggering inverse-CDF phases across quiet transverse quartets resolves
    the triangular tail without altering the exact physical profile. Every
    cross node is still represented by ns equal-charge longitudinal samples.
    """
    half=ns//2
    q=(np.arange(start,stop)[:,None]+(phase if stagger else np.full_like(phase,.5)))/half
    if profile=='uniform':
        return L/2*q
    return L/2*(-np.expm1(.5*np.log1p(-q)))


def source(profile,ns,nrad,nphi,stagger=True):
    if ns%2 or ns<2:
        raise ValueError('ns must be a positive even number')
    directory=ROOT/'sources';directory.mkdir(exist_ok=True)
    name=f'{profile}-ns{ns}-nr{nrad}-np{nphi}'+('-stagger' if stagger else '-layered')
    path=directory/(name+'.dist');meta=directory/(name+'.json')
    if meta.exists():
        result=json.loads(meta.read_text())
        if result['generator_sha256']!=sha(__file__):
            raise ValueError('Source generator changed; use a new source name or remove this generated source')
        if not path.exists() or sha(path)!=result['sha256']:
            raise ValueError('Source integrity failed')
        return result
    cross,phase=cross_section(nrad,nphi)
    np.savez(directory/(name+'.npz'),cross_section_uy=cross,longitudinal_phase=phase)
    probes=points()[['u_m','y_m','s_m']].to_numpy()
    nc=len(cross);nsource=ns*nc;ntotal=nsource+len(probes)
    sum_s2=0.;smin=np.inf;smax=0.
    with path.open('w') as stream:
        stream.write(f'{ntotal}\nx px y py z pz\n')
        for start in range(0,ns//2,16):
            sp=longitudinal_positions(profile,ns,phase,start,min(start+16,ns//2),stagger)
            sum_s2+=2*float(np.sum(sp*sp));smin=min(smin,float(sp.min()));smax=max(smax,float(sp.max()))
            for sign in [-1.,1.]:
                local=np.c_[np.tile(cross,(len(sp),1)),sign*sp.ravel()]
                np.savetxt(stream,global_values(local),fmt='%.17e')
        np.savetxt(stream,global_values(probes),fmt='%.17e')
    result=dict(path=str(path),sha256=sha(path),profile=profile,ns=ns,nrad=nrad,nphi=nphi,
        ncross=nc,source_particles=nsource,probe_particles=len(probes),total_particles=ntotal,
        nominal_charge_C=Q,source_charge_C=Q*nsource/ntotal,macrocharge_C=Q/ntotal,
        mean_u_m=float(cross[:,0].mean()),expected_mean_u_m=A*A/(4*R),
        mean_y_m=float(cross[:,1].mean()),mean_s_m=0.,mean_s_squared_m2=sum_s2/nsource,
        expected_mean_s_squared_m2=(L/2)**2/(3 if profile=='uniform' else 6),
        min_abs_s_m=smin,max_abs_s_m=smax,end_gap_m=L/2-smax,
        source_full_density='physical rho(s) uniform over each ellipse; physical Jacobian J=1+u/R',
        longitudinal_sampling='positive inverse-CDF with exact s reflection; quartet-staggered phases' if stagger else 'positive midpoint inverse-CDF with exact s reflection',
        longitudinal_stagger=stagger,layout='equal-area polar; exact J angular-CDF inverse',
        generator_sha256=sha(__file__),points_sha256=sha(ROOT/'reference/points_extended.csv'))
    meta.write_text(json.dumps(result,indent=2)+'\n')
    return result


def reference(step):
    directory=ROOT/'sources';directory.mkdir(exist_ok=True)
    path=directory/f'path-step{step:g}.dat'
    if path.exists():
        return path
    halfpath=PATH_LENGTH/2
    nodes=np.linspace(-halfpath,halfpath,round(PATH_LENGTH/step)+1)
    targets=np.unique(points().s_m.to_numpy())
    separation=float(np.diff(targets).min())
    half=min(.001,step/4,separation/4)
    for s in targets:
        nodes=nodes[abs(nodes-s)>half*1.001]
        nodes=np.r_[nodes,s-half,s+half]
    nodes=np.sort(nodes);theta=nodes/R
    data=np.zeros((len(nodes),15));data[:,0]=nodes+halfpath
    data[:,1]=R*(np.cos(theta)-1);data[:,3]=R*np.sin(theta)
    data[:,4]=-BETA*np.sin(theta);data[:,6]=BETA*np.cos(theta)
    np.savetxt(path,data,header='s rx ry rz px py pz ex ey ez bx by bz ke time',fmt='%.17e')
    return path


def make(name,mesh,src,step,probe_only=False,mpi_ranks=1):
    directory=ROOT/'runs'/name;directory.mkdir(parents=True,exist_ok=True)
    manifest_path=directory/'manifest.json'
    if manifest_path.exists():
        old=json.loads(manifest_path.read_text())
        if old.get('returncode')==0:
            if sha(directory/'tube.in')!=old['input_sha256'] or sha(BINARY)!=old['binary_sha256']:
                raise ValueError('Preserved run integrity mismatch')
            return directory,old
    sourcepath=Path(src['path']);ntotal=src['total_particles'];charge=Q
    if probe_only:
        sourcepath=directory/'probes.dist';p=points()
        ntotal=len(p);charge=src['macrocharge_C']*ntotal
        with sourcepath.open('w') as stream:
            stream.write(f'{ntotal}\nx px y py z pz\n')
            np.savetxt(stream,global_values(p[['u_m','y_m','s_m']].to_numpy()),fmt='%.17e')
    ref=reference(step);nx,ny,nz=mesh
    p0=BETA/np.sqrt(1-BETA**2)*proton_mass*c*c/e/1e9
    text=f'''// Frozen {src['profile']} physical-density curved tube; one tiny step.
OPTION, VERSION=10900;
OPTION, PSDUMPFREQ=1;
OPTION, STATDUMPFREQ=1;
OPTION, EBDUMP=TRUE;
OPTION, MINBINEMITTED=0;
REAL P0={p0:.17g};
DIST1: DISTRIBUTION, TYPE=FROMFILE, NPARTDIST={ntotal}, FNAME="{sourcepath}";
E1: EMISSIONSOURCE, DISTRIBUTION=DIST1, R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0,ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;
ELIST1: EMISSIONSOURCELIST=(E1);
FS: FIELDSOLVER,TYPE="FFT2D5",NX={nx},NY={ny},NZ={nz},PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE=OPEN,REFPATHFNAME="{ref}",BEAMR={A:.17g},CLOSEDRING=FALSE,PIPESIZEX={BOX[0]:.17g},PIPESIZEY={BOX[1]:.17g},SCATTERLONGITUDINALLY=TRUE;
B1: BEAM,PARTICLE=PROTON,NALLOC={ntotal},BCHARGE={charge:.17g},SOURCES="ELIST1";
D1: DRIFT,L=1,ELEMEDGE=1000;
L1: LINE=(D1);
TRACK,BEAM=B1,LINE=L1,MAXSTEPS=1,ZSTOP={{100}},DT={{{DT:.17g}}};
RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1;
ENDTRACK;
'''
    inp=directory/'tube.in';inp.write_text(text)
    binary_digest=sha(BINARY)
    binary_snapshot=ROOT/'sources'/'binaries'/binary_digest/'opalx'
    binary_snapshot.parent.mkdir(parents=True,exist_ok=True)
    if not binary_snapshot.exists():
        shutil.copy2(BINARY,binary_snapshot)
    elif sha(binary_snapshot)!=binary_digest:
        raise ValueError('Archived executable integrity mismatch')
    m=dict(name=name,directory=str(directory),profile=src['profile'],mesh=list(mesh),pipe_size_m=list(BOX),
        radius_m=R,full_length_m=L,radial_semiaxis_m=A,vertical_semiaxis_m=C,beta=BETA,dt_s=DT,
        probe_only=probe_only,charge_C=charge,source=src,reference_path=str(ref),reference_path_sha256=sha(ref),
        path_step_m=step,reference_path_points=len(np.loadtxt(ref)),h5=str(directory/'tube.h5'),
        expected_particles=ntotal,distribution=str(sourcepath),distribution_sha256=sha(sourcepath),
        binary=str(BINARY),binary_sha256=binary_digest,binary_snapshot=str(binary_snapshot),
        input_sha256=sha(inp),generator_sha256=sha(__file__),
        reference_fields_sha256=sha(ROOT/f'reference/{src["profile"]}_fields_reference.csv'),
        points_sha256=sha(ROOT/'reference/points_extended.csv'),external_fields='none; frozen geometry only',mpi_ranks=mpi_ranks)
    manifest_path.write_text(json.dumps(m,indent=2)+'\n')
    return directory,m


def run(directory,manifest):
    if manifest.get('returncode')==0:
        return
    env=os.environ.copy();env.update(OMP_NUM_THREADS='4',OMP_PROC_BIND='false')
    if sha(BINARY)!=manifest['binary_sha256']:
        raise ValueError('Executable changed after input generation; regenerate the case manifest')
    command=[str(BINARY),'tube.in','--info','4']
    if manifest['mpi_ranks']>1:
        command=['mpiexec','-n',str(manifest['mpi_ranks'])]+command
    start=time.monotonic()
    with (directory/'tube.out').open('w') as stream:
        result=subprocess.run(command,cwd=directory,env=env,stdout=stream,stderr=subprocess.STDOUT)
    manifest.update(returncode=result.returncode,elapsed_s=time.monotonic()-start,command=command)
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({key:manifest[key] for key in ['name','profile','mesh','mpi_ranks','returncode','elapsed_s']}),flush=True)
    if result.returncode:
        raise RuntimeError('OPALX failed; see '+str(directory/'tube.out'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name');parser.add_argument('--profile',choices=['uniform','triangle'],required=True)
    parser.add_argument('--mesh',type=int,nargs=3,required=True)
    parser.add_argument('--ns',type=int,default=5120);parser.add_argument('--nrad',type=int,default=16)
    parser.add_argument('--nphi',type=int,default=64);parser.add_argument('--path-step',type=float,default=.02)
    parser.add_argument('--layered-source',action='store_true',help='disable stagger for a source-sampling control')
    parser.add_argument('--mpi-ranks',type=int,default=1);parser.add_argument('--run',action='store_true')
    args=parser.parse_args()
    src=source(args.profile,args.ns,args.nrad,args.nphi,not args.layered_source)
    for probes in [False,True]:
        directory,manifest=make(args.name+('-probes' if probes else ''),tuple(args.mesh),src,args.path_step,probes,args.mpi_ranks)
        if args.run:
            run(directory,manifest)
        else:
            print(directory/'tube.in',flush=True)


if __name__=='__main__':
    main()
