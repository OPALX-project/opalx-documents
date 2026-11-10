# Space-charge radial line density

User requests 32^3 mesh, 32^3*8=262144 particles, last eight turns; logarithmic radial line density plot matching supplied example without inset.
Workspace: /Users/adelmann/git/opalx-master, branch 615-probe-command-does-not-work; coasting candidate-selection fix built and validated.

Found maintained input: /Users/adelmann/git/regression-tests-x/RegressionTests/Cyclotron-SC-Midpoint/Cyclotron-SC-Midpoint.in.
It already has 262144 fixed Gaussian particles, OPEN 32^3, STANDARD Green function, one GAMMAZ bin, BBOXINCR=2, MIDPOINT updates, total bunch charge 3.9486673247778873e-11 C (2 mA / 50.65 MHz), dt=1.6452780519907864e-10 s. Gaussian parameters/provenance are in /Users/adelmann/git/opalx/sandbox/cyclotron/SPACE_CHARGE_PLAN.md: initial rms positions 1 mm, transverse normalized rms emittance 1 mm mrad, longitudinal rms dp/p=1e-4. This is coasting 72 MeV, no RF.

Block to extraction-style peaks: ParallelTracker.cpp::timeIntegration2 explicitly requires one particle/one container/one rank for SINGLEGAP; supported accelerating example uses TYPE=NONE. Enabling PIC in that input is not a supported operation. Asked user to select coasting ten-turn demonstration (last eight overlapping profiles) or implement accelerating multi-particle space charge first. Dependent run is awaiting answer; no production source edits or simulation launched for this request.

Planned coasting path if selected: fresh copied fixture; HDF5 probes at laboratory Z=0 on positive radial axis, 0.1 mm binning, ten directed turns, final phase-space only and modest stats output; one MPI rank, selected OpenMP thread count. Verify termination/counts/charge/losses. Plot last eight complete crossings using common physical radial bins, q-weighted density [C/mm] or shared arbitrary scaling on log axis, no smoothing or inset. Keep per-turn labels and optional combined profile consistent with data. Record hashes/executable/source/settings/runtime; scientific Python ~/.venv-h6. No convergence/experimental reproduction claim.

User chose accelerating multi-particle space charge, then extraction profiles.
Implementation in progress (not yet validated): 3D thin RF gap preserves vertical momentum; unmanaged read-only field/kick descriptors reuse original kernels; Kokkos per-particle localized external step with frozen gathered self-field half kicks; ballistic midpoint prediction before gather and undone before transport; reference terminal time moved before gather. Added real device tests for individual RF times, 3D energy balance, uniform self-field, empty rank. Builds pending. No long accelerating PIC run yet. Current build log /tmp/bunch-build.log.
