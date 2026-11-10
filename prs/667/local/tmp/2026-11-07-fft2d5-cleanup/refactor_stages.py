from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp');s=p.read_text()
# Scatter: orchestrate containers, validate coverage, deposit, then normalize and fold halos.
a=s.index('    template <typename DiagnosticPolicy>\n    void FFT2D5Algorithm::scatterToGrid(');b=s.index('    // This is a Kokkos kernel that deposits',a);old=s[a:b]
container=old[old.index('                    auto* pc = particles_m[container];'):old.index('                // Handle the closed ring')];container=container[:container.rfind('                }')]
v0=container.index('                    pc->updateMoments();');v1=container.index('                    pc->scaleDtByCharge();');validation=container[v0:v1]
container=container[:v0]+'                    validateDepositionContainer(container, usePreparedProjections);\n'+container[v1:]
finish=old[old.index('                // Handle the closed ring'):old.index('                diagnostic.scatterChargeDensity(rhoView);')+len('                diagnostic.scatterChargeDensity(rhoView);')]
new='''    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::scatterToGrid(const SpaceChargeSolveContext& context,
            DiagnosticPolicy diagnostic, bool usePreparedProjections) {
        fft2d5_detail::timed("2D5 Scatter", [&] {
            if (solveReferencePath_m.extent(0) < 2) return;
            Kokkos::deep_copy(fieldStorage_m->chargeDensity().getView(), 0.);
            for (size_t c = 0; c < particles_m.size(); ++c)
                if (context.trackingActive()[c]) scatterContainer(c, diagnostic, usePreparedProjections);
            finishChargeDeposition(context, diagnostic);
        });
    }

    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::scatterContainer(size_t container, DiagnosticPolicy diagnostic,
                                          bool usePreparedProjections) {
        const auto ref = solveReferencePath_m;
        const auto invDr = 1.0 / fieldStorage_m->spacing();
        const int nGhost = fieldStorage_m->chargeDensity().getNghost();
        const auto lDom = fieldStorage_m->chargeDensity().getLayout().getLocalNDIndex();
        const auto rhoView = fieldStorage_m->chargeDensity().getView();
        const auto origin = fieldStorage_m->origin();
'''+container+'''    }

    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::finishChargeDeposition(const SpaceChargeSolveContext& context,
                                                DiagnosticPolicy diagnostic) {
        using Policy2D_t = Kokkos::MDRangePolicy<Kokkos::Rank<2>>;
        using Policy3D_t = Kokkos::MDRangePolicy<Kokkos::Rank<3>>;
        const auto rhoView = fieldStorage_m->chargeDensity().getView();
'''+finish+'''    }

'''
s=s[:a]+new+s[b:]
# Store non-policy coverage validation out of line; no diagnostics/state mutation is hidden.
validation_setup='''        auto* pc = particles_m[container];
        const auto ref = solveReferencePath_m;
        const auto geometry = usePreparedProjections ? segmentGeometry_m : SegmentGeometryView_t();
        const auto projectedR = usePreparedProjections ? projectedPositions_m[container] : VectorView_t();
        const auto projectedSegment = usePreparedProjections ? projectedSegments_m[container] : SegmentIndexView_t();
'''
cpp=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');c=cpp.read_text();pos=c.rfind('}  // namespace opalx::spacecharge');c=c[:pos]+'''    void FFT2D5Algorithm::validateDepositionContainer(size_t container, bool usePreparedProjections) {
'''+validation_setup+validation+'''    }

