#!/usr/bin/env python3
"""Read-only curved native data audit with independent complex-plane geometry."""
from pathlib import Path
import hashlib
import json
import math
import h5py
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
R=2.
C=299792458.


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(2**20),b''):h.update(chunk)
    return h.hexdigest()


def circle_material(position):
    zeta=position[:,0]+R+1j*position[:,2]
    return np.c_[np.abs(zeta)-R,position[:,1],R*np.angle(zeta)]


def native_arrays(group):
    ref=np.asarray(group.attrs['RefPartR'])
    pref=np.asarray(group.attrs['RefPartP'])
    theta=math.atan2(-pref[0],pref[2])
    c,s=math.cos(theta),math.sin(theta)
    local=np.c_[group['x'][:],group['y'][:],group['z'][:]]
    local_p=np.c_[group['px'][:],group['py'][:],group['pz'][:]]
    basis=np.array([[c,0.,-s],[0.,1.,0.],[s,0.,c]])
    order=np.argsort(group['id'][:])
    return (local@basis.T+ref)[order],(local_p@basis.T)[order]


def main():
    source_path=ROOT/'tracking/sources/bend-uniform-n1048576.json'
    source=json.loads(source_path.read_text())
    assert sha(source['npz'])==source['npz_sha256']
    with np.load(source['npz']) as f:
        initial=f['material_m'];ids=f['source_particle_id']
    n=len(initial);q=1e-11/n
    theta0=initial[:,2]/R
    bg=.001/math.sqrt(1-.001**2)
    result=dict(date='2026-11-04',source_npz_sha256=source['npz_sha256'],
                no_native_runs=True,no_production_edits=True,cases=[])
    moments=[]
    for code in ['opalx','pyorbit']:
        for mode in ['ZeroSC','10pC']:
            suffix='-e85' if code=='opalx' else ''
            case=ROOT/'tracking'/code/'runs'/f'bend-{mode}-10steps{suffix}'
            m=json.loads((case/'manifest.json').read_text())
            assert m['source']['npz_sha256']==source['npz_sha256']
            assert m['steps']==10 and m['mesh']==[128,128,512]
            assert abs(m['dt_s']-.1/(.001*C))<1e-21
            reference=np.loadtxt(m['reference_path'])[:,[1,2,3]]
            chord=np.linalg.norm(np.diff(reference,axis=0),axis=1)
            assert abs(chord.sum()-m['longitudinal_period_m'])<1e-14
            table=pd.read_csv(case/'moments.csv',float_precision='round_trip')
            assert table.step.tolist()==list(range(11))
            assert np.max(abs(table.time_s-np.arange(11)*m['dt_s']))<1e-18
            check=dict(code=code,mode=mode,identical_initial_source_hash=True,
                       rows=11,period_m=float(chord.sum()),
                       source_json_sha256=sha(m['source_json']),
                       maximum_geometric_sagitta_m=float(R-np.sqrt(R*R-(chord.max()/2)**2)))
            if code=='opalx':
                assert m['original_solver'] and not m['nonlocal_3D_operator']
                assert m['g']==6.36 and m['sc_field_update']=='MIDPOINT'
                assert abs(m['By_T']-bg*938272088.16/(C*R))<1e-18
                max_pos=max_p=max_sigma=max_mean=0.
                with h5py.File(case/'track.h5') as h:
                    assert len(h)==10
                    for key in sorted(h,key=lambda k:int(k.split('#')[-1])):
                        group=h[key]
                        t=float(np.asarray(group.attrs['TIME']).ravel()[0])
                        step=round(t/m['dt_s']);assert 1<=step<=10
                        assert np.array_equal(np.sort(group['id'][:]),ids)
                        assert np.max(abs(group['q'][:]-q))<q*5e-12
                        positions,p=native_arrays(group)
                        material=circle_material(positions)
                        mean=material.mean(axis=0);sigma=material.std(axis=0)
                        row=table[table.step==step].iloc[0]
                        stored_mean=np.array([row.mean_frenet_u_m,row.mean_frenet_y_m,
                            row.mean_frenet_s_m+R*row.reference_phase_rad])
                        stored_sigma=np.array([row.sigma_frenet_u_m,row.sigma_frenet_y_m,row.sigma_frenet_s_m])
                        max_sigma=max(max_sigma,float(np.max(abs(sigma-stored_sigma))))
                        max_mean=max(max_mean,float(np.max(abs(mean-stored_mean))))
                        assert max_sigma<1e-10 and max_mean<1e-10
                        if mode=='ZeroSC':
                            phase=step*2*math.atan(.001*C*m['dt_s']/(2*R))
                            exact=initial[:,0]*np.exp(1j*theta0)+R*np.exp(1j*(theta0+phase))
                            expected=np.c_[exact.real-R,initial[:,1],exact.imag]
                            expected_p=bg*np.c_[-np.sin(theta0+phase),np.zeros(n),np.cos(theta0+phase)]
                            max_pos=max(max_pos,float(np.max(abs(positions-expected))))
                            max_p=max(max_p,float(np.max(abs(p-expected_p))))
                            assert max_pos<1e-10 and max_p<1e-14
                        if step==10:
                            for j,c in enumerate(['u','y','s']):
                                moments.append(dict(code=code,mode=mode,component=c,
                                    sigma_m=sigma[j],absolute_mean_m=mean[j]))
                check.update(all_ten_native_q_ids_times_passed=True,
                    maximum_moment_sigma_residual_m=max_sigma,
                    maximum_common_absolute_mean_residual_m=max_mean)
                if mode=='ZeroSC':check.update(exact_discrete_Boris_position_residual_m=max_pos,
                    exact_discrete_Boris_momentum_residual_betagamma=max_p)
            else:
                assert m['fixed_lab_mesh'] and not m['transverse_work_patch']
                effective_g=m['longitudinal_period_m']*m['native_encoded_step_g']/.1
                assert abs(effective_g-6.36)<1e-14
                assert m['guard_check']['maximum_native_gradient']==0.
                with np.load(case/'final-particles.npz') as f:
                    positions=f['positions_m'];p=f['momenta_betagamma'];state=f['native_state']
                    assert np.array_equal(f['source_particle_id'],ids)
                assert np.isfinite(positions).all() and np.isfinite(p).all()
                material=circle_material(positions)
                reconstructed=np.c_[state[:,0],state[:,2],state[:,4]+1.]
                assert np.max(abs(material-reconstructed))<2e-15
                row=table[table.step==10].iloc[0]
                sigma=material.std(axis=0);mean=material.mean(axis=0)
                sigma_res=np.max(abs(sigma-np.array([row.sigma_frenet_u_m,row.sigma_frenet_y_m,row.sigma_frenet_s_m])))
                assert 'mean_absolute_s_m' in table
                mean_res=np.max(abs(mean-np.array([row.mean_frenet_u_m,row.mean_frenet_y_m,row.mean_absolute_s_m])))
                assert sigma_res<1e-9 and mean_res<1e-9,(case,sigma_res,mean_res,mean,row.mean_absolute_s_m)
                check.update(longitudinal_step_encoding_recovers_g=effective_g,
                    final_native_state_embedding_residual_m=float(np.max(abs(material-reconstructed))),
                    final_sigma_residual_m=float(sigma_res),absolute_mean_residual_m=float(mean_res),
                    absolute_arc_mean_column='mean_absolute_s_m',
                    original_frenet_mean_s_m=float(row.mean_frenet_s_m))
                if mode=='ZeroSC':
                    phase=.5
                    exact=initial[:,0]*np.exp(1j*theta0)+R*np.exp(1j*(theta0+phase))
                    expected=np.c_[exact.real-R,initial[:,1],exact.imag]
                    exact_material=circle_material(expected)
                    check.update(maximum_difference_from_exact_continuous_B_position_m=float(np.max(abs(positions-expected))),
                        RMS_difference_from_exact_continuous_B_percent=(100*(sigma/exact_material.std(axis=0)-1)).tolist(),
                        centroid_difference_from_exact_continuous_B_m=(mean-exact_material.mean(axis=0)).tolist())
                for j,c in enumerate(['u','y','s']):
                    moments.append(dict(code=code,mode=mode,component=c,
                        sigma_m=sigma[j],absolute_mean_m=mean[j]))
            result['cases'].append(check)
    final_moments=pd.DataFrame(moments)
    merged=pd.read_csv(ROOT/'tracking/analysis/moments.csv',float_precision='round_trip')
    merged=merged[(merged.geometry=='bend')&(merged.step==10)].copy()
    merged['code']=merged.code.map({'OPALX 2D5':'opalx','PyORBIT':'pyorbit'})
    merged['mode']=merged.zero_sc.map({True:'ZeroSC',False:'10pC'})
    compare=final_moments.merge(merged,on=['code','mode','component'],suffixes=('_independent','_merged'))
    assert len(compare)==12
    sigma_difference=float(abs(compare.sigma_m_independent-compare.sigma_m_merged).max())
    mean_difference=float(abs(compare.absolute_mean_m-compare.mean_m).max())
    assert sigma_difference<1e-9 and mean_difference<1e-9
    result['root_merged_analysis_check']=dict(components=12,
        maximum_sigma_difference_m=sigma_difference,
        maximum_absolute_arc_mean_difference_m=mean_difference,
        merged_moments_sha256=sha(ROOT/'tracking/analysis/moments.csv'))
    responses=[]
    for c in ['u','y','s']:
        responses.append(dict(component=c,**{code:float(
            final_moments[(final_moments.code==code)&(final_moments.component==c)&(final_moments['mode']=='10pC')].absolute_mean_m.iloc[0]
            -final_moments[(final_moments.code==code)&(final_moments.component==c)&(final_moments['mode']=='ZeroSC')].absolute_mean_m.iloc[0])
            for code in ['opalx','pyorbit']}))
    result['charged_minus_own_zeroSC_centroid_response_m']=responses
    result['passed']=True
    result['limits']=[
        'Original slice models only; this is not a corrected-curvature model tracking validation.',
        'Native PyORBIT sector maps are paraxial, and its SC coordinates remain Frenet while OPALX uses a 5mm polyline.',
        'The sagitta is a coordinate bound, not a field or trajectory error bound.',
        'Exactly ten steps provide a consistency screen without step convergence.',
        'Endpoint RMS-growth agreement does not extend to the weak radial or arc centroid responses.'
    ]
    final_moments.to_csv(OUT/'bend-tracking-final-moments.csv',index=False,float_format='%.17g')
    (OUT/'bend-tracking-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
