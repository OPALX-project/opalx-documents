from pathlib import Path
import subprocess
p=Path('unit_tests/SpaceCharge/TestFFT2D5Algorithm.cpp');s=p.read_text();old=subprocess.check_output(['git','show','HEAD:src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp'],text=True);a=old.index('                            T prefix = 0.0;');b=old.index('                        });',a);body=old[a:b]
helper='''        // Preserve the previous serial device build as an independent exact oracle.
        void launchSerialGeometryOracle(
                FFT2D5Algorithm::ReferenceView_t ref,
                FFT2D5Algorithm::SegmentGeometryView_t geometry,
                FFT2D5Algorithm::SegmentGeometryView_t bounds) {
            using T = FFT2D5Algorithm::T;
            using Vector3D_t = FFT2D5Algorithm::Vector3D_t;
            const size_t segments = ref.extent(0) - 1;
            const size_t leaves = bounds.extent(0) / 2;
            Kokkos::parallel_for("serialGeometryOracle", 1, KOKKOS_LAMBDA(size_t) {
'''+body+'''            });
        }

'''
s=s.replace('        class FFT2D5AlgorithmTest',helper+'        class FFT2D5AlgorithmTest',1)
needle='''                    const auto ref  = solver.getReferencePath();
'''
addition='''                    FFT2D5Algorithm::SegmentGeometryView_t serialGeometry(
                            "serialGeometry", solver.getSegmentGeometry().extent(0));
                    FFT2D5Algorithm::SegmentGeometryView_t serialBounds(
                            "serialBounds", solver.getSegmentBounds().extent(0));
                    launchSerialGeometryOracle(ref, serialGeometry, serialBounds);
                    auto expectedGeometry = Kokkos::create_mirror_view_and_copy(
                            Kokkos::HostSpace(), serialGeometry);
                    auto expectedBounds = Kokkos::create_mirror_view_and_copy(
                            Kokkos::HostSpace(), serialBounds);
                    auto actualGeometry = Kokkos::create_mirror_view_and_copy(
                            Kokkos::HostSpace(), solver.getSegmentGeometry());
                    auto actualBounds = Kokkos::create_mirror_view_and_copy(
                            Kokkos::HostSpace(), solver.getSegmentBounds());
                    for (size_t i = 0; i < serialGeometry.extent(0); ++i)
                        for (unsigned d = 0; d < 6; ++d)
                            ASSERT_EQ(actualGeometry(i, d), expectedGeometry(i, d))
                                    << scenario << " " << repeat << " segment=" << i << " col=" << d;
                    // Heap index zero is unused and intentionally uninitialized.
                    for (size_t i = 1; i < serialBounds.extent(0); ++i)
                        for (unsigned d = 0; d < 6; ++d)
                            ASSERT_EQ(actualBounds(i, d), expectedBounds(i, d))
                                    << scenario << " " << repeat << " node=" << i << " col=" << d;
'''
assert s.count(needle)==1;s=s.replace(needle,needle+addition);p.write_text(s)
