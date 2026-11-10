#!/usr/bin/env python3
"""Generate the deterministic frozen longitudinal-physics regression fixture.

Only the standard library is required. No OPALX output enters the source or
analytic reference. The sparse transverse quadrature is sufficient here
because this test checks the prescribed longitudinal uniform-round closure;
transverse mesh accuracy is covered by other tests.
"""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent
NAME = "FFT2D5-TriangularPipe"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ns, nr, nphi = 8192, 2, 4
    nsource = ns * nr * nphi
    cfg = dict(name=NAME, full_length_m=10.0, beam_radius_m=.005,
               pipe_radius_m=.020, numerical_width_m=.060,
               kinetic_energy_GeV=.4, proton_mass_GeV=.93827208816,
               elementary_charge_C=1.602176634e-19,
               epsilon0_F_per_m=8.8541878128e-12, real_protons=1.e14,
               dt_s=1.e-20, ns=ns, nrad=nr, nphi=nphi,
               source_particles=nsource, mesh=[32, 32, 64],
               relative_field_tolerance=.01, wall_absolute_tolerance_V_per_m=1.e-4,
               source_file="triangle.dist", reference_path_file="reference_path.dat")
    cfg["gamma"] = 1. + cfg["kinetic_energy_GeV"] / cfg["proton_mass_GeV"]
    bg = math.sqrt(cfg["gamma"]**2 - 1.)
    cfg["beta"] = bg / cfg["gamma"]
    cfg["source_charge_C"] = cfg["real_protons"] * cfg["elementary_charge_C"]
    radii = [0., cfg["beam_radius_m"] / 2., cfg["beam_radius_m"],
             (cfg["beam_radius_m"] + cfg["pipe_radius_m"]) / 2., cfg["pipe_radius_m"]]
    probes = [dict(probe_id=i * len(radii) + j, x_m=r, y_m=0., s_m=s)
              for i, s in enumerate([-2.5, 2.5]) for j, r in enumerate(radii)]
    cfg["probe_particles"] = len(probes)
    cfg["expected_particles"] = nsource + len(probes)
    cfg["macrocharge_C"] = cfg["source_charge_C"] / nsource
    cfg["assigned_charge_C"] = cfg["macrocharge_C"] * cfg["expected_particles"]
    cfg["beta_gamma"] = bg
    with (ROOT / "probes.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(probes[0]))
        writer.writeheader()
        writer.writerows(probes)
    cross = []
    for ir in range(nr):
        r = cfg["beam_radius_m"] * math.sqrt((ir + .5) / nr)
        for iphi in range(nphi):
            phi = 2. * math.pi * (iphi + .5) / nphi
            cross.append((r * math.cos(phi), r * math.sin(phi)))
    with (ROOT / cfg["source_file"]).open("w") as stream:
        stream.write(f"{cfg['expected_particles']}\nx px y py z pz\n")
        for iz in range(ns):
            u = (iz + .5) / ns
            s = (-5. + 5. * math.sqrt(2. * u) if u < .5
                 else 5. - 5. * math.sqrt(2. * (1. - u)))
            for x, y in cross:
                stream.write(f"{x:.17e} 0 {y:.17e} 0 {s:.17e} {bg:.17e}\n")
        for p in probes:
            stream.write(f"{p['x_m']:.17e} 0 {p['y_m']:.17e} 0 {p['s_m']:.17e} {bg:.17e}\n")
    with (ROOT / cfg["reference_path_file"]).open("w") as stream:
        stream.write("# s rx ry rz px py pz ex ey ez bx by bz ke time\n")
        for arc, z in [(0., -6.), (12., 6.)]:
            stream.write(" ".join(f"{v:.17e}" for v in [arc, 0., 0., z, 0., 0., cfg["beta"], *([0.] * 8)]) + "\n")
    inp = f'''// Frozen, nonzero longitudinal field in a prescribed round beam and grounded pipe.
OPTION, VERSION=10900;
OPTION, PSDUMPFREQ=1;
OPTION, STATDUMPFREQ=1;
OPTION, EBDUMP=TRUE;
OPTION, MINBINEMITTED=0;
DIST1: DISTRIBUTION,TYPE=FROMFILE,NPARTDIST={cfg['expected_particles']},FNAME="triangle.dist";
E1: EMISSIONSOURCE,DISTRIBUTION=DIST1,R0X=0,R0Y=0,R0Z=0,P0X=0,P0Y=0,P0Z=0,T0=0,ZEROFACE_R0Z=FALSE,SHIFTED_GREENS_FUNCTION=FALSE,ZEROFACEPLANEDUMP=0,ZEROFACE_MAXSTEPS=0,EMISSIONMODEL=NONE,EKIN=0;
ELIST1: EMISSIONSOURCELIST=(E1);
FS: FIELDSOLVER,TYPE="FFT2D5",NX=32,NY=32,NZ=64,PARFFTX=FALSE,PARFFTY=FALSE,PARFFTZ=FALSE,PIPEMODE="CIRCULAR_UNIFORM",PIPERADIUS=0.020,BEAMR=0.005,PIPESIZEX=0.060,PIPESIZEY=0.060,CLOSEDRING=FALSE,SCATTERLONGITUDINALLY=TRUE,REFPATHFNAME="reference_path.dat";
B1: BEAM,PARTICLE=PROTON,NALLOC={cfg['expected_particles']},BCHARGE={cfg['assigned_charge_C']:.17g},SOURCES="ELIST1";
D1: DRIFT,L=1,ELEMEDGE=1000;
L1: LINE=(D1);
TRACK,BEAM=B1,LINE=L1,MAXSTEPS=1,ZSTOP={{100}},DT={{{cfg['dt_s']:.17g}}};
RUN,FIELDSOLVER=FS,METHOD="PARALLEL",TURNS=1;
ENDTRACK;
'''
    (ROOT / f"{NAME}.in").write_text(inp)
    (ROOT / "physics_config.json").write_text(json.dumps(cfg, indent=2) + "\n")
    names = [cfg["source_file"], cfg["reference_path_file"], f"{NAME}.in", "probes.csv", "physics_config.json", "prepare.py", "validate.py"]
    provenance = dict(source_description="Equal-charge inverse-CDF triangular quantiles times equal-area disk midpoint quadrature", fixtures={name: digest(ROOT / name) for name in names})
    (ROOT / "analytic_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(f"Generated {nsource} source particles and {len(probes)} probes.")


if __name__ == "__main__":
    main()
