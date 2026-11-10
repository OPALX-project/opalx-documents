// Copyright (c) 2026, Paul Scherrer Institute, Villigen PSI, Switzerland
#ifndef OPALX_CYCLOTRON_BUNCH_STEPPER_H
#define OPALX_CYCLOTRON_BUNCH_STEPPER_H
#include "AbsBeamline/CyclotronSector.h"
#include "AbsBeamline/RFCavity.h"
#include "Algorithms/DeviceExternalField.h"

/** Device event transport in laboratory SI coordinates. Each particle localizes
 * its own positive gap-plane crossings (40 bisections), ordered by arrival time.
 * Sector kernels own exact support. The caller brackets crossings with dt; a
 * plane may occur at most once per step. Descriptors borrow immutable map storage.
 * Self fields, frozen at the predicted midpoint, are split into two Boris half
 * kicks around this external transport. This is a thin-gap PIC approximation,
 * not a self-consistent solve inside an RF event. No collectives or allocations
 * occur within particle transport; failure leaves the caller's live views intact.
 */
namespace cyclotron_bunch {
    using Vector = Vector_t<double, 3>;
    struct Sector {
        device_external::Rigid frame;
        CyclotronSector::DeviceField field;
    };
    struct Gap {
        device_external::Rigid frame;
        RFCavity::DeviceGap field;
    };
    struct Lattice {
        Kokkos::View<Sector*> sectors;
        Kokkos::View<Gap*> gaps;
        /// Drift-kick-drift in the spatial magnetic map; no self fields or RF.
        KOKKOS_INLINE_FUNCTION bool magnetic(Vector& r, Vector& p, double dt, double mass) const {
            Vector x = r, v = p;
            x += (0.5 * dt * Physics::c / Kokkos::sqrt(1 + dot(v, v))) * v;
            Vector b(0);
            bool supported = false;
            for (size_t j = 0; j < sectors.extent(0); ++j) {
                const auto& sector = sectors(j);
                Vector localB(0);
                supported = sector.field.add(sector.frame.pointTo(x), localB) || supported;
                b += sector.frame.vectorFrom(localB);
            }
            if (!supported) return false;
            BorisPusher().kick(x, v, Vector(0), b, dt, mass, 1);
            x += (0.5 * dt * Physics::c / Kokkos::sqrt(1 + dot(v, v))) * v;
            r = x;
            p = v;
            return true;
        }
        /// Whole external step, including independently timed RF impulses.
        KOKKOS_INLINE_FUNCTION bool advance(
                Vector& position, Vector& momentum, double time, double dt, double mass) const {
            if (gaps.extent(0) > 64 || !(dt >= 0)) return false;
            Vector r = position, p = momentum;
            unsigned long long visited = 0;
            double remaining           = dt;
            while (remaining > 0) {
                Vector endR = r, endP = p;
                if (!magnetic(endR, endP, remaining, mass)) return false;
                double earliest = remaining;
                int selected    = -1;
                for (size_t j = 0; j < gaps.extent(0); ++j) {
                    if (visited & (1ULL << j)) continue;
                    const auto& gap = gaps(j);
                    if (!(gap.frame.pointTo(r)(2) < 0) || gap.frame.pointTo(endR)(2) < 0) continue;
                    double low = 0, high = remaining;
                    for (int iteration = 0; iteration < 40; ++iteration) {
                        double mid    = .5 * (low + high);
                        Vector trialR = r, trialP = p;
                        if (!magnetic(trialR, trialP, mid, mass)) return false;
                        if (gap.frame.pointTo(trialR)(2) < 0)
                            low = mid;
                        else
                            high = mid;
                    }
                    Vector trialR = r, trialP = p;
                    if (!magnetic(trialR, trialP, high, mass)) return false;
                    if (gap.field.supports(gap.frame.pointTo(trialR)(0)) && high <= earliest) {
                        earliest = high;
                        selected = j;
                    }
                }
                if (selected < 0) {
                    r = endR;
                    p = endP;
                    break;
                }
                if (!magnetic(r, p, earliest, mass)) return false;
                time += earliest;
                remaining -= earliest;
                const auto& gap = gaps(selected);
                auto localP     = gap.frame.vectorTo(p);
                if (!gap.field.apply(gap.frame.pointTo(r)(0), time, mass, localP)) return false;
                p = gap.frame.vectorFrom(localP);
                visited |= 1ULL << selected;
            }
            position = r;
            momentum = p;
            return true;
        }
        /// Frozen gathered self fields [V/m,T] in laboratory axes, Strang half kicks.
        KOKKOS_INLINE_FUNCTION bool advanceWithSelfFields(
                Vector& r, Vector& p, const Vector& e, const Vector& b, double t, double dt,
                double mass) const {
            Vector x = r, v = p;
            BorisPusher().kick(x, v, e, b, .5 * dt, mass, 1);
            if (!advance(x, v, t, dt, mass)) return false;
            BorisPusher().kick(x, v, e, b, .5 * dt, mass, 1);
            r = x;
            p = v;
            return true;
        }
    };
}  // namespace cyclotron_bunch
#endif
