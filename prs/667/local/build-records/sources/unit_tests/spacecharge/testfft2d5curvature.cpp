#include <gtest/gtest.h>

#include "Physics/Physics.h"
#include "SpaceCharge/FFT2D5/FFT2D5Curvature.h"
#include "SpaceCharge/FFT2D5/FFT2D5FieldStorage.h"
#include "Utilities/OpalException.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>

namespace opalx::spacecharge {
namespace {

class FFT2D5CurvatureTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() {
        int argc = 0;
        char** argv = nullptr;
        ippl::initialize(argc, argv);
    }
    static void TearDownTestSuite() { ippl::finalize(); }

    // Independent quadrature of the radial field of a positive circular line
    // element, from Cartesian source-target displacement. No finite-part weight
    // formula is used by this reference.
    static double lineIntervalQuadrature(double low, double high, double curvature) {
        constexpr unsigned subdivisions = 4096;
        const double radius = 1.0 / std::abs(curvature);
        const double ds = (high - low) / subdivisions;
        double integral = 0.0;
        for (unsigned i = 0; i < subdivisions; ++i) {
            const double s = low + (i + 0.5) * ds;
            const double angle = s / radius;
            const double radialDisplacement = 2.0 * radius * std::pow(std::sin(angle / 2), 2);
            const double tangentDisplacement = -radius * std::sin(angle);
            const double distance = std::hypot(radialDisplacement, tangentDisplacement);
            integral += std::copysign(radialDisplacement, curvature)
                        / (distance * distance * distance);
        }
        return integral * ds;
    }

    static double triangularPrimitive(double s, double halfLength) {
        s = std::clamp(s, -halfLength, halfLength);
        return s < 0.0 ? (s + halfLength) * (s + halfLength) / (2.0 * halfLength)
                       : halfLength / 2.0 + s - s * s / (2.0 * halfLength);
    }

    static double profileCellAverage(double centre, double width, bool triangular) {
        constexpr double halfLength = 2.5;
        const double low = centre - width / 2.0;
        const double high = centre + width / 2.0;
        if (triangular) {
            return (triangularPrimitive(high, halfLength)
                    - triangularPrimitive(low, halfLength)) / width;
        }
        return std::max(0.0, std::min(high, halfLength) - std::max(low, -halfLength))
               / width;
    }

    static std::size_t fillEllipticalArc(
            FFT2D5FieldStorage& fields, double curvature, bool triangular) {
        constexpr double a = .005, c = .0005, charge = 1.0e-11;
        constexpr int subdivisions = 8;
        const double density = charge / (Physics::pi * a * c * (triangular ? 2.5 : 5.0));
        auto& rho = fields.chargeDensity();
        auto host = rho.getHostMirror();
        Kokkos::deep_copy(host, 0.0);
        const auto spacing = fields.spacing();
        const auto origin = fields.origin();
        const auto mesh = fields.meshSize();
        const int ng = rho.getNghost();
        std::size_t occupied = 0;
        for (std::size_t k = 0; k < mesh[2]; ++k) {
            const double s = (k + .5) * spacing[2] - fields.size()[2] / 2.0;
            const double longitudinal = profileCellAverage(s, spacing[2], triangular);
            if (longitudinal == 0.0) continue;
            ++occupied;
            for (std::size_t i = 0; i < mesh[0]; ++i) {
                const double u = origin[0] + (i + .5) * spacing[0];
                for (std::size_t j = 0; j < mesh[1]; ++j) {
                    unsigned inside = 0;
                    for (int ii = 0; ii < subdivisions; ++ii)
                        for (int jj = 0; jj < subdivisions; ++jj) {
                            const double x = origin[0] + (i + (ii + .5) / subdivisions) * spacing[0];
                            const double y = origin[1] + (j + (jj + .5) / subdivisions) * spacing[1];
                            if (x * x / (a * a) + y * y / (c * c) < 1.0) ++inside;
                        }
                    // The deposited density is charge per flat du dy ds. The
                    // physical density differs by the curved-volume Jacobian.
                    host(i + ng, j + ng, k + ng) = density * longitudinal
                        * (1.0 + curvature * u) * inside / (subdivisions * subdivisions);
                }
            }
        }
        Kokkos::deep_copy(rho.getView(), host);
        return occupied;
    }

