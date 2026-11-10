// Copyright (c) 2026, Paul Scherrer Institut, Villigen PSI, Switzerland
// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef OPALX_FFT2D5_FREE_SPACE_KERNEL_H
#define OPALX_FFT2D5_FREE_SPACE_KERNEL_H

#include <Kokkos_Core.hpp>
#include <Kokkos_MathematicalFunctions.hpp>

namespace opalx::spacecharge::fft2d5_free {

/** Cell-integrated kernels for the first-order circular Frenet Coulomb potential.
 *
 * G=(x*x+y*y+xi*xi)^(-1/2), H=xi*xi*G^3, F=x*H,
 * xi=2*sin(kappa*s/2)/kappa.  G,H have units 1/length and F is dimensionless.
 * The singular flat-cell integrals are analytic.  A smooth curved-minus-flat
 * correction is integrated by Gauss quadrature.  No charge-profile assumptions
 * enter this kernel.  Source density is the coordinate density dq/(du*dy*ds).
 */
struct CellKernel {
    enum Kind { G = 0, H = 1, F = 2 };

    KOKKOS_INLINE_FUNCTION static double ratioAtan(double n, double d) {
        if (d == 0.0) {
            return n > 0.0 ? 1.57079632679489661923
                          : (n < 0.0 ? -1.57079632679489661923 : 0.0);
        }
        return Kokkos::atan(n / d);
    }

    KOKKOS_INLINE_FUNCTION static double logTerm(double coefficient, double argument) {
        return coefficient == 0.0 ? 0.0 : coefficient * Kokkos::log(argument);
    }

    KOKKOS_INLINE_FUNCTION static double volumePrimitive(double x, double y, double z) {
        const double r = Kokkos::sqrt(x * x + y * y + z * z);
        if (r == 0.0) {
            return 0.0;
        }
        return logTerm(y * z, x + r) + logTerm(x * z, y + r)
               + logTerm(x * y, z + r)
               - 0.5 * (x * x * ratioAtan(y * z, x * r)
                        + y * y * ratioAtan(x * z, y * r)
                        + z * z * ratioAtan(x * y, z * r));
    }

    // Mixed y,z primitive of 1/sqrt(a*a+y*y+z*z), with the continuous a=0 limit.
    KOKKOS_INLINE_FUNCTION static double facePrimitive(double a, double y, double z) {
        a              = Kokkos::abs(a);
        const double r = Kokkos::sqrt(a * a + y * y + z * z);
        if (r == 0.0) {
            return 0.0;
        }
        return logTerm(y, z + r) + logTerm(z, y + r)
               - (a == 0.0 ? 0.0 : a * ratioAtan(y * z, a * r));
    }

    KOKKOS_INLINE_FUNCTION static double faceG(
            double a, double y0, double y1, double z0, double z1) {
        return facePrimitive(a, y1, z1) - facePrimitive(a, y0, z1)
               - facePrimitive(a, y1, z0) + facePrimitive(a, y0, z0);
    }

    KOKKOS_INLINE_FUNCTION static double lineG(double a, double z, double y0, double y1) {
        const double b = Kokkos::sqrt(a * a + z * z);
        return Kokkos::asinh(y1 / b) - Kokkos::asinh(y0 / b);
    }

    KOKKOS_INLINE_FUNCTION static double zLineG(
            double a, double z, double y0, double y1) {
        return z == 0.0 ? 0.0 : z * lineG(a, z, y0, y1);
    }

    // Integral over a y,z face of z*z/r^3, from H=G-d_z(z*G).
    KOKKOS_INLINE_FUNCTION static double faceH(
            double a, double y0, double y1, double z0, double z1) {
        return faceG(a, y0, y1, z0, z1) - zLineG(a, z1, y0, y1)
               + zLineG(a, z0, y0, y1);
    }

    KOKKOS_INLINE_FUNCTION static double z2LinePrimitive(double a2, double z) {
        const double r = Kokkos::sqrt(a2 + z * z);
        return 0.5 * (z * r - (a2 == 0.0 ? 0.0 : a2 * Kokkos::asinh(z / Kokkos::sqrt(a2))));
    }

    // Integral over a y,z face of z*z/r.  The 2D divergence theorem gives
    // 3*W = boundary((y,z)*z*z/r) - a*a*integral(z*z/r^3).
    KOKKOS_INLINE_FUNCTION static double faceZ2G(
            double a, double y0, double y1, double z0, double z1) {
        const double a2 = a * a;
        const double by =
                y1 * (z2LinePrimitive(a2 + y1 * y1, z1)
                      - z2LinePrimitive(a2 + y1 * y1, z0))
                - y0 * (z2LinePrimitive(a2 + y0 * y0, z1)
                        - z2LinePrimitive(a2 + y0 * y0, z0));
        const double bz =
                z1 * z1 * zLineG(a, z1, y0, y1)
                - z0 * z0 * zLineG(a, z0, y0, y1);
        return (by + bz - a2 * faceH(a, y0, y1, z0, z1)) / 3.0;
    }

