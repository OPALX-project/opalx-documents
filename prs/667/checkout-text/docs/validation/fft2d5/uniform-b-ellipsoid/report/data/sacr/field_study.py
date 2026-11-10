"""Reproducible SACR field verification at interior points and increasing radius.

Uniform physical density on a tapered curved ellipsoid. This is a static-field
study; no OPALX output, g-factor, softening or tracking model is used.
"""
from pathlib import Path
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
import os
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import pandas as pd
from scipy.integrate import quad_vec
from validate_dubin_limit import dubin_field, sacr_field, tangent_endpoint

ROOT = Path(__file__).resolve().parent
DIRECTIONS = ("radial", "vertical", "tangential")
CASES = {"sphere": (.005, .005, .005),
         "previous_100mm_ellipsoid": (.005, .05, .0005),
         "five_metre_ellipsoid": (.005, 2.5, .0005)}
RADII = (2., 5., 10., 20., 50., 100., 200., 500., 1000., 2000., math.inf)
TOLERANCE = 1e-8   # Resolve weak large-R curvature differences above quadrature.
LEVELS = (128, 256, 512, 1024, 2048, 4096)


def point_set():
    rows = [("centre", "symmetry", 0., 0., 0.)]
    for index, label in enumerate(("r", "y", "s")):
        for value in (-.9, -.5, .5, .9):
            xyz = [0., 0., 0.]
            xyz[index] = value
            rows.append((f"axis_{label}_{value:+.1f}", "axes", *xyz))
    for x in (-.2, .2):
        for y in (-.15, .15):
            for s in (-.3, .3):
                rows.append((f"bulk_{x:+.2f}_{y:+.2f}_{s:+.2f}", "bulk", x,y,s))
    for x,y in ((.35,.2),(-.35,-.2)):
        for s in (-.6,.6):
            rows.append((f"end_bulk_{x:+.2f}_{y:+.2f}_{s:+.2f}", "off_axis",x,y,s))
    for x,y,sabs,label in ((.1,.1,.9,"near_end"),(.85,.2,.1,"near_radial_wall"),
                           (.1,.9,.1,"near_vertical_wall"),(.55,.45,.5,"diagonal")):
        for s in (-sabs,sabs):
            rows.append((f"{label}_{s:+.2f}", label,x,y,s))
    data = pd.DataFrame(rows,columns=["point_id","group","u_over_a","y_over_c","s_over_b"])
    data["normalized_radius"] = np.linalg.norm(data.iloc[:,2:5],axis=1)
    assert len(data)==33 and data.normalized_radius.max()<.95
    return data


def characteristic(a,b,c):
    return dubin_field(a,b,c,[a,c,b])


def surface_vectorized(a,b,c,target,radius,nphi):
    """Same boundary integral as the scalar prototype, vectorized in phi.

    Components are projected before integration onto the target's r/y/s basis.
    Normalizing each component makes the adaptive norm sensitive to the weak
    longitudinal field as well as the stronger transverse fields.
    """
    ut,yt,st = target
    if (ut/a)**2+(yt/c)**2+(st/b)**2>=1:
        raise ValueError("Target is not strictly inside the test shape")
    if not math.isinf(radius) and (radius<=a or b/radius>=np.pi):
        raise ValueError("Non-injective curved source")
    phi = 2*np.pi*(np.arange(nphi)+.5)/nphi
    cp,sp = np.cos(phi),np.sin(phi)
    scales = characteristic(a,b,c)
    def f(mu):
        w = np.sqrt(max(0.,1-mu*mu))
        u,y = a*w*cp,c*w*sp
        if math.isinf(radius):
            delta,jac = 0.,1.
            distance = np.sqrt((ut-u)**2+(yt-y)**2+(st-b*mu)**2)
        else:
            delta = (b*mu-st)/radius
            jac = 1+u/radius
            distance = np.sqrt((ut-u)**2+(yt-y)**2
                               +4*(radius+ut)*(radius+u)*np.sin(delta/2)**2)
        ar,ay,ass = b*c*jac*w*cp,a*b*jac*w*sp,a*c*mu
        cd,sd = np.cos(delta),np.sin(delta)
        area = np.array([ar*cd-ass*sd,ay,ar*sd+ass*cd])
        return (area/distance/scales[:,None]).ravel()
    value,error,info = quad_vec(f,-1,1,points=[st/b],epsabs=2e-11,epsrel=2e-11,
                               limit=800,full_output=True)
    if not info.success:
        raise RuntimeError(f"Surface quadrature failed: {info.message}")
    value = value.reshape(3,nphi).sum(axis=1)*(2*np.pi/nphi)*scales
    # Norm-based adaptive error estimate, not a rigorous componentwise bound.
    error_scaled = float(2*np.pi*error/np.sqrt(nphi))
    return value,error_scaled,int(info.neval)