'''+c[pos:];cpp.write_text(c)
# Line density: retain the ordered host profile assembly separately from area scaling/gradient.
a=s.index('    template <typename DiagnosticPolicy>\n    void FFT2D5Algorithm::calculateLineDensity(');b=s.index('    template <typename DiagnosticPolicy>\n    void FFT2D5Algorithm::solvePoissons(',a);old=s[a:b]
profile=old[old.index('                const auto rho3d'):old.index('                diagnostic.totalDensity(lineDensity_m);')]
scale=old[old.index('                // Convert this to line density'):old.index('            } else {')]
empty=old[old.index('                Kokkos::deep_copy(lineDensity_m, 0);'):old.rfind('            }')]
new='''    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::calculateLineDensity(DiagnosticPolicy diagnostic) {
        fft2d5_detail::timed("2D5 Line density", [&] {
            if (config_m.longitudinalFieldMode == LongitudinalFieldMode::None) {
'''+empty+'''                return;
            }
            sumLineDensityProfile();
            diagnostic.totalDensity(lineDensity_m);
            scaleLineDensityAndGradient(diagnostic);
        });
    }

    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::scaleLineDensityAndGradient(DiagnosticPolicy diagnostic) {
        const auto deviceLineDensity = lineDensity_m;
        const auto numSlices = fieldStorage_m->meshSize()[2];
'''+scale+'''    }

''';s=s[:a]+new+s[b:]
c=cpp.read_text();pos=c.rfind('}  // namespace opalx::spacecharge');c=c[:pos]+'''    void FFT2D5Algorithm::sumLineDensityProfile() {
'''+profile+'''    }

'''+c[pos:];cpp.write_text(c)
# Poisson: choose native or diagnostic serial/batched path, then set boundary ghosts.
a=s.index('    template <typename DiagnosticPolicy>\n    void FFT2D5Algorithm::solvePoissons(');b=s.index('    template <typename DiagnosticPolicy>\n    void FFT2D5Algorithm::gatherFromGrid(',a);old=s[a:b]
serial=old[old.index('                const auto& s = fieldStorage_m->workspace();'):old.index('            // Set the ghost slices')];serial=serial[:serial.rfind('            }')]
ghosts=old[old.index('            // Set the ghost slices'):old.index('            diagnostic.eField(e3d);')]
new='''    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::solvePoissons(DiagnosticPolicy diagnostic) {
        fft2d5_detail::timed("2D5 Poisson", [&] {
            using Policy = Kokkos::MDRangePolicy<Kokkos::Rank<2>>;
            auto e3d = fieldStorage_m->electricField().getView();
            const auto rho3d = fieldStorage_m->chargeDensity().getView();
            const auto nGhost = fieldStorage_m->electricField().getNghost();
            const auto numSlices = fieldStorage_m->layout().getLocalNDIndex()[2].length();
            fieldStorage_m->resetBackendSolves();
            Kokkos::deep_copy(e3d, Vector3D_t(0.));
            Kokkos::View<int*> occupiedSlices("FFT2D5OccupiedSlices", numSlices);
            Kokkos::deep_copy(occupiedSlices, 0);
            Kokkos::parallel_for("Solve2d5::solvePoissons::occupancy",
                    Policy({0, 0}, {numSlices, rho3d.extent(0)}),
                    fft2d5_detail::OccupiedSlicesFunctor{rho3d, occupiedSlices, nGhost});
            auto occupiedHost = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), occupiedSlices);
            bool batched = false;
            if constexpr (std::is_same_v<DiagnosticPolicy, NullDiagnostic>) {
                if (fieldStorage_m->batchSize() > 0) {
                    std::vector<size_t> occupied;
                    for (size_t z = 0; z < size_t(numSlices); ++z)
                        if (occupiedHost(z)) occupied.push_back(z);
                    fieldStorage_m->solveBatchedSlices(occupied);
                    batched = true;
                }
            }
            if (!batched && ippl::Comm->size() > 1) {
                solveDiagnosticSlabs(occupiedHost, diagnostic);
                batched = true;
            }
            if (!batched) solveSerialSlices(occupiedHost, diagnostic);
            setTransverseFieldGhosts();
            diagnostic.eField(e3d);
        });
    }

    template <typename OccupiedView, typename DiagnosticPolicy>
    void FFT2D5Algorithm::solveDiagnosticSlabs(OccupiedView occupiedHost, DiagnosticPolicy diagnostic) {
        const auto nGhost = fieldStorage_m->electricField().getNghost();
        const auto numSlices = fieldStorage_m->layout().getLocalNDIndex()[2].length();
        std::vector<size_t> occupied;
        for (size_t z = 0; z < size_t(numSlices); ++z)
            if (occupiedHost(z)) occupied.push_back(z);
        FFT2D5FieldStorage::ScalarField3 potential(fieldStorage_m->mesh(), fieldStorage_m->layout());
        fieldStorage_m->solveBatchedSlices(occupied, &potential);
        const auto phi = potential.getView();
        const auto first = fieldStorage_m->layout().getLocalNDIndex()[2].first();
        for (size_t z = 0; z < size_t(numSlices); ++z) {
            const auto slice = Kokkos::subview(phi, Kokkos::ALL(), Kokkos::ALL(), z + nGhost);
            diagnostic.potential(slice, z + first + nGhost);
        }
    }

    template <typename OccupiedView, typename DiagnosticPolicy>
    void FFT2D5Algorithm::solveSerialSlices(OccupiedView occupiedHost, DiagnosticPolicy diagnostic) {
        using Policy = Kokkos::MDRangePolicy<Kokkos::Rank<2>>;
        auto e3d = fieldStorage_m->electricField().getView();
        const auto rho3d = fieldStorage_m->chargeDensity().getView();
        const auto nGhost = fieldStorage_m->electricField().getNghost();
        const auto numSlices = fieldStorage_m->layout().getLocalNDIndex()[2].length();
'''+serial+'''    }

