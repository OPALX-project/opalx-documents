"""Native OPALX frozen-field meshes for the 5 m, R=2 m uniform SACR tube."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import time

import numpy as np
import pandas as pd
from scipy.constants import c, proton_mass, e

ROOT=Path(__file__).resolve().parent
BINARY=Path('/Users/adelmann/git/opalx/build-omp/src/opalx')
R=2.; A=.005; C=.0005; L=5.; Q=1e-11; BETA=.001; DT=1e-17
BOX=(.016,.004); PATH_LENGTH=8.

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def points():
    return pd.read_csv(ROOT/'reference/points.csv',float_precision='round_trip')

def global_values(local):
    u,y,s=np.asarray(local).T
    theta=s/R
    co,si=np.cos(theta),np.sin(theta)
    position=np.c_[u*co-2*R*np.sin(theta/2)**2,y,(R+u)*si]
    bg=BETA/np.sqrt(1-BETA**2)
    momentum=bg*np.c_[-si,np.zeros_like(si),co]
    return np.column_stack([position[:,0],momentum[:,0],position[:,1],momentum[:,1],position[:,2],momentum[:,2]])

def source(ns,nrad,nphi,layout='polar'):
    directory=ROOT/'sources';directory.mkdir(exist_ok=True)
    name=f'tube-ns{ns}-nr{nrad}-np{nphi}'+('' if layout=='polar' else '-cartesian')
    path=directory/(name+'.dist');meta=directory/(name+'.json')
    if meta.exists():
        result=json.loads(meta.read_text())
        if not path.exists() or sha(path)!=result['sha256']:
            raise ValueError('Source integrity failed')
        return result
    if layout=='polar':
        radii=np.sqrt((np.arange(nrad)+.5)/nrad)
        base=2*np.pi*(np.arange(nphi)+.5)/nphi
        rr,pp=np.meshgrid(radii,base,indexing='ij');rr=rr.ravel();pp=pp.ravel()
        phi=pp.copy()
        # At fixed radius, physical measure is (1+a*r*cos(phi)/R) dphi.
        for _ in range(5):
            phi-=(phi+A*rr/R*np.sin(phi)-pp)/(1+A*rr/R*np.cos(phi))
        cross=np.c_[A*rr*np.cos(phi),C*rr*np.sin(phi)]
        quadrature='midpoint equal-area polar; exact Jacobian angular inverse'
    else:
        # Equal-area Cartesian midpoint cloud, clipped to the ellipse. This
        # avoids annular quadrature structure at a fine transverse CIC mesh.
        uu=-BOX[0]/2+(np.arange(nrad)+.5)*BOX[0]/nrad
        yy=-BOX[1]/2+(np.arange(nphi)+.5)*BOX[1]/nphi
        u0,y=np.meshgrid(uu,yy,indexing='ij');keep=(u0/A)**2+(y/C)**2<1
        u0=u0[keep];y=y[keep];w2=A*A*(1-(y/C)**2)
        # Conditional uniform-u CDF -> density proportional to 1+u/R.
        u=(2*R*u0+w2)/(np.sqrt(R*R+2*R*u0+w2)+R)
        cross=np.c_[u,y]
        quadrature='clipped Cartesian midpoint lattice; exact conditional Jacobian inverse'
    np.savez(directory/(name+'.npz'),cross_section_uy=cross)
    p=points();probes=p[['u_m','y_m','s_m']].to_numpy()
    nc=len(cross);nsource=ns*nc;ntotal=nsource+len(probes)
    with path.open('w') as stream:
        stream.write(f'{ntotal}\nx px y py z pz\n')
        for start in range(0,ns,32):
            s=-L/2+(np.arange(start,min(start+32,ns))+.5)*L/ns
            local=np.c_[np.tile(cross,(len(s),1)),np.repeat(s,nc)]
            np.savetxt(stream,global_values(local),fmt='%.17e')
        np.savetxt(stream,global_values(probes),fmt='%.17e')
    result=dict(path=str(path),sha256=sha(path),ns=ns,nrad=nrad,nphi=nphi,
                ncross=nc,source_particles=nsource,probe_particles=len(p),
                total_particles=ntotal,source_charge_C=Q*nsource/ntotal,
                macrocharge_C=Q/ntotal,
                mean_u_m=float(cross[:,0].mean()),expected_mean_u_m=A*A/(4*R),
                mean_y_m=float(cross[:,1].mean()),
                source_spacing_m=L/ns,quadrature=quadrature,layout=layout,
                script_sha256=sha(__file__),points_sha256=sha(ROOT/'reference/points.csv'))
    meta.write_text(json.dumps(result,indent=2)+'\n')
    return result

def reference(step):
    directory=ROOT/'sources';directory.mkdir(exist_ok=True)
    path=directory/f'path-step{step:g}.dat'
    if path.exists():return path
    # Exactly +/-4 m endpoints; target-centred segments give exact circle
    # tangent at every probe independently of the coarse path elsewhere.
    nodes=np.linspace(-4.,4.,round(8/step)+1)
    targets=np.unique(points().s_m.to_numpy())
    half=min(.001,step/4)
    for s in targets:
        nodes=nodes[abs(nodes-s)>half*1.001]
        nodes=np.r_[nodes,s-half,s+half]
    nodes=np.sort(nodes);theta=nodes/R
    data=np.zeros((len(nodes),15));data[:,0]=nodes+4
    data[:,1]=R*(np.cos(theta)-1);data[:,3]=R*np.sin(theta)
    data[:,4]=-BETA*np.sin(theta);data[:,6]=BETA*np.cos(theta)
    np.savetxt(path,data,header='s rx ry rz px py pz ex ey ez bx by bz ke time',fmt='%.17e')
    return path

def fieldmap():
    path=ROOT/'sources/uniform-by.g4blmap'
    if path.exists():return path
    p_GeV=BETA/np.sqrt(1-BETA**2)*proton_mass*c*c/e/1e9
    by=p_GeV/(.299792458*R)
    with path.open('w') as f:
        f.write('param normB=1 current=1\ngrid X0=-4500 Y0=-100 Z0=-2300 dX=2300 dY=100 dZ=2300 nX=3 nY=3 nZ=3\ndata\n')
        for x in [-4500,-2200,100]:
            for y in [-100,0,100]:
                for z in [-2300,0,2300]:
                    f.write(f'{x} {y} {z} 0 {by:.17g} 0\n')
    return path

def make(name,mesh,src,step,probe_only=False):
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
        with sourcepath.open('w') as f:
            f.write(f'{ntotal}\nx px y py z pz\n')
            np.savetxt(f,global_values(p[['u_m','y_m','s_m']].to_numpy()),fmt='%.17e')
    ref=reference(step);nx,ny,nz=mesh
    p0=BETA/np.sqrt(1-BETA**2)*proton_mass*c*c/e/1e9
    text=f'''// Frozen constant-section physical-density SACR tube; one tiny step.
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
    m=dict(name=name,directory=str(directory),mesh=list(mesh),pipe_size_m=list(BOX),
           radius_m=R,full_length_m=L,radial_semiaxis_m=A,vertical_semiaxis_m=C,
           beta=BETA,dt_s=DT,probe_only=probe_only,charge_C=charge,source=src,
           reference_path=str(ref),reference_path_sha256=sha(ref),path_step_m=step,
           reference_path_points=len(np.loadtxt(ref)),
           h5=str(directory/'tube.h5'),expected_particles=ntotal,
           distribution=str(sourcepath),distribution_sha256=sha(sourcepath),
           binary=str(BINARY),binary_sha256=sha(BINARY),input_sha256=sha(inp),
           generator_sha256=sha(__file__),external_fields='none; frozen geometry only',mpi_ranks=1)
    manifest_path.write_text(json.dumps(m,indent=2)+'\n')
    return directory,m

def run(directory,m):
    if m.get('returncode')==0:return
    env=os.environ.copy();env.update(OMP_NUM_THREADS='4',OMP_PROC_BIND='false')
    start=time.monotonic()
    with (directory/'tube.out').open('w') as f:
        result=subprocess.run([str(BINARY),'tube.in','--info','4'],cwd=directory,env=env,stdout=f,stderr=subprocess.STDOUT)
    m.update(returncode=result.returncode,elapsed_s=time.monotonic()-start)
    (directory/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps({k:m[k] for k in ['name','mesh','returncode','elapsed_s']}),flush=True)
    if result.returncode:raise RuntimeError('OPALX failed; see '+str(directory/'tube.out'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('name');p.add_argument('--mesh',type=int,nargs=3,required=True)
    p.add_argument('--ns',type=int,default=2560);p.add_argument('--nrad',type=int,default=16)
    p.add_argument('--nphi',type=int,default=64);p.add_argument('--path-step',type=float,default=.02)
    p.add_argument('--cross-layout',choices=['polar','cartesian'],default='polar')
    p.add_argument('--run',action='store_true');args=p.parse_args()
    src=source(args.ns,args.nrad,args.nphi,args.cross_layout)
    for probes in [False,True]:
        d,m=make(args.name+('-probes' if probes else ''),tuple(args.mesh),src,args.path_step,probes)
        if args.run:run(d,m)
        else:print(d/'tube.in',flush=True)

if __name__=='__main__':main()
