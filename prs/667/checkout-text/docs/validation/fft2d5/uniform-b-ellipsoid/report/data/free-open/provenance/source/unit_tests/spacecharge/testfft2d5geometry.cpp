#include <gtest/gtest.h>

#include "Algorithms/CoordinateSystemTrafo.h"
#include "Algorithms/Quaternion.hpp"
#include "Ippl.h"
#include "SpaceCharge/FFT2D5/FFT2D5Geometry.h"
#include "Utilities/OpalException.h"

#include <cmath>
#include <vector>

namespace opalx::spacecharge {
    namespace {
        using Vector = FFT2D5Geometry::Vector;

        class FFT2D5GeometryTest : public ::testing::Test {
        protected:
            static void SetUpTestSuite() {
                int argc    = 0;
                char** argv = nullptr;
                ippl::initialize(argc, argv);
            }
            static void TearDownTestSuite() { ippl::finalize(); }

            static ReferencePath::View points(const std::vector<Vector>& values) {
                ReferencePath::View result("FFT2D5GeometryTestPoints", values.size());
                auto host = Kokkos::create_mirror_view(result);
                for (std::size_t i = 0; i < values.size(); ++i) host(i) = values[i];
                Kokkos::deep_copy(result, host);
                return result;
            }

            static std::vector<Vector> circle(double curvature, double length = 8.0) {
                std::vector<Vector> result;
                for (unsigned i = 0; i <= 40; ++i) {
                    const double s = length * i / 40.0;
                    const double a = curvature * s;
                    result.emplace_back(
                            (std::cos(a) - 1.0) / curvature, 0.0,
                            std::sin(a) / curvature);
                }
                return result;
            }

            static void expectVector(const Vector& actual, const Vector& expected, double tol) {
                for (unsigned d = 0; d < 3; ++d) EXPECT_NEAR(actual[d], expected[d], tol);
            }
        };

        TEST_F(FFT2D5GeometryTest, DefaultGeometryIsDisabled) {
            EXPECT_FALSE(FFT2D5Geometry{}.isValid());
        }

        TEST_F(FFT2D5GeometryTest, StraightLineUsesUnclampedExactCoordinates) {
            const auto geometry = FFT2D5Geometry::fit(points(
                    {Vector(2.0, 3.0, -1.0), Vector(2.6, 3.0, -0.2), Vector(3.2, 3.0, 0.6)}));
            ASSERT_TRUE(geometry.isStraight());
            EXPECT_NEAR(geometry.pathLength(), 2.0, 1.0e-14);
            EXPECT_DOUBLE_EQ(geometry.signedCurvature(), 0.0);
            for (const double s : {-0.2, 0.0, 0.7, 2.0, 2.2}) {
                const Vector local(0.003, -0.0002, s);
                expectVector(geometry.toFrenet(geometry.position(local)), local, 2.0e-14);
            }
        }

        TEST_F(FFT2D5GeometryTest, BothCircleSignsHaveExactArcAndRoundTripBeyondPi) {
            for (const double curvature : {-0.5, 0.5}) {
                const auto geometry = FFT2D5Geometry::fit(points(circle(curvature)));
                ASSERT_TRUE(geometry.isValid());
                EXPECT_FALSE(geometry.isStraight());
                EXPECT_NEAR(geometry.signedCurvature(), curvature, 1.0e-14);
                EXPECT_NEAR(geometry.pathLength(), 8.0, 1.0e-13);
                for (const double s : {-0.01, 0.0, 0.5, 4.0, 7.9, 8.0, 8.01}) {
                    const Vector local(0.004, -0.0003, s);
                    expectVector(geometry.toFrenet(geometry.position(local)), local, 2.0e-13);
                    Vector b, n, t;
                    geometry.basis(s, b, n, t);
                    EXPECT_NEAR(b.dot(t), 0.0, 2.0e-14);
                    EXPECT_NEAR(b.dot(b), 1.0, 2.0e-14);
                    EXPECT_NEAR(t.dot(t), 1.0, 2.0e-14);
                    const double h = 1.0e-5;
                    const Vector derivative =
                            (geometry.position(Vector(local[0], local[1], s + h))
                             - geometry.position(Vector(local[0], local[1], s - h)))
                            / (2.0 * h);
                    // The subtraction of metre-scale coordinates has O(epsilon/h)
                    // roundoff; this bound also covers the O(h²) difference error.
                    expectVector(derivative, Vector(geometry.metric(local[0]) * t), 2.0e-10);
                }
            }
        }

