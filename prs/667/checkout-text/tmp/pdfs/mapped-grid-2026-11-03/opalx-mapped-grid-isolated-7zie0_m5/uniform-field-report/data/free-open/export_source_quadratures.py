"""Compact, self-contained physical-cell source evidence (no large H5 file)."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import run_grid_study as grid
import run_study as base

ROOT=base.ROOT


def main():
    output=ROOT/'analysis/source_quadratures';output.mkdir(parents=True,exist_ok=True)
    catalog=[]
    for path in sorted((ROOT/'sources').glob('cell-*.json')):
        meta=json.loads(path.read_text())
        xy,area=grid.cross_cell_charges(*meta['source_mesh'][:2],meta['source_box_m'],meta['cell_area_gauss_order'])
        ss,longweight=grid.longitudinal_cells(meta['source_mesh'][2],meta['profile'])
        norm=meta['normalization_density_C_m3'];hasher=hashlib.sha256()
        for start in range(0,len(ss),32):
            charge=(norm*longweight[start:start+32,None]*area).ravel()
            hasher.update(charge.tobytes())
        hasher.update(np.full(meta['probe_particles'],meta['macrocharge_C'],dtype=np.float64).tobytes())
        if hasher.hexdigest()!=meta['q_dataset_sha256']:
            raise ValueError('Compact reconstruction disagrees with original q attributes: '+path.name)
        compact=output/(path.stem+'.npz')
        np.savez_compressed(compact,cross_uy_m=xy,cross_integral_J_m2=area,
                            s_m=ss,profile_integral_ds_m=longweight,
                            density_normalization_C_m3=norm,
                            probe_uy_s_m=base.points()[['u_m','y_m','s_m']].to_numpy(),
                            probe_q_C=meta['macrocharge_C'],radius_m=base.R,beta=base.BETA)
        catalog.append(dict(source=path.stem,profile=meta['profile'],source_mesh=meta['source_mesh'],
            source_box_m=meta['source_box_m'],gauss_order=meta['cell_area_gauss_order'],
            source_particles=meta['source_particles'],source_charge_C=meta['source_charge_C'],
            compact_npz=compact.name,compact_sha256=base.sha(compact),
            full_q_attributes_sha256=hasher.hexdigest(),full_q_reconstruction_passed=True,
            schema='For each s, q_i=density_normalization*profile_integral_ds*cross_integral_J. Positions from curved X(s,u,y). Append listed probes. m_i=q_i/e*proton mass[GeV].',
            original_source_checkpoint_sha256=meta['path_sha256']))
    (output/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    pd.DataFrame(catalog).to_csv(output/'catalog.csv',index=False)
    print(f'Exported {len(catalog)} compact source quadratures; every original full q-attribute hash reproduced.')


if __name__=='__main__':
    main()
