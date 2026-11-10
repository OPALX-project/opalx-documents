from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');s=p.read_text().replace('        void preparePathGeometryAndProjections(const SpaceChargeSolveContext& context);','''        void preparePathGeometryAndProjections(const SpaceChargeSolveContext& context);

        /** @brief Reuse OPEN spatial migration with logical (u,v,s) ownership.
         * Cartesian positions are saved in a registered particle attribute so IPPL
         * migrates them, IDs, momenta and charges together. R is temporarily replaced
         * by the prepared path projection, then restored exactly before any physics
         * operation. Invalid particles remain invalid. All active ranks participate,
         * including ranks with no local particles. Projection caches are rebuilt after
         * migration because local particle order and count may change.
         * @pre Particles and path are in the common solve frame; projections are current.
         * @post Tracking coordinates are Cartesian, and each particle belongs to its s slab.
         */
        void migrateToSlabs(const SpaceChargeSolveContext& context);
        /// Exchange slab halos while preserving open transverse boundaries.
        void accumulateDensityHalos();
        void fillFieldHalos();''');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text();a=s.index('    void FFT2D5Algorithm::preparePathGeometryAndProjections');s=s[:a]+'''    void FFT2D5Algorithm::migrateToSlabs(const SpaceChargeSolveContext& context) {
        const auto origin = fieldStorage_m->origin();
        const auto size = fieldStorage_m->size();
        const auto length = referencePath_m->length();
        for (size_t c = 0; c < particles_m.size(); ++c) {
            if (!context.trackingActive()[c]) continue;
            auto& pc = *particles_m[c];
            const auto projected = projectedPositions_m[c];
            const auto invalid = pc.InvalidMask.getView();
            size_t outside = 0;
            Kokkos::parallel_reduce("FFT2D5::checkMigrationDomain", pc.getLocalNum(),
                KOKKOS_LAMBDA(size_t i, size_t& count) {
                    if (!invalid(i) && (projected(i)[0] < origin[0] || projected(i)[0] >= origin[0]+size[0]
                        || projected(i)[1] < origin[1] || projected(i)[1] >= origin[1]+size[1])) ++count;
                }, outside);
            ippl::Comm->allreduce(outside, outside, 1, std::plus<size_t>());
            if (outside) throw OpalException("FFT2D5Algorithm::migrateToSlabs",
                "Particle outside transverse FFT2D5 domain; enlarge PIPESIZEX/PIPESIZEY.");
            auto saved = pc.migrationPositions().getView();
            auto r = pc.R.getView();
            Kokkos::parallel_for("FFT2D5::saveCartesianPositions", pc.getLocalNum(),
                KOKKOS_LAMBDA(size_t i) {
                    saved(i) = r(i);
                    auto q = invalid(i) ? Vector3D_t(0.) : projected(i);
                    q[2] = q[2] >= length ? 0. : q[2];
                    r(i) = q;
                });
            Kokkos::fence();
            pc.updateLayout(fieldStorage_m->layout(), fieldStorage_m->mesh());
            const auto restore = [&] {
                const auto positions = pc.R.getView();
                const auto cartesian = pc.migrationPositions().getView();
                Kokkos::parallel_for("FFT2D5::restoreCartesianPositions", pc.getLocalNum(),
                    KOKKOS_LAMBDA(size_t i) { positions(i) = cartesian(i); });
                Kokkos::fence();
                pc.markMomentsDirty();
            };
            try { pc.update(); } catch (...) { restore(); throw; }
            restore();
        }
        preparePathGeometryAndProjections(context);
    }

    void FFT2D5Algorithm::accumulateDensityHalos() {
        auto& rho = fieldStorage_m->chargeDensity();
        auto view = rho.getView();
        const int nx = fieldStorage_m->meshSize()[0], ny = fieldStorage_m->meshSize()[1];
        // OPEN transverse boundaries: do not wrap transverse CIC spill when the
        // longitudinal layout is periodic. Only z ghosts enter halo accumulation.
        Kokkos::parallel_for("FFT2D5::clearTransverseSourceHalo",
            Kokkos::MDRangePolicy<Kokkos::Rank<3>>({0,0,0}, {view.extent(0),view.extent(1),view.extent(2)}),
            KOKKOS_LAMBDA(size_t i,size_t j,size_t k) {
                if (i == 0 || j == 0 || i > size_t(nx) || j > size_t(ny)) view(i,j,k)=0.;
            });
        Kokkos::fence();
        rho.accumulateHalo();
    }

    void FFT2D5Algorithm::fillFieldHalos() {
        auto& field = fieldStorage_m->electricField();
        field.fillHalo();
        auto view = field.getView();
        const int nx = fieldStorage_m->meshSize()[0], ny = fieldStorage_m->meshSize()[1];
        Kokkos::parallel_for("FFT2D5::clearTransverseFieldHalo",
            Kokkos::MDRangePolicy<Kokkos::Rank<3>>({0,0,0}, {view.extent(0),view.extent(1),view.extent(2)}),
            KOKKOS_LAMBDA(size_t i,size_t j,size_t k) {
                if (i == 0 || j == 0 || i > size_t(nx) || j > size_t(ny)) view(i,j,k)=Vector3D_t(0.);
            });
        Kokkos::fence();
    }

