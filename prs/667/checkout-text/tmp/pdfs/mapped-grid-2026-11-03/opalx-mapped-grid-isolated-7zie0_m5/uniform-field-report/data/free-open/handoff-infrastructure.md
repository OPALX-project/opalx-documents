# FFT2D5 free-space infrastructure audit

Date: 2026-11-02. Read-only production audit by subagent `free_infrastructure_audit`.
Goal: identify existing geometry, density, gather, and nonlocal-kernel infrastructure for the finite 5 m beam at R = 2 m. No production files were changed and no build was run.

## Critical interfaces and units

- `src/SpaceCharge/FFT2D5/ReferencePath.h:19`: a `ReferencePath` owns a `Kokkos::View<Vector_t<double,3>*>`. Public access is `deviceView()` and `length()`.
- `ReferencePath.cpp:38–67`: the loader parses the path file's 15 columns but stores only Cartesian positions. It ignores supplied s, momentum, and fields. Path length is the sum of Cartesian chord lengths. It does not store curvature, a cumulative-s index, metric factors, or a smoothly interpolated frame.
- `FFT2D5Algorithm.hpp:429–477`: particle-to-path mapping finds the closest clamped line segment. Its frame is tangent `t = segment/|segment|`, fixed vertical `n = (0,1,0)`, outward horizontal `b = n cross t`. The transverse coordinates are projections on b and n; s is the cumulative chord length plus distance along the chosen segment. This is appropriate for the present horizontal x–z curve; the fixed n is not a general three-dimensional transported frame.
- `FFT2D5Algorithm.hpp:383–397`: charge deposition is divided by `dt*du*dy*ds`. There is **no Jacobian J** in deposition. Consequently the staged `rho3D` is coordinate density `dq/(du dy ds)`. In a circular tube it represents `rho_physical*(1+u/R)` when the physical density is uniform. A source-cell charge is therefore `q = rho3D*du*dy*ds`; multiplying by J again would double-count the curvature metric.
- `FFT2D5FieldStorage.h:45–106`: the persistent fields are `ScalarField3 chargeDensity()` and `VectorField3 electricField()`. Existing public geometry accessors are `spacing()`, `origin()`, `size()`, `meshSize()`, and `layout()`. The grid covers `(-Wx/2,-Wy/2,0)` to `(Wx/2,Wy/2,pathLength)`. The two-dimensional `workspace()` and `solveSlice()` reuse one FFT workspace.
- `FFT2D5Algorithm.hpp:577–649`: the existing solve clears the staged E field and solves occupied slices separately. Open s-boundary ghost slices are zero; closed ones wrap. This has no nonlocal finite-bunch Coulomb contribution between slices.
- `FFT2D5Algorithm.hpp:652–813`: gather interpolates E from the staged grid, constructs transverse self B, then assigns the old/local longitudinal field according to the selected longitudinal model before rotating E/B back into Cartesian coordinates (`convertFromFrenetSerret`, lines 894–897). A replacement all-component OPEN solve must avoid overwriting its Es with the local g-factor expression.

The comments in deposition state that positions and charge density remain in laboratory coordinates; the helper `boostToBeamFrame()` changes the particle momentum used by diagnostics, not the geometric density. For this low-beta frozen-field benchmark, relativistic differences are O(beta²), about 10^-6. A general curved relativistic source model requires an explicit later decision and cannot be inferred from the name of that helper.

## Existing nonlocal solvers: limited reuse

Searches of OPALX and IPPL source found no octree, Barnes–Hut, or FMM implementation.

`src/SpaceCharge/Poisson/P3MAdapters.h` reuses spatial overlap/neighbour pairs for the short-range Ewald part, but its long-range solve is still a Cartesian 3D FFT (`FFTTruncatedGreenSolver_t<double,3>`). It does not avoid the Cartesian volume/aspect-ratio problem of the long curved tube. The neighbour machinery is tied to the Cartesian particle layout; it is not a drop-in tree over Frenet source cells.

IPPL contains an exact rectangular-cell **potential** kernel:

- `build-omp/_deps/ippl-src/src/PoissonSolvers/FFTOpenPoissonSolver.hpp:967`: `integratedGreenAtanTerm` uses a principal atan ratio and explicit zero-denominator limits.
- Line 984: `integratedGreenLogTerm` handles zero prefactors.
- Line 994: `integratedGreenAntiderivative(x,y,z)` is the triple primitive of 1/r.
- Lines 1015–1038: `integratedGreenAverage(x,y,z,h)` takes the eight corner differences and divides by Cartesian voxel volume.

