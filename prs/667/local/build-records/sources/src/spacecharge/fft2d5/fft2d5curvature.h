/** @file FFT2D5Curvature.h @brief Thin circular-tube transverse slice correction. */
#ifndef OPALX_FFT2D5_CURVATURE_H
#define OPALX_FFT2D5_CURVATURE_H

#include "SpaceCharge/FFT2D5/FFT2D5FieldStorage.h"

namespace opalx::spacecharge {
    /**
     * First-order transverse curvature with the full circular arc retained.
     * Two ordinary 2D Poisson solves (rho and u*rho) and one 1D line-density
     * integral replace neither the source with a fitted ellipse nor the slice
     * solver with a 3D FFT. Longitudinal fields are supplied by the caller.
     *
     * rho_grid is charge per du dy ds; physical density is rho_grid/(1+kappa*u).
     * For the 2D logarithmic reference length r0=1 metre, the transverse
     * potential is Phi0 + kappa*(Phiu-u*Phi0)/2 + kappa*k*lambda*u-u*C(s).
     * C is the finite-part circular line integral with its near singularity
     * matched analytically to that same logarithmic reference length.
     */
    class FFT2D5Curvature final {
    public:
        // Physical source and gathered-particle extent, excluding empty mesh padding.
        static constexpr double MaxTransverseRatio = 0.01;
        [[nodiscard]] static double lineSelfWeight(
                double ds, double curvature, double referenceLength = 1.0);
        [[nodiscard]] static double lineOffDiagonalWeight(
                double distance, double ds, double curvature);
        std::size_t solve(FFT2D5FieldStorage& fields, double curvature, bool closedRing);
    };
}  // namespace opalx::spacecharge
#endif
