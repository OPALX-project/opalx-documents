#!/usr/bin/env python3
"""Native PyORBIT3 frozen triangular-bunch pipe kick, with zero-weight probes.

No solver formula is reimplemented for the numerical result: native trackBunch
sets the particle kicks. Inputs are immutable NPZ source and CSV probes.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from orbit.core import orbit_mpi
from orbit.core.bunch import Bunch
from orbit.core.spacecharge import (
    Boundary2D, SpaceChargeCalcSliceBySlice2D, SpaceChargeCalc2p5Drb,
)

HERE = Path(__file__).resolve().parent
E_CHARGE = 1.602176634e-19
EPS0 = 8.8541878128e-12
REVISION = "28df66018aebe4e2b780b9747f4a2d7b8430a5c0"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--probes", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--model", choices=["slice", "rb"], default="slice")
    p.add_argument("--nx", type=int, default=64)
    p.add_argument("--ny", type=int)
    p.add_argument("--nz", type=int, default=64)
    p.add_argument("--boundary-points", type=int, default=128)
    p.add_argument("--boundary-modes", type=int, default=32)
    p.add_argument("--beam-radius", type=float, default=.005)
    p.add_argument("--pipe-radius", type=float, default=.020)
    p.add_argument("--full-length", type=float, default=10.)
    p.add_argument("--kinetic-energy-gev", type=float, default=.4)
    p.add_argument("--n-real", type=float, default=1.e14)
    p.add_argument("--kick-length", type=float, default=1.)
    a = p.parse_args()
    a.ny = a.ny or a.nx
    comm = orbit_mpi.mpi_comm.MPI_COMM_WORLD
    rank = orbit_mpi.MPI_Comm_rank(comm)
    size = orbit_mpi.MPI_Comm_size(comm)
    a.out.mkdir(parents=True, exist_ok=True)
    rank_csv = a.out / f"probes-rank{rank}.csv"
    if rank_csv.exists():
        raise FileExistsError(rank_csv)
    start = time.monotonic()
    inp = np.load(a.source)
    if "s_nodes_m" in inp and "cross_xy_m" in inp:
        ss = inp["s_nodes_m"]
        xy = inp["cross_xy_m"]
        positions = np.column_stack((np.tile(xy[:,0],len(ss)),
                                     np.tile(xy[:,1],len(ss)),
                                     np.repeat(ss,len(xy))))
    elif "positions_m" in inp:
        positions = inp["positions_m"]
    elif "positions" in inp:
        positions = inp["positions"]
    else:
        positions = np.column_stack([inp[k] for k in ["x", "y", "s"]])
    if "weights_number" in inp:
        weights = inp["weights_number"]
    elif "weight" in inp:
        weights = inp["weight"]
    else:
        weights = np.full(len(positions), a.n_real / len(positions))
    assert positions.ndim == 2 and positions.shape[1] == 3
    assert weights.shape == (len(positions),)
    assert np.isfinite(positions).all() and np.isfinite(weights).all()
    assert np.all(weights >= 0)
    assert math.isclose(float(weights.sum()), a.n_real, rel_tol=5e-12)
    assert np.max(np.linalg.norm(positions[:, :2], axis=1)) <= a.beam_radius*(1+1e-12)
    assert np.max(abs(positions[:, 2])) <= a.full_length/2*(1+1e-12)
    with a.probes.open(newline="") as f:
        probes = list(csv.DictReader(f))
    b = Bunch()
    b.addPartAttr("macrosize")
    b.macroSize(0.)
    b.getSyncParticle().kinEnergy(a.kinetic_energy_gev)
    for i in range(rank, len(positions), size):
        x, y, s = positions[i]
        j = b.addParticle(float(x), 0., float(y), 0., float(s), 0.)
        # addParticle returns None; the new local particle is last in bunch.
        b.partAttrValue("macrosize", b.getSize()-1, 0, float(weights[i]))
    local_sources = b.getSize()
    probe_indices = []
    for i in range(rank, len(probes), size):
        row = probes[i]
        x = float(row.get("x_m", row.get("r_m", 0.)))
        y = float(row.get("y_m", 0.))
        s = float(row.get("s_m", row.get("z_m")))
        b.addParticle(x, 0., y, 0., s, 0.)
        j = b.getSize()-1
        b.partAttrValue("macrosize", j, 0, 0.)
        probe_indices.append((i, j, x, y, s))
    # Zero-charge markers enforce the same physical source extent for all grids.
    guards = [(-a.beam_radius,0.,0.), (a.beam_radius,0.,0.),
              (0.,-a.beam_radius,0.), (0.,a.beam_radius,0.),
              (0.,0.,-a.full_length/2), (0.,0.,a.full_length/2)]
    for i in range(rank, len(guards), size):
        x,y,s = guards[i]
        b.addParticle(x,0.,y,0.,s,0.)
        b.partAttrValue("macrosize",b.getSize()-1,0,0.)
    gamma, beta = b.getSyncParticle().gamma(), b.getSyncParticle().beta()
    pre = np.array([[b.x(j), b.y(j), b.z(j)] for _,j,_,_,_ in probe_indices])
    if a.model == "slice":
        solver = SpaceChargeCalcSliceBySlice2D(a.nx, a.ny, a.nz)
        solver.longTracking(1)
        boundary = Boundary2D(a.boundary_points, a.boundary_modes,
                              "Circle", 2*a.pipe_radius, 2*a.pipe_radius)
        solver.trackBunch(b, a.kick_length, boundary)
        assert solver.longTracking() == 1
    else:
        solver = SpaceChargeCalc2p5Drb(a.nx, a.ny, a.nz)
        solver.setLongAveragingPointsN(3)
        solver.trackBunch(b, a.kick_length, a.pipe_radius)
    post = np.array([[b.x(j), b.y(j), b.z(j)] for _,j,_,_,_ in probe_indices])
    assert np.array_equal(pre, post), "Native direct kick unexpectedly moved probes"
    rows = []
    h = a.full_length/2
    scale = a.n_real*E_CHARGE/(h*h*4*math.pi*EPS0*gamma**2)
    native_scale = a.n_real/(h*h)*b.classicalRadius()*b.mass()*1e9/gamma**2
    for i,j,x,y,s in probe_indices:
        r = math.hypot(x,y)
        if r <= a.beam_radius:
            g = 1+2*math.log(a.pipe_radius/a.beam_radius)-(r/a.beam_radius)**2
        else:
            g = 2*math.log(a.pipe_radius/r)
        es = b.dE(j)*1e9/a.kick_length
        ex = b.xp(j)*b.mass()*1e9*beta**2*gamma**3/a.kick_length
        ey = b.yp(j)*b.mass()*1e9*beta**2*gamma**3/a.kick_length
        sign = float(np.sign(s)) if abs(s) < h else 0.
        rows.append(dict(probe_id=probes[i].get("probe_id",probes[i].get("point_id",probes[i].get("id",i))),
            x_m=x,y_m=y,s_m=s,r_m=r,g=g,
            Es_V_m=es,Ex_V_m=ex,Ey_V_m=ey,dE_GeV=b.dE(j),
            Es_analytic_SI_V_m=sign*scale*g,
            Es_analytic_native_constants_V_m=sign*native_scale*g))
    if rows:
        with rank_csv.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    else:
        rank_csv.write_text("probe_id,x_m,y_m,s_m,r_m,g,Es_V_m,Ex_V_m,Ey_V_m,dE_GeV,Es_analytic_SI_V_m,Es_analytic_native_constants_V_m\n")
    meta = dict(model=a.model,nx=a.nx,ny=a.ny,nz=a.nz,rank=rank,mpi_size=size,
        source_particles_global=len(positions),source_particles_local=local_sources,
        source_number=float(weights.sum()),source_charge_C=float(weights.sum())*E_CHARGE,
        probe_count_local=len(rows),zero_probe_weights=True,
        beta=beta,gamma=gamma,mass_GeV=b.mass(),classical_radius_m=b.classicalRadius(),
        full_length_m=a.full_length,beam_radius_m=a.beam_radius,pipe_radius_m=a.pipe_radius,
        kinetic_energy_GeV=a.kinetic_energy_gev,kick_length_m=a.kick_length,
        boundary_points=a.boundary_points,boundary_modes=a.boundary_modes,
        source_sha256=sha256(a.source),probe_input_sha256=sha256(a.probes),
        harness_sha256=sha256(__file__),pyorbit_revision=REVISION,
        probe_positions_unchanged=True,elapsed_seconds=time.monotonic()-start,
        python=sys.executable,argv=sys.argv)
    (a.out/f"manifest-rank{rank}.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps(dict(rank=rank,model=a.model,probes=len(rows),seconds=meta["elapsed_seconds"])),flush=True)


if __name__ == "__main__":
    main()
