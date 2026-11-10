"""Compact tensor source refinements for PyORBIT's native deposition checks."""
from pathlib import Path
import json
import numpy as np
from prepare_common import ROOT, sha

def write(ns,nr,nphi):
    directory=ROOT/'common';name=f'triangle-ns{ns}-nr{nr}-np{nphi}'
    path=directory/(name+'.npz')
    u=(np.arange(ns)+.5)/ns
    s=np.where(u<.5,-5+5*np.sqrt(2*u),5-5*np.sqrt(2*(1-u)))
    r,p=np.meshgrid(.005*np.sqrt((np.arange(nr)+.5)/nr),2*np.pi*(np.arange(nphi)+.5)/nphi,indexing='ij')
    cross=np.c_[r.ravel()*np.cos(p.ravel()),r.ravel()*np.sin(p.ravel())]
    if not path.exists():np.savez_compressed(path,s_nodes_m=s,cross_xy_m=cross)
    m=dict(npz=str(path),npz_sha256=sha(path),ns=ns,nrad=nr,nphi=nphi,
           ncross=nr*nphi,source_particles=ns*nr*nphi,script_sha256=sha(__file__),
           source_charge_C=1e14*1.602176634e-19,
           description='Same continuum and equal-charge tensor construction as prepare_common.py; compact only, no OPALX distribution emitted')
    (directory/(name+'-compact.json')).write_text(json.dumps(m,indent=2)+'\n')
    print(path)

if __name__=='__main__':
    write(65536,16,32)
    write(8192,32,64)
