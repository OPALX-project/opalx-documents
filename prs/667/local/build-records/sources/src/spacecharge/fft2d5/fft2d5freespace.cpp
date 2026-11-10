// Copyright (c) 2026, Paul Scherrer Institut, Villigen PSI, Switzerland
// SPDX-License-Identifier: GPL-3.0-or-later
#include "SpaceCharge/FFT2D5/FFT2D5FreeSpace.h"
#include "SpaceCharge/FFT2D5/FFT2D5FreeSpaceKernel.h"

#include "Physics/Physics.h"
#include "Utilities/OpalException.h"

#include <algorithm>
#include <cmath>

namespace opalx::spacecharge {
namespace {
    using Policy = Kokkos::MDRangePolicy<Kokkos::Rank<3>>;

    // A two-cell target halo needs displacement N+1.  Ordinary 2N padding
    // aliases that displacement.  Keep the larger FFT economical by choosing
    // its next even 2/3/5-smooth length.
    std::size_t paddedLength(std::size_t physical) {
        std::size_t candidate = 2 * physical + 4;
        for (;; candidate += 2) {
            std::size_t factors = candidate;
            for (const std::size_t prime : {2u, 3u, 5u}) {
                while (factors % prime == 0) {
                    factors /= prime;
                }
            }
            if (factors == 1) {
                return candidate;
            }
        }
    }
}

FFT2D5FreeSpace::FFT2D5FreeSpace() {
    parameters_m.add("use_heffte_defaults", false);
    parameters_m.add("use_pencils", true);
    parameters_m.add("use_gpu_aware", true);
    parameters_m.add("comm", ippl::a2av);
    parameters_m.add("r2c_direction", 0);
    parameters_m.add("use_reorder", true);
}

FFT2D5FreeSpace::~FFT2D5FreeSpace() = default;

void FFT2D5FreeSpace::initialise(const ScalarField3& rho) {
    const auto mesh = rho.get_mesh();
    const auto spacing = mesh.getMeshSpacing();
    const auto origin = mesh.getOrigin();
    std::array<std::size_t, 3> size;
    bool changed = !fft_m;
    for (unsigned d = 0; d < 3; ++d) {
        size[d] = static_cast<std::size_t>(mesh.getGridsize(d));
        if (size[d] < 2 || !(spacing[d] > 0.0)) {
            throw OpalException("FFT2D5FreeSpace::initialise", "Invalid FFT2D5 source mesh.");
        }
        changed = changed || size[d] != size_m[d] || spacing[d] != spacing_m[d];
    }
    origin_m = origin;
    if (!changed) {
        return;
    }
    // Release the previous FFT plan before replacing its layouts and arrays.
    fft_m.reset();
    size_m = size;
    spacing_m = spacing;
    for (unsigned d = 0; d < 3; ++d) {
        paddedSize_m[d] = paddedLength(size[d]);
        realDomain_m[d] = ippl::Index(static_cast<int>(paddedSize_m[d]));
        complexDomain_m[d] = ippl::Index(static_cast<int>(
                d == 0 ? paddedSize_m[d] / 2 + 1 : paddedSize_m[d]));
    }
    realMesh_m.initialize(realDomain_m, spacing_m, Vector3(0.0));
    complexMesh_m.initialize(complexDomain_m, spacing_m, Vector3(0.0));
    realLayout_m.initialize(realDomain_m, {false, false, false});
    complexLayout_m.initialize(complexDomain_m, {false, false, false});
    real_m.initialize(realMesh_m, realLayout_m, 0);
    rhoSpectrum_m.initialize(complexMesh_m, complexLayout_m, 0);
    workSpectrum_m.initialize(complexMesh_m, complexLayout_m, 0);
    potential_m = PotentialView("FFT2D5FreeSpacePotential", size[0] + 4, size[1] + 4, size[2] + 4);
    fft_m = std::make_unique<FFT>(realLayout_m, complexLayout_m, parameters_m);
}

std::size_t FFT2D5FreeSpace::solve(
        ScalarField3& rho, VectorField3& electricField, double curvature, double gamma) {
    if (ippl::Comm->size() != 1) {
        throw OpalException("FFT2D5FreeSpace::solve", "FFT2D5 supports a single MPI rank.");
    }
    if (!std::isfinite(curvature) || !std::isfinite(gamma) || gamma < 1.0
        || (curvature != 0.0 && gamma != 1.0)) {
        throw OpalException(
                "FFT2D5FreeSpace::solve",
                "A finite curvature and gamma >= 1 are required; curved electrostatics uses gamma=1.");
    }
    const auto rhoView = rho.getView();
    const int ng = rho.getNghost();
    const auto mesh = rho.get_mesh();
    const int nx = static_cast<int>(mesh.getGridsize(0));
    const int ny = static_cast<int>(mesh.getGridsize(1));
    const int nz = static_cast<int>(mesh.getGridsize(2));
    double maxDensity = 0.0;
    Kokkos::parallel_reduce(
            "FFT2D5FreeSpaceNonempty", Policy({0, 0, 0}, {nx, ny, nz}),
            KOKKOS_LAMBDA(int i, int j, int k, double& maximum) {
                const double value = Kokkos::abs(rhoView(i + ng, j + ng, k + ng));
                if (value > maximum) {
                    maximum = value;
                }
            }, Kokkos::Max<double>(maxDensity));
    if (maxDensity == 0.0) {
        Kokkos::deep_copy(electricField.getView(), Vector3(0.0));
        return 0;
    }
    initialise(rho);
    const double u0 = origin_m[0] - 1.5 * spacing_m[0];
    const double u1 = origin_m[0] + (size_m[0] + 1.5) * spacing_m[0];
    if (1.0 + curvature * u0 <= 0.0 || 1.0 + curvature * u1 <= 0.0) {
        throw OpalException("FFT2D5FreeSpace::solve", "The circular Frenet metric must be positive.");
    }
    if (std::abs(curvature) * std::max(std::abs(u0), std::abs(u1)) > 0.01) {
        throw OpalException(
                "FFT2D5FreeSpace::solve",
                "The first-order curved free-space operator requires |curvature*u| <= 0.01 "
                "throughout the mesh and its two-cell halo; reduce the transverse mesh width.");
    }
    const auto real = real_m.getView();
    Kokkos::deep_copy(real, 0.0);
    Kokkos::parallel_for(
            "FFT2D5FreeSpacePlaceDensity", Policy({0, 0, 0}, {nx, ny, nz}),
            KOKKOS_LAMBDA(int i, int j, int k) { real(i, j, k) = rhoView(i + ng, j + ng, k + ng); });
    fft_m->transform(ippl::FORWARD, real_m, rhoSpectrum_m);
    Kokkos::deep_copy(potential_m, 0.0);
    convolve(fft2d5_free::CellKernel::G, curvature, gamma);
    if (curvature != 0.0) {
        convolve(fft2d5_free::CellKernel::H, curvature, 1.0);
        convolve(fft2d5_free::CellKernel::F, curvature, 1.0);
    }
    determineField(electricField, curvature, gamma);
    return 1;
}

void FFT2D5FreeSpace::convolve(int kind, double curvature, double gamma) {
    const auto real = real_m.getView();
    const auto h = spacing_m;
    const int px = static_cast<int>(paddedSize_m[0]);
    const int py = static_cast<int>(paddedSize_m[1]);
    const int pz = static_cast<int>(paddedSize_m[2]);
    Kokkos::parallel_for(
            "FFT2D5FreeSpaceKernel", Policy({0, 0, 0}, {px, py, pz}),
            KOKKOS_LAMBDA(int i, int j, int k) {
                const int ix = i <= px / 2 ? i : px - i;
                const int iy = j <= py / 2 ? j : py - j;
                const int iz = k <= pz / 2 ? k : pz - k;
                double value = fft2d5_free::CellKernel::average(
                        kind, ix * h[0], iy * h[1], iz * h[2], h[0], h[1], h[2], curvature, gamma);
                // Enforce exact even G/H and odd F parity.  The Nyquist plane
                // is unused by physical/halo source-target displacements.
                if (kind == fft2d5_free::CellKernel::F) {
                    value = i == px / 2 ? 0.0 : (i > px / 2 ? -value : value);
                }
                real(i, j, k) = value;
            });
    fft_m->transform(ippl::FORWARD, real_m, workSpectrum_m);
    const auto rhoSpectrum = rhoSpectrum_m.getView();
    const auto work = workSpectrum_m.getView();
    // heFFTe normalizes each forward transform by the full transform size.
    // Its inverse is unnormalized, hence this compensating size factor.
    const double scaling = static_cast<double>(paddedSize_m[0])
                           * static_cast<double>(paddedSize_m[1])
                           * static_cast<double>(paddedSize_m[2])
                           * h[0] * h[1] * h[2] / (4.0 * Physics::pi * Physics::epsilon_0);
    Kokkos::parallel_for(
            "FFT2D5FreeSpaceProduct", Policy({0, 0, 0}, {px / 2 + 1, py, pz}),
            KOKKOS_LAMBDA(int i, int j, int k) {
                work(i, j, k) *= rhoSpectrum(i, j, k) * scaling;
            });
    fft_m->transform(ippl::BACKWARD, real_m, workSpectrum_m);
    extractPotential(kind, curvature);
}

void FFT2D5FreeSpace::extractPotential(int kind, double curvature) {
    const auto real = real_m.getView();
    const auto phi = potential_m;
    const auto h = spacing_m;
    const double originX = origin_m[0];
    const int nx = static_cast<int>(size_m[0]) + 4;
    const int ny = static_cast<int>(size_m[1]) + 4;
    const int nz = static_cast<int>(size_m[2]) + 4;
    const int px = static_cast<int>(paddedSize_m[0]);
    const int py = static_cast<int>(paddedSize_m[1]);
    const int pz = static_cast<int>(paddedSize_m[2]);
    Kokkos::parallel_for(
            "FFT2D5FreeSpacePotential", Policy({0, 0, 0}, {nx, ny, nz}),
            KOKKOS_LAMBDA(int i, int j, int k) {
                const int ix = (i - 2 + px) % px;
                const int iy = (j - 2 + py) % py;
                const int iz = (k - 2 + pz) % pz;
                const double u = originX + (i - 1.5) * h[0];
                const double factor = kind == fft2d5_free::CellKernel::G
                                              ? 1.0
                                              : (kind == fft2d5_free::CellKernel::H ? -curvature * u
                                                                                  : 0.5 * curvature);
                phi(i, j, k) += factor * real(ix, iy, iz);
            });
}

void FFT2D5FreeSpace::determineField(
        VectorField3& electricField, double curvature, double gamma) {
    const auto phi = potential_m;
    const auto e = electricField.getView();
    const auto h = spacing_m;
    const double originX = origin_m[0];
    const int ng = electricField.getNghost();
    const int ex = static_cast<int>(e.extent(0));
    const int ey = static_cast<int>(e.extent(1));
    const int ez = static_cast<int>(e.extent(2));
    const int nx = static_cast<int>(size_m[0]);
    const int ny = static_cast<int>(size_m[1]);
    const int nz = static_cast<int>(size_m[2]);
    if (ng > 1) {
        throw OpalException("FFT2D5FreeSpace::determineField", "At most one electric-field halo cell is supported.");
    }
    Kokkos::parallel_for(
            "FFT2D5FreeSpaceGradient", Policy({0, 0, 0}, {ex, ey, ez}),
            KOKKOS_LAMBDA(int i, int j, int k) {
                const int x = i - ng + 2, y = j - ng + 2, z = k - ng + 2;
                const bool physicalX = i >= ng && i < nx + ng;
                const bool physicalY = j >= ng && j < ny + ng;
                const bool physicalZ = k >= ng && k < nz + ng;
                const double du = physicalX
                        ? (phi(x - 2, y, z) - 8.0 * phi(x - 1, y, z)
                           + 8.0 * phi(x + 1, y, z) - phi(x + 2, y, z)) / (12.0 * h[0])
                        : (phi(x + 1, y, z) - phi(x - 1, y, z)) / (2.0 * h[0]);
                const double dy = physicalY
                        ? (phi(x, y - 2, z) - 8.0 * phi(x, y - 1, z)
                           + 8.0 * phi(x, y + 1, z) - phi(x, y + 2, z)) / (12.0 * h[1])
                        : (phi(x, y + 1, z) - phi(x, y - 1, z)) / (2.0 * h[1]);
                const double ds = physicalZ
                        ? (phi(x, y, z - 2) - 8.0 * phi(x, y, z - 1)
                           + 8.0 * phi(x, y, z + 1) - phi(x, y, z + 2)) / (12.0 * h[2])
                        : (phi(x, y, z + 1) - phi(x, y, z - 1)) / (2.0 * h[2]);
                const double u = originX + (i - ng + 0.5) * h[0];
                e(i, j, k)[0] = -gamma * du;
                e(i, j, k)[1] = -gamma * dy;
                e(i, j, k)[2] = -ds / (gamma * (1.0 + curvature * u));
            });
    Kokkos::fence();
}

}  // namespace opalx::spacecharge