    template <class HostView>
    static std::array<double, 2> midpointField(
            const HostView& e, int ng, const std::array<std::size_t, 3>& mesh) {
        std::array<double, 2> result{};
        for (int i = -1; i <= 0; ++i)
            for (int j = -1; j <= 0; ++j)
                for (int k = -1; k <= 0; ++k)
                    for (unsigned d = 0; d < 2; ++d)
                        result[d] += e(mesh[0] / 2 + i + ng, mesh[1] / 2 + j + ng,
                                       mesh[2] / 2 + k + ng)[d] / 8.0;
        return result;
    }

    static double uncorrectedMidpointRadial(FFT2D5FieldStorage& fields) {
        const auto& source = fields.chargeDensity();
        const auto rho = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), source.getView());
        auto& slice = fields.workspace();
        auto host = slice.chargeDensity->getHostMirror();
        Kokkos::deep_copy(host, 0.0);
        const int ns = source.getNghost();
        const int nr = slice.chargeDensity->getNghost();
        const auto mesh = fields.meshSize();
        const std::size_t k = mesh[2] / 2;
        for (std::size_t i = 0; i < mesh[0]; ++i)
            for (std::size_t j = 0; j < mesh[1]; ++j)
                host(i + nr, j + nr) = rho(i + ns, j + ns, k + ns) / Physics::epsilon_0;
        Kokkos::deep_copy(slice.chargeDensity->getView(), host);
        fields.solveSlice();
        const auto e = Kokkos::create_mirror_view_and_copy(
                Kokkos::HostSpace(), slice.electricField->getView());
        const int ne = slice.electricField->getNghost();
        double result = 0.0;
        for (int i = -1; i <= 0; ++i)
            for (int j = -1; j <= 0; ++j)
                result += e(mesh[0] / 2 + i + ne, mesh[1] / 2 + j + ne)[0] / 4.0;
        return result;
    }
};

TEST_F(FFT2D5CurvatureTest, NativeNormalCrossTangentPointsOutwardAndPositiveArcChargesRepelOutward) {
    constexpr double radius = 2.0, theta = .4, delta = .2;
    const std::array<double, 3> tangent{-std::sin(theta), 0.0, std::cos(theta)};
    const std::array<double, 3> radial{tangent[2], 0.0, -tangent[0]};
    EXPECT_NEAR(radial[0], std::cos(theta), 1e-15);
    EXPECT_NEAR(radial[2], std::sin(theta), 1e-15);
    const std::array<double, 3> target{radius * (std::cos(theta) - 1.0), 0.0,
                                       radius * std::sin(theta)};
    double projected = 0.0;
    for (const double sign : {-1.0, 1.0}) {
        const double angle = theta + sign * delta;
        const double dx = target[0] - radius * (std::cos(angle) - 1.0);
        const double dz = target[2] - radius * std::sin(angle);
        projected += (dx * radial[0] + dz * radial[2]) / std::pow(std::hypot(dx, dz), 3);
    }
    EXPECT_GT(projected, 0.0);
    EXPECT_NEAR(projected, 1.0 / (2.0 * radius * radius * std::sin(delta / 2)), 1e-13);
}

TEST_F(FFT2D5CurvatureTest, OffDiagonalCellWeightMatchesIndependentCartesianCoulombQuadrature) {
    constexpr double ds = .025;
    for (const double curvature : {.5, -.5, .02}) {
        for (const double distance : {.025, .125, 1.25}) {
            SCOPED_TRACE(curvature);
            SCOPED_TRACE(distance);
            const double expected = lineIntervalQuadrature(distance - ds / 2, distance + ds / 2,
                                                           curvature);
            EXPECT_NEAR(FFT2D5Curvature::lineOffDiagonalWeight(distance, ds, curvature),
                        expected, 2e-8 * std::abs(expected));
        }
    }
}

TEST_F(FFT2D5CurvatureTest, SelfWeightHasRequiredGaugeShiftAndStraightLimit) {
    constexpr double ds = .025, curvature = .5, gauge = .01;
    const double self = FFT2D5Curvature::lineSelfWeight(ds, curvature);
    EXPECT_NEAR(FFT2D5Curvature::lineSelfWeight(ds, curvature, gauge) - self,
                -curvature * std::log(gauge), 1e-14);
    EXPECT_NEAR(FFT2D5Curvature::lineSelfWeight(ds, -curvature), -self, 1e-14);
    constexpr double weak = 1e-8;
    EXPECT_NEAR(FFT2D5Curvature::lineSelfWeight(ds, weak), weak * std::log(ds), 1e-21);
    EXPECT_DOUBLE_EQ(FFT2D5Curvature::lineSelfWeight(ds, 0.0), 0.0);
    EXPECT_DOUBLE_EQ(FFT2D5Curvature::lineOffDiagonalWeight(.125, ds, 0.0), 0.0);
}

