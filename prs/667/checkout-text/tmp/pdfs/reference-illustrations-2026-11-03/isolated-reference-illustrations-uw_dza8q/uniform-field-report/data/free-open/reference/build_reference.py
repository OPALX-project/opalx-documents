"""Reproduce physical-profile SACR fields and numerical/physics validation."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
import pandas as pd
from scipy.constants import epsilon_0
from scipy.integrate import quad
from uniform_reference import field as uniform_field, position, transverse_scale
from profile_reference import triangle_field, direct_volume_field, primitives, cross_rule

ROOT=Path(__file__).resolve().parent
A,C,H,R,Q=.005,.0005,2.5,2.,1e-11
K=1/(4*np.pi*epsilon_0)
SCALE=transverse_scale(A,C)


def targets():
    old=pd.read_csv(ROOT/'points.csv')
    old['original_target']=True
    extra=[]
    for st in [-2.4999,-2.499,-.05,-.01,.01,.05,2.499,2.4999]:
        p=position(st,0.,0.,R)
        extra.append(dict(point_id=f'extra_axis_{st:+.4f}',label=f'extra_axis_{st:+.4f}',
                          u_m=0.,y_m=0.,s_m=st,end_distance_m=H-abs(st),
                          cross_section_normalized_radius=0.,x_m=p[0],global_y_m=p[1],
                          z_m=p[2],original_target=False))
    # Retain the original string identifiers exactly.
    result=pd.concat([old,pd.DataFrame(extra)],ignore_index=True)
    if result.point_id.duplicated().any():
        raise ValueError('Duplicate target identifiers')
    return result


def calc(profile,target,nphi=4096,nrad=96,info=False):
    if profile=='uniform':
        return uniform_field(A,C,H,target,R,nphi=nphi,nrad=nrad,return_info=info)
    return triangle_field(A,C,H,target,R,nphi=nphi,nrad=nrad,return_info=info)


def make_tables():
    points=targets()
    points.to_csv(ROOT/'points_extended.csv',index=False)
    rows=[]
    for profile in ['uniform','triangle']:
        for nphi,nrad in [(256,32),(512,32),(1024,64),(2048,64),(4096,96)]:
            ts=time.time()
            for pt in points.itertuples(index=False):
                target=(pt.u_m,pt.y_m,pt.s_m)
                val,info=calc(profile,target,nphi,nrad,True)
                rho=Q/(np.pi*A*C*H*(2 if profile=='uniform' else 1))
                out=pt._asdict()|dict(profile=profile,nphi=nphi,nrad=nrad,
                    rho_normalization_C_m3=rho,F_r_m=val[0],F_y_m=val[1],F_s_m=val[2],
                    E_r_V_m=K*rho*val[0],E_y_V_m=K*rho*val[1],E_s_V_m=K*rho*val[2],
                    side_neval=info['side_neval'],
                    side_quad_error_normalized=info['side_quad_error_normalized'])
                if profile=='triangle':
                    out['F_s_filament_m']=info['filament_s']
                    out['tangent_identity_difference_m']=val[2]-info['filament_s']
                rows.append(out)
            print(f'{profile} nphi={nphi} nrad={nrad}, {len(points)} points: {time.time()-ts:.2f}s',flush=True)
            pd.DataFrame(rows).to_csv(ROOT/'quadrature_fields.csv',index=False)
    allrows=pd.DataFrame(rows)
    final=allrows[allrows.nphi==4096].copy()
    final.to_csv(ROOT/'fields_reference.csv',index=False)
    for profile in ['uniform','triangle']:
        final[final.profile==profile].to_csv(ROOT/f'{profile}_fields_reference.csv',index=False)
    changes=[]
    for profile in ['uniform','triangle']:
        previous=None
        for nphi in [256,512,1024,2048,4096]:
            now=allrows[(allrows.profile==profile)&(allrows.nphi==nphi)].set_index('point_id')
            if previous is not None:
                for component in ['r','y','s']:
                    delta=(now[f'F_{component}_m']-previous[f'F_{component}_m']).abs()
                    fieldscale=max(final.loc[final.profile==profile,f'F_{component}_m'].abs().max(),SCALE*1e-12)
                    ii=delta.idxmax()
                    changes.append(dict(profile=profile,nphi=nphi,nrad=int(now.nrad.iloc[0]),component=component,
                        max_change_m=delta.max(),max_change_over_component_scale=delta.max()/fieldscale,
                        max_change_over_transverse_scale=delta.max()/SCALE,point_id=ii,
                        worst_label=now.loc[ii,'label']))
            previous=now
    changes=pd.DataFrame(changes)
    changes.to_csv(ROOT/'quadrature_changes.csv',index=False)
    return final,changes


def validation(final,changes):
    checks=[]
    # Elliptic primitives checked against direct, adaptive elementary integrals.
    for st,u,ut,y,yt in [(1.25,.001,.0025,.0001,.000125),(0.,0.,0.,1e-8,0.),(2.49,-.004,0.,.0002,0.)]:
        rr=np.hypot(ut-u,yt-y)
        aa=(R+ut)*(R+u)
        for lo,hi in [(-H,0.),(0.,H)]:
            plo,clo=primitives(lo,st,rr,u,ut,R)
            phi,chi=primitives(hi,st,rr,u,ut,R)
            for kind,actual in [('potential',phi-plo),('cosine',chi-clo)]:
                def fn(s):
                    delta=(s-st)/R
                    return (1 if kind=='potential' else np.cos(delta))/np.sqrt(rr*rr+4*aa*np.sin(delta/2)**2)
                expected,error=quad(fn,lo,hi,points=[st] if lo<st<hi else None,epsabs=1e-10,epsrel=2e-12,limit=1000)
                checks.append(dict(kind=kind,s_target=st,r_m=rr,lo=lo,hi=hi,analytic=float(actual),direct=expected,
                                   difference=float(actual-expected),relative_difference=float((actual-expected)/expected)))
    pd.DataFrame(checks).to_csv(ROOT/'primitive_checks.csv',index=False)

    # Separate refinement of cross-section Gauss radial quadrature.
    radial=[]
    for target in [(0.,0.,0.),(.0025,.000125,1.25),(0.,0.,2.4999)]:
        ref=calc('triangle',target,4096,128)
        for nr in [8,16,32,64,96]:
            val=calc('triangle',target,1024,nr)
            radial.append(dict(u_m=target[0],y_m=target[1],s_m=target[2],nrad=nr,
                radial_difference_m=val[0]-ref[0],vertical_difference_m=val[1]-ref[1],
                tangent_difference_m=val[2]-ref[2],max_difference_over_transverse_scale=max(abs(val-ref))/SCALE))
    pd.DataFrame(radial).to_csv(ROOT/'radial_quadrature_checks.csv',index=False)

    # Independent original Coulomb volume integral, no boundary identity.
    volume=[]
    for target in [(0.,0.,0.),(.0025,.000125,1.25),(0.,0.,2.49)]:
        ref=calc('triangle',target)
        for nphi,nrad in [(128,24),(256,48),(512,64)]:
            val,info=direct_volume_field(A,C,H,target,R,nphi,nrad,quadrature_tol=2e-9)
            for k,component in enumerate(['r','y','s']):
                volume.append(dict(u_m=target[0],y_m=target[1],s_m=target[2],nphi=nphi,nrad=nrad,
                    component=component,boundary_m=ref[k],volume_m=val[k],difference_m=val[k]-ref[k],
                    difference_over_transverse_scale=(val[k]-ref[k])/SCALE,
                    relative_component_difference=(val[k]-ref[k])/ref[k] if abs(ref[k])>1e-15 else np.nan,
                    neval=info['neval']))
    volume=pd.DataFrame(volume)
    volume.to_csv(ROOT/'volume_checks.csv',index=False)

    # Curvilinear differential Maxwell checks, away from cusp and surface.
    pde=[]
    for target in [(.001,.0001,.7),(-.002,-.0001,2.2)]:
        center=np.asarray(target)
        value=calc('triangle',center,2048,64)
        for refinement in [1.,.5]:
            deriv=[]
            for direction,step in enumerate([1e-5,1e-6,1e-3]):
                delta=np.zeros(3);delta[direction]=step*refinement
                samples=[calc('triangle',center+j*delta,2048,64) for j in [-2,-1,1,2]]
                deriv.append((samples[0]-8*samples[1]+8*samples[2]-samples[3])/(12*step*refinement))
            du,dy,ds=deriv
            metric=(R+center[0])/R
            div=du[0]+dy[1]+value[0]/(R+center[0])+ds[2]/metric
            curl=np.array([dy[2]-ds[1]/metric,ds[0]/metric-du[2]-value[2]/(R+center[0]),du[1]-dy[0]])
            exact=4*np.pi*(1-abs(center[2])/H)
            pde.append(dict(u_m=center[0],y_m=center[1],s_m=center[2],step_refinement=refinement,
                            divergence=div,expected_divergence=exact,divergence_relative_error=(div-exact)/exact,
                            curl_r=curl[0],curl_y=curl[1],curl_s=curl[2],curl_norm_over_4pi=np.linalg.norm(curl)/(4*np.pi)))
    pde=pd.DataFrame(pde);pde.to_csv(ROOT/'pde_checks.csv',index=False)

    # Reflection parity, zero reference components excluded from relative errors.
    symmetry=[]
    for profile in ['uniform','triangle']:
        target=np.array([.0025,.000125,1.25]);base=calc(profile,target,2048,64)
        for kind,pt,sign in [('longitudinal',target*np.array([1,1,-1]),np.array([1,1,-1])),
                             ('vertical',target*np.array([1,-1,1]),np.array([1,-1,1]))]:
            reflected=calc(profile,pt,2048,64)
            symmetry.append(dict(profile=profile,reflection=kind,
                            maximum_difference_over_transverse_scale=max(abs(reflected-sign*base))/SCALE))
    pd.DataFrame(symmetry).to_csv(ROOT/'symmetry_checks.csv',index=False)

    # Physical-volume charge normalization checked by quadrature, including J.
    uu,yy,weights,rr=cross_rule(A,C,(0.,0.,0.),1024,64)
    area_j=float(np.sum(weights*(1+uu/R)))
    norm=[]
    for profile in ['uniform','triangle']:
        longitudinal=2*H if profile=='uniform' else quad(lambda ss:1-abs(ss)/H,-H,H,points=[0.],epsabs=1e-13)[0]
        rho=Q/(np.pi*A*C*H*(2 if profile=='uniform' else 1))
        numerical=rho*area_j*longitudinal
        norm.append(dict(profile=profile,charge_C=numerical,charge_relative_error=(numerical-Q)/Q,
                         cross_section_integral_J_m2=area_j,density_normalization_C_m3=rho))
    pd.DataFrame(norm).to_csv(ROOT/'charge_checks.csv',index=False)

    # Uniform data reproduce the existing exact SACR at the original 43 targets.
    old=pd.read_csv(ROOT.parent.parent/'frozen-r2/reference/fields_reference.csv')
    oldcols=list(old.columns)
    comparison=[]
    ours=final[(final.profile=='uniform')&final.original_target].set_index('point_id')
    # Historical reference uses the same F units, detect historical labels explicitly.
    for component in ['r','y','s']:
        longname={'r':'radial','y':'vertical','s':'tangential'}[component]
        candidates=[f'F_{component}_m',f'F_{longname}',f'field_{component}_m',f'E{component}_over_krho_m']
        col=next((name for name in candidates if name in oldcols),None)
        if col is None:
            continue
        previous=old.set_index('point_id')[col]
        comparison.append(dict(component=component,max_difference_m=float((ours[f'F_{component}_m']-previous).abs().max())))
    pd.DataFrame(comparison).to_csv(ROOT/'uniform_previous_checks.csv',index=False)

    last=changes[changes.nphi==4096]
    allfields=pd.read_csv(ROOT/'quadrature_fields.csv')
    previous=allfields[allfields.nphi==2048].set_index(['profile','point_id'])
    current=allfields[allfields.nphi==4096].set_index(['profile','point_id'])
    pointwise=[]
    for component in ['r','y','s']:
        col=f'F_{component}_m'
        # Relative errors of symmetry-zero components have no numerical meaning.
        nonzero=current[col].abs()>1e-14
        pointwise.extend(((current.loc[nonzero,col]-previous.loc[nonzero,col]).abs()/
                          current.loc[nonzero,col].abs()).tolist())
    filament=float(final.loc[final.profile=='triangle','tangent_identity_difference_m'].abs().max())
    endvolume=volume[volume.nphi==512]
    results=dict(model='independent exact Coulomb weighted-boundary SACR; physical longitudinal density',
        parameters=dict(radius_m=R,full_length_m=2*H,radial_semiaxis_m=A,vertical_semiaxis_m=C,charge_C=Q),
        number_original_targets=43,number_total_targets=int(len(final)//2),
        field_units='SI electric field V/m; F=E/(k*rho_normalization) in metres',
        final_quadrature=dict(side_angular_nodes=4096,cross_section_angular_nodes=4096,radial_gauss_nodes=96),
        last_refinement_max_change_over_component_scale=float(last.max_change_over_component_scale.max()),
        last_refinement_max_change_over_transverse_scale=float(last.max_change_over_transverse_scale.max()),
        last_refinement_max_relative_pointwise_nonzero_component_change=max(pointwise),
        relative_component_reference_threshold_m=1e-14,
        triangle_tangent_identity_max_abs_difference_m=filament,
        independent_volume_max_abs_error_over_transverse_scale=float(endvolume.difference_over_transverse_scale.abs().max()),
        independent_volume_max_relative_nonzero_component_error=float(endvolume.relative_component_difference.abs().max()),
        pde_max_relative_divergence_error=float(pde.divergence_relative_error.abs().max()),
        pde_max_curl_norm_over_4pi=float(pde.curl_norm_over_4pi.max()),
        max_charge_relative_error=max(abs(x['charge_relative_error']) for x in norm),
        primitive_max_relative_error=max(abs(row['relative_difference']) for row in checks),
        uniform_previous_reference_max_abs_difference_m=max(row['max_difference_m'] for row in comparison),
        source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['uniform_reference.py','profile_reference.py','build_reference.py']})
    results['passed']=bool(results['last_refinement_max_change_over_component_scale']<1e-3
        and results['independent_volume_max_relative_nonzero_component_error']<1e-3
        and results['pde_max_relative_divergence_error']<1e-5
        and results['pde_max_curl_norm_over_4pi']<1e-5)
    (ROOT/'acceptance.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2),flush=True)
    if not results['passed']:
        raise SystemExit('Reference validation failed')


if __name__=='__main__':
    final,changes=make_tables()
    validation(final,changes)
