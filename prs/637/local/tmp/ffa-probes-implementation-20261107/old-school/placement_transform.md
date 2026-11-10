# Independent legacy Ring → native FFA placement verification

7 November 2026. Read-only production-source audit. The executable source revision is a4e0e14466557289b4f7a843fb9eb72700ff1992; pinned source copies and manifests accompany this note. Integration analysis files are the only additions.

## Derived geometry

Let a = LAT_PHIINIT + sum(previous MAGNET_END)/R0, in radians. The legacy Ring places the next element at

    start = R0 (sin a, cos a, 0)
    tangent = (cos a, -sin a, 0).

For a physical point (r cos theta, r sin theta, z), RingSection translates to start, rotates by a and cycles axes (x,y,z)→(y,z,x). Its local T-frame radial vector is

    (x_local+R0, z_local) = r (sin(theta+a), cos(theta+a)),

so phi_old = pi/2 - theta - a (with the usual local atan2 wrapping). This is clockwise placement viewed in the legacy horizontal X–Y plane. It cannot be converted by merely relabeling the current native template's counterclockwise phi=a+offset.

For the school fringe, let L=X0_START+X0_END. Old Enge::getCentreLength returns x0/2, so AsymmetricEnge returns L/4; ScalingFFAMagnet then adds half of that to MAGNET_START. The actual old profile argument is

    u_old = pi/2 - theta - a - (MAGNET_START+L/8)/R0
            - tan(delta_old) log(r/R0).

Current native Mode-A placement sets the profile centre offset to L/(2R0) from the entrance. Define

    phi_template = a + (MAGNET_START-3L/8)/R0
    phi_native_entrance = pi/2 - (phi_template+L/R0)
    tan(delta_native) = -tan(delta_old).

Then u_native=-u_old. Equivalently, the new entrance is pi/2-a-MAGNET_START/R0-5L/(8R0). Apply this to each physical magnet in a COPY of the migrated template. Its old clockwise sequence corresponds to a reversed physical field layout; do not change the canonical native beam/frame convention or PROBE geometry to disguise the mismatch.

## Magnetic field and off-plane parity

The agreed position map is native(X,Y,Z)=(old_x-R0,old_z,old_y). Its axis permutation has determinant -1. Magnetic field is an axial vector, hence

    B_native = (-B_old_x, -B_old_z, -B_old_y).

The existing B0_native=-B0_old is therefore required. Under u_native=-u_old and tan(delta_native)=-tan(delta_old), the scaling-series recurrence gives cylindrical component mapping

    Br_native=-Br_old,
    By_native=-Bvertical_old,
    Bphi_native=+Bphi_old.

The azimuthal basis reverses with the placement direction, yielding exactly the laboratory axial-vector map above. This holds off midplane, including all retained vertical expansion terms. Ordinary position/momentum vectors use the direct axis permutation, without the magnetic-field minus sign.

## Asymmetric Enge: do not swap twice

The generic scalar-profile requirement is F_native(u)=F_old(-u). Current native AsymmetricEnge already changes the old start/end argument convention:

    old:    F(u)=E_start(u-x0_start)+E_end(-u-x0_end)-1
    native: F(u)=E_start(-u-x0_start)+E_end(u-x0_end)-1.

Therefore retain the same START/END half-lengths, fringe lengths and coefficient arrays for this API. An additional start/end swap would undo the needed reflection for a genuinely asymmetric profile. The school uses identical ends, so its profiles would not expose a mistaken double swap. Other end-field families require their own profile reflection check.

## Independent numerical algebra check

Run ~/.venv-h6/bin/python check_field_transform.py. It implements the literal old frame matrices, current native entrance matrices and scalar field-series equations independently. Analytic Enge derivatives are calculated by truncated Taylor series, including a deliberately asymmetric profile. It does not call native C++ kernels or serve as a unit-test dependency.

450 points cover three placements, radii 0.99/1/1.01 R0, five angular offsets, midplane and vertical offsets ±1/5 mm. Maximum component errors are 8.05e-15 T (school profile) and 7.05e-15 T (asymmetric profile). Omitting the spiral reversal produces a 0.3113 T negative-control error. Results are in check_field_transform.json. These are algebraic mapping checks; actual old/native integration remains necessary to validate parser, resolved placement, field selection, support and pusher behavior.
