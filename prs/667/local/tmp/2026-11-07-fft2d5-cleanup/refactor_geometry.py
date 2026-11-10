from pathlib import Path
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.cpp');s=p.read_text();a=s.index('    void FFT2D5Algorithm::preparePathGeometryAndProjections(');b=s.index('    std::size_t FFT2D5Algorithm::sliceCount()',a);old=s[a:b]
seg=old[old.index('                Kokkos::parallel_for('):old.index('                // The preceding kernel')]
hier=old[old.index('                Kokkos::parallel_for(',old.index('                // The preceding kernel')):old.index('                Kokkos::fence();')]
new='''    void FFT2D5Algorithm::preparePathGeometryAndProjections(
            const SpaceChargeSolveContext& context, bool rebuildGeometry) {
        fft2d5_detail::timed("2D5 Geometry", [&] {
            if (solveReferencePath_m.extent(0) < 2) return;
            const size_t leaves = resizePathGeometry();
            if (rebuildGeometry) {
                buildPathSegments(leaves);
                buildPathHierarchy(leaves);
                Kokkos::fence();
            }
            projectedPositions_m.resize(particles_m.size());
            projectedSegments_m.resize(particles_m.size());
            const T periodicLength =
                    !rebuildGeometry && config_m.closedRing ? referencePath_m->length() : 0.;
            for (size_t c = 0; c < particles_m.size(); ++c)
                if (context.trackingActive()[c]) projectContainer(c, leaves, periodicLength);
            Kokkos::fence();
        });
    }

    size_t FFT2D5Algorithm::resizePathGeometry() {
        const size_t segments = solveReferencePath_m.extent(0) - 1;
        if (segmentGeometry_m.extent(0) != segments)
            segmentGeometry_m = SegmentGeometryView_t("FFT2D5SegmentGeometry", segments);
        size_t leaves = 1;
        while (leaves < segments) {
            if (leaves > std::numeric_limits<size_t>::max() / 4)
                throw OpalException("FFT2D5Algorithm::preparePathGeometryAndProjections",
                                    "Reference path is too large for the bounds hierarchy.");
            leaves *= 2;
        }
        if (segmentBounds_m.extent(0) != 2 * leaves)
            segmentBounds_m = SegmentGeometryView_t("FFT2D5SegmentBounds", 2 * leaves);
        return leaves;
    }

    void FFT2D5Algorithm::buildPathSegments(size_t leaves) {
        const auto ref = solveReferencePath_m;
        const auto geometry = segmentGeometry_m, bounds = segmentBounds_m;
        const size_t segments = ref.extent(0) - 1;
'''+seg+'''    }

    void FFT2D5Algorithm::buildPathHierarchy(size_t leaves) {
        const auto geometry = segmentGeometry_m, bounds = segmentBounds_m;
        const size_t segments = solveReferencePath_m.extent(0) - 1;
'''+hier+'''    }

    void FFT2D5Algorithm::projectContainer(size_t container, size_t leaves, T periodicLength) {
        const size_t count = particles_m[container]->getLocalNum();
        const auto ref = solveReferencePath_m;
        const size_t segments = ref.extent(0) - 1;
        if (projectedPositions_m[container].extent(0) != count) {
            projectedPositions_m[container] = VectorView_t("FFT2D5ProjectedPositions", count);
            projectedSegments_m[container] = SegmentIndexView_t("FFT2D5ProjectedSegments", count);
            Kokkos::deep_copy(projectedSegments_m[container], segments);
        }
        const auto positions = particles_m[container]->R.getView();
        const auto invalid = particles_m[container]->InvalidMask.getView();
        const auto projected = projectedPositions_m[container];
        const auto indices = projectedSegments_m[container];
        const auto geometry = segmentGeometry_m, bounds = segmentBounds_m;
        Kokkos::parallel_for("FFT2D5::prepareParticleProjections", count,
            KOKKOS_LAMBDA(const size_t n) {
                projectPreparedParticle(n, positions, invalid, ref, geometry, bounds,
                                        projected, indices, leaves, periodicLength);
            });
    }

'''
s=s[:a]+new+s[b:];p.write_text(s)
# Move the numerical per-particle operations verbatim into inline device helpers.
q=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp');h=q.read_text();pos=h.rfind('}  // namespace opalx::spacecharge')
evalbody=old[old.index('                                const T length2 = geometry(i, 3);'):old.index('                            };',old.index('                                const T length2 = geometry(i, 3);'))]
roundbody=old[old.index('                            T scale = 0.0;'):old.index('                            const auto lowerBound')];roundbody=roundbody.replace('                            const T roundoff    =','                            return')
lower=old[old.index('                                T distance2 = 0.0;'):old.index('                            };',old.index('                                T distance2 = 0.0;'))]
search=old[old.index('                            size_t stack[64];'):old.index('                            const Vector3D_t tangent')]
project=old[old.index('                            const Vector3D_t tangent'):old.index('                        });',old.index('                            const Vector3D_t tangent'))]
helpers='''    KOKKOS_INLINE_FUNCTION void FFT2D5Algorithm::evaluatePathSegment(
            size_t i, const Vector3D_t& position, const ReferenceView_t& ref,
            const SegmentGeometryView_t& geometry, T& bestDistance2, size_t& best,
            T& bestFraction, Vector3D_t& closest) {
'''+evalbody+'''    }

    KOKKOS_INLINE_FUNCTION FFT2D5Algorithm::T FFT2D5Algorithm::pathDistanceRoundoff(
            const Vector3D_t& position, const SegmentGeometryView_t& bounds) {
'''+roundbody+'''    }

    KOKKOS_INLINE_FUNCTION FFT2D5Algorithm::T FFT2D5Algorithm::pathNodeDistance2(
            size_t node, const Vector3D_t& position, const SegmentGeometryView_t& bounds) {
'''+lower+'''    }

    KOKKOS_INLINE_FUNCTION void FFT2D5Algorithm::findClosestPathSegment(
            const Vector3D_t& position, size_t seed, const ReferenceView_t& ref,
            const SegmentGeometryView_t& geometry, const SegmentGeometryView_t& bounds,
            size_t leaves, size_t& best, T& bestFraction, Vector3D_t& closest) {
        const size_t segments = ref.extent(0) - 1;
        T bestDistance2 = Kokkos::Experimental::finite_max_v<T>;
        const auto evaluate = [&](size_t i) {
            evaluatePathSegment(i, position, ref, geometry, bestDistance2, best, bestFraction, closest);
        };
        evaluate(seed < segments ? seed : 0);
        const T roundoff = pathDistanceRoundoff(position, bounds);
        const auto lowerBound = [&](size_t node) { return pathNodeDistance2(node, position, bounds); };
'''+search+'''    }

    KOKKOS_INLINE_FUNCTION void FFT2D5Algorithm::projectPreparedParticle(
            size_t n, const VectorView_t& positions, const BooleanView_t& invalid,
            const ReferenceView_t& ref, const SegmentGeometryView_t& geometry,
            const SegmentGeometryView_t& bounds, const VectorView_t& projected,
            const SegmentIndexView_t& indices, size_t leaves, T periodicLength) {
        const size_t segments = ref.extent(0) - 1;
        if (invalid(n)) { projected(n) = Vector3D_t(0.); indices(n) = segments; return; }
        const Vector3D_t position = positions(n);
        size_t best = 0;
        T bestFraction = 0.;
        Vector3D_t closest(0.);
        findClosestPathSegment(position, indices(n), ref, geometry, bounds,
                               leaves, best, bestFraction, closest);
'''+project+'''    }

'''
h=h[:pos]+helpers+h[pos:];q.write_text(h)
p=Path('src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h');h=p.read_text();pos=h.index('    private:\n');decl='''        /** @internal @brief Resize segment and complete binary-heap bounds storage.
         * @return Power-of-two leaf count. @throws OpalException On index overflow. */
        size_t resizePathGeometry();
        /** @internal @brief Compute independent segment data and endpoint boxes in one kernel.
         * @param leaves Complete heap leaf count; padded leaves receive empty boxes. */
        void buildPathSegments(size_t leaves);
        /** @internal @brief Preserve ordered arc lengths and merge bounds level by level.
         * @param leaves Complete heap leaf count; preceding segment kernel shares the stream. */
        void buildPathHierarchy(size_t leaves);
        /** @internal @brief Refresh projections for one active container without moving particles.
         * @param container Container index. @param leaves Heap leaf count.
         * @param periodicLength Positive only for post-migration closed-ring seam wrapping.
         * Kernel-launching helpers are public to satisfy NVCC extended-lambda accessibility. */
        void projectContainer(size_t container, size_t leaves, T periodicLength);
        /** @internal @brief Score one nondegenerate segment with the unchanged lowest-index tie.
         * @param i Segment index. @param position Cartesian query. @param ref Path vertices.
         * @param geometry Segment data. @param bestDistance2 Current squared distance, updated.
         * @param best Winning index, updated. @param bestFraction Winning clamped fraction.
         * @param closest Winning Cartesian closest point; updated with the score. */
        KOKKOS_FUNCTION static void evaluatePathSegment(size_t i, const Vector3D_t& position,
                const ReferenceView_t& ref, const SegmentGeometryView_t& geometry,
                T& bestDistance2, size_t& best, T& bestFraction, Vector3D_t& closest);
        /** @internal @brief Conservative pruning allowance for rounded Cartesian arithmetic.
         * @param position Query point. @param bounds Complete heap. @return Squared-distance margin. */
        KOKKOS_FUNCTION static T pathDistanceRoundoff(const Vector3D_t& position,
                                                   const SegmentGeometryView_t& bounds);
        /** @internal @brief Compute the unchanged squared point-to-box lower bound.
         * @param node Heap index. @param position Query point. @param bounds Heap boxes.
         * @return Rounded squared lower bound, used only with the conservative allowance. */
        KOKKOS_FUNCTION static T pathNodeDistance2(size_t node, const Vector3D_t& position,
                                                 const SegmentGeometryView_t& bounds);
        /** @internal @brief Search the full hierarchy, falling back to exhaustive scoring on stack exhaustion.
         * @param position Query point. @param seed Previous segment, used only as an upper bound.
         * @param ref Vertices. @param geometry Segment data. @param bounds Heap boxes.
         * @param leaves Power-of-two leaves. @param best Winning index, initialized by caller.
         * @param bestFraction Winning fraction. @param closest Winning Cartesian point. */
        KOKKOS_FUNCTION static void findClosestPathSegment(const Vector3D_t& position, size_t seed,
                const ReferenceView_t& ref, const SegmentGeometryView_t& geometry,
                const SegmentGeometryView_t& bounds, size_t leaves, size_t& best,
                T& bestFraction, Vector3D_t& closest);
        /** @internal @brief Project one particle using exact segment scoring and the existing basis.
         * @param n Particle index. @param positions Cartesian source. @param invalid Invalid mask.
         * @param ref Vertices. @param geometry Segment data. @param bounds Heap boxes.
         * @param projected Output local coordinates. @param indices Output winning indices.
         * @param leaves Heap leaf count. @param periodicLength Post-migration seam-wrap length. */
        KOKKOS_FUNCTION static void projectPreparedParticle(size_t n, const VectorView_t& positions,
                const BooleanView_t& invalid, const ReferenceView_t& ref,
                const SegmentGeometryView_t& geometry, const SegmentGeometryView_t& bounds,
                const VectorView_t& projected, const SegmentIndexView_t& indices,
                size_t leaves, T periodicLength);

''';h=h[:pos]+decl+h[pos:];p.write_text(h)