''';s=s[:a]+new+s[b:]
c=cpp.read_text();pos=c.rfind('}  // namespace opalx::spacecharge');c=c[:pos]+'''    void FFT2D5Algorithm::setTransverseFieldGhosts() {
        using Policy = Kokkos::MDRangePolicy<Kokkos::Rank<2>>;
        auto e3d = fieldStorage_m->electricField().getView();
'''+ghosts+'''    }

'''+c[pos:];cpp.write_text(c)
# Gather: one bool-specialized launcher removes duplicate 20-field functor construction.
a=s.index('    template <typename DiagnosticPolicy>\n    void FFT2D5Algorithm::gatherFromGrid(');b=s.index('    template <bool ScatterLongitudinally, typename DiagnosticPolicy>\n    KOKKOS_FUNCTION void FFT2D5Algorithm::doGatherFromGrid(',a);old=s[a:b]
setup=old[old.index('                    auto* pc = particles_m[container];'):old.index('                    const auto pipeRadius =')]
# Original spelling may use `T g;`; find the first pipeRadius then include through coupling.
start=old.index('                    T g') if '                    T g' in old else old.index('                    double g')
g=old[start:old.index('                    if (config_m.scatterLongitudinally)',start)]
arg_start=old.index('                                        r,',old.index('fft2d5_detail::GatherFromGridFunctor<'))
arg_end=old.index('                                        diagnostic});',arg_start)+len('                                        diagnostic')
args=old[arg_start:arg_end]
new='''    template <typename DiagnosticPolicy>
    void FFT2D5Algorithm::gatherFromGrid(const SpaceChargeSolveContext& context,
            DiagnosticPolicy diagnostic, bool usePreparedProjections) {
        fft2d5_detail::timed("2D5 Gather", [&] {
            if (solveReferencePath_m.extent(0) < 2) return;
            for (size_t c = 0; c < particles_m.size(); ++c) {
                if (!context.trackingActive()[c]) continue;
                if (config_m.scatterLongitudinally)
                    gatherContainer<true>(c, diagnostic, usePreparedProjections);
                else gatherContainer<false>(c, diagnostic, usePreparedProjections);
            }
        });
    }

    template <bool ScatterLongitudinally, typename DiagnosticPolicy>
    void FFT2D5Algorithm::gatherContainer(size_t container, DiagnosticPolicy diagnostic,
                                         bool usePreparedProjections) {
'''+setup+'''        const T gBy4PiEpsilon0 = longitudinalCoupling();
        const auto kernel = fft2d5_detail::GatherFromGridFunctor<
                ScatterLongitudinally, DiagnosticPolicy, decltype(invDr)>{
'''+args+'''};
        Kokkos::parallel_for("Solver2d5::GatherFromGrid", pc->getLocalNum(), kernel);
        Kokkos::fence();
    }