'''+s[a:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp');s=p.read_text().replace('        preparePathGeometryAndProjections(context);\n        scatterToGrid','        preparePathGeometryAndProjections(context);\n        if (ippl::Comm->size() > 1) migrateToSlabs(context);\n        scatterToGrid',1).replace('                    if (outside != 0) {','                    ippl::Comm->allreduce(outside, outside, 1, std::plus<size_t>());\n                    if (outside != 0) {',1).replace('            if (config_m.closedRing) {\n                constexpr auto firstRealZ','            if (ippl::Comm->size() > 1) {\n                accumulateDensityHalos();\n            } else if (config_m.closedRing) {\n                constexpr auto firstRealZ',1)
a=s.index('            // Calculate the total charge density for each z slice');b=s.index('            // Set the ghost cells',a);s=s[:a]+'''            Kokkos::deep_copy(hostLineDensity, 0.);
            const auto localDomain = fieldStorage_m->layout().getLocalNDIndex();
            for (size_t k = 0; k < size_t(localDomain[2].length()); ++k) {
                T sum{};
                Kokkos::parallel_reduce(
                        Policy2D_t({1, 1}, {rho3d.extent(0)-1, rho3d.extent(1)-1}),
                        fft2d5_detail::SliceDensitySumFunctor{rho3d, k + LineDensityFirstRealCell}, sum);
                hostLineDensity(k + localDomain[2].first() + LineDensityFirstRealCell) = sum;
            }
            // Only the small 1D profile is replicated; no 3D field all-reduction.
            if (ippl::Comm->size() > 1)
                ippl::Comm->allreduce(hostLineDensity.data(), numSlices + LineDensityGhostCells, std::plus<T>());
'''+s[b:]
s=s.replace('        const auto numSlices = fieldStorage_m->meshSize()[2];\n        fieldStorage_m->resetBackendSolves();','        const auto numSlices = fieldStorage_m->layout().getLocalNDIndex()[2].length();\n        fieldStorage_m->resetBackendSolves();',1).replace('        ippl::Comm->allreduce(occupiedHost.data(), numSlices, std::greater<int>());','        // Each rank independently solves only its owned planes.',1)
s=s.replace('        if constexpr (std::is_same_v<DiagnosticPolicy, NullDiagnostic>) {','        if constexpr (std::is_same_v<DiagnosticPolicy, NullDiagnostic>) {',1)
# Non-null diagnostics retain serial path only on one rank; avoid world FFT collectives.
s=s.replace('        // Diagnostic policies retain the serial path', '''        if (ippl::Comm->size() > 1 && !batched) {
            std::vector<size_t> occupied;
            for (size_t z = 0; z < size_t(numSlices); ++z)
                if (occupiedHost(z)) occupied.push_back(z);
            fieldStorage_m->solveBatchedSlices(occupied);
            batched = true;
        }
        // Diagnostic policies retain the serial path''',1)
s=s.replace('        if (config_m.closedRing) {\n            Kokkos::parallel_for(\n                    "Solve2d5::solvePoissons::ghostClosed",','        if (ippl::Comm->size() > 1) {\n            fillFieldHalos();\n        } else if (config_m.closedRing) {\n            Kokkos::parallel_for(\n                    "Solve2d5::solvePoissons::ghostClosed",',1);p.write_text(s)
