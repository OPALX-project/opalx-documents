from pathlib import Path
p=Path('src/SpaceCharge/SpaceChargeConfig.cpp');s=p.read_text();a=s.index('            if (std::any_of(',s.index('void validateFFT2D5'));b=s.index('            if (!std::isfinite',a);s=s[:a]+'''            if (config.grid.decomposition[0] || config.grid.decomposition[1]) {
                throw OpalException("validateSpaceChargeConfig",
                                    "FFT2D5 supports only longitudinal decomposition (PARFFTZ).");
            }
'''+s[b:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp');s=p.read_text().replace('std::array<bool, 3>{false, false, false}, true','config.grid.decomposition, config.closedRing').replace('sliceLayout_m(MPI_COMM_WORLD','sliceLayout_m(MPI_COMM_SELF').replace('batchSize_m = Options::fft2d5BatchSize;','batchSize_m = Options::fft2d5BatchSize;\n        if (ippl::Comm->size() > 1 && batchSize_m == 0) batchSize_m = 1;').replace('workspace_m.solver2->initialiseViews(*workspace_m.chargeDensity);','if (ippl::Comm->size() == 1)\n            workspace_m.solver2->initialiseViews(*workspace_m.chargeDensity);');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.h');s=p.read_text().replace('[[nodiscard]] Mesh2& sliceMesh()', '[[nodiscard]] Mesh3& mesh() { return mesh_m; }\n        [[nodiscard]] Mesh2& sliceMesh()');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.cpp');s=p.read_text().replace('if (batchSize <= 0 || ippl::Comm->size() != 1)','if (batchSize <= 0)').replace('Positive batch size and one MPI rank required.','Positive batch size required.').replace('nz = mesh.getGridsize(2);','nz = density.getLayout().getLocalNDIndex()[2].length();');a=s.index('    if (nx2_ != 2 * nx',s.index('void FFT2D5Poisson::solveBatched'));b=s.index('    for (size_t z : occupied)',a);s=s[:a]+'''    const bool localMPI = ippl::Comm->size() > 1;
    if (localMPI) {
        if (nx2_ != 2 * nx || ny2_ != 2 * ny || dr_[0] != spacing[0] || dr_[1] != spacing[1]) {
            batchPlan_m.reset();
            nx2_ = 2 * nx; ny2_ = 2 * ny;
            dr_ = Vector2_t(spacing[0], spacing[1]);
        }
    } else if (nx2_ != 2 * nx || ny2_ != 2 * ny || dr_[0] != spacing[0] || dr_[1] != spacing[1]) {
        throw OpalException("FFT2D5Poisson::solveBatched", "Initialize the matching workspace.");
    }
'''+s[b:];s=s.replace('inbox, outbox, 0, ippl::Comm->getCommunicator(),','inbox, outbox, 0, MPI_COMM_SELF,');a=s.index('    const auto originalGreen',s.index('void FFT2D5Poisson::solveBatched'));b=s.index('    const auto source',a);s=s[:a]+'''    if (localMPI) {
        // Every rank owns complete x-y planes. Use the same integrated kernel and
        // normalization as makeGreensFn(), with a private heFFTe communicator.
        const auto real = batchReal_m;
        const auto nx2 = nx2_, ny2 = ny2_;
        const auto dx = dr_[0], dy = dr_[1];
        Kokkos::parallel_for("FFT2D5Batch::localGreen", nr, KOKKOS_LAMBDA(size_t p) {
            const size_t i = p % nx2, j = p / nx2;
            const double x = (i <= nx2 / 2 ? double(i) : double(i) - nx2) * dx;
            const double y = (j <= ny2 / 2 ? double(j) : double(j) - ny2) * dy;
            real(p) = cellAveragedGreensFunction(x, y, dx, dy);
        });
        Kokkos::fence();
        batchPlan_m->forward(1, real.data(), green.data(), batchWorkspace_m.data(), heffte::scale::full);
        Kokkos::fence();
    } else {
        const auto originalGreen = greensFnTr_m.getView();
        const auto ng = greensFnTr_m.getNghost();
        Kokkos::parallel_for("FFT2D5Batch::green", nc, KOKKOS_LAMBDA(size_t p) {
            green(p) = originalGreen(p % ncx + ng, p / ncx + ng);
        });
    }
'''+s[b:];p.write_text(s)
p=Path('src/PartBunch/ParticleContainer.hpp');s=p.read_text();key='    void setupBCs(ippl::BC particleBC)';a=s.index(key);s=s[:a]+'''    /** Scratch Cartesian positions registered lazily so OPEN-style spatial migration
     * carries them with every other particle attribute. No allocation for other solvers. */
    ippl::ParticleAttrib<ippl::Vector<T, Dim>>& migrationPositions() {
        if (!migrationPositions_m) {
            migrationPositions_m = std::make_unique<ippl::ParticleAttrib<ippl::Vector<T, Dim>>>();
            this->addAttribute(*migrationPositions_m);
            migrationPositions_m->create(0);
        }
        return *migrationPositions_m;
    }

'''+s[a:];a=s.index('private:',s.index('void setupBCs'));s=s[:a]+s[a:].replace('private:', 'private:\n    std::unique_ptr<ippl::ParticleAttrib<ippl::Vector<T, Dim>>> migrationPositions_m;',1);p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text();a=s.index('        if (context.stepState().mpiSize != 1');b=s.index('        if (bunchState_m->fixedCartesianDomain()',a);s=s[:a]+'''        if (ippl::Comm->size() > 1 && !config_m.grid.decomposition[2]) {
            throw OpalException("FFT2D5Algorithm::solve", "Multiple ranks require PARFFTZ=TRUE.");
        }
'''+s[b:];p.write_text(s)
