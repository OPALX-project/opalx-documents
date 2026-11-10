"""Deterministic equal-charge triangular-bunch source shared by both codes."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
CONFIG = dict(full_length_m=10., beam_radius_m=.005, pipe_radius_m=.020,
              kinetic_energy_GeV=.4, proton_mass_GeV=.93827208816,
              elementary_charge_C=1.602176634e-19, real_protons=1e14,
              epsilon0_F_per_m=8.8541878128e-12, kick_length_m=1.,
              path_length_m=12., dt_s=1e-20)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def prepare(ns=8192, nr=16, nphi=32):
    directory=ROOT/'common';directory.mkdir(exist_ok=True)
    cfg=CONFIG.copy();cfg['charge_C']=cfg['real_protons']*cfg['elementary_charge_C']
    cfg['gamma']=1+cfg['kinetic_energy_GeV']/cfg['proton_mass_GeV']
    cfg['beta_gamma']=np.sqrt(cfg['gamma']**2-1)
    cfg['beta']=cfg['beta_gamma']/cfg['gamma']
    (directory/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    rows=[]
    for s in np.linspace(-5,5,101):
        rows.append(dict(point_id=f'axis-{len(rows):03}',x_m=0.,y_m=0.,s_m=s,kind='axis'))
    for s in (-2.5,2.5):
        for r in np.linspace(-cfg['beam_radius_m'],cfg['beam_radius_m'],41):
            rows.append(dict(point_id=f'radial-{len(rows):03}',x_m=r,y_m=0.,s_m=s,kind='radial'))
    pd.DataFrame(rows).to_csv(directory/'probes.csv',index=False,float_format='%.17g')
    name=f'triangle-ns{ns}-nr{nr}-np{nphi}'
    meta=directory/(name+'.json');dist=directory/(name+'.dist');npz=directory/(name+'.npz')
    if meta.exists():
        m=json.loads(meta.read_text())
        if sha(dist)!=m['distribution_sha256'] or sha(npz)!=m['npz_sha256']:
            raise ValueError('Preserved source hash mismatch')
        return meta
    # Midpoint quantiles of triangular probability density on [-L/2,L/2].
    u=(np.arange(ns)+.5)/ns;h=cfg['full_length_m']/2
    s=np.where(u<.5,-h+h*np.sqrt(2*u),h-h*np.sqrt(2*(1-u)))
    radii=cfg['beam_radius_m']*np.sqrt((np.arange(nr)+.5)/nr)
    phi=2*np.pi*(np.arange(nphi)+.5)/nphi
    r,p=np.meshgrid(radii,phi,indexing='ij')
    cross=np.c_[r.ravel()*np.cos(p.ravel()),r.ravel()*np.sin(p.ravel())]
    np.savez_compressed(npz,s_nodes_m=s,cross_xy_m=cross)
    probes=pd.read_csv(directory/'probes.csv');nsource=ns*len(cross)
    with dist.open('w') as f:
        f.write(f'{nsource+len(probes)}\nx px y py z pz\n')
        for start in range(0,ns,64):
            ss=s[start:start+64];data=np.zeros((len(ss)*len(cross),6))
            data[:,0]=np.tile(cross[:,0],len(ss));data[:,2]=np.tile(cross[:,1],len(ss))
            data[:,4]=np.repeat(ss,len(cross));data[:,5]=cfg['beta_gamma']
            np.savetxt(f,data,fmt='%.17e')
        data=np.zeros((len(probes),6));data[:,[0,2,4]]=probes[['x_m','y_m','s_m']]
        data[:,5]=cfg['beta_gamma'];np.savetxt(f,data,fmt='%.17e')
    data=dict(name=name,ns=ns,nrad=nr,nphi=nphi,ncross=len(cross),
              source_particles=nsource,probe_particles=len(probes),
              macrocharge_C=cfg['charge_C']/nsource,
              source_charge_C=cfg['charge_C'],npz=str(npz),distribution=str(dist),
              distribution_sha256=sha(dist),npz_sha256=sha(npz),
              probe_sha256=sha(directory/'probes.csv'),script_sha256=sha(__file__),
              cross_mean_r2_m2=float(np.mean(np.sum(cross**2,axis=1))),
              source_description='Equal-area polar midpoint tensor x inverse-CDF triangular midpoint quantiles; equal source charges; probes appended separately')
    meta.write_text(json.dumps(data,indent=2)+'\n')
    print(meta,flush=True)
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ns',type=int,default=8192)
    p.add_argument('--nr',type=int,default=16);p.add_argument('--nphi',type=int,default=32)
    a=p.parse_args();print(prepare(a.ns,a.nr,a.nphi))
