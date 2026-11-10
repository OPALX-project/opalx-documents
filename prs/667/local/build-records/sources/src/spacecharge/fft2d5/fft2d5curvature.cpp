#include "SpaceCharge/FFT2D5/FFT2D5Curvature.h"

#include "Physics/Physics.h"
#include "Utilities/OpalException.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

namespace opalx::spacecharge {
    double FFT2D5Curvature::lineSelfWeight(double ds, double curvature, double referenceLength) {
        if (curvature == 0.0) return 0.0;
        const double a = std::abs(curvature);
        return curvature * std::log(8.0 * std::tan(a * ds / 8.0) / (a * referenceLength));
    }

    double FFT2D5Curvature::lineOffDiagonalWeight(double distance, double ds, double curvature) {
        if (curvature == 0.0) return 0.0;
        const double a  = std::abs(curvature);
        const double lo = a * (distance - 0.5 * ds) / 4.0;
        const double hi = a * (distance + 0.5 * ds) / 4.0;
        return 0.5 * curvature * (std::log(std::tan(hi)) - std::log(std::tan(lo)));
    }

    std::size_t FFT2D5Curvature::solve(
            FFT2D5FieldStorage& fields, double curvature, bool closedRing) {
        if (ippl::Comm->size() != 1) {
            throw OpalException("FFT2D5Curvature::solve", "FFT2D5 supports a single MPI rank.");
        }
        if (!std::isfinite(curvature) || curvature == 0.0) {
            throw OpalException(
                    "FFT2D5Curvature::solve", "A finite nonzero curvature is required.");
        }
        using Policy       = Kokkos::MDRangePolicy<Kokkos::Rank<2>>;
        const auto size    = fields.meshSize();
        const auto spacing = fields.spacing();
        const auto origin  = fields.origin();
        const int nx       = static_cast<int>(size[0]);
        const int ny       = static_cast<int>(size[1]);
        const int nz       = static_cast<int>(size[2]);
        const double dx = spacing[0], dy = spacing[1], ds = spacing[2];
        const double u0 = origin[0];
        if (1.0 + curvature * (u0 - dx) <= 0.0 || 1.0 + curvature * (u0 + (nx + 1) * dx) <= 0.0) {
            throw OpalException(
                    "FFT2D5Curvature::solve",
                    "The circular metric must stay positive across the numerical mesh and halo.");
        }
        const double circumference = 2.0 * Physics::pi / std::abs(curvature);
        if ((closedRing && std::abs(nz * ds - circumference) > 1e-9 * circumference)
            || (!closedRing && nz * ds >= circumference)) {
            throw OpalException(
                    "FFT2D5Curvature::solve",
                    "A closed circular reference must span one turn; an open arc must be shorter.");
        }
        const auto rho3           = fields.chargeDensity().getView();
        double maximumSourceRatio = 0.0;
        const int sourceGhost     = fields.chargeDensity().getNghost();
        Kokkos::parallel_reduce(
                "FFT2D5CurvatureSourceExtent",
                Kokkos::MDRangePolicy<Kokkos::Rank<3>>({0, 0, 0}, {nx, ny, nz}),
                KOKKOS_LAMBDA(int i, int j, int z, double& value) {
                    if (rho3(i + sourceGhost, j + sourceGhost, z + sourceGhost) != 0.0) {
                        const double u = u0 + (i + 0.5) * dx;
                        value          = Kokkos::max(value, Kokkos::abs(curvature * u));
                    }
                },
                Kokkos::Max<double>(maximumSourceRatio));
        // CIC places a valid source on adjacent cell centres up to dx away.
        // Empty numerical padding does not change the physical expansion scale.
        if (maximumSourceRatio > MaxTransverseRatio + std::abs(curvature) * dx
                                         + 64 * std::numeric_limits<double>::epsilon()) {
            throw OpalException(
                    "FFT2D5Curvature::solve",
                    "The occupied source exceeds |curvature*u| <= 0.01 plus its CIC stencil.");
        }
        const auto e3         = fields.electricField().getView();
        const int ng3         = fields.chargeDensity().getNghost();
        const int nge3        = fields.electricField().getNghost();
        const auto& workspace = fields.workspace();
        const auto rho2       = workspace.chargeDensity->getView();
        const auto e2         = workspace.electricField->getView();
        const int ng2         = workspace.chargeDensity->getNghost();
        const int nge2        = workspace.electricField->getNghost();
        Kokkos::View<double**> phi0("FFT2D5CurvatureBasePotential", rho2.extent(0), rho2.extent(1));
        std::vector<double> lambda(nz), occupied(nz), weights(nz), radialLine(nz);
        const double kCoulomb   = 1.0 / (4.0 * Physics::pi * Physics::epsilon_0);
        const double invEpsilon = 1.0 / Physics::epsilon_0;
        // Keep the conserved coordinate density intact; only slice sources
        // are divided by the metric. Neutral slices must still be solved.
        for (int z = 0; z < nz; ++z) {
            double total = 0.0, absolute = 0.0;
            Kokkos::parallel_reduce(
                    "FFT2D5CurvatureLineDensity", Policy({0, 0}, {nx, ny}),
                    KOKKOS_LAMBDA(int i, int j, double& value) {
                        const double u = u0 + (i + 0.5) * dx;
                        value += rho3(i + ng3, j + ng3, z + ng3) / (1.0 + curvature * u);
                    },
                    total);
            Kokkos::parallel_reduce(
                    "FFT2D5CurvatureOccupancy", Policy({0, 0}, {nx, ny}),
                    KOKKOS_LAMBDA(int i, int j, double& value) {
                        value += Kokkos::abs(rho3(i + ng3, j + ng3, z + ng3));
                    },
                    absolute);
            lambda[z]   = total * dx * dy;
            occupied[z] = absolute;
        }
        weights[0] = lineSelfWeight(ds, curvature);
        for (int offset = 1; offset < nz; ++offset) {
            const int d     = closedRing ? std::min(offset, nz - offset) : offset;
            weights[offset] = lineOffDiagonalWeight(d * ds, ds, curvature);
        }
        for (int z = 0; z < nz; ++z) {
            double value = 0.0;
            for (int source = 0; source < nz; ++source) {
                value += weights[std::abs(source - z)] * lambda[source];
            }
            radialLine[z] = kCoulomb * value;
        }
        fields.resetBackendSolves();
        Kokkos::deep_copy(e3, FFT2D5FieldStorage::Vector3(0.0));
        for (int z = 0; z < nz; ++z) {
            if (occupied[z] == 0.0) {
                const double line = radialLine[z];
                Kokkos::parallel_for(
                        "FFT2D5CurvatureVacuumField", Policy({0, 0}, {nx, ny}),
                        KOKKOS_LAMBDA(int i, int j) {
                            e3(i + nge3, j + nge3, z + nge3) =
                                    FFT2D5FieldStorage::Vector3(line, 0.0, 0.0);
                        });
                continue;
            }
            Kokkos::parallel_for(
                    "FFT2D5CurvaturePhysicalSource",
                    Policy({0, 0}, {rho2.extent(0), rho2.extent(1)}), KOKKOS_LAMBDA(int i, int j) {
                        const double u = u0 + (i - ng2 + 0.5) * dx;
                        rho2(i, j)     = invEpsilon * rho3(i - ng2 + ng3, j - ng2 + ng3, z + ng3)
                                     / (1.0 + curvature * u);
                    });
            fields.solveSlice();
            Kokkos::deep_copy(phi0, rho2);
            Kokkos::parallel_for(
                    "FFT2D5CurvatureMomentSource", Policy({0, 0}, {rho2.extent(0), rho2.extent(1)}),
                    KOKKOS_LAMBDA(int i, int j) {
                        const double u = u0 + (i - ng2 + 0.5) * dx;
                        rho2(i, j) = invEpsilon * u * rho3(i - ng2 + ng3, j - ng2 + ng3, z + ng3)
                                     / (1.0 + curvature * u);
                    });
            fields.solveSlice();
            const double line  = radialLine[z];
            const double local = kCoulomb * lambda[z];
            Kokkos::parallel_for(
                    "FFT2D5CurvaturePotential", Policy({0, 0}, {rho2.extent(0), rho2.extent(1)}),
                    KOKKOS_LAMBDA(int i, int j) {
                        const double u    = u0 + (i - ng2 + 0.5) * dx;
                        const double base = phi0(i, j);
                        rho2(i, j)        = base + 0.5 * curvature * (rho2(i, j) - u * base)
                                     + curvature * local * u - u * line;
                    });
            // Differentiate one corrected scalar potential, including its
            // convolved halo. This preserves the transverse curl identity.
            Kokkos::parallel_for(
                    "FFT2D5CurvatureGradient", Policy({0, 0}, {nx, ny}),
                    KOKKOS_LAMBDA(int i, int j) {
                        const double eu = -(rho2(i + ng2 + 1, j + ng2) - rho2(i + ng2 - 1, j + ng2))
                                          / (2.0 * dx);
                        const double ey = -(rho2(i + ng2, j + ng2 + 1) - rho2(i + ng2, j + ng2 - 1))
                                          / (2.0 * dy);
                        e2(i + nge2, j + nge2)           = FFT2D5FieldStorage::Vector2(eu, ey);
                        e3(i + nge3, j + nge3, z + nge3) = FFT2D5FieldStorage::Vector3(eu, ey, 0.0);
                    });
        }
        Kokkos::parallel_for(
                "FFT2D5CurvatureLongitudinalGhosts", Policy({0, 0}, {e3.extent(0), e3.extent(1)}),
                KOKKOS_LAMBDA(int i, int j) {
                    if (closedRing) {
                        e3(i, j, 0)      = e3(i, j, nz);
                        e3(i, j, nz + 1) = e3(i, j, 1);
                    }
                });
        Kokkos::fence();
        return fields.backendSolves();
    }
}  // namespace opalx::spacecharge
