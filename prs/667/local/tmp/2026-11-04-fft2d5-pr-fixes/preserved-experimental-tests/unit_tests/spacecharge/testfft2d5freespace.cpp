#include <gtest/gtest.h>

#include "Physics/Physics.h"
#include "SpaceCharge/FFT2D5/FFT2D5FieldStorage.h"
#include "SpaceCharge/FFT2D5/FFT2D5FreeSpace.h"
#include "SpaceCharge/FFT2D5/FFT2D5FreeSpaceKernel.h"

#include <array>
#include <cmath>

namespace opalx::spacecharge {
namespace {
class FFT2D5FreeSpaceTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() {
        int argc = 0;
        char** argv = nullptr;
        ippl::initialize(argc, argv);
    }
    static void TearDownTestSuite() { ippl::finalize(); }

    // Independent ellipsoidal depolarization integral, not a sampled Green kernel.
    static double ellipsoidCoefficient(const std::array<double, 3>& axes, unsigned d) {
        constexpr unsigned intervals = 32768;
        double sum = 0.0;
        for (unsigned i = 0; i < intervals; ++i) {
            const double t = (i + 0.5) / intervals;
            const double u = t / (1.0 - t);
            double product = 1.0;
            for (double a : axes) product *= a * a + u;
            const double integrand = 1.0 / ((axes[d] * axes[d] + u) * std::sqrt(product)
                                           * (1.0 - t) * (1.0 - t));
            sum += integrand;
        }
        return axes[0] * axes[1] * axes[2] * sum / intervals;
    }
};

TEST_F(FFT2D5FreeSpaceTest, IntegratedSingularCubeHasKnownPotentialAndSymmetry) {
    using Kernel = fft2d5_free::CellKernel;
    const double expected = (24.0 * std::log((1.0 + std::sqrt(3.0)) / std::sqrt(2.0))
                             - 2.0 * Physics::pi) / 8.0;
    EXPECT_NEAR(Kernel::average(Kernel::G, 0, 0, 0, 2, 2, 2, 0), expected, 1e-13);
    EXPECT_NEAR(Kernel::average(Kernel::H, 0, 0, 0, 2, 2, 2, 0), expected / 3.0, 1e-13);
    EXPECT_NEAR(Kernel::average(Kernel::F, 0, 0, 0, 2, 2, 2, 0), 0.0, 1e-13);
    for (int kind : {Kernel::G, Kernel::H, Kernel::F}) {
        const double value = Kernel::average(kind, .3, .2, .7, .05, .02, .1, .5);
        const double reflected = Kernel::average(kind, -.3, -.2, -.7, .05, .02, .1, .5);
        EXPECT_NEAR(reflected, kind == Kernel::F ? -value : value, 1e-12);
    }
}

TEST_F(FFT2D5FreeSpaceTest, FiniteUniformEllipsoidMatchesAllThreeAnalyticFields) {
    FFT2D5Config config;
    config.grid.meshSize = {48, 48, 48};
    config.pipeSizeX = config.pipeSizeY = 2.0;
    FFT2D5FieldStorage fields(config, 2.0);
    auto& rho = fields.chargeDensity();
    auto host = rho.getHostMirror();
    Kokkos::deep_copy(host, 0.0);
    constexpr double density = 1.0e-12;
    const std::array<double, 3> axes{.65, .5, .8};
    const auto spacing = fields.spacing();
    const auto origin = fields.origin();
    const int ng = rho.getNghost();
    // Geometric subcell volume fractions reduce the boundary staircase error.
    constexpr int subdivisions = 4;
    for (int i = 0; i < 48; ++i) for (int j = 0; j < 48; ++j) for (int k = 0; k < 48; ++k) {
        int inside = 0;
        for (int ii = 0; ii < subdivisions; ++ii)
            for (int jj = 0; jj < subdivisions; ++jj)
                for (int kk = 0; kk < subdivisions; ++kk) {
                    const double x = origin[0] + (i + (ii + .5) / subdivisions) * spacing[0];
                    const double y = origin[1] + (j + (jj + .5) / subdivisions) * spacing[1];
                    const double z = origin[2] + (k + (kk + .5) / subdivisions) * spacing[2] - 1.0;
                    if (x*x/(axes[0]*axes[0]) + y*y/(axes[1]*axes[1])
                        + z*z/(axes[2]*axes[2]) < 1.0) ++inside;
                }
        host(i+ng,j+ng,k+ng) = density * inside / (subdivisions*subdivisions*subdivisions);
    }
    Kokkos::deep_copy(rho.getView(), host);
    FFT2D5FreeSpace solver;
    for (const double gamma : {1.0, 2.0}) {
        SCOPED_TRACE(gamma);
        ASSERT_EQ(solver.solve(rho, fields.electricField(), 0.0, gamma), 1u);
        auto restAxes = axes;
        restAxes[2] *= gamma;
        std::array<double, 3> slope;
        for (unsigned d = 0; d < 3; ++d)
            slope[d] = density * ellipsoidCoefficient(restAxes, d) / (2.0 * Physics::epsilon_0);
        const auto e = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), fields.electricField().getView());
        const int ne = fields.electricField().getNghost();
        for (const auto index : {std::array<int,3>{19,20,21}, {28,26,27}, {21,28,26}}) {
            const std::array<double,3> position{
                origin[0]+(index[0]+.5)*spacing[0], origin[1]+(index[1]+.5)*spacing[1],
                origin[2]+(index[2]+.5)*spacing[2]-1.0};
            for (unsigned d = 0; d < 3; ++d) {
                const double expected = slope[d] * position[d];
                // 1% covers a 48-cell ellipsoid boundary and finite differences;
                // the independent reference is the exact continuum interior field.
                EXPECT_NEAR(e(index[0]+ne,index[1]+ne,index[2]+ne)[d], expected,
                            .01 * std::abs(expected));
            }
        }
    }
}

TEST_F(FFT2D5FreeSpaceTest, EmptyDensityHasZeroFieldsAndNoBackendSolve) {
    FFT2D5Config config;
    config.grid.meshSize = {4,4,4};
    config.pipeSizeX = config.pipeSizeY = 1.0;
    FFT2D5FieldStorage fields(config, 1.0);
    Kokkos::deep_copy(fields.chargeDensity().getView(), 0.0);
    FFT2D5FreeSpace solver;
    EXPECT_EQ(solver.solve(fields.chargeDensity(), fields.electricField(), 0.0), 0u);
    const auto e = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), fields.electricField().getView());
    for (std::size_t i=0;i<e.extent(0);++i)
        for (std::size_t j=0;j<e.extent(1);++j)
            for (std::size_t k=0;k<e.extent(2);++k)
                for (unsigned d=0;d<3;++d) EXPECT_DOUBLE_EQ(e(i,j,k)[d],0.0);
}
} // namespace
} // namespace opalx::spacecharge