def endpoint_vectorized(a,b,c,target,radius,nphi):
    """Independent tangential integral with transverse-dependent endpoints."""
    ut,yt,st=target
    phi=2*np.pi*(np.arange(nphi)+.5)/nphi
    cp,sp=np.cos(phi),np.sin(phi)
    scale=characteristic(a,b,c)[2]
    def f(w):
        rr=np.sqrt(max(0.,1-w*w))
        u,y=a*rr*cp,c*rr*sp
        if math.isinf(radius):
            dp=np.sqrt((ut-u)**2+(yt-y)**2+(st-b*w)**2)
            dm=np.sqrt((ut-u)**2+(yt-y)**2+(st+b*w)**2)
            ratio=1.
        else:
            rt,rs=radius+ut,radius+u
            dp=np.sqrt((ut-u)**2+(yt-y)**2+4*rt*rs*np.sin((b*w-st)/(2*radius))**2)
            dm=np.sqrt((ut-u)**2+(yt-y)**2+4*rt*rs*np.sin((-b*w-st)/(2*radius))**2)
            ratio=rs/rt
        return a*c*w*ratio*(1/dp-1/dm)/scale
    value,error,info=quad_vec(f,0,1,points=[abs(st)/b],epsabs=2e-11,epsrel=2e-11,
                             limit=800,full_output=True)
    if not info.success:
        raise RuntimeError(f"Endpoint quadrature failed: {info.message}")
    return float(value.sum()*(2*np.pi/nphi)*scale),float(error)


def task(job):
    case,p,radius=job
    a,b,c=CASES[case]
    target=np.array([p["u_over_a"]*a,p["y_over_c"]*c,p["s_over_b"]*b])
    scales=characteristic(a,b,c)
    exact=dubin_field(a,b,c,target)
    records=[];refinements=[];previous=None;best=None
    for nphi in LEVELS:
        start=time.perf_counter()
        value,error,neval=surface_vectorized(a,b,c,target,radius,nphi)
        elapsed=time.perf_counter()-start
        for i,direction in enumerate(DIRECTIONS):
            record=dict(case=case,point_id=p["point_id"],radius_m=radius,nphi=nphi,
                        direction=direction,sacr_field=float(value[i]),dubin_field=float(exact[i]),
                        characteristic_scale=float(scales[i]),
                        normalized_difference=float((value[i]-exact[i])/scales[i]),
                        relative_difference=float(value[i]/exact[i]-1) if abs(exact[i])>1e-8*scales[i] else np.nan,
                        quad_error_norm=error,adaptive_evaluations=neval,runtime_s=elapsed)
            records.append(record)
        change=np.full(3,np.inf) if previous is None else np.abs(value-previous)/scales
        if previous is not None:
            for i,direction in enumerate(DIRECTIONS):
                refinements.append(dict(case=case,point_id=p["point_id"],radius_m=radius,
                                        direction=direction,coarse_nphi=nphi//2,fine_nphi=nphi,
                                        normalized_change=float(change[i])))
        # At least 128/256/512 are evaluated for every point so their worst-point
        # summary curves always cover the same complete point set.
        flat_ok=not math.isinf(radius) or np.max(np.abs(value-exact)/scales)<TOLERANCE
        if nphi>=512 and change.max()<TOLERANCE and flat_ok:
            best=nphi
            break
        previous=value
    converged=best is not None
    if best is None:best=LEVELS[-1]
    endpoint=None
    if case=="five_metre_ellipsoid" and (math.isinf(radius) or radius in (2.,20.)):
        endpoint_value,endpoint_error=endpoint_vectorized(a,b,c,target,radius,best)
        endpoint=dict(case=case,point_id=p["point_id"],radius_m=radius,nphi=best,
                      surface_tangential=float(value[2]),endpoint_tangential=endpoint_value,
                      normalized_difference=float((endpoint_value-value[2])/scales[2]),
                      endpoint_quad_error=endpoint_error)
    return dict(records=records,refinements=refinements,best_nphi=best,converged=converged,
                endpoint=endpoint,case=case,point_id=p["point_id"],radius_m=radius)


