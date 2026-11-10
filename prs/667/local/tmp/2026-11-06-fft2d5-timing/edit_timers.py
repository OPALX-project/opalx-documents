from pathlib import Path

def block(s,start):
 a=s.index('{',start);depth=1;b=a+1
 while depth:
  depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return a,b-1

def wrap(s,needle,name):
 a,b=block(s,s.index(needle));return s[:a+1]+f'\n        opalx::spacecharge::fft2d5_detail::timed("{name}", [&] {{'+s[a+1:b]+'\n        });\n    '+s[b:]

p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.h');s=p.read_text();i=s.index('class FFT2D5Poisson');s=s[:i]+'''namespace opalx::spacecharge::fft2d5_detail {
    /** Register the same names/order on every rank, including ranks with no occupied planes.
     * IPPL prints timers with collectives; rank-dependent registration can deadlock printing. */
    inline void registerTimers() {
        for (const char* name : {
             "2D5 Initialize", "2D5 Warmup", "2D5 Plan", "2D5 Green Init",
             "2D5 First Solve", "2D5 Solve", "2D5 Geometry", "2D5 Migration",
             "2D5 Scatter", "2D5 Rho Halo", "2D5 Poisson", "2D5 Line density",
             "2D5 E Halo", "2D5 Gather", "2D5 Pack", "2D5 FFT Rho",
             "2D5 Convolution", "2D5 FFT Back", "2D5 Extract", "2D5 Field"})
            IpplTimings::getTimer(name);
    }

    /** Time completed device work, not asynchronous launch submission. No MPI barrier is
     * introduced. Timers are inclusive: parent phases contain their named subphases.
     * Stop on exceptions too, so a failed diagnostic call cannot contaminate later samples. */
    template<class Work>
    void timed(const char* name, Work&& work) {
        const auto timer = IpplTimings::getTimer(name);
        Kokkos::fence("FFT2D5 timing begin");
        IpplTimings::startTimer(timer);
        try { work(); }
        catch (...) {
            Kokkos::fence("FFT2D5 timing exception");
            IpplTimings::stopTimer(timer);
            throw;
        }
        Kokkos::fence("FFT2D5 timing end");
        IpplTimings::stopTimer(timer);
    }
}

'''+s[i:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text().replace('        validateSpaceChargeConfig(SpaceChargeConfig(config_m));','        validateSpaceChargeConfig(SpaceChargeConfig(config_m));\n        fft2d5_detail::registerTimers();',1)
a=s.index('        // Design-path points');b=s.index('        return result;',a)
body=s[a:b].replace('        SpaceChargeSolveResult result;\n','')
s=s[:a]+'''        SpaceChargeSolveResult result;
        fft2d5_detail::timed(firstPhysicalSolve_m ? "2D5 First Solve" : "2D5 Solve", [&] {
'''+body+'''        });
        firstPhysicalSolve_m = false;
'''+s[b:]
for method,name in [('migrateToSlabs','2D5 Migration'),('preparePathGeometryAndProjections','2D5 Geometry'),('accumulateDensityHalos','2D5 Rho Halo'),('fillFieldHalos','2D5 E Halo')]:
 s=wrap(s,'void FFT2D5Algorithm::'+method+'(',name)
a=s.index('        // Publish dependent storage');b=s.index('\n    }',a)
s=s[:a]+'''        fft2d5_detail::timed("2D5 Initialize", [&] {
'''+s[a:b]+'''
        });
        fft2d5_detail::timed("2D5 Warmup", [&] { fieldStorage_m->warmup(); });
'''+s[b:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');s=p.read_text().replace('        FFT2D5Config config_m;','''        // The first physical step is retained, but its cache/migration setup cost is
        // reported separately from subsequent (steady-state) space-charge solves.
        bool firstPhysicalSolve_m = true;
        FFT2D5Config config_m;''');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp');s=p.read_text()
for method,name in [('scatterToGrid','2D5 Scatter'),('solvePoissons','2D5 Poisson'),('calculateLineDensity','2D5 Line density'),('gatherFromGrid','2D5 Gather')]:
 s=wrap(s,'void FFT2D5Algorithm::'+method+'(',name)
p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.h');s=p.read_text().replace('        ~FFT2D5FieldStorage();','''        ~FFT2D5FieldStorage();
        /** Prepare plans, Green spectra and FFT execution on a zero source, without
         * touching particles or counting a physical solve. Runtime FFT-phase samples
         * are cleared afterward; preparation retains its own named timers. */
        void warmup();''');p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5FieldStorage.cpp');s=p.read_text().replace('#include <array>','#include <array>\n#include <numeric>\n#include <vector>');a=s.index('    void FFT2D5FieldStorage::solveBatchedSlices');s=s[:a]+'''    void FFT2D5FieldStorage::warmup() {
        Kokkos::deep_copy(chargeDensity_m.getView(), 0.);
        Kokkos::deep_copy(electricField_m.getView(), Vector3(0.));
        Kokkos::deep_copy(workspace_m.chargeDensity->getView(), 0.);
        Kokkos::deep_copy(workspace_m.electricField->getView(), Vector2(0.));
        if (batchSize_m > 0) {
            const auto count = std::min(size_t(batchSize_m), size_t(layout_m.getLocalNDIndex()[2].length()));
            std::vector<size_t> planes(count);
            std::iota(planes.begin(), planes.end(), 0);
            // Force a complete zero-source batch despite its empty occupancy.
            solveBatchedSlices(planes);
        } else {
            solveSlice();
        }
        Kokkos::deep_copy(chargeDensity_m.getView(), 0.);
        Kokkos::deep_copy(electricField_m.getView(), Vector3(0.));
        Kokkos::fence();
        resetBackendSolves();
        // Keep plan/Green/Warmup totals; runtime phase counters describe physical work only.
        for (const char* name : {"2D5 Pack", "2D5 FFT Rho", "2D5 Convolution",
                                 "2D5 FFT Back", "2D5 Extract", "2D5 Field"})
            IpplTimings::infoTimer(name)->clearAll();
    }