        TEST_F(FFT2D5GeometryTest, TiltedAndVerticalStraightLinesHaveOrthonormalFrames) {
            for (const Vector& end : {Vector(1.0, 2.0, 3.0), Vector(0.0, -2.0, 0.0)}) {
                const auto geometry = FFT2D5Geometry::fit(points({Vector(0.0), end}));
                ASSERT_TRUE(geometry.isStraight());
                EXPECT_NEAR(geometry.pathLength(), std::sqrt(end.dot(end)), 2.0e-14);
                const Vector local(0.003, 0.0004, 0.7);
                expectVector(geometry.toFrenet(geometry.position(local)), local, 2.0e-14);
                Vector b, n, t;
                geometry.basis(0.0, b, n, t);
                EXPECT_NEAR(n.dot(t), 0.0, 2.0e-14);
                EXPECT_NEAR(b.dot(t), 0.0, 2.0e-14);
                EXPECT_NEAR(n.dot(b), 0.0, 2.0e-14);
                EXPECT_NEAR(b.dot(b), 1.0, 2.0e-14);
                EXPECT_NEAR(n.dot(n), 1.0, 2.0e-14);
            }
        }

        TEST_F(FFT2D5GeometryTest, GeometryTransformsWithGeneralRigidSolveFrame) {
            const auto lab = FFT2D5Geometry::fit(points(circle(0.5)));
            const double a = 0.7;
            const double q = std::sin(0.5 * a) / std::sqrt(14.0);
            const CoordinateSystemTrafo transform(
                    Vector(3.0, -2.0, 1.0), Quaternion(std::cos(0.5 * a), q, 2.0 * q, 3.0 * q));
            const auto solve = lab.transformed(transform);
            for (const double s : {0.0, 3.0, 7.0, 8.0}) {
                const Vector local(-0.004, 0.0002, s);
                expectVector(solve.position(local), transform.transformTo(lab.position(local)), 3.0e-14);
                expectVector(solve.toFrenet(solve.position(local)), local, 2.0e-13);
                const Vector field(1.0, 2.0, -3.0);
                expectVector(
                        solve.toGlobalVector(field, s),
                        transform.rotateTo(lab.toGlobalVector(field, s)), 3.0e-14);
                expectVector(solve.toLocalVector(solve.toGlobalVector(field, s), s), field, 3.0e-14);
            }
        }

        TEST_F(FFT2D5GeometryTest, MappingRunsInsideKokkosKernel) {
            const auto geometry = FFT2D5Geometry::fit(points(circle(0.5)));
            ReferencePath::View results("FFT2D5GeometryDeviceResults", 3);
            Kokkos::parallel_for(
                    "FFT2D5GeometryTestRoundTrip", 3, KOKKOS_LAMBDA(const unsigned i) {
                        const Vector local(0.003, -0.0001, 4.0 * i);
                        results(i) = geometry.toFrenet(geometry.position(local));
                    });
            const auto host = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), results);
            for (unsigned i = 0; i < 3; ++i) {
                expectVector(host(i), Vector(0.003, -0.0001, 4.0 * i), 2.0e-13);
            }
        }

        TEST_F(FFT2D5GeometryTest, RejectsUnsupportedAndReversingPaths) {
            auto values = circle(0.5);
            values[20][0] += 0.01;
            EXPECT_THROW(static_cast<void>(FFT2D5Geometry::fit(points(values))), OpalException);
            values = circle(0.5);
            values[20][1] = 0.01;
            EXPECT_THROW(static_cast<void>(FFT2D5Geometry::fit(points(values))), OpalException);
            EXPECT_THROW(
                    static_cast<void>(FFT2D5Geometry::fit(points(
                            {Vector(0.0), Vector(0.0, 0.0, 1.0), Vector(0.0, 0.0, 0.5)}))),
                    OpalException);
            EXPECT_THROW(
                    static_cast<void>(FFT2D5Geometry::fit(points(circle(0.5, 4.0 * std::acos(-1.0))))),
                    OpalException);
        }
    }  // namespace
}  // namespace opalx::spacecharge