TEST_F(FFT2D5CurvatureTest, ConstantLineWeightsSumToIndependentFiniteArcAndFullRingLimits) {
    constexpr double radius = 2.0, curvature = 1.0 / radius, length = 5.0;
    constexpr unsigned cells = 65;
    const double ds = length / cells;
    double finite = FFT2D5Curvature::lineSelfWeight(ds, curvature);
    for (unsigned j = 1; j <= cells / 2; ++j)
        finite += 2.0 * FFT2D5Curvature::lineOffDiagonalWeight(j * ds, ds, curvature);
    const double expectedFinite = curvature * std::log(8.0 * radius * std::tan(length / (8.0 * radius)));
    EXPECT_NEAR(finite, expectedFinite, 2e-14);
    constexpr unsigned ringCells = 64;
    const double ringDs = 2.0 * Physics::pi * radius / ringCells;
    double periodic = FFT2D5Curvature::lineSelfWeight(ringDs, curvature);
    for (unsigned j = 1; j < ringCells; ++j) {
        const double distance = std::min(j, ringCells - j) * ringDs;
        periodic += FFT2D5Curvature::lineOffDiagonalWeight(distance, ringDs, curvature);
    }
    EXPECT_NEAR(periodic, curvature * std::log(8.0 * radius), 2e-14);
}

TEST_F(FFT2D5CurvatureTest, UniformAndTriangularFiveMetreArcRestorePhysicalOutwardMidpoint) {
    ASSERT_EQ(ippl::Comm->size(), 1) << "The original FFT2D5 slice backend requires one rank.";
    constexpr double radius = 2.0, a = .005, c = .0005, charge = 1.0e-11;
    constexpr double k = 1.0 / (4.0 * Physics::pi * Physics::epsilon_0);
    // Independent original 3-D Coulomb volume integration, with no SACR
    // boundary helper or cell kernel: 96 radial x1024 angular x256 longitudinal
    // nodes; last quadrature change <4.2e-10 V/m. These are physical outward Eu.
    const std::array<double, 2> physicalReference{.05509202225014298, .09183886568862973};
    const std::array<double, 2> firstOrderReference{.05509204053254229, .09180790250056382};
    for (unsigned profile = 0; profile < 2; ++profile) {
        SCOPED_TRACE(profile);
        FFT2D5Config config;
        config.grid.meshSize = {128, 64, 256};
        config.pipeSizeX = .012;
        config.pipeSizeY = .0015;
        FFT2D5FieldStorage fields(config, 2.0 * Physics::pi * radius);
        const auto occupied = fillEllipticalArc(fields, 1.0 / radius, profile != 0);
        // create_mirror_view_and_copy may alias a HostSpace/OpenMP source;
        // allocate a separate snapshot so mutations cannot hide in this check.
        const auto before = Kokkos::create_mirror(fields.chargeDensity().getView());
        Kokkos::deep_copy(before, fields.chargeDensity().getView());
        const double old = uncorrectedMidpointRadial(fields);
        const double lambda = charge / (profile ? 2.5 : 5.0);
        const double oldExpected = -2.0 * k * lambda * a / (radius * (a + c));
        EXPECT_LT(old, 0.0);
        EXPECT_NEAR(old, oldExpected, .03 * std::abs(oldExpected));
        fields.resetBackendSolves();
        FFT2D5Curvature solver;
        EXPECT_EQ(solver.solve(fields, 1.0 / radius, true), 2u * occupied);
        EXPECT_EQ(fields.backendSolves(), 2u * occupied);
        const auto e = Kokkos::create_mirror_view_and_copy(
                Kokkos::HostSpace(), fields.electricField().getView());
        const auto result = midpointField(e, fields.electricField().getNghost(), fields.meshSize());
        EXPECT_GT(result[0], 0.0);
        // 1% measures the weak curvature field itself. It covers finite XY
        // cells/gradients and longitudinal cell averages, rather than hiding
        // this field behind the much larger transverse boundary-field scale.
        // The continuum first-order truncation is .000034% / .0338% here.
        EXPECT_NEAR(result[0], physicalReference[profile], .01 * physicalReference[profile]);
        EXPECT_NEAR(result[0], firstOrderReference[profile], .01 * firstOrderReference[profile]);
        EXPECT_NEAR(result[1], 0.0, 1e-10);
        const auto after = Kokkos::create_mirror_view_and_copy(
                Kokkos::HostSpace(), fields.chargeDensity().getView());
        double maxChange = 0.0;
        for (std::size_t i = 0; i < before.extent(0); ++i)
            for (std::size_t j = 0; j < before.extent(1); ++j)
                for (std::size_t l = 0; l < before.extent(2); ++l)
                    maxChange = std::max(maxChange, std::abs(before(i, j, l) - after(i, j, l)));
        EXPECT_DOUBLE_EQ(maxChange, 0.0);
    }
}