'''+s[a:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Poisson.cpp');s=p.read_text().replace('FFT2D5Poisson::FFT2D5Poisson() {','FFT2D5Poisson::FFT2D5Poisson() {\n    opalx::spacecharge::fft2d5_detail::registerTimers();',1)
for method,name in [('makeGreensFn','2D5 Green Init'),('placeChargeDensity','2D5 Pack'),('extractPotential','2D5 Extract'),('determineField','2D5 Field')]:
 s=wrap(s,'void FFT2D5Poisson::'+method+'(',name)
# Serial planning/setup; Green preparation is its own timer, called after the plan timer.
a=s.index('        const bool resizeFields');b=s.index('        makeGreensFn();',a)
s=s[:a]+'''        opalx::spacecharge::fft2d5_detail::timed("2D5 Plan", [&] {
'''+s[a:b]+'''        });
'''+s[b:]
# Serial convolution phases (existing fences are retained within the timed work).
a=s.index('    fft_m->transform(ippl::FORWARD',s.index('void FFT2D5Poisson::performConvolution'));b=s.index('    const auto greens',a)
s=s[:a]+'''    opalx::spacecharge::fft2d5_detail::timed("2D5 FFT Rho", [&] {
'''+s[a:b]+'''    });
'''+s[b:]
a=s.index('    Kokkos::parallel_for(',s.index('void FFT2D5Poisson::performConvolution'));b=s.index('    fft_m->transform(ippl::BACKWARD',a)
s=s[:a]+'''    opalx::spacecharge::fft2d5_detail::timed("2D5 Convolution", [&] {
'''+s[a:b]+'''    });
'''+s[b:]
a=s.index('    fft_m->transform(ippl::BACKWARD',s.index('void FFT2D5Poisson::performConvolution'));b=s.index('\n}',a)
s=s[:a]+'''    opalx::spacecharge::fft2d5_detail::timed("2D5 FFT Back", [&] {
'''+s[a:b]+'''    });
'''+s[b:]
# Native batched plan and local Green setup.
a=s.index('    if (!batchPlan_m',s.index('void FFT2D5Poisson::solveBatched'));x,y=block(s,a)
s=s[:x+1]+'''\n        opalx::spacecharge::fft2d5_detail::timed("2D5 Plan", [&] {'''+s[x+1:y]+'''\n        });\n    '''+s[y:]
a=s.index('    if (localMPI && !localGreenReady_m)',s.index('void FFT2D5Poisson::solveBatched'));x,y=block(s,a)
s=s[:x+1]+'''\n        opalx::spacecharge::fft2d5_detail::timed("2D5 Green Init", [&] {'''+s[x+1:y]+'''\n        });\n    '''+s[y:]
# Four batch operations and extraction, keeping the existing operation ordering.
base=s.index('    for (size_t first =',s.index('void FFT2D5Poisson::solveBatched'))
for begin,end,name in [
 ('        Kokkos::parallel_for(\n                "FFT2D5Batch::field"',None,'2D5 Field'),
 ('        Kokkos::parallel_for(\n                "FFT2D5Batch::applyGreen"','        batchPlan_m->backward(','2D5 Convolution'),
 ('        batchPlan_m->backward(','        opalx::spacecharge::fft2d5_detail::timed("2D5 Field"','2D5 FFT Back'),
 ('        batchPlan_m->forward(','        opalx::spacecharge::fft2d5_detail::timed("2D5 Convolution"','2D5 FFT Rho'),
 ('        Kokkos::parallel_for(\n                "FFT2D5Batch::pack"','        opalx::spacecharge::fft2d5_detail::timed("2D5 FFT Rho"','2D5 Pack')]:
 a=s.index(begin,base)
 b=s.index(end,a) if end else s.rindex('    }')
 s=s[:a]+f'        opalx::spacecharge::fft2d5_detail::timed("{name}", [&] {{\n'+s[a:b]+'''        });
'''+s[b:]
p.write_text(s)
