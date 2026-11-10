"""Build reproducible constant-section R=2 m SACR frozen-field references."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import time

import numpy as np
import pandas as pd

from tube_reference import (field, tangent_endpoint, transverse_scale,
                            position, basis)

ROOT=Path(__file__).resolve().parent
A,C,B,R=.005,.0005,2.5,2.
DIRECTIONS=("radial","vertical","tangential")
LEVELS=((128,16),(256,32),(512,64),(1024,128),(2048,128),(4096,128))


def points():
    rows=[dict(point_id="centre",label="centre",u_m=0.,y_m=0.,s_m=0.)]
    for i,label in ((0,"r"),(1,"y")):
        for fraction in (-.9,-.5,.5,.9):
            target=[0.,0.,0.]
            target[i]=fraction*(A if i==0 else C)
            rows.append(dict(point_id=f"axis_{label}_{fraction:+.1f}",
                             label="transverse_midplane",u_m=target[0],
                             y_m=target[1],s_m=target[2]))
    for fraction in (-.998,-.996,-.98,-.9,-.5,.5,.9,.98,.996,.998):
        label="bulk_axis" if abs(fraction)<=.9 else "end_axis"
        rows.append(dict(point_id=f"axis_s_{fraction:+.3f}",label=label,
                         u_m=0.,y_m=0.,s_m=fraction*B))
    for sf in (-.9,-.5,.5,.9):
        for uf in (-.5,.5):
            for yf in (-.25,.25):
                rows.append(dict(point_id=f"bulk_{uf:+.2f}_{yf:+.2f}_{sf:+.2f}",
                                 label="bulk_off_axis",u_m=uf*A,y_m=yf*C,s_m=sf*B))
    for sf in (-.996,.996):
        for uf in (-.5,.5):
            for yf in (-.25,.25):
                rows.append(dict(point_id=f"end_{uf:+.2f}_{yf:+.2f}_{sf:+.3f}",
                                 label="end_off_axis",u_m=uf*A,y_m=yf*C,s_m=sf*B))
    result=pd.DataFrame(rows)
    result["end_distance_m"]=B-result.s_m.abs()
    result["cross_section_normalized_radius"]=np.sqrt((result.u_m/A)**2+(result.y_m/C)**2)
    xyz=np.array([position(p.s_m,p.u_m,p.y_m,R) for p in result.itertuples()])
    result[["x_m","global_y_m","z_m"]]=xyz
    assert len(result)==43
    return result


def coordinate_local(xyz,radius):
    x,y,z=xyz
    if math.isinf(radius):return np.array([x,y,z])
    theta=np.arctan2(z,radius+x)
    return np.array([np.hypot(radius+x,z)-radius,y,radius*theta])


def independent_checks(final,scales):
    checks={}
    # Endpoints integrate the Coulomb kernel along source arclength instead
    # of using the boundary normal, and include the physical Jacobian ratio.
    endpoints=[]
    for p in final.itertuples():
        target=(p.u_m,p.y_m,p.s_m)
        es=tangent_endpoint(A,C,B,target,R,1024,128)
        endpoints.append(dict(point_id=p.point_id,surface_tangential=p.F_tangential,
                              endpoint_tangential=es,
                              normalized_difference=(es-p.F_tangential)/scales[2]))
    endpoint_frame=pd.DataFrame(endpoints)
    endpoint_frame.to_csv(ROOT/"endpoint_checks.csv",index=False)
    checks["maximum_endpoint_difference_normalized"]=float(endpoint_frame.normalized_difference.abs().max())
    # Local electrostatic Maxwell checks are made by perturbing global XYZ;
    # differentiating rotating local components directly would be incorrect.
    pde=[]
    targets=[np.array([0.,0.,0.]),np.array([.35*A,.2*C,.4*B]),
             np.array([-.3*A,-.25*C,-.9*B]),
             np.array([.3*A,.2*C,B-.01])]
    for ti,target in enumerate(targets):
        xyz=position(target[2],target[0],target[1],R)
        for h in (5e-6,2.5e-6):
            derivative=np.empty((3,3))
            for j in range(3):
                dx=np.zeros(3);dx[j]=h
                values=[]
                for sign in (-1,1):
                    local=coordinate_local(xyz+sign*dx,R)
                    values.append(basis(local[2],R)@field(A,C,B,local,R,512,64))
                derivative[:,j]=(values[1]-values[0])/(2*h)
            div=np.trace(derivative)
            curl=np.array([derivative[2,1]-derivative[1,2],
                           derivative[0,2]-derivative[2,0],
                           derivative[1,0]-derivative[0,1]])
            pde.append(dict(target=ti,h_m=h,div_F=div,
                            relative_divergence_error=div/(4*np.pi)-1,
                            curl_norm_over_4pi=np.linalg.norm(curl)/(4*np.pi)))
    pde_frame=pd.DataFrame(pde);pde_frame.to_csv(ROOT/"pde_checks.csv",index=False)
    finest=pde_frame[pde_frame.h_m==2.5e-6]
    checks["maximum_relative_divergence_error"]=float(finest.relative_divergence_error.abs().max())
    checks["maximum_curl_norm_over_4pi"]=float(finest.curl_norm_over_4pi.max())
    # The b->infinity straight-cylinder limit has an exact interior ellipse
    # field. Its two equal boundary scales are used throughout this study.
    target=np.array([.4*A,-.3*C,0.])
    expected=4*np.pi*np.array([C*target[0]/(A+C),A*target[1]/(A+C),0.])
    straight=field(A,C,2500.,target,math.inf,512,64)
    checks["long_straight_ellipse_difference_normalized"]=float(np.max(np.abs(straight-expected))/scales[0])
    # A Cartesian bend-plane reflection reverses local s but not local r/y;
    # a vertical reflection reverses only the vertical component.
    lookup={tuple(np.round([p.u_m,p.y_m,p.s_m],12)):p for p in final.itertuples()}
    symmetry=[]
    for p in final.itertuples():
        value=np.array([getattr(p,f"F_{d}") for d in DIRECTIONS])
        for name,coord,signs in (
            ("s_reflection",[p.u_m,p.y_m,-p.s_m],[1,1,-1]),
            ("y_reflection",[p.u_m,-p.y_m,p.s_m],[1,-1,1])):
            other=lookup.get(tuple(np.round(coord,12)))
            if other is None:continue
            other_value=np.array([getattr(other,f"F_{d}") for d in DIRECTIONS])
            difference=(value-np.array(signs)*other_value)/scales
            symmetry.append(dict(point_id=p.point_id,reflection=name,
                                 maximum_normalized_difference=np.max(np.abs(difference))))
    symmetry_frame=pd.DataFrame(symmetry)
    symmetry_frame.to_csv(ROOT/"symmetry_checks.csv",index=False)
    checks["maximum_symmetry_difference_normalized"]=float(symmetry_frame.maximum_normalized_difference.max())
    # At the bend centre the Coulomb source-angle integration is analytic.
    # Compare that volume integral with a separately assembled Gauss boundary
    # integral (not the interior-target API) to check geometry and end caps.
    from tube_reference import disk_rule
    from numpy.polynomial.legendre import leggauss
    rows=[]
    for order in (32,64,128):
        nphi=256
        gx,gw=leggauss(order)
        ss,ww=B*gx,B*gw
        phi=2*np.pi*(np.arange(nphi)+.5)/nphi
        cp,sp=np.cos(phi),np.sin(phi)
        u,y=A*cp,C*sp
        radius_source=R+u
        distance=np.sqrt(radius_source**2+y**2)
        jac=radius_source/R
        # Project boundary normals into the global x direction.
        side=np.sum(ww[:,None]*C*cp[None,:]*jac[None,:]
                    *np.cos(ss[:,None]/R)/distance[None,:])*(2*np.pi/nphi)
        du,dy,weights=disk_rule(nphi,order)
        du,dy=A*du,C*dy
        rs=R+du;distance=np.sqrt(rs**2+dy**2)
        caps=-2*np.sin(B/R)*np.sum(A*C*weights/distance)
        volume=-2*np.sin(B/R)*np.sum(A*C*weights*rs**2/distance**3)
        boundary=side+caps
        rows.append(dict(radial_gauss_nodes=order,nphi=nphi,
                         volume_global_x=volume,boundary_global_x=boundary,
                         relative_difference=boundary/volume-1))
    volume_frame=pd.DataFrame(rows)
    volume_frame.to_csv(ROOT/"volume_surface_checks.csv",index=False)
    checks["maximum_volume_surface_relative_difference"]=float(volume_frame.relative_difference.abs().max())
    checks["passed"]=all(checks[name]<1e-7 for name in checks)
    return checks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points-only",action="store_true")
    args=parser.parse_args()
    pts=points();pts.to_csv(ROOT/"points.csv",index=False)
    if args.points_only:
        print(f"Wrote {len(pts)} exact diagnostic points",flush=True);return
    started=time.perf_counter()
    records=[]
    for nphi,nrad in LEVELS:
        for p in pts.itertuples():
            value,info=field(A,C,B,(p.u_m,p.y_m,p.s_m),R,nphi,nrad,return_info=True)
            records.append(dict(point_id=p.point_id,nphi=nphi,nrad=nrad,
                                **{f"F_{d}":float(value[i]) for i,d in enumerate(DIRECTIONS)},
                                side_neval=info["side_neval"],
                                side_quad_error_normalized=info["side_quad_error_normalized"]))
        print(f"Completed {nphi} x {nrad}: {time.perf_counter()-started:.2f}s",flush=True)
    all_fields=pd.DataFrame(records)
    all_fields.to_csv(ROOT/"fields_all_resolutions.csv",index=False)
    final=pts.merge(all_fields[all_fields.nphi==LEVELS[-1][0]],on="point_id")
    previous=all_fields[all_fields.nphi==LEVELS[-2][0]].set_index("point_id").loc[final.point_id]
    scale_perp=transverse_scale(A,C)
    scale_s=float(final.F_tangential.abs().max())
    scales=np.array([scale_perp,scale_perp,scale_s])
    refinement_rows=[]
    for (coarse,_),(fine,_) in zip(LEVELS[:-1],LEVELS[1:]):
        f=all_fields[all_fields.nphi==fine].set_index("point_id").loc[pts.point_id]
        p=all_fields[all_fields.nphi==coarse].set_index("point_id").loc[pts.point_id]
        for i,d in enumerate(DIRECTIONS):
            diff=(f[f"F_{d}"].to_numpy()-p[f"F_{d}"].to_numpy())/scales[i]
            for point_id,value in zip(pts.point_id,diff):
                refinement_rows.append(dict(point_id=point_id,direction=d,
                                             coarse_nphi=coarse,fine_nphi=fine,
                                             normalized_change=value))
    refinements=pd.DataFrame(refinement_rows)
    refinements.to_csv(ROOT/"quadrature_changes.csv",index=False)
    refinements.groupby(["coarse_nphi","fine_nphi","direction"])["normalized_change"].agg(
        lambda values:values.abs().max()).rename("maximum_normalized_change").reset_index().to_csv(
            ROOT/"quadrature_summary.csv",index=False)
    change=[]
    for i,d in enumerate(DIRECTIONS):
        final[f"scale_{d}"]=scales[i]
        final[f"normalized_{d}"]=final[f"F_{d}"]/scales[i]
        final[f"last_change_{d}"]=final[f"F_{d}"].to_numpy()-previous[f"F_{d}"].to_numpy()
        final[f"normalized_last_change_{d}"]=final[f"last_change_{d}"]/scales[i]
        change.append(float(final[f"normalized_last_change_{d}"].abs().max()))
    final.to_csv(ROOT/"fields_reference.csv",index=False)
    checks=independent_checks(final,scales)
    summary=dict(model="SACR uniform-physical-density constant-section finite curved tube",
                 scope="43 sampled interior frozen-field targets; no tracking claim",
                 geometry=dict(a_m=A,c_m=C,half_length_m=B,radius_m=R,
                               volume_m3=float(np.pi*A*C*2*B)),
                 field_units="F=E/(k*rho), k=1/(4*pi*epsilon0), units metre",
                 local_coordinate_and_field_order=["radial","vertical","tangential"],
                 scales_div_k_rho_m=dict(zip(DIRECTIONS,map(float,scales))),
                 scale_definition="radial and vertical: 4*pi*a*c/(a+c); tangential: maximum absolute converged SACR Es over the fixed 43 diagnostic targets",
                 points=43,levels=LEVELS,
                 final_normalized_refinement_changes=dict(zip(DIRECTIONS,change)),
                 refinement_tolerance=1e-6,
                 independent_checks=checks,
                 passed=bool(max(change)<1e-6 and checks["passed"]),
                 runtime_s=time.perf_counter()-started,
                 source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (ROOT/"tube_reference.py",Path(__file__))})
    (ROOT/"acceptance.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    if not summary["passed"]:raise RuntimeError("Reference checks did not pass")


if __name__=="__main__":main()
