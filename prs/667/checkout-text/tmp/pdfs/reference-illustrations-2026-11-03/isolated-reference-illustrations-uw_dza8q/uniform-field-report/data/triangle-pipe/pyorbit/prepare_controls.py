#!/usr/bin/env python3
"""Compact equal-charge source controls; same construction as common cloud."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--ns',type=int,required=True)
    p.add_argument('--nr',type=int,default=16)
    p.add_argument('--nphi',type=int,default=32)
    a=p.parse_args()
    directory=Path(__file__).resolve().parent/'sources'
    directory.mkdir(exist_ok=True)
    target=directory/f'triangle-ns{a.ns}-nr{a.nr}-np{a.nphi}.npz'
    if target.exists(): raise FileExistsError(target)
    u=(np.arange(a.ns)+.5)/a.ns
    ss=np.where(u<.5,-5+5*np.sqrt(2*u),5-5*np.sqrt(2*(1-u)))
    rr=.005*np.sqrt((np.arange(a.nr)+.5)/a.nr)
    pp=2*np.pi*(np.arange(a.nphi)+.5)/a.nphi
    r,phi=np.meshgrid(rr,pp,indexing='ij')
    xy=np.c_[r.ravel()*np.cos(phi.ravel()),r.ravel()*np.sin(phi.ravel())]
    np.savez_compressed(target,s_nodes_m=ss,cross_xy_m=xy)
    meta=dict(ns=a.ns,nr=a.nr,nphi=a.nphi,ncross=len(xy),
        total_source_particles=len(ss)*len(xy),equal_real_proton_weight=1e14/(len(ss)*len(xy)),
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        physical_model='Triangle full length10m, centered uniform disk radius5mm; midpoint quantiles x equal-area radial/azimuthal midpoints',
        scope='Source-resolution control; no OPALX distribution generated')
    target.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(target)

if __name__=='__main__': main()