TEST_F(FFT2D5CurvatureTest, EmptySourceClearsFieldsWithoutAnySliceFFT) {
    FFT2D5Config config;
    config.grid.meshSize = {4, 4, 8};
    config.pipeSizeX = config.pipeSizeY = .01;
    FFT2D5FieldStorage fields(config, 4.0 * Physics::pi);
    Kokkos::deep_copy(fields.chargeDensity().getView(), 0.0);
    Kokkos::deep_copy(fields.electricField().getView(), FFT2D5FieldStorage::Vector3(3.0));
    FFT2D5Curvature solver;
    EXPECT_EQ(solver.solve(fields, .5, true), 0u);
    const auto e = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), fields.electricField().getView());
    double maxMagnitude = 0.0;
    for (std::size_t i = 0; i < e.extent(0); ++i)
        for (std::size_t j = 0; j < e.extent(1); ++j)
            for (std::size_t l = 0; l < e.extent(2); ++l)
                for (unsigned d = 0; d < 3; ++d)
                    maxMagnitude = std::max(maxMagnitude, std::abs(e(i, j, l)[d]));
    EXPECT_DOUBLE_EQ(maxMagnitude, 0.0);
}

TEST_F(FFT2D5CurvatureTest, EmptyTransversePaddingDoesNotChangeThePhysicalThinTube) {
    std::array<double, 2> centres{};
    for (unsigned padding = 0; padding < 2; ++padding) {
        FFT2D5Config config;
        // Both boxes resolve the identical source at dx=dy=1mm. The larger
        // empty box extends beyond |kappa*u|=.01, but the physical source does not.
        config.grid.meshSize = {padding ? 80u : 40u, padding ? 80u : 40u, 8};
        config.pipeSizeX = config.pipeSizeY = padding ? .08 : .04;
        FFT2D5FieldStorage fields(config, 4.0 * Physics::pi);
        auto source = fields.chargeDensity().getHostMirror();
        Kokkos::deep_copy(source, 0.0);
        const int ng = fields.chargeDensity().getNghost();
        const auto n = fields.meshSize();
        for (int i = -2; i <= 1; ++i)
            for (int j = -2; j <= 1; ++j) {
                const double u = (i + .5) * .001;
                source(n[0]/2 + i + ng, n[1]/2 + j + ng, n[2]/2 + ng) =
                        1e-8 * (1.0 + .5 * u);
            }
        Kokkos::deep_copy(fields.chargeDensity().getView(), source);
        FFT2D5Curvature solver;
        EXPECT_EQ(solver.solve(fields, .5, true), 2u);
        const auto e = Kokkos::create_mirror_view_and_copy(
                Kokkos::HostSpace(), fields.electricField().getView());
        centres[padding] = 2.0 * midpointField(e, fields.electricField().getNghost(), n)[0];
        // An occupied source outside the physical thin region still fails;
        // numerical padding does not extend the supported particle regime.
        if (padding) {
            source(n[0]/2 + 25 + ng, n[1]/2 + ng, n[2]/2 + ng) = 1e-8;
            Kokkos::deep_copy(fields.chargeDensity().getView(), source);
            EXPECT_THROW(solver.solve(fields, .5, true), OpalException);
        }
    }
    EXPECT_GT(centres[0], 0.0);
    EXPECT_NEAR(centres[0], centres[1], 1e-11);
}

}  // namespace
}  // namespace opalx::spacecharge
