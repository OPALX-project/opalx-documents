// Copyright (c) 2026, Paul Scherrer Institut, Villigen PSI, Switzerland
// SPDX-License-Identifier: GPL-3.0-or-later
#ifndef OPALX_FFT2D5_FREE_SPACE_H
#define OPALX_FFT2D5_FREE_SPACE_H

#include "SpaceCharge/FFT2D5/FFT2D5FieldStorage.h"

#include <array>
#include <cstddef>
#include <memory>

namespace opalx::spacecharge {

/** Nonlocal finite-source Coulomb solve on the existing thin Frenet mesh.
 *
 * The reference is straight or circular with constant signed curvature, with
 * u directed toward increasing radius when curvature is positive.  The full
 * longitudinal chord is retained, while the transverse metric is expanded to
 * first order in curvature*u.  This implementation requires |curvature*u|<=0.01
 * throughout the mesh and target halo.  All three fields derive from one potential.
 * This is an electrostatic operator; the caller controls the frame in which
 * the density and path are supplied and the validity of curved moving beams.
 *
 * The input is coordinate density dq/(du*dy*ds), including any Frenet
 * Jacobian already represented by particle deposition.  No extra Jacobian is
 * applied.  gamma stretches the straight source coordinate and transforms its
 * electric field back to the lab; curved solves require gamma=1.
 *
 * Existing FFT2D5 is single rank.  Workspace is one padded real field, two
 * half-complex fields, and one unpadded potential, independent of kernel count.
 */
class FFT2D5FreeSpace final {
public:
    using Storage      = FFT2D5FieldStorage;
    using ScalarField3 = Storage::ScalarField3;
    using VectorField3 = Storage::VectorField3;
    using Mesh3        = Storage::Mesh3;
    using Layout3      = Storage::Layout3;
    using Vector3      = Storage::Vector3;
    using FFT          = ippl::FFT<ippl::RCTransform, ScalarField3>;
    using ComplexField = FFT::ComplexField;
    using PotentialView = ScalarField3::view_type;

    FFT2D5FreeSpace();
    ~FFT2D5FreeSpace();
    FFT2D5FreeSpace(const FFT2D5FreeSpace&) = delete;
    FFT2D5FreeSpace& operator=(const FFT2D5FreeSpace&) = delete;

    /// Returns zero for an empty source and one for a completed physical solve.
    std::size_t solve(
            ScalarField3& rho, VectorField3& electricField, double signedCurvature,
            double gamma = 1.0);

private:
    void initialise(const ScalarField3& rho);
    void convolve(int kind, double curvature, double gamma);
    void extractPotential(int kind, double curvature);
    void determineField(VectorField3& electricField, double curvature, double gamma);

    std::array<std::size_t, 3> size_m{};
    std::array<std::size_t, 3> paddedSize_m{};
    Vector3 spacing_m{};
    Vector3 origin_m{};
    ippl::NDIndex<3> realDomain_m;
    ippl::NDIndex<3> complexDomain_m;
    Mesh3 realMesh_m;
    Mesh3 complexMesh_m;
    Layout3 realLayout_m;
    Layout3 complexLayout_m;
    ScalarField3 real_m;
    ComplexField rhoSpectrum_m;
    ComplexField workSpectrum_m;
    PotentialView potential_m;
    std::unique_ptr<FFT> fft_m;
    ippl::ParameterList parameters_m;
};

}  // namespace opalx::spacecharge
#endif