''';s=s[:a]+new+s[b:]
# Move constant longitudinal geometry calculation without changing operation order.
g=g.replace('                    const T gBy4PiEpsilon0 = g / (4 * Physics::pi * Physics::epsilon_0);','                    return g / (4 * Physics::pi * Physics::epsilon_0);')
c=cpp.read_text();pos=c.rfind('}  // namespace opalx::spacecharge');c=c[:pos]+'''    FFT2D5Algorithm::T FFT2D5Algorithm::longitudinalCoupling() const {
        const auto pipeRadius = std::min(fieldStorage_m->size()[0], fieldStorage_m->size()[1]);
'''+g+'''    }

'''+c[pos:];cpp.write_text(c)
p.write_text(s)
# Document each new substage at its declaration.
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');s=p.read_text();pos=s.index('    private:\n');decl='''        /** @internal @brief Refresh moments, check charge and validate open-path coverage before deposition.
         * @param container Active source index. @param usePreparedProjections Use the per-solve caches. */
        void validateDepositionContainer(size_t container, bool usePreparedProjections);
        /** @internal @brief Deposit one container and restore its charge-scaled time steps.
         * @tparam DiagnosticPolicy Stage observer. @param container Active source index.
         * @param diagnostic Observer. @param usePreparedProjections Use current projection caches. */
        template <typename DiagnosticPolicy>
        void scatterContainer(size_t container, DiagnosticPolicy diagnostic, bool usePreparedProjections);
        /** @internal @brief Fold serial periodic ghosts, scale charge and accumulate MPI source halos.
         * @tparam DiagnosticPolicy Stage observer. @param context Current dt/activity.
         * @param diagnostic Receives normalized density after pre-halo line-density assembly. */
        template <typename DiagnosticPolicy>
        void finishChargeDeposition(const SpaceChargeSolveContext& context, DiagnosticPolicy diagnostic);
        /** @internal @brief Sum transverse planes and assemble the replicated ordered 1D profile.
         * Source ghosts stay separate until host accumulation; boundary ghosts are filled before return. */
        void sumLineDensityProfile();
        /** @internal @brief Convert raw plane sums to line charge and centered longitudinal differences.
         * @tparam DiagnosticPolicy Observer. @param diagnostic Receives area-scaled density and gradient. */
        template <typename DiagnosticPolicy>
        void scaleLineDensityAndGradient(DiagnosticPolicy diagnostic);
        /** @internal @brief Run MPI-local batches while exposing each slice potential to diagnostics.
         * @tparam OccupiedView Host mask type. @tparam DiagnosticPolicy Observer.
         * @param occupiedHost Mask of nonzero local planes. @param diagnostic Potential observer. */
        template <typename OccupiedView, typename DiagnosticPolicy>
        void solveDiagnosticSlabs(OccupiedView occupiedHost, DiagnosticPolicy diagnostic);
        /** @internal @brief Solve occupied one-rank slices with a shared serial workspace.
         * @tparam OccupiedView Host mask type. @tparam DiagnosticPolicy Observer.
         * @param occupiedHost Nonzero source mask; neutral nonzero sources remain active.
         * @param diagnostic Receives potentials including empty planes and halos. */
        template <typename OccupiedView, typename DiagnosticPolicy>
        void solveSerialSlices(OccupiedView occupiedHost, DiagnosticPolicy diagnostic);
        /** @internal @brief Fill z field ghosts and retain open transverse boundaries. */
        void setTransverseFieldGhosts();
        /** @internal @brief Return the unchanged local longitudinal closure coefficient.
         * @return Geometry factor divided by 4*pi*epsilon0; OPEN uses its fixed model constant. */
        T longitudinalCoupling() const;
        /** @internal @brief Gather one active container with the selected z interpolation.
         * @tparam ScatterLongitudinally Select linear z interpolation. @tparam DiagnosticPolicy Observer.
         * @param container Source index. @param diagnostic Field observer.
         * @param usePreparedProjections Use current per-solve path caches. */
        template <bool ScatterLongitudinally, typename DiagnosticPolicy>
        void gatherContainer(size_t container, DiagnosticPolicy diagnostic, bool usePreparedProjections);

''';s=s[:pos]+decl+s[pos:];p.write_text(s)
