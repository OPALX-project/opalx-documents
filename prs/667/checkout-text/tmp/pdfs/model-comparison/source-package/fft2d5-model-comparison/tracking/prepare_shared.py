#!/usr/bin/env python3
"""Shared cold physical sources for native ten-step tracking comparisons.

Existing audited D4 disk/quasi-uniform longitudinal generators are reused.
The bent source samples physical volume J du dy ds; all particles have the
same charge and momentum magnitude, directed along the local tangent.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, sys
import numpy as np

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
NS,NR,NPHI=64,64,256
A,L,R,Q,BETA=.02,5.,2.,1e-11,.001


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    straight_helper=STUDY/'opalx/run_straight_octets.py'
    bend_helper=STUDY/'curved/opalx/source_geometry.py'
    sh=load('tracking_straight_source',straight_helper)
    bh=load('tracking_bent_source',bend_helper)
    bg=BETA/np.sqrt(1-BETA*BETA)
    for geometry in ['straight','bend']:
        cross,phase=sh.quiet_cross_section(A,NR,NPHI) if geometry=='straight' else bh.cross_section(NR,NPHI)
        blocks=[]
        for begin in range(0,NS//2,8):
            sp=L/2*(np.arange(begin,min(begin+8,NS//2))[:,None]+phase)/(NS//2)
            for sign in [-1.,1.]:
                blocks.append(np.c_[np.tile(cross,(len(sp),1)),sign*sp.ravel()])
        material=np.concatenate(blocks);n=len(material)
        assert n==NS*NR*NPHI
        # Compensated sums avoid the 4e-13 relative accumulation error of
        # NumPy's axis-0 sequential reduction for the million-particle array.
        mean=np.array([math.fsum(material[:,j])/n for j in range(3)])
        mean_square=np.array([math.fsum(material[:,j]**2)/n for j in range(3)])
        assert np.allclose(mean_square[:2],A*A/4,rtol=2e-13,atol=0)
        u,y,s=material.T
        theta=s/R if geometry=='bend' else np.zeros(n)
        co,si=np.cos(theta),np.sin(theta)
        cartesian=np.c_[u*co-2*R*np.sin(theta/2)**2,y,(R+u)*si] if geometry=='bend' else material.copy()
        momentum=bg*np.c_[-si,np.zeros(n),co]
        stem=ROOT/'sources'/f'{geometry}-uniform-n{n}'
        meta=stem.with_suffix('.json')
        if meta.exists():
            prior=json.loads(meta.read_text())
            assert prior['generator_sha256']==sha(__file__)
            for key in ['npz','distribution']:
                assert sha(prior[key])==prior[key+'_sha256']
            print(meta);continue
        npz=stem.with_suffix('.npz')
        np.savez_compressed(npz,material_m=material,cartesian_m=cartesian,
            momenta_betagamma=momentum,positions_local_m=material,positions_m=cartesian,
            source_particle_id=np.arange(n,dtype=np.int64),macrocharge_C=Q/n,
            charge_C=Q,beta=BETA,longitudinal_period_m=12. if geometry=='straight' else 2*np.pi*R)
        distribution=stem.with_suffix('.dist')
        with distribution.open('w') as stream:
            stream.write(f'{n}\nx px y py z pz\n')
            for begin in range(0,n,32768):
                stop=min(n,begin+32768);rr,pp=cartesian[begin:stop],momentum[begin:stop]
                np.savetxt(stream,np.c_[rr[:,0],pp[:,0],rr[:,1],pp[:,1],rr[:,2],pp[:,2]],fmt='%.17e')
        record=dict(geometry=geometry,profile='uniform',source_particles=n,
            charge_C=Q,macrocharge_C=Q/n,full_length_m=L,cross_section_radius_m=A,
            nominal_rms_x_m=A/2,nominal_rms_y_m=A/2,bend_radius_m=R if geometry=='bend' else None,
            beta=BETA,momentum_betagamma=bg,ns=NS,nrad=NR,nphi=NPHI,
            material_mean_m=mean.tolist(),material_std_m=np.sqrt(mean_square-mean**2).tolist(),
            material_raw_rms_m=np.sqrt(mean_square).tolist(),
            longitudinal_period_m=12. if geometry=='straight' else 2*np.pi*R,
            sampling='audited D4 phases; physical-volume J sampling in bend; no fitted rescaling',
            npz=str(npz),npz_sha256=sha(npz),distribution=str(distribution),distribution_sha256=sha(distribution),
            generator=str(Path(__file__).resolve()),generator_sha256=sha(__file__),
            helper_sha256={str(straight_helper):sha(straight_helper),str(bend_helper):sha(bend_helper)})
        meta.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))


if __name__=='__main__':main()
