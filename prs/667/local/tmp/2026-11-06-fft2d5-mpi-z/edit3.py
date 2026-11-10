from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.h');s=p.read_text().replace('    int batchCapacity_m = 0;','    int batchCapacity_m = 0;\n    bool localGreenReady_m = false;').replace('This is not MPI batching.','MPI ranks own disjoint z slabs; each rank uses MPI_COMM_SELF for its transverse plans.').replace('@pre One MPI rank; unique occupied physical slice indices; matching source/output grids.','@pre Unique occupied local slice indices; complete x-y planes and matching source/output grids.').replace('@pre initialiseViews() has received a matching transverse workspace.','@pre On one rank, initialiseViews() has received a matching transverse workspace.');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.cpp');s=p.read_text().replace('        batchCapacity_m  = capacity;','        batchCapacity_m  = capacity;\n        localGreenReady_m = false;').replace('    if (localMPI) {\n        // Every rank','    if (localMPI && !localGreenReady_m) {\n        // Every rank').replace('        Kokkos::fence();\n    } else {\n        const auto originalGreen','        Kokkos::fence();\n        localGreenReady_m = true;\n    } else if (!localMPI) {\n        const auto originalGreen');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.h');s=p.read_text().replace('void solveBatchedSlices(std::span<const size_t> occupied);','void solveBatchedSlices(std::span<const size_t> occupied, ScalarField3* potential = nullptr);');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp');s=p.read_text().replace('void FFT2D5FieldStorage::solveBatchedSlices(std::span<const size_t> occupied) {','void FFT2D5FieldStorage::solveBatchedSlices(\n            std::span<const size_t> occupied, ScalarField3* potential) {').replace('occupied, batchSize_m, 1 / Physics::epsilon_0);','occupied, batchSize_m, 1 / Physics::epsilon_0, potential);');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp');s=p.read_text().replace('        // All ranks must execute the same FFT calls, even if their local sources differ.\n','');s=s.replace('''            fieldStorage_m->solveBatchedSlices(occupied);
            batched = true;
        }
        // Diagnostic policies''','''            FFT2D5FieldStorage::ScalarField3 potential(fieldStorage_m->mesh(), fieldStorage_m->layout());
            fieldStorage_m->solveBatchedSlices(occupied, &potential);
            const auto phi = potential.getView();
            const auto first = fieldStorage_m->layout().getLocalNDIndex()[2].first();
            for (size_t z = 0; z < size_t(numSlices); ++z) {
                const auto slice = Kokkos::subview(phi, Kokkos::ALL(), Kokkos::ALL(), z + nGhost);
                diagnostic.potential(slice, z + first + nGhost);
            }
            batched = true;
        }
        // Diagnostic policies''');# Restore original transverse summation range on serial
s=s.replace('Policy2D_t({1, 1}, {rho3d.extent(0)-1, rho3d.extent(1)-1}),','Policy2D_t({0, 0}, {rho3d.extent(0), rho3d.extent(1)}),');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text().replace('        result.backendSolves = fieldStorage_m->backendSolves();','''        result.backendSolves = fieldStorage_m->backendSolves();
        if (ippl::Comm->size() > 1) {
            const auto local = result.backendSolves;
            ippl::Comm->allreduce(local, result.backendSolves, 1, std::plus<size_t>());
        }''').replace('        ensureInitialized();','''        if (size_t(ippl::Comm->size()) > config_m.grid.meshSize[2])
            throw OpalException("FFT2D5Algorithm::solve", "Need at least one z slice per MPI rank.");
        ensureInitialized();''',1);p.write_text(s)
p=Path('unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp');s=p.read_text().replace('Configuration_ParallelLayoutRejected','Configuration_TransverseParallelLayoutRejected').replace('''        fsCmd_m->setParallelDimensions(false, false, true);

        EXPECT_NO_THROW(fsCmd_m->execute());
        EXPECT_THROW''','''        fsCmd_m->setParallelDimensions(true, false, false);

        EXPECT_NO_THROW(fsCmd_m->execute());
        EXPECT_THROW''',1).replace('Configuration_MultipleRanksRejected','Configuration_MultipleRanksRequireZDecomposition');p.write_text(s)