These helpers are private static functions in `FFTOpenPoissonSolver`, not public kernel utilities. They supply a useful implementation pattern and limit conventions, but no direct E primitive, source-cell tree, oriented prism, or curved voxel integration. The 3D backend itself would still require a Cartesian volume grid.

## Feasible new tree route, with necessary qualifications

A tree over occupied source cells can use physical cell charges `q = rho3D*du*dy*ds` and their mapped Cartesian positions. For a generic grid cell, the missing reusable piece is inverse path interpolation `X(s,u,y)` and its local frame. That should share the path representation used for deposition, to avoid a source/target geometry mismatch.

Near source cells should not be treated as softened point charges: ds can be orders of magnitude larger than du or dy. A tangent rectangular prism is a feasible near-cell approximation. Its tangential physical width is approximately `J*ds`, and physical density is `q/(J*du*dy*ds)`. A curved voxel is only approximately that prism; longitudinal/path refinement must bound the geometry error. Arbitrary source profiles must come from deposited density, not a fitted uniform/triangular model.

An exact flat-prism field can be obtained by face integrals. With source bounds measured relative to the target, define

`F(y,z;d) = y log(z+r) + z log(y+r) - |d| atan(y*z/(|d|*r))`,

where `r = sqrt(d*d+y*y+z*z)` and the last term is zero at d = 0. The face potential is the two-dimensional corner difference of F. Then

`E_x/(k*rho) = I_face(x_hi) - I_face(x_lo)`,

with cyclic formulas for y and z. Zero times logarithm terms need analytic limits. The absolute value of d and principal atan are important: a naive atan2 continuation across a negative d creates spurious branch terms. This handles a flat cell containing its target and yields zero self field at its centre.

A small independent NumPy/Gauss–Legendre check in memory compared this formula with direct three-dimensional integration. Two nonsingular prisms agreed to 2.2e-15 relative vector norm; a highly anisotropic near prism agreed to 1.8e-6 with only 90 quadrature points per direction (the direct quadrature, not the closed form, was underresolved). A centred symmetric prism gave the exact zero field. These are derivation checks, not production validation or a curved-cell error bound.

Tree accuracy must be judged against the weak curvature signal as well as the strong transverse field. In the existing uniform SACR target set, central radial E is about +0.05509 V/m whereas the transverse scale is about 13.07 V/m. One percent of the central signal is only 0.000551 V/m. A monopole tree tolerance of one percent of the bulk transverse scale would be insufficient by roughly two orders of magnitude. Higher multipoles, conservative opening, and convergence at the centre/end targets are needed. For mixed-sign sources, use geometric node centres and moments including dipole/quadrupole plus absolute-charge bounds; a charge-weighted centroid or dropping a neutral node is unsafe.

## Costs and unresolved design choices

At Nx=128, Ny=64, Nz=8192, the staged grid has 67 million cells, about 1.6 GB for E plus 0.54 GB for rho before halos/workspace. For a=5 mm and c=0.5 mm in a 16 mm by 4 mm box, roughly 12% of transverse cells are occupied, still about 8 million occupied sources. Full tree evaluation at every occupied cell or tens of millions of particles is substantial work even though it avoids a Cartesian enclosing grid. A simpler nonlocal correction using the existing slice solve may be more economical; it must be derived and independently converged rather than assuming a tree automatically meets the target.

The 5 mm-inside-end probe and the triangular cusp are sensitive to longitudinal deposition width. Cell integration fixes point-source singularity errors but not profile smearing. Nz/path refinement, reference-path chord refinement, transverse refinement, and tree/kernel approximation refinement are distinct error controls. Relevant single-rank and multi-rank checks remain required after any implementation.

## Status and next step

No public interface was changed. The existing pipe model remains a side control and unrelated dirty FFA files were not touched. The root/design agents should select the nonlocal OPEN algorithm, then verify its source geometry and density metric against the independent SACR reference before investing in the largest mesh runs.

## Follow-up: smooth geometry implementation

Root subsequently assigned implementation of new files only. Added:

- `src/SpaceCharge/FFT2D5/FFT2D5Geometry.h`
- `src/SpaceCharge/FFT2D5/FFT2D5Geometry.cpp`
- `unit_tests/SpaceCharge/TestFFT2D5Geometry.cpp`

