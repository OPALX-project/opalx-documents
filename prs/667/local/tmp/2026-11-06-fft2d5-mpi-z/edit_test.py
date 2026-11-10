from pathlib import Path
p=Path('unit_tests/SpaceCharge/TestFFT2D5Parallel.cpp');s=p.read_text();key='                const auto ids =';print('key?',key in s)
# Inspect names after clang formatting by using stable source marker.
key='                size_t count =';a=s.index(key)
s=s[:a]+'''                const auto electric = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), pc.E.getView());
                const auto magnetic = Kokkos::create_mirror_view_and_copy(Kokkos::HostSpace(), pc.B.getView());
'''+s[a:]
key='                    for (int d = 0; d < 3; ++d) {';a=s.index(key)
s=s[:a]+'''                    const auto r = sources[ids(n)];
                    const int i = int(std::lround((r[0]+.5)/dx-.5));
                    const int j = int(std::lround((r[1]+.5)/dx-.5));
                    const double cell = r[2]/dz-.5;
                    const int left = int(std::floor(cell));
                    const double fraction = cell-left;
                    auto sample = [&](const Grid& values, int k) {
                        if (closed) k=(k%nz+nz)%nz;
                        return k>=0 && k<nz ? values[index(i,j,k)] : 0.;
                    };
                    double expectedX, expectedY;
                    if(cicZ) {
                        expectedX=(1.-fraction)*sample(ex,left)+fraction*sample(ex,left+1);
                        expectedY=(1.-fraction)*sample(ey,left)+fraction*sample(ey,left+1);
                    } else {
                        expectedX=sample(ex,int(std::floor(r[2]/dz+.5)));
                        expectedY=sample(ey,int(std::floor(r[2]/dz+.5)));
                    }
                    auto slope = [&](int k) {
                        k=closed ? (k%nz+nz)%nz : std::clamp(k,0,nz-1);
                        return gradient[k];
                    };
                    const double derivative=cicZ ? (1.-fraction)*slope(left)+fraction*slope(left+1)
                        : slope(int(std::floor(r[2]/dz)));
                    const double expectedZ=-6.36/(4*Physics::pi*Physics::epsilon_0)*derivative/1.16;
                    EXPECT_NEAR(electric(n)[0],expectedX,1.e-11);
                    EXPECT_NEAR(electric(n)[1],expectedY,1.e-11);
                    EXPECT_NEAR(electric(n)[2],expectedZ,1.e-11);
                    const double beta=.4/std::sqrt(1.16);
                    EXPECT_NEAR(magnetic(n)[0],-beta*expectedY/Physics::c,1.e-19);
                    EXPECT_NEAR(magnetic(n)[1],beta*expectedX/Physics::c,1.e-19);
                    EXPECT_DOUBLE_EQ(magnetic(n)[2],0.);
'''+s[a:];p.write_text(s)
