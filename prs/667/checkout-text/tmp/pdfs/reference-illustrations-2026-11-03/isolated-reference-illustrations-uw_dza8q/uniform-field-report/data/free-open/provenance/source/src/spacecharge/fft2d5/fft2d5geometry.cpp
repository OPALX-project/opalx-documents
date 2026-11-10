/**
 * @file FFT2D5Geometry.cpp
 * @brief Validate and recover exact straight/circular reference-path geometry.
 */

#include "SpaceCharge/FFT2D5/FFT2D5Geometry.h"

#include "Algorithms/CoordinateSystemTrafo.h"
#include "Utilities/OpalException.h"

#include <algorithm>
#include <cmath>
#include <limits>

namespace opalx::spacecharge {
    namespace {
        double norm(const FFT2D5Geometry::Vector& vector) {
            return std::sqrt(vector.dot(vector));
        }

        [[noreturn]] void reject(const char* reason) {
            throw OpalException("FFT2D5Geometry::fit", reason);
        }
    }  // namespace

    FFT2D5Geometry FFT2D5Geometry::fit(
            const ReferencePath::View& points, double relativeTolerance,
            double absoluteTolerance) {
        if (points.extent(0) < 2) reject("At least two reference-path points are required.");
        if (!std::isfinite(relativeTolerance) || !std::isfinite(absoluteTolerance)
            || relativeTolerance < 0.0 || absoluteTolerance < 0.0
            || relativeTolerance + absoluteTolerance == 0.0) {
            reject("Reference-path fit tolerances must be finite, nonnegative, and nonzero.");
        }
        const auto host = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), points);
        const auto count = host.extent(0);
        const Vector origin = host(0);
        double extent = 0.0;
        double coordinateScale = 0.0;
        std::size_t farthest = 0;
        for (std::size_t i = 0; i < count; ++i) {
            for (unsigned d = 0; d < 3; ++d) {
                if (!std::isfinite(host(i)[d])) reject("Reference-path points must be finite.");
                coordinateScale = std::max(coordinateScale, std::abs(host(i)[d]));
            }
            const double distance = norm(Vector(host(i) - origin));
            if (distance > extent) {
                extent   = distance;
                farthest = i;
            }
        }
        if (!(extent > 0.0)) reject("Reference-path points must not all coincide.");
        const double tolerance = absoluteTolerance + relativeTolerance * extent
                                 + 32.0 * std::numeric_limits<double>::epsilon() * coordinateScale;
        for (std::size_t i = 0; i < count; ++i) {
            if (i > 0 && norm(Vector(host(i) - host(i - 1))) == 0.0) {
                reject("Successive reference-path points must be distinct.");
            }
        }

        FFT2D5Geometry geometry;
        geometry.origin_m = origin;
        geometry.n0_m     = Vector(0.0, 1.0, 0.0);
        Vector line       = host(farthest) - origin;
        const double lineLength = norm(line);
        if (!(lineLength > 0.0)) reject("Reference path has no extent.");
        line /= lineLength;
        double maximumDeparture = 0.0;
        std::size_t offLine = 0;
        for (std::size_t i = 0; i < count; ++i) {
            const Vector delta = host(i) - origin;
            const double departure = norm(Vector(delta - delta.dot(line) * line));
            if (departure > maximumDeparture) {
                maximumDeparture = departure;
                offLine          = i;
            }
        }
        if (maximumDeparture <= tolerance) {
            const Vector end = host(count - 1) - origin;
            if (!(end.dot(line) > 0.0)) reject("Straight reference path reverses direction.");
            double previous = 0.0;
            for (std::size_t i = 1; i < count; ++i) {
                const double s = Vector(host(i) - origin).dot(line);
                if (!(s > previous)) reject("Straight reference path must be ordered monotonically.");
                previous = s;
            }
            geometry.t0_m    = line;
            Vector normal = Vector(0.0, 1.0, 0.0) - line[1] * line;
            if (norm(normal) < 64.0 * std::numeric_limits<double>::epsilon()) {
                normal = Vector(0.0, 0.0, 1.0) - line[2] * line;
            }
            geometry.n0_m = normal / norm(normal);
            const Vector n = geometry.n0_m;
            geometry.b0_m = Vector(
                    n[1] * line[2] - n[2] * line[1], n[2] * line[0] - n[0] * line[2],
                    n[0] * line[1] - n[1] * line[0]);
            geometry.length_m = end.dot(line);
            geometry.valid_m = true;
            return geometry;
        }

        for (std::size_t i = 0; i < count; ++i) {
            if (std::abs(host(i)[1] - origin[1]) > tolerance) {
                reject("Curved free-space FFT2D5 requires a horizontal circular lab path.");
            }
        }

        // The first point, the farthest point, and the point farthest from their
        // line form a well-conditioned circumcircle without a profile-dependent fit.
        const Vector a = host(farthest) - origin;
        const Vector b = host(offLine) - origin;
        const double determinant = a[0] * b[2] - a[2] * b[0];
        const double a2 = a[0] * a[0] + a[2] * a[2];
        const double b2 = b[0] * b[0] + b[2] * b[2];
        const Vector centre(
                origin[0] + (a2 * b[2] - b2 * a[2]) / (2.0 * determinant),
                origin[1],
                origin[2] + (a[0] * b2 - b[0] * a2) / (2.0 * determinant));
        const double radius = norm(Vector(origin - centre));
        if (!std::isfinite(radius) || !(radius > 0.0)) {
            reject("Reference path has no finite circular geometry.");
        }
        Vector radial0 = (origin - centre) / radius;
        radial0[1] = 0.0;
        double totalAngle = 0.0;
        double direction  = 0.0;
        Vector previousRadial = radial0;
        for (std::size_t i = 0; i < count; ++i) {
            Vector radial = host(i) - centre;
            radial[1] = 0.0;
            const double radialLength = norm(radial);
            if (std::abs(radialLength - radius) > tolerance) {
                reject("Reference path is neither straight nor a constant-radius circle.");
            }
            radial /= radialLength;
            if (i > 0) {
                const double sine = previousRadial[0] * radial[2]
                                    - previousRadial[2] * radial[0];
                const double cosine = previousRadial.dot(radial);
                const double angle  = std::atan2(sine, cosine);
                if (direction == 0.0) direction = angle > 0.0 ? 1.0 : -1.0;
                if (!(direction * angle > 0.0) || std::abs(angle) >= std::acos(-1.0)) {
                    reject("Circular reference path must be ordered with steps smaller than pi.");
                }
                totalAngle += angle;
            }
            previousRadial = radial;
        }
        const double pi = std::acos(-1.0);
        if (!(std::abs(totalAngle) < 2.0 * pi - tolerance / radius)) {
            reject("Free-space FFT2D5 circular reference path must be shorter than one turn.");
        }
        geometry.curvature_m = direction / radius;
        geometry.length_m    = radius * std::abs(totalAngle);
        geometry.b0_m        = direction * radial0;
        geometry.t0_m        = Vector(-geometry.b0_m[2], 0.0, geometry.b0_m[0]);
        geometry.valid_m     = true;
        return geometry;
    }

    FFT2D5Geometry FFT2D5Geometry::transformed(const CoordinateSystemTrafo& transform) const {
        auto result = *this;
        if (!valid_m) return result;
        result.origin_m = transform.transformTo(origin_m);
        result.b0_m     = transform.rotateTo(b0_m);
        result.n0_m     = transform.rotateTo(n0_m);
        result.t0_m     = transform.rotateTo(t0_m);
        return result;
    }

}  // namespace opalx::spacecharge
