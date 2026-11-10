from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text();a=s.index('    void FFT2D5Algorithm::migrateToSlabs(');b=s.index('    void FFT2D5Algorithm::accumulateDensityHalos()',a);old=s[a:b]
check=old[old.index('                size_t outside'):old.index('                auto saved =')]
save=old[old.index('                auto saved ='):old.index('                pc.updateLayout')]
restore=old[old.index('                    const auto positions ='):old.index('                };',old.index('                    const auto positions ='))]
new='''    void FFT2D5Algorithm::migrateToSlabs(const SpaceChargeSolveContext& context) {
        fft2d5_detail::timed("2D5 Migration", [&] {
            for (size_t c = 0; c < particles_m.size(); ++c)
                if (context.trackingActive()[c]) migrateContainer(c);
            preparePathGeometryAndProjections(context, false);
        });
    }

    void FFT2D5Algorithm::checkMigrationDomain(size_t container) {
        const auto origin = fieldStorage_m->origin(), size = fieldStorage_m->size();
        const auto projected = projectedPositions_m[container];
        const auto invalid = particles_m[container]->InvalidMask.getView();
        auto& pc = *particles_m[container];
'''+check+'''    }

    void FFT2D5Algorithm::saveMigrationPositions(size_t container) {
        auto& pc = *particles_m[container];
        const auto projected = projectedPositions_m[container];
        const auto invalid = pc.InvalidMask.getView();
        const auto length = referencePath_m->length();
        const auto closed = config_m.closedRing;
'''+save+'''    }

    void FFT2D5Algorithm::restoreMigrationPositions(ParticleContainer& pc) {
'''+restore+'''    }

    void FFT2D5Algorithm::migrateContainer(size_t container) {
        checkMigrationDomain(container);
        auto& pc = *particles_m[container];
        saveMigrationPositions(container);
        pc.updateLayout(fieldStorage_m->layout(), fieldStorage_m->mesh());
        // Disable spatial periodic remapping of the already-bounded logical coordinates.
        const auto particleBC = pc.getPL().getParticleBC();
        pc.setParticleBC(ippl::BC::NO);
        try {
            pc.update();
        } catch (...) {
            pc.setParticleBC(particleBC);
            restoreMigrationPositions(pc);
            throw;
        }
        pc.setParticleBC(particleBC);
        restoreMigrationPositions(pc);
    }

''';s=s[:a]+new+s[b:]
# Factor both frame loops without changing exception handling or moment refreshes.
a=s.index('            for (std::size_t index = 0; index < particles_m.size(); ++index) {');b=s.index('            try {',a)
loops=s[a:b];restore_start=loops.index('                for (std::size_t index',loops.index('const auto restoreFrames'))
restorebody=loops[restore_start:loops.rfind('            };')]
enterbody=loops[:loops.index('            const auto restoreFrames')]
s=s[:a]+'''            enterParticleSolveFrames(context, labToSolve);
'''+s[b:];s=s.replace('                restoreFrames();','                restoreParticleSolveFrames(context, labToSolve);',1).replace('            restoreFrames();','            restoreParticleSolveFrames(context, labToSolve);',1)
pos=s.index('    void FFT2D5Algorithm::migrateToSlabs(')
helpers='''    void FFT2D5Algorithm::enterParticleSolveFrames(
            const SpaceChargeSolveContext& context, const CoordinateSystemTrafo& labToSolve) {
'''+enterbody+'''    }

    void FFT2D5Algorithm::restoreParticleSolveFrames(
            const SpaceChargeSolveContext& context, const CoordinateSystemTrafo& labToSolve) {
'''+restorebody+'''    }

''';s=s[:pos]+helpers+s[pos:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');s=p.read_text();pos=s.index('    private:\n');decl='''        /** @internal @brief Clear self fields and enter the common solve frame for active containers.
         * @param context Activity flags. @param labToSolve Current laboratory-to-solve transform. */
        void enterParticleSolveFrames(const SpaceChargeSolveContext& context,
                                      const CoordinateSystemTrafo& labToSolve);
        /** @internal @brief Restore tracker frames and their moments, also after solver exceptions.
         * @param context Activity flags. @param labToSolve Transform used for entry. */
        void restoreParticleSolveFrames(const SpaceChargeSolveContext& context,
                                        const CoordinateSystemTrafo& labToSolve);
        /** @internal @brief Reject transverse ownership outside the fixed open FFT domain.
         * @param container Active container index. All ranks participate in the error reduction. */
        void checkMigrationDomain(size_t container);
        /** @internal @brief Save registered Cartesian coordinates and expose logical slab coordinates.
         * @param container Active container with current projections; particle attributes migrate together. */
        void saveMigrationPositions(size_t container);
        /** @internal @brief Restore Cartesian coordinates from the migrated registered attribute.
         * @param pc Container on its current ownership; invalidates its moment cache. */
        void restoreMigrationPositions(ParticleContainer& pc);
        /** @internal @brief Migrate one container through OPEN spatial infrastructure and restore its BC.
         * @param container Active container index. Restoration also runs if particle migration throws. */
        void migrateContainer(size_t container);

''';s=s[:pos]+decl+s[pos:];p.write_text(s)
