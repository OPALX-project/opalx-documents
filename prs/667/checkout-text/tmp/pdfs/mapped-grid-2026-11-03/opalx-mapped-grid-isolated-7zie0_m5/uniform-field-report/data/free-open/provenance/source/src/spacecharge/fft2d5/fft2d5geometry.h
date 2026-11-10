/**
 * @file FFT2D5Geometry.h
 * @brief Smooth straight/circular geometry for the finite free-space FFT2D5 solve.
 */

#ifndef OPALX_SPACE_CHARGE_FFT2D5_GEOMETRY_H
#define OPALX_SPACE_CHARGE_FFT2D5_GEOMETRY_H

#include "SpaceCharge/FFT2D5/ReferencePath.h"

#include <Kokkos_Core.hpp>

class CoordinateSystemTrafo;

namespace opalx::spacecharge {

    /**
     * @brief Value geometry that may be copied into Kokkos kernels.
     *
     * fit() accepts an ordered straight line or horizontal circular arc in laboratory
     * coordinates. transformed() subsequently supports an arbitrary rigid solve-frame
     * transformation. Local coordinates are (u,y,s), with b = n cross t and
     * dt/ds = -signedCurvature()*b. Thus the metric is 1 + signedCurvature()*u.
     * The first path point is s=0 and pathLength() is the exact smooth arc length.
     * Circular arcs must be shorter than one complete turn. No general path is fitted
     * approximately or silently replaced with a circle. For a tilted straight line,
     * n is the normalized lab-y projection perpendicular to t (lab-z is used when
     * the line is parallel to lab-y).
     */
    class FFT2D5Geometry final {
    public:
        using Vector = ReferencePath::Vector;

        KOKKOS_DEFAULTED_FUNCTION FFT2D5Geometry() = default;
        KOKKOS_DEFAULTED_FUNCTION FFT2D5Geometry(const FFT2D5Geometry&) = default;
        KOKKOS_DEFAULTED_FUNCTION FFT2D5Geometry& operator=(const FFT2D5Geometry&) = default;

        [[nodiscard]] static FFT2D5Geometry fit(
                const ReferencePath::View& points, double relativeTolerance = 1.0e-9,
                double absoluteTolerance = 1.0e-11);

        [[nodiscard]] FFT2D5Geometry transformed(const CoordinateSystemTrafo& transform) const;

        [[nodiscard]] KOKKOS_INLINE_FUNCTION bool isValid() const { return valid_m; }
        [[nodiscard]] KOKKOS_INLINE_FUNCTION bool isStraight() const {
            return valid_m && curvature_m == 0.0;
        }
        [[nodiscard]] KOKKOS_INLINE_FUNCTION double signedCurvature() const {
            return curvature_m;
        }
        [[nodiscard]] KOKKOS_INLINE_FUNCTION double pathLength() const { return length_m; }
        [[nodiscard]] KOKKOS_INLINE_FUNCTION double metric(double u) const {
            return 1.0 + curvature_m * u;
        }

        /** @brief Smooth orthonormal frame at s; valid also outside the path endpoints. */
        KOKKOS_INLINE_FUNCTION void basis(double s, Vector& b, Vector& n, Vector& t) const {
            const double angle = curvature_m * s;
            const double cs    = Kokkos::cos(angle);
            const double sn    = Kokkos::sin(angle);
            b                  = cs * b0_m + sn * t0_m;
            n                  = n0_m;
            t                  = cs * t0_m - sn * b0_m;
        }

        /** @brief Map local (u,y,s) to Cartesian position. Requires metric(u)>0. */
        [[nodiscard]] KOKKOS_INLINE_FUNCTION Vector position(const Vector& local) const {
            const double u = local[0];
            const double s = local[2];
            if (curvature_m == 0.0) {
                return origin_m + u * b0_m + local[1] * n0_m + s * t0_m;
            }
            const double angle = curvature_m * s;
            const double sn    = Kokkos::sin(angle);
            const double cs    = Kokkos::cos(angle);
            const double sh    = Kokkos::sin(0.5 * angle);
            // -2 sin²(angle/2) avoids cancellation of cos(angle)-1 in shallow arcs.
            const double alongB = -2.0 * sh * sh / curvature_m + u * cs;
            const double alongT = sn / curvature_m + u * sn;
            return origin_m + alongB * b0_m + local[1] * n0_m + alongT * t0_m;
        }

        /**
         * @brief Map a Cartesian point to (u,y,s) without clamping to endpoints.
         *
         * Circular angles are unwrapped around the arc midpoint, placing the branch
         * cut outside the fitted arc even when it spans more than pi radians. The
         * mapping is unique on the regular tube (metric(u)>0); it is undefined at
         * the circle centre. Coordinates slightly before/after the endpoints are
         * retained so the caller can reject uncovered source charge.
         */
        [[nodiscard]] KOKKOS_INLINE_FUNCTION Vector toFrenet(const Vector& point) const {
            const Vector delta = point - origin_m;
            const double xb    = delta.dot(b0_m);
            const double yt    = delta.dot(n0_m);
            const double zt    = delta.dot(t0_m);
            if (curvature_m == 0.0) return Vector(xb, yt, zt);

            const double qb = 1.0 + curvature_m * xb;
            const double qt = curvature_m * zt;
            const double rm = Kokkos::sqrt(qb * qb + qt * qt);
            const double am = 0.5 * curvature_m * length_m;
            const double cm = Kokkos::cos(am);
            const double sm = Kokkos::sin(am);
            const double da = Kokkos::atan2(qt * cm - qb * sm, qb * cm + qt * sm);
            // Rationalized (rm-1)/curvature avoids subtracting nearly equal values.
            const double u = (2.0 * xb + curvature_m * (xb * xb + zt * zt)) / (rm + 1.0);
            return Vector(u, yt, 0.5 * length_m + da / curvature_m);
        }

        [[nodiscard]] KOKKOS_INLINE_FUNCTION Vector toLocalVector(
                const Vector& vector, double s) const {
            Vector b, n, t;
            basis(s, b, n, t);
            return Vector(vector.dot(b), vector.dot(n), vector.dot(t));
        }

        [[nodiscard]] KOKKOS_INLINE_FUNCTION Vector toGlobalVector(
                const Vector& vector, double s) const {
            Vector b, n, t;
            basis(s, b, n, t);
            return vector[0] * b + vector[1] * n + vector[2] * t;
        }

    private:
        bool valid_m       = false;
        double curvature_m = 0.0;
        double length_m    = 0.0;
        Vector origin_m;
        Vector b0_m;
        Vector n0_m;
        Vector t0_m;
    };

}  // namespace opalx::spacecharge

#endif  // OPALX_SPACE_CHARGE_FFT2D5_GEOMETRY_H