    KOKKOS_INLINE_FUNCTION static double flatIntegral(
            int kind, double x, double y, double z, double hx, double hy, double hz) {
        const double x0 = x - 0.5 * hx, x1 = x + 0.5 * hx;
        const double y0 = y - 0.5 * hy, y1 = y + 0.5 * hy;
        const double z0 = z - 0.5 * hz, z1 = z + 0.5 * hz;
        if (kind == F) {
            // Integrate x*z*z/r^3 first in x: its primitive is -z*z/r.
            return faceZ2G(x0, y0, y1, z0, z1) - faceZ2G(x1, y0, y1, z0, z1);
        }
        double integral = 0.0;
        for (int i = 0; i < 2; ++i) {
            for (int j = 0; j < 2; ++j) {
                for (int k = 0; k < 2; ++k) {
                    const double sign = ((i + j + k) % 2 == 0) ? -1.0 : 1.0;
                    integral += sign * volumePrimitive(
                                               i == 0 ? x0 : x1, j == 0 ? y0 : y1,
                                               k == 0 ? z0 : z1);
                }
            }
        }
        if (kind == H) {
            integral -= z1 * faceG(z1, x0, x1, y0, y1)
                        - z0 * faceG(z0, x0, x1, y0, y1);
        }
        return integral;
    }

    KOKKOS_INLINE_FUNCTION static double chord(double s, double curvature) {
        return curvature == 0.0 ? s : 2.0 * Kokkos::sin(0.5 * curvature * s) / curvature;
    }

    KOKKOS_INLINE_FUNCTION static double point(int kind, double x, double y, double z) {
        const double r2 = x * x + y * y + z * z;
        if (r2 == 0.0) {
            // Only the continuous curved-minus-flat correction calls this at 0.
            return 0.0;
        }
        const double g = 1.0 / Kokkos::sqrt(r2);
        return kind == G ? g : (kind == H ? z * z * g / r2 : x * z * z * g / r2);
    }

    KOKKOS_INLINE_FUNCTION static double average(
            int kind, double x, double y, double s, double hx, double hy, double hs,
            double curvature, double longitudinalScale = 1.0) {
        const double value = averagePositive(
                kind, Kokkos::abs(x), Kokkos::abs(y), Kokkos::abs(s), hx, hy, hs,
                curvature, longitudinalScale);
        // Corner primitives can lose different last bits on opposite faces.
        // Enforce the exact physical parity before the kernel reaches an FFT.
        return kind == F && x < 0.0 ? -value : value;
    }

    KOKKOS_INLINE_FUNCTION static double averagePositive(
            int kind, double x, double y, double s, double hx, double hy, double hs,
            double curvature, double longitudinalScale) {
        const double z  = longitudinalScale * s;
        const double hz = longitudinalScale * hs;
        const double width = Kokkos::fmax(hx, Kokkos::fmax(hy, hz));
        const double xi = chord(z, curvature);
        const double r2 = x * x + y * y + xi * xi;
        constexpr double nodes[4] = {
                -0.8611363115940525752, -0.3399810435848562648,
                0.3399810435848562648, 0.8611363115940525752};
        constexpr double weights[4] = {
                0.3478548451374538574, 0.6521451548625461426,
                0.6521451548625461426, 0.3478548451374538574};
        if (r2 >= 256.0 * width * width) {
            // Four-point integration in the long direction and exact second
            // transverse moments.  The omitted terms are O((h_transverse/r)^4),
            // below 1e-6 at this cutoff, and much smaller for a thin mesh.
            double result = 0.0;
            for (int k = 0; k < 4; ++k) {
                const double zz  = chord(z + 0.5 * hz * nodes[k], curvature);
                const double rr2 = x * x + y * y + zz * zz;
                const double g   = 1.0 / Kokkos::sqrt(rr2);
                const double g3  = g / rr2, g5 = g3 / rr2, g7 = g5 / rr2;
                double value, dxx, dyy;
                if (kind == G) {
                    value = g;
                    dxx = (3.0 * x * x - rr2) * g5;
                    dyy = (3.0 * y * y - rr2) * g5;
                } else {
                    value = zz * zz * g3;
                    dxx = zz * zz * (15.0 * x * x - 3.0 * rr2) * g7;
                    dyy = zz * zz * (15.0 * y * y - 3.0 * rr2) * g7;
                    if (kind == F) {
                        value *= x;
                        dxx = x * dxx - 6.0 * zz * zz * x * g5;
                        dyy *= x;
                    }
                }
                result += 0.5 * weights[k]
                          * (value + hx * hx * dxx / 24.0 + hy * hy * dyy / 24.0);
            }
            return result;
        }
        // Scale the analytic corner primitives before subtracting them.  The
        // far branch above prevents cancellation for distant, very thin cells.
        const double xx = x / width, yy = y / width, zz = z / width;
        const double ax = hx / width, ay = hy / width, az = hz / width;
        double value = flatIntegral(kind, xx, yy, zz, ax, ay, az) / (ax * ay * az);
        if (kind != F) {
            value /= width;
        }
        if (curvature == 0.0) {
            return value;
        }
        // The exact curved kernel minus its flat singular part is O(r/R^2)
        // (O(r^2/R^2) for F), so ordinary quadrature is well behaved even in
        // the self cell.  Two transverse and four longitudinal Gauss points.
        constexpr double node2 = 0.57735026918962576451;
        double correction = 0.0;
        for (int i = 0; i < 2; ++i) {
            for (int j = 0; j < 2; ++j) {
                const double xp = x + 0.5 * hx * (i == 0 ? -node2 : node2);
                const double yp = y + 0.5 * hy * (j == 0 ? -node2 : node2);
                for (int k = 0; k < 4; ++k) {
                    const double zp = z + 0.5 * hz * nodes[k];
                    correction += 0.125 * weights[k]
                                  * (point(kind, xp, yp, chord(zp, curvature))
                                     - point(kind, xp, yp, zp));
                }
            }
        }
        return value + correction;
    }
};

}  // namespace opalx::spacecharge::fft2d5_free
#endif
