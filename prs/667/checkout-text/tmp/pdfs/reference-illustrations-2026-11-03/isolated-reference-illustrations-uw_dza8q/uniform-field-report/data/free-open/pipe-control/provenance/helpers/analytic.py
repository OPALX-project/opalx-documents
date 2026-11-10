#!/usr/bin/env python3
"""Independent local conducting-pipe reference for a triangular bunch.

The source has constant circular radius and longitudinally varying density.
This is the long-beam round-pipe benchmark, not the parabolic/ellipsoid
equivalent-field convention used for OPALX's CircularPipeG0=0.67.

All coordinates and fields use SI. PyORBIT dE is GeV; its equivalent frozen
field is dE*1e9/(charge_state*kick_length), in V/m. No fitted coefficients.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

# Exact constants used by the inspected OPALX build (Physics/Physics.h).
EPSILON_0 = 8.8541878128e-12
ELEMENTARY_CHARGE = 1.602176634e-19
PROTON_MASS_GEV = 0.93827208816
COULOMB_K = 1.0 / (4.0 * np.pi * EPSILON_0)


@dataclass(frozen=True)
class Benchmark:
    length_m: float = 10.0
    beam_radius_m: float = 0.005
    pipe_radius_m: float = 0.020
    real_protons: float = 1.0e14
    kinetic_energy_GeV: float = 0.400
    rest_energy_GeV: float = PROTON_MASS_GEV
    kick_length_m: float = 1.0

    @property
    def charge_C(self):
        return self.real_protons * ELEMENTARY_CHARGE

    @property
    def gamma(self):
        return 1.0 + self.kinetic_energy_GeV / self.rest_energy_GeV

    @property
    def beta(self):
        return np.sqrt(1.0 - self.gamma ** -2)

    @property
    def lambda_peak(self):
        return 2.0 * self.charge_C / self.length_m

    @property
    def abs_lambda_prime(self):
        return 4.0 * self.charge_C / self.length_m ** 2

    @property
    def longitudinal_base(self):
        return COULOMB_K * self.abs_lambda_prime / self.gamma ** 2

    def line_density(self, s):
        """Triangle lambda(s), centered at zero, total integral Q."""
        return self.lambda_peak * np.maximum(0.0, 1.0 - 2.0 * np.abs(s) / self.length_m)

    def line_density_prime(self, s):
        """Piecewise slope; NaN at the cusp and exact support endpoints.

        A physical nonlocal field is continuous at these points; the local
        model is not an appropriate pointwise reference there. They are
        deliberately not assigned an invented analytic value.
        """
        s = np.asarray(s, dtype=float)
        half = 0.5 * self.length_m
        value = np.where(np.abs(s) < half, -self.abs_lambda_prime * np.sign(s), 0.0)
        return np.where((s == 0.0) | (np.abs(s) == half), np.nan, value)

    def geometry_factor(self, radius):
        """Round uniform disk factor, including its vacuum annulus."""
        radius = np.asarray(radius, dtype=float)
        if np.any(radius < 0.0) or np.any(radius > self.pipe_radius_m):
            raise ValueError("Targets must lie inside the conducting pipe")
        a = self.beam_radius_m
        b = self.pipe_radius_m
        inside = 1.0 + 2.0 * np.log(b / a) - (radius / a) ** 2
        outside = 2.0 * np.log(b / np.maximum(radius, a))
        return np.where(radius <= a, inside, outside)

    @property
    def g_axis(self):
        return float(self.geometry_factor(0.0))

    @property
    def g_mean(self):
        """Charge-weighted uniform-disk mean; <r^2>=a^2/2."""
        return 0.5 + 2.0 * np.log(self.pipe_radius_m / self.beam_radius_m)

    def longitudinal_field(self, s, radius=0.0):
        return -COULOMB_K * self.line_density_prime(s) * self.geometry_factor(radius) / self.gamma ** 2

    def mean_longitudinal_field(self, s):
        return -COULOMB_K * self.line_density_prime(s) * self.g_mean / self.gamma ** 2

    def radial_field(self, s, radius):
        """Lab electric field; transverse Lorentz force/q is E_r/gamma^2."""
        radius = np.asarray(radius, dtype=float)
        if np.any(radius < 0.0) or np.any(radius > self.pipe_radius_m):
            raise ValueError("Targets must lie inside the conducting pipe")
        a = self.beam_radius_m
        interior = radius / a ** 2
        exterior = 1.0 / np.maximum(radius, a)
        return self.line_density(s) / (2.0 * np.pi * EPSILON_0) * np.where(radius <= a, interior, exterior)

    def opal_native_g(self, full_width_x=None, full_width_y=None, beam_radius=None):
        """As implemented: uses full mesh width as 'pipeRadius'.

        Defaults match the primary benchmark: W=b in the longitudinal formula,
        while the OPEN transverse numerical grid spans +/-W/2. There is no
        actual transverse wall in this OPALX solver. Passing W=2b reproduces
        the wider numerical-domain control. Both widths must be labelled;
        this records behavior without correcting or fitting.
        """
        wx = self.pipe_radius_m if full_width_x is None else full_width_x
        wy = self.pipe_radius_m if full_width_y is None else full_width_y
        a = self.beam_radius_m if beam_radius is None else beam_radius
        return 0.67 + 2.0 * np.log(min(wx, wy) / a)

    def opal_native_longitudinal_field(self, s, **kwargs):
        return -COULOMB_K * self.line_density_prime(s) * self.opal_native_g(**kwargs) / self.gamma ** 2

    def equivalent_kick_eV(self, field_V_per_m, charge_state=1.0):
        return np.asarray(field_V_per_m) * self.kick_length_m * charge_state

    def field_from_pyorbit_dE_GeV(self, energy_kick_GeV, charge_state=1.0):
        return np.asarray(energy_kick_GeV) * 1.0e9 / (charge_state * self.kick_length_m)

    def acceptance_mask(self, s, guard_m=1.0, coordinate_atol_m=1.0e-12):
        """Fixed physical window, independent of fitted errors or mesh.

        The picometre comparison tolerance includes the intended exact1m/4m
        target IDs despite decimal/binary CSV representation. It changes no
        physical accuracy threshold or mesh-dependent exclusion distance.
        """
        s = np.asarray(s, dtype=float)
        return ((np.abs(s) >= guard_m-coordinate_atol_m)
                & (np.abs(s) <= 0.5*self.length_m-guard_m+coordinate_atol_m))

    def metadata(self):
        out = asdict(self)
        out.update(
            charge_C=self.charge_C,
            gamma=float(self.gamma),
            beta=float(self.beta),
            lambda_peak_C_per_m=self.lambda_peak,
            abs_lambda_prime_C_per_m2=self.abs_lambda_prime,
            longitudinal_base_V_per_m=self.longitudinal_base,
            g_axis=self.g_axis,
            g_disk_average=float(self.g_mean),
            g_edge=float(self.geometry_factor(self.beam_radius_m)),
            g_opal_native=float(self.opal_native_g()),
            g_opal_native_full_width=float(self.opal_native_g(2*self.pipe_radius_m, 2*self.pipe_radius_m)),
            g_opal_native_effective_radius=float(self.opal_native_g(self.pipe_radius_m, self.pipe_radius_m)),
            abs_Es_axis_V_per_m=self.longitudinal_base * self.g_axis,
            abs_Es_disk_average_V_per_m=self.longitudinal_base * self.g_mean,
            abs_Es_edge_V_per_m=self.longitudinal_base * self.geometry_factor(self.beam_radius_m),
            abs_Es_opal_native_V_per_m=self.longitudinal_base * self.opal_native_g(),
            abs_Es_opal_native_full_width_V_per_m=self.longitudinal_base * self.opal_native_g(2*self.pipe_radius_m, 2*self.pipe_radius_m),
            abs_Es_opal_native_effective_radius_V_per_m=self.longitudinal_base * self.opal_native_g(self.pipe_radius_m, self.pipe_radius_m),
            native_relative_axis_error_percent=100.0 * (self.opal_native_g() / self.g_axis - 1.0),
            native_relative_disk_average_error_percent=100.0 * (self.opal_native_g() / self.g_mean - 1.0),
            radius_fixed_g0_only_axis_error_percent=100.0 * ((0.67 + 2.0*np.log(self.pipe_radius_m/self.beam_radius_m)) / self.g_axis - 1.0),
            acceptance_window_abs_s_m=[1.0, 4.0],
            acceptance_coordinate_atol_m=1.0e-12,
        )
        return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    case = Benchmark()
    (args.output / "analytic-reference.json").write_text(json.dumps(case.metadata(), indent=2) + "\n")
    s = np.linspace(-0.5*case.length_m, 0.5*case.length_m, 401)
    rows = []
    for radius in [0.0, 0.5*case.beam_radius_m, case.beam_radius_m]:
        rows.append(pd.DataFrame({
            "s_m": s, "radius_m": radius,
            "lambda_C_per_m": case.line_density(s),
            "lambda_prime_C_per_m2": case.line_density_prime(s),
            "analytic_Es_V_per_m": case.longitudinal_field(s, radius),
            "analytic_Er_V_per_m": case.radial_field(s, radius),
            "analytic_disk_mean_Es_V_per_m": case.mean_longitudinal_field(s),
            "opal_native_Es_V_per_m": case.opal_native_longitudinal_field(s),
            "acceptance": case.acceptance_mask(s),
        }))
    pd.concat(rows, ignore_index=True).to_csv(args.output / "analytic-reference.csv", index=False)
    print(json.dumps(case.metadata(), indent=2))


if __name__ == "__main__":
    main()
