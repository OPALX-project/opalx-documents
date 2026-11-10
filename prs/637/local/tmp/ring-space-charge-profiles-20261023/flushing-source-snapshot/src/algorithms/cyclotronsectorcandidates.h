// Copyright (c) 2026, Paul Scherrer Institute, Villigen PSI, Switzerland
#ifndef OPALX_CYCLOTRON_SECTOR_CANDIDATES_H
#define OPALX_CYCLOTRON_SECTOR_CANDIDATES_H

#include <algorithm>
#include <cmath>
#include <limits>
#include <set>
#include "AbsBeamline/ElementBase.h"
#include "Utilities/ElementList.h"

/** @brief Conservative spatial candidates for existing cyclotron device kernels.
 *
 * A periodic path index describes the threader's first orbit, not every TRACK
 * midpoint or every particle orbit. Do not let it omit a sector's magnetic kick.
 * This host-side broad phase uses the current tracking-frame bunch AABB [m].
 * The device field kernel still owns radial/vertical bounds and half-open seam
 * ownership. No field formula, physical boundary or integration step is changed.
 */
namespace cyclotron_candidates {
    using Vector     = Vector_t<double, 3>;
    using Candidates = std::set<std::shared_ptr<ElementBase>>;

    /** @brief Could the transformed AABB intersect the angular wedge?
     *
     * For sector angle 0<a<=pi and local X=x+Rm, the wedge lies in z>=0 and
     * sin(a)*X-cos(a)*z>=0. A linear function attains its box maximum at a
     * corner, so reject only if every transformed corner violates a half-plane.
     * A roundoff margin of 64 epsilon times the input/translation scale broadens
     * candidates only; it never broadens the actual field's half-open support.
     * Invalid bounds/geometry conservatively retain the candidate. Radial and
     * vertical limits are intentionally left to the existing field kernel.
     */
    inline bool mayIntersect(
            const Geometry& geometry, const CoordinateSystemTrafo& toLocal, const Vector& minimum,
            const Vector& maximum) {
        const double curvature = geometry.getCurvature();
        const double radius    = 1.0 / curvature;
        const double angle     = geometry.getArcLength() * curvature;
        if (!std::isfinite(radius) || radius <= 0 || !std::isfinite(angle) || angle <= 0
            || angle > std::acos(-1.0) + 1e-14)
            return true;
        double scale = std::max(1.0, radius);
        for (unsigned d = 0; d < 3; ++d) {
            if (!std::isfinite(minimum(d)) || !std::isfinite(maximum(d)) || minimum(d) > maximum(d))
                return true;
            scale = std::max(
                    {scale, std::abs(minimum(d)), std::abs(maximum(d)),
                     std::abs(toLocal.getOrigin()(d))});
        }
        const double sine = std::sin(angle), cosine = std::cos(angle);
        double maxEntrance = -std::numeric_limits<double>::infinity();
        double maxExit     = maxEntrance;
        for (unsigned corner = 0; corner < 8; ++corner) {
            Vector point;
            for (unsigned d = 0; d < 3; ++d)
                point(d) = (corner & (1u << d)) ? maximum(d) : minimum(d);
            const Vector local = toLocal.transformTo(point);
            if (!std::isfinite(local(0)) || !std::isfinite(local(2))) return true;
            maxEntrance = std::max(maxEntrance, local(2));
            maxExit     = std::max(maxExit, sine * (local(0) + radius) - cosine * local(2));
        }
        const double margin = 64 * std::numeric_limits<double>::epsilon() * scale;
        return maxEntrance >= -margin && maxExit >= -margin;
    }

    /** Replace mapped cyclotron membership; preserve all other candidates.
     * The composed transform matches ParallelTracker's ordinary element callback,
     * including misalignment. Bounds already reside on the host, so selection
     * needs neither particle copies nor additional MPI collectives.
     */
    inline Candidates select(
            const ElementList& sectors, const CoordinateSystemTrafo& toLab, const Vector& minimum,
            const Vector& maximum, Candidates mapped) {
        for (auto it = mapped.begin(); it != mapped.end();) {
            if ((*it)->getType() == ElementType::CYCLOTRONSECTOR)
                it = mapped.erase(it);
            else
                ++it;
        }
        for (const auto& sector : sectors) {
            const auto frame =
                    sector->getMisalignment() * (sector->getCSTrafoGlobal2Local() * toLab);
            if (mayIntersect(sector->getGeometry(), frame, minimum, maximum)) mapped.insert(sector);
        }
        return mapped;
    }
}  // namespace cyclotron_candidates
#endif