No existing production file or CMake file was edited by this subagent. Root integrates the files and uses geometry only for the new finite-source OPEN path.

The value object defaults to disabled (`isValid()==false`) and can be captured in Kokkos kernels. API: `fit(pathView)`, `transformed(rigidTransform)`, `pathLength()`, `signedCurvature()`, `isStraight()`, `metric(u)`, `position(local)`, `toFrenet(point)`, `basis(s,b,n,t)`, `toLocalVector(vector,s)`, and `toGlobalVector(vector,s)`. Fit occurs once in laboratory coordinates and the complete frame/origin is subsequently transformed for each solve; this avoids rejecting a horizontal lab circle after a general solve-frame rotation.

Straight lines can have arbitrary 3D direction. Their normal is the perpendicular lab-y projection, with lab-z fallback for a vertical line. Curves must be horizontal circles, with explicit finite/radial/order checks. Duplicate points, reversing paths, arbitrary/nonplanar curves, and full/multiple turns are rejected. Arc length is exact, not summed chord length. Positive signed curvature means `t'=-kappa*b` and `J=1+kappa*u`. Midpoint angle unwrapping supports arcs exceeding pi radians, including the 8 m R=2 m reference, while retaining small negative or beyond-end s values for coverage checking.

Validation: isolated compilation of geometry/test and linking against current OPALX/IPPL/gtest succeeded. All 7 geometry unit tests passed with 1 rank and with 2 MPI ranks. Test coverage includes both curvature signs; >pi arcs; unclamped endpoint coordinates; tilted/vertical straight lines; general rigid solve-frame transformation; metric derivative; Kokkos-kernel execution; and rejection of unsupported paths. The derivative test uses 2e-10 absolute tolerance because subtracting metre-scale positions with h=1e-5 has O(epsilon/h) roundoff (first 5e-11 bound failed at 7.2e-11; this was a test discretization bound, not a physics tolerance). Two-rank launch required `mpirun --oversubscribe --map-by slot --bind-to none -n 2`, with `OMP_NUM_THREADS=1 OMP_PROC_BIND=false`; default local MPI mapping failed before launching tests.

Read-only root-integration audit: exact mapping is now shared by OPEN scatter and gather, source charge normalization remains correct, and the nonlocal gather returns before local-g Es overwrite. Curved velocity rejection is inside frame restoration's try/catch. Flagged to root: common straight gamma is currently taken from the last active container while each container gathers with its own mean Pz; differing active source velocities need a clear common-velocity restriction. Also, curved gather's `B=beta*t_target cross E/c` remains a local approximation, not a nonlocal magnetic solve. The current beta=0.001 frozen electric-field target is within the intended electrostatic scope; beta<=0.1 alone is not a proven 1% bound for each cancellation-small field component.

## Follow-up: numerical-stage test scope

Root assigned `unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp` only. Its historical fixture had implicitly selected OPEN while testing isolated transverse-slice stages, arbitrary polylines, local g-factor gradients, and closed-ring wrapping. Those are different numerics from the new finite-source OPEN solve.

The fixture now explicitly selects NONE for transverse-slice/polyline stage tests. The total/line density, line gradient, longitudinal gather, closed/open boundary legacy field tests, and main-API/direct-stage compatibility checks explicitly select CIRCULAR. Their expected longitudinal coefficient is independently computed from the specified legacy CIRCULAR formula `0.67+2 log(b/a)`; hardcoded old OPEN `6.36` values are removed. The three-source periodic test documents its deposited CIC gradients (+0.5 at the pair, -1 at the endpoint) and gamma²=2, rather than retaining an opaque decimal field snapshot. All original numerical tolerances remain unchanged. The new CIRCULAR_UNIFORM analytic-potential, radius-independence, and physical-wall tests were not changed. The finite OPEN path-end rejection test explicitly retains OPEN; independent new backend/API tests cover finite fields elsewhere.

Built `cmake --build build-omp --target TestFFT2D5Numerics -j 2`. Ran all 70 numerical tests with OMP_NUM_THREADS=2: 69 passed and only `Configuration_MultipleRanksRejected` was intentionally skipped on 1 rank. Ran that skipped case with 2 ranks using explicit slot mapping; it passed on both ranks. No OPALX executable relink was requested; production library was already up to date. Afterwards only expression factoring and comments were adjusted for readability, without changing the expected algebra or tolerances. Root's final rebuild/test run should consume that last formatting cleanup.
