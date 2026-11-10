"""Native one-step OPALX triangular pipe-field benchmark; no solver changes."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from prepare_common import sha
BINARY=Path('/Users/adelmann/git/opalx/build-omp/src/opalx')

def run(name,mesh,source,width):
    cfg=json.loads((ROOT/'common/config.json').read_text());src=json.loads(source.read_text())
    points=pd.read_csv(ROOT/'common/probes.csv');common=ROOT/'common'
    path=common/'straight-path.dat'
    data=np.zeros((2,15));data[:,0]=[0,12];data[:,3]=[-6,6];data[:,6]=cfg['beta']
    np.savetxt(path,data,header='s rx ry rz px py pz ex ey ez bx by bz ke time',fmt='%.17e')
    for companion in (False,True):
        directory=ROOT/'opalx/runs'/(name+('-probes' if companion else ''));directory.mkdir(parents=True,exist_ok=True)
        manifest=directory/'manifest.json'
        if manifest.exists() and json.loads(manifest.read_text()).get('returncode')==0:
            old=json.loads(manifest.read_text())
            if sha(BINARY)!=old['binary_sha256'] or sha(directory/'triangle.in')!=old['input_sha256']:
                raise ValueError('Completed-run integrity mismatch')
            continue
        n=src['probe_particles']+(0 if companion else src['source_particles'])
        charge=n*src['macrocharge_C'];dist=Path(src['distribution'])
        if companion:
            dist=directory/'probes.dist';arr=np.zeros((len(points),6))
            arr[:,[0,2,4]]=points[['x_m','y_m','s_m']];arr[:,5]=cfg['beta_gamma']
            with dist.open('w') as f:
                f.write(f'{n}\nx px y py z pz\n');np.savetxt(f,arr,fmt='%.17e')
        nx,ny,nz=mesh
        text=f'''// Frozen triangular source, equivalent one-metre kick; numerical width also enters native longitudinal g.
OPTION, VERSION=10900;
OPTION, PSDUMPFREQ=1;
OPTION, STATDUMPFREQ=1;
OPTION, EBDUMP=TRUE;
OPTION, MINBINEMITTED=0;
DIST1: DISTRIBUTION,TYPE=FROMFILE,NPARTDIST={n},FNAME="{dist}";
E1: EMISSIONSOURCE,DISTRIBUTION=DIST1,R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0,ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;
ELIST1: EMISSIONSOURCELIST=(E1);
FS: FIELDSOLVER,TYPE="FFT2D5",NX={nx},NY={ny},NZ={nz},PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE="CIRCULAR",REFPATHFNAME="{path}",BEAMR={cfg['beam_radius_m']:.17g},CLOSEDRING=FALSE,PIPESIZEX={width:.17g},PIPESIZEY={width:.17g},SCATTERLONGITUDINALLY=TRUE;
B1: BEAM,PARTICLE=PROTON,NALLOC={n},BCHARGE={charge:.17g},SOURCES="ELIST1";
D1: DRIFT,L=1,ELEMEDGE=1000;
L1: LINE=(D1);
TRACK,BEAM=B1,LINE=L1,MAXSTEPS=1,ZSTOP={{100}},DT={{{cfg['dt_s']:.17g}}};
RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1;
ENDTRACK;
'''
        inp=directory/'triangle.in';inp.write_text(text)
        m=dict(case=directory.name,mesh=list(mesh),numerical_width_m=width,companion=companion,expected_particles=n,
               charge_C=charge,source=src,config=cfg,binary=str(BINARY),binary_sha256=sha(BINARY),
               input_sha256=sha(inp),distribution=str(dist),distribution_sha256=sha(dist),
               reference_path=str(path),reference_path_sha256=sha(path),mpi_ranks=1,
               h5=str(directory/'triangle.h5'),script_sha256=sha(__file__))
        env=os.environ.copy();env.update(OMP_NUM_THREADS='4',OMP_PROC_BIND='false')
        start=time.monotonic()
        with (directory/'triangle.out').open('w') as stream:
            result=subprocess.run([str(BINARY),'triangle.in','--info','4'],cwd=directory,env=env,stdout=stream,stderr=subprocess.STDOUT)
        m.update(returncode=result.returncode,elapsed_s=time.monotonic()-start)
        manifest.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(case=m['case'],returncode=m['returncode'],elapsed_s=m['elapsed_s'])),flush=True)
        if result.returncode:raise RuntimeError(str(directory/'triangle.out'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--mesh',nargs=3,type=int,required=True)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--width',type=float,default=.020)
    a=p.parse_args();run(a.name,a.mesh,a.source,a.width)