def scalar_implementation_checks(points):
    tests=[("sphere","centre",math.inf),
           ("previous_100mm_ellipsoid","bulk_+0.20_+0.15_+0.30",math.inf),
           ("previous_100mm_ellipsoid","bulk_-0.20_-0.15_-0.30",2.),
           ("five_metre_ellipsoid","axis_s_-0.9",math.inf),
           ("five_metre_ellipsoid","axis_s_+0.5",2.),
           ("five_metre_ellipsoid","near_vertical_wall_+0.10",20.)]
    rows=[]
    for case,point_id,radius in tests:
        p=points[points.point_id==point_id].iloc[0]
        a,b,c=CASES[case]
        target=np.array([p.u_over_a*a,p.y_over_c*c,p.s_over_b*b])
        vector,_,_=surface_vectorized(a,b,c,target,radius,128)
        scalar=sacr_field(a,b,c,target,radius=radius,nphi=128)
        scale=characteristic(a,b,c)
        for i,d in enumerate(DIRECTIONS):
            rows.append(dict(case=case,point_id=point_id,radius_m=radius,direction=d,
                             normalized_difference=float((vector[i]-scalar[i])/scale[i])))
    frame=pd.DataFrame(rows)
    assert frame.normalized_difference.abs().max()<1e-8
    return frame


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir",type=Path,default=ROOT/"study-results")
    parser.add_argument("--workers",type=int,default=6)
    args=parser.parse_args()
    out=args.outdir;out.mkdir(parents=True,exist_ok=True)
    points=point_set();points.to_csv(out/"points.csv",index=False)
    jobs=[]
    for case in CASES:
        for p in points.to_dict("records"):
            jobs.append((case,p,math.inf))
    for radius in RADII[:-1]:
        for p in points.to_dict("records"):
            jobs.append(("five_metre_ellipsoid",p,radius))
    start=time.perf_counter();results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(task,j):j for j in jobs}
        for future in as_completed(futures):
            result=future.result();results.append(result)
            if len(results)%33==0:
                print(f"Completed {len(results)}/{len(jobs)} point/radius cases in {time.perf_counter()-start:.1f}s",flush=True)
    records=pd.DataFrame([v for r in results for v in r["records"]])
    refinements=pd.DataFrame([v for r in results for v in r["refinements"]])
    bests=pd.DataFrame([{k:r[k] for k in ("case","point_id","radius_m","best_nphi","converged")}
                       for r in results])
    records=records.sort_values(["case","point_id","radius_m","nphi","direction"])
    records.to_csv(out/"fields_all_resolutions.csv",index=False)
    final=records.merge(bests,on=["case","point_id","radius_m"])
    final=final[final.nphi==final.best_nphi].copy()
    final.to_csv(out/"fields.csv",index=False)
    refinements.to_csv(out/"quadrature_changes.csv",index=False)
    qfinal=refinements.merge(bests,on=["case","point_id","radius_m"])
    qfinal=qfinal[qfinal.fine_nphi==qfinal.best_nphi]
    qsummary=qfinal.groupby(["case","radius_m","direction"],dropna=False).agg(
        points=("point_id","nunique"),max_normalized_change=("normalized_change","max"),
        max_nphi=("best_nphi","max"),all_converged=("converged","all")).reset_index()
    qsummary.to_csv(out/"quadrature_summary.csv",index=False)
    flat=records[np.isinf(records.radius_m)]
    flat_summary=flat.groupby(["case","nphi","direction"]).agg(
        points=("point_id","nunique"),
        max_abs_normalized_difference=("normalized_difference",lambda x:x.abs().max()),
        rms_normalized_difference=("normalized_difference",lambda x:np.sqrt(np.mean(x*x)))).reset_index()
    flat_summary.to_csv(out/"flat_summary.csv",index=False)
    flat_best=final[np.isinf(final.radius_m)].groupby(["case","direction"]).agg(
        points=("point_id","nunique"),max_nphi=("nphi","max"),
        max_abs_normalized_difference=("normalized_difference",lambda x:x.abs().max()),
        rms_normalized_difference=("normalized_difference",lambda x:np.sqrt(np.mean(x*x)))).reset_index()
    flat_best.to_csv(out/"flat_best_summary.csv",index=False)
    radius_summary=final[final.case=="five_metre_ellipsoid"].groupby(["radius_m","direction"]).agg(
        points=("point_id","nunique"),max_nphi=("nphi","max"),
        max_abs_normalized_difference=("normalized_difference",lambda x:x.abs().max()),
        rms_normalized_difference=("normalized_difference",lambda x:np.sqrt(np.mean(x*x)))).reset_index()
    radius_summary=radius_summary.merge(qsummary[qsummary.case=="five_metre_ellipsoid"]
                                        [["radius_m","direction","max_normalized_change"]],
                                        on=["radius_m","direction"])
    radius_summary.to_csv(out/"radius_summary.csv",index=False)
    endpoint=pd.DataFrame([r["endpoint"] for r in results if r["endpoint"] is not None])
    endpoint.to_csv(out/"endpoint_checks.csv",index=False)
    scalar=scalar_implementation_checks(points)
    scalar.to_csv(out/"scalar_vectorized_checks.csv",index=False)
    # Symmetry checks include zero vertical field on y=0 and zero tangential
    # field at the arc midpoint. A nonzero midpoint radial field is physical.
    joined=final.merge(points,on="point_id")
    symmetry=joined[((joined.direction=="vertical") & (joined.y_over_c==0))
                    | ((joined.direction=="tangential") & (joined.s_over_b==0))].copy()
    symmetry["normalized_field"]=symmetry.sacr_field/symmetry.characteristic_scale
    symmetry[["case","point_id","radius_m","direction","normalized_field"]].to_csv(out/"symmetry_checks.csv",index=False)
    accepted=bool(bests.converged.all() and flat_best.max_abs_normalized_difference.max()<TOLERANCE
                  and endpoint.normalized_difference.abs().max()<TOLERANCE
                  and symmetry.normalized_field.abs().max()<TOLERANCE)
    summary={"model":"semi-analytic curved-tube reference (SACR)",
             "scope":"static uniform-density tapered ellipsoid family; no OPALX comparison or tracking",
             "points_per_geometry":len(points),"geometries":len(CASES),
             "point_radius_cases":len(jobs),"field_component_values":len(final),
             "radii_m":[r if np.isfinite(r) else "infinity" for r in RADII],
             "component_scale":"E_i*=4*pi*D_i*a_i in E/(k*rho) units; a_i=(a,c,b)",
             "quadrature_tolerance_characteristic":TOLERANCE,
             "largest_flat_normalized_error":float(flat_best.max_abs_normalized_difference.max()),
             "largest_last_refinement_normalized_change":float(qfinal.normalized_change.max()),
             "largest_endpoint_normalized_difference":float(endpoint.normalized_difference.abs().max()),
             "largest_symmetry_normalized_field":float(symmetry.normalized_field.abs().max()),
             "largest_scalar_vectorized_normalized_difference":float(scalar.normalized_difference.abs().max()),
             "maximum_angular_nodes":int(final.nphi.max()),"runtime_s":time.perf_counter()-start,
             "passed":accepted}
    (out/"acceptance.json").write_text(json.dumps(summary,indent=2)+"\n")
    provenance={"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "prototype_sha256":hashlib.sha256((ROOT/"validate_dubin_limit.py").read_bytes()).hexdigest(),
                "cases_semiaxes_r_s_y_m":CASES,
                "target_coordinates":"u/a, y/c, s/b; field order radial,vertical,tangential",
                "radius_comparison":"same material target points; local target Frenet field components",
                "normalization":"E/(k*rho), k=1/(4*pi*epsilon0), has units metre",
                "density":"uniform physical volume density; parabolic line density; sameQatallR",
                "vertical_size":"0.5mm is a chosen verification semiaxis, not a confirmed real-beam parameter",
                "quadrature":"periodic phi midpoint rule; adaptive mu quad_vec; 128/256/512 allpoints, furtherdoublingwhenneeded",
                "sampling_scope":"33 selected interior points, maximum scaled radius<0.95; no boundary/exterior guarantee",
                "numpy_version":np.__version__,"pandas_version":pd.__version__}
    (out/"provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    if not accepted:raise SystemExit(2)


if __name__=="__main__":
    main()
