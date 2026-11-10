from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text();a=s.index('                // This short serial prefix');b=s.index('                Kokkos::fence();',a)
s=s[:a]+'''                // Independent segment arithmetic and endpoint boxes span the device.
                Kokkos::parallel_for(
                        "FFT2D5::preparePathSegments", leaves, KOKKOS_LAMBDA(const size_t i) {
                            if (i < segments) {
                                const Vector3D_t direction = ref(i + 1) - ref(i);
                                const T length = euclidean_norm(direction);
                                for (unsigned d = 0; d < 3; ++d)
                                    geometry(i, d) = direction[d];
                                geometry(i, 3) = direction.dot(direction);
                                geometry(i, 4) = length;
                            }
                            for (unsigned d = 0; d < 3; ++d) {
                                bounds(leaves + i, d) =
                                        i < segments ? Kokkos::min(ref(i)[d], ref(i + 1)[d])
                                                     : Kokkos::Experimental::finite_max_v<T>;
                                bounds(leaves + i, d + 3) =
                                        i < segments ? Kokkos::max(ref(i)[d], ref(i + 1)[d])
                                                     : -Kokkos::Experimental::finite_max_v<T>;
                            }
                        });
                // The preceding kernel completes before this team reads its output.
                // Keep the prefix ordered; a parallel scan would reassociate additions.
                Kokkos::parallel_for(
                        "FFT2D5::preparePathHierarchy", Kokkos::TeamPolicy<>(1, Kokkos::AUTO),
                        KOKKOS_LAMBDA(const Kokkos::TeamPolicy<>::member_type& team) {
                            Kokkos::single(Kokkos::PerTeam(team), [&] {
                                T prefix = 0.0;
                                for (size_t i = 0; i < segments; ++i) {
                                    geometry(i, 5) = prefix;
                                    prefix += geometry(i, 4);
                                }
                            });
                            for (size_t first = leaves / 2; first > 0; first /= 2) {
                                Kokkos::parallel_for(
                                        Kokkos::TeamThreadRange(team, first), [&](const size_t j) {
                                            const size_t i = first + j;
                                            for (unsigned d = 0; d < 3; ++d) {
                                                bounds(i, d) = Kokkos::min(
                                                        bounds(2 * i, d), bounds(2 * i + 1, d));
                                                bounds(i, d + 3) = Kokkos::max(
                                                        bounds(2 * i, d + 3),
                                                        bounds(2 * i + 1, d + 3));
                                            }
                                        });
                                team.team_barrier();
                            }
                        });
'''+s[b:];p.write_text(s)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');s=p.read_text().replace('Two ordered device stages are required: one geometry kernel, followed by a\n         * projection kernel for each active container.', 'Two ordered preparation kernels precede the projection kernel for each active\n         * container: independent segments/leaves, then one team for prefix and hierarchy.').replace('A short single-work-item geometry kernel\n         * accumulates S_i in increasing segment order;', 'One team thread\n         * accumulates S_i in increasing segment order from the stored lengths;').replace('padded leaves are empty. Rebuild all boxes in the geometry kernel, so frame','padded leaves are empty. Team threads merge one level at a time, with a team\n         * barrier between levels. No inter-block barrier or parallel prefix scan is used.\n         * Rebuild all boxes each solve, so frame')
s=s.replace('        const ReferenceView_t& getReferencePath() const { return referencePathView(); }','''        const ReferenceView_t& getReferencePath() const { return referencePathView(); }
        /// Read-only handles for independent geometry and hierarchy validation.
        const SegmentGeometryView_t& getSegmentGeometry() const { return segmentGeometry_m; }
        const SegmentGeometryView_t& getSegmentBounds() const { return segmentBounds_m; }''');p.write_text(s)
