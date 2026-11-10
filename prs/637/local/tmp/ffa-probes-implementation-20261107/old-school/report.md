# Old OPAL FFA school probe baselines

Prepared 7 November 2026. Integration evidence only: original school inputs, production C++ and native unit tests are unchanged.

## Provenance

Executable: /Users/adelmann/OPAL-2022.1/bin/opal.
SHA256: 3e20fe1e8b040e10dcbb958b2d1a92d5020f5397361b230a615c0e41ca0b5ecd.
Binary reports OPAL2022.1.0 revision a4e0e14466557289b4f7a843fb9eb72700ff1992 in HDF5 root metadata. This exact commit exists locally; relevant sources are copied under legacy-source/ with legacy-source-manifest.json SHA256 checksums.

Previously inspected release tag OPAL-2022.1.0 is commit0d1bf29f85c1799203116a6781db7fbb178b918c. Relevant Ring, RingSection, ScalingFFA, Probe, PluginElement, ParallelCyclotronTracker, PeakFinder, Track and parser sources are identical. Only LossDataSink changes: the release tag removes one destructor MPI barrier. See installed-vs-release.patch; no crossing numerics/output-format change.

Sources are FFA25-school/migration-audit/legacy-16-cell.in and legacy-fourfold.in. Each launch.json records source/input/distribution/executable hashes, full initial state, actual timestep, command, process result, requested/recorded steps, station counts and losses. prepare_and_run.py uses fresh run directories and checked process status; no optimizer or random fallback. Some initial trial launches lose the particle despite process return0, so explicit completion/loss inspection is required.

The16cell spiral is3.142/4 as actually invoked in the original notebook, matching native CASES; the extracted migration-audit file used pi/4. The D-off variant uses the notebook's55-degree spiral and BD=0. Other fields, supports, apertures and physical station lists are unchanged. Runs use one particle, no space charge and the original fourth-order Runge–Kutta integrator (confirmed in run.log). Vertical variants use1mm old z displacement.

## Accepted runs

Every accepted run returns0, records exactly the requested number of pre-step orbit samples, retains the particle and creates exactly4 or16 physical probe files. See accepted-baselines.json for exact initial states and radial ranges.

| Directory | Stations | Steps | Physical crossing records |
|---|---:|---:|---:|
| 16-cell-steps10000-scale1 | 16 | 10000 | 57 |
| 16-cell-steps10000-scale1-vertical | 16 | 10000 | 57 |
| 16-cell-steps20000-scale0.5-refined | 16 | 20000 | 57 |
| 16-cell-steps20000-scale0.5-vertical-refined | 16 | 20000 | 57 |
| 55deg-d-off-steps10000-scale1-negative-pr | 16 | 10000 | 61 |
| fourfold-steps10000-scale1-valid | 4 | 10000 | 15 |
| fourfold-steps20000-scale0.5-valid-refined | 4 | 20000 | 15 |
| 55deg-d-off-steps20000-scale0.5-negative-pr-refined | 16 | 20000 | 61 |
| 16-cell-steps40000-scale0.25-quarter | 16 | 40000 | 57 |

Physical records exclude two identical initial-plane t=0 records emitted by oldPROBE1. Original files retain both. Native OPALX suppresses initial-plane records. The16cell runs span about3.6 physical revolutions, fourfold about3.9, D-off about3.8. These are short probe comparisons, not long-term tune/convergence studies.

## Matched state and timestep

Metadata initial_old_x_y_z_px_py_pz lists positions[m], then momenta p/(mc). Native lab R=(old_x-R0,old_z,old_y), P=(old_px,old_pz,old_py). The school adapter reverses this explicit conversion.

P_MASS=938.272MeV in the school determines its P0 formula. PARTICLE=PROTON selects physical mass938.27208816MeV, so actual bare tangent beta-gamma is.16044470156470977 for nominal12MeV and.08003096964411771 for nominal3MeV; actual energies11.999998886718801 and2.9999997190185437MeV. Nonzero-radial-momentum launches adjust the tangent offset to preserve that total momentum. Match full6D, not just nominal energy.

TRACK truncates STEPSPERTURN to integer. Actual dt at STEP_SIZE=.01m,BFREQ1MHz is1e-6/4752s (16cell/Doff),1e-6/2393s (fourfold). STEP_SIZE=.005m gives1e-6/9505s and1e-6/4786s. Fourfold refinement is exactlyhalf;16cell almosthalf. NUM_TURNS controls a5000*NUM_TURNS step budget, not exact physical revolutions.

## Old turn labels and output precision

Installed ParallelCyclotronTracker.cpp:2789 implements isTurnDone as(step_m+1)%stepsPerTurn. Thus probe turn labels advance at1us RF-step intervals, not the~.59us physical revolution of16cell. A constant+1 does not map these labels to native directed turns. Compare by station,stableID and chronological passage/time, retaining original labels. Do not force parity by silently relabeling differing trajectories.

Old PROBE extrapolates a pre-step state using current momentum; native PROBE interpolates accepted endpoints coherently. Differences can depend on timestep, especially momentum sampling. Native particle integration may use a different pusher; record that distinction and assess timestep convergence rather than assigning all differences to detector interpolation. Legacy lossASCII has six significant digits; orbitASCII eight scientific decimals. HDF5 in single-particle legacy mode is metadata-only even when enabled, so it is not a full-precision particle baseline.

## Excluded attempts and loss cause

All other local trial directories are excluded as primary comparison baselines; see excluded-launches.json. Fourfold R4m,pr0 and the native CASE.guess R3.9849687589484386m,pr+.0087047468374380575 fail to survive. CASE.guess is an initial solver guess, not a solved closed orbit.

The latter saved RINGDEF.loss state is R=(-3.82181,.461527,.00304534)m, radius about3.84958m, below original lower radial field support R0-RADIAL_NEG_EXTENT=3.85m. All ScalingFFA fields reject that radius; Ring::apply reports out-of-bounds. The process returns0 after ending early. The original notebook's stored fourfold optimizer output also contains MPI_ABORT and a huge missing-data/random objective; it supplies no trusted closed orbit.

A small deterministic state scan found surviving negative-radial-momentum launches without changing fields or apertures. Accepted fourfold R=(4,0,.001)m,P=(-.0087,.07955668483652201,0) survives at coarse/refineddt. D-off positive-pr trial similarly loses; the accepted negative-pr full state is explicit in its metadata. Every trial and raw loss record is retained.

No old/new bitwise equivalence,long-term stability,tune convergence,space-charge parity or performance result is claimed by baseline preparation.

## Final focused refinements

The native comparison requested one D-off half-step run to quantify its legacy current-step momentum difference and one 16-cell quarter-step run to assess the residual radial-position floor. Both retained identical accepted fields and full initial states and completed without loss. D-off uses 20,000 steps, STEPSPERTURN 9505 and dt=1.0520778537611783e-10s. The 16-cell quarter case uses 40,000 steps, STEPSPERTURN 19010 and dt=5.260389268805892e-11s. These are the only additional refinement cases; they establish input/output evidence, while the native comparison driver measures the old/new differences.
