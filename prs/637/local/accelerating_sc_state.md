# Accelerating PIC and last-eight-turn profiles

User approved extending accelerating SINGLEGAP transport for space charge, then running 32^3 cells, 32^3*8=262144 particles and plotting radial line density of the last eight turns without inset. FFA probes remain deferred.

Workspace /Users/adelmann/git/opalx-master, branch 615-probe-command-does-not-work. All earlier probe/coasting fixes retained. No commits/pushes.

Implementation:
- CyclotronSector common host/device field formula moved into header; borrowed unmanaged device descriptor exposes same immutable map/coil data.
- RFCavity borrowed device gap descriptor uses existing RF profile/kick.
- RF kick supports 3D forward protons: includes py in gamma/transit speed and subtracts py^2 from outgoing pz^2; py unchanged. No vertical voltage variation/focusing is modeled.
- New Algorithms/CyclotronBunchStepper.h Kokkos event transport: exact spatial map support, individual positive gap-plane arrival localization with 40 bisections, earliest event first, at most 64 gaps, no allocations/collectives inside particle kernel.
- PIC MIDPOINT ballistic half-drift predictor, gather existing self fields, undo predictor, frozen-self-field Boris half kicks around external magnetic+RF transport. PRESTEP samples initial positions. Approximate collective split, not Poisson solve at each particle event; needs refinement checks for quantitative use.
- Reference event stop localized before PIC prediction/gather. terminalStepDt_m prevents selectDT restoring nominal dt. Reference remains external-field-only; finite bunch shares accepted duration, individual particles may be before/after a discontinuous RF kick at that time.
- Retained established host one-particle/NONE path for exact backward compatibility at reference terminal discontinuity. Other bunches use device kernel. Original TrackRun solver NONE-only guard removed.
- Error count collective after kernel; single container/unpolarized positive protons/no restart retained. CUDA not tested.

Tests so far:
- TestCyclotronSector, TestCyclotronSectorMPI, TestCyclotronRF pass, including actual device tests for distinct particle arrival phases, 3D energy balance/vertical momentum, frozen uniform electric self field, empty MPI rank. First test attempt used invalid negative gap RMIN; corrected fixture to legal positive support.
- 100-step full 262144-particle 32^3 PIC benchmark passes.
- 720-step nominal one-turn accelerating PIC run at 164.5278 ps passes, all 262144 retained, five reference gap events.
- Initial device single-particle full-cycle comparison exposed (1) nominal dt being restored after terminal localization (fixed via terminalStepDt_m), (2) final RF impulse discontinuity from sub-ulp arrival differences; retained original host single-particle event convention. Need rerun final full-cycle parity on current executable.
- Seven focused CTest targets last run pending result session 77891.

ACTIVE FULL RUN:
- tmp/ring-space-charge-profiles-20261023/accelerating-pic, one rank/four OpenMP threads.
- Started by reproducible run_acceleration.py, tool exec session 78471. launch.json contains actual PID, binary/input hashes, git revision/diff, start time. Do not duplicate/kill unrelated processes.
- Fixed Gaussian samples from maintained Cyclotron-SC-Midpoint: 1 mm rms coordinates, normalized transverse rms emittances 1 mm mrad, longitudinal dp/p 1e-4. Centered and rigidly rotated into established 72 MeV accelerating launch. Bunch charge 3.9486673247778873e-11 C = 2 mA/50.65 MHz. This is an initially sampled Gaussian, not a demonstrated matched accelerating equilibrium.
- OPEN solver, one GAMMAZ bin, STANDARD Green function, BBOXINCR=2, MIDPOINT. 164.527805 ps (720 nominal injection steps/turn), target reference 590 MeV, max180000 steps. This is a coarse diagnostic, not converged extraction physics.
- Probe positive lab X axis, radial segment4320..4450 mm, Z=0, 0.1mm bins, only outer turns intersect, avoids storing hundreds of full bunch passages. Final PSDUMP only; stats every100steps.
- Merlin6 SSH hostname did not resolve; no remote job or remote filesystem changes.

Next:
1. Check active run progress/exit and current focused tests. Save smoke/parity/zero-charge/MPI diagnostics, review code, validate/render manual changes.
2. Prepare reproducible analysis that reads completed probe HDF5 q-weighted common radial bins, selects final eight complete reference-turn groups (check per-turn particle counts/charge/clipping/time); no inset or smoothing. Produce PNG/PDF/CSV/summary with settings, charge/losses and limitations.
3. Wait for long run while doing independent validation. If aborts, preserve failure and diagnose; do not relabel partial outputs as final.
4. Verify normal EKINSTOP completion, actual steps/time/reference and mean energy; review final plot and report real limits. No FFA work.

Artifacts staging scripts and inputs in tmp/ring-space-charge-profiles-20261023; study Python ~/.venv-h6. Earlier coasting diagnosis remains in COASTING_FIX_STATE.md.


Validation update:
- All seven focused CTest targets passed (CyclotronSector, CyclotronSectorMPI, CyclotronRF, TrackReferenceStep, DeviceExternalField, CyclotronProbe, CyclotronProbeMPI).
- Full-cycle single-particle comparison after preserving the host endpoint convention passes: maxima over all 546 saved states x=3.02e-12 m,z=3.65e-12 m,px=1.82e-12,pz=6.56e-13. Small rounding changes from exposing the shared field formula; no tolerance rebaseline.
- tools/check_cyclotron_bunch.py maintained integration harness passes: near-zero OPEN (1e-30 C because adapter intentionally rejects exact zero charge) vs NONE maxposition2.67e-15 m; charged one/two-rank physical-state sets maxposition8.45e-15 m, maxmomentum2.78e-15. Resolved charged momentum change1.02e-4. FROMFILE sample-to-ID mapping differs with rank count, so MPI state-set comparison sorts by unique x; IDs unique per run. No numeric tolerance widened.
- Initial harness failures preserved: exactzero PIC explicitly rejected as expected adapter contract; MPI ID-sorted mismatch was sample-ID remapping, physical states agree after spatial matching. Final report bunch-integration-final/report.json.
- Manual source58chapters and edited page HTML validation64pages passed. Subsequent diagnostic-array wording clarified; final render pending.
- Full run active at step3000 (~79.6 MeV) as of11:02 local; measured about100sec/1000steps implies several hours to target. All262144 retained so far. No final density plot yet.
- finish_when_done.py (session54268) waits for this one launched run to complete and executes plot_last_eight.py automatically. Plotting strictly requires normal EKINSTOP completion and eight complete262144-particle probe passages with correct per-turn charge. Writes PNG/PDF/CSV/profile-summary.json. This is a continuation of this simulation process, not a recurring scheduled automation.
- Important scope: one transported bunch and its successive turn passages. Space charge between neighbouring turns/bunches is not included. No septum modeled, no inset. Coarse PIC and unmatched initial Gaussian are explicitly labeled.
- Code diff reviewed; git diff --check clean. Existing PROBE work preserved; no pushes/commits. CUDA untested. Remaining task is long-run completion, any failure diagnosis, and actual plot review.

Current progress: step4000, mean82.314MeV, all262144particles retained. Exact running binary copied to study opalx-run; source-snapshot/tracked.patch plus added source/test/tool files preserve implementation. Current executable hash37d808d742b4cb7bdbb8ac203a9433ab999bbf914f41f4fa17c6b652615cc918. Subsequent edits are comments/formatting/analysis only.

## User reduction to16^3 (2026-10-23)
User requests16^3 cells and8*16^3=32768particles; check whether completed and show last-eight-turn density if available.
32^3 run was still running around turn7/~86MeV. Verified own PID12128 command then sent SIGTERM; partial run preserved, not interpreted as completed. Its waiting analysis exits on failed/cancelled launch.
New fresh case: tmp/ring-space-charge-profiles-20261023/accelerating-pic-16. Same frozen opalx-run binary, charge/current, fields, timestep and590MeV target. Seed61516 subset32768 of original samples; centered and Cholesky covariance matched in6D to original population (max covariance error2.12e-21, meanerror6.72e-15). Input hashes/provenance in input-manifest.json, reproducible reduce_to_16.py.
Launcher run_acceleration_16.py, final plotting plot_last_eight_16.py, completion continuation finish_when_done_16.py. Output directory profiles-16; no final plot yet because run just started. One rank/four OpenMP threads. Preserve this active run; no duplicate launch.

## Terminal16^3 outcome, 2026-10-23 11:50 local
The run failed (MPI exit156) after2471.19s (~41.2min), after completing directed turn187. Last reference gaps RF1=583.4041MeV and RF3=584.1575MeV, then ParallelTracker error: "SINGLEGAP particle left field support or received an unphysical kick." This combined error does not distinguish the cause or particle ID. Last logged population32561 of32768 (207 particles removed by10-sigma boundary during transport). Target590MeV not reached. Probe output was buffered until normal completion, so radial.h5/hist/peaks are absent; no valid completed last-eight-turn plot can be shown. finish_when_done_16.py correctly refused analysis on failure. No restart or duplicate simulation performed. Heartbeat disabled following terminal failure. Next engineering task, if requested: instrument distinct support/kick failure and particle state; review loss handling and periodic probe flushing/checkpointing before rerunning. Do not silently drop failed particles or widen supports/tolerances.

## Periodic flushing and8^3/580MeV request
User authorized periodic probe flushing, diagnosing584MeV failure, and revised run8^3 cells,8*8^3=4096particles,target580MeV. Current case tmp/ring-space-charge-profiles-20261023/accelerating-pic-8-580; launcher run_acceleration_8.py; active exec session92792. Same2mA/39.49pC bunch charge, full6D covariance matched subset seed6158. Wider probe1900..4700mm avoids clipping and is affordable at4096particles. Particle snapshots every1000steps.
Implemented recorder save() using APPEND (fresh basename guard remains); cumulative hist/peaks overwritten from cumulative local counters. Main tracker flushes every100acceptedsteps and flushes accepted endpoints before rethrowing collective SINGLEGAP OpalException. Failed step not observed. Tests cover repeated empty flush, HDF5 multiple steps, ASCII append, cumulative counts and preserved histories on one/two ranks. Initial tests omitted reverse-direction arming observation; corrected trajectory fixture without changing crossing kernel. All4focused targets pass: CyclotronProbe/MPI and CyclotronSector/MPI.
New device diagnostics distinguish FieldSupport/GapKick/InvalidStep, reporting first bad particle per rank, ID, gap index, time and laboratory R/P; tests exercise actual support and kick rejections, transactional state. Old16failure cannot be retrospectively resolved to exact particle because buffered endpoints/snapshots absent; do not claim precise diagnosis without reproduction. No tolerances/supports/physics formula relaxed.
Current8run passed12turns/~95MeV and radial.h5 already flushed4.6MB to disk. Final8analysis plot_last_eight_8.py validates completion, last8complete passages using final-survivor IDs, per-particle charges and loss-aware counts. No final density plot yet. Need monitor run, execute analysis on successful580MeV completion, inspect plot, validate docs, report limitations and unresolved old584cause honestly.

Flushing follow-up validation: ten-turn OFF/HDF5/ASCII and short RF-stop integration harness all pass; saved physical states/timing/reference are exactly unchanged by flushing and all rejection contracts pass. Manual58sourcechapters, edited elements page rendered,64HTML pages validated. Frozen running executable opalx-flush-run SHA2560c4f905d4aec6b0766a29e8619296b52cff337b6ef75a952718d5cc1477734fd; source snapshot flushing-source-snapshot.

##8^3/580MeV completed and plotted
Run completed return0 in431.26seconds,133932steps,t=22.0354053688us. Reference580.470767685MeV at full RF1 kick crossing the requested580MeV threshold. Final4049/4096survivors,47lost(1.14746%) via existing10sigma boundary; no SINGLEGAP failure before stop. Flushing preserved759907hitrecords in187HDF5steps; cumulative histogram exactly matches record count, cumulative .peaks means match HDF5 turn means.
Final8complete passages zero-based178..185;4052particles first2,4049remaining6; each contains every final surviving ID exactly once. Per-turn charge verified against original macrocharge, no normalization hiding losses. Reproducible plot_last_eight_8.py creates profiles-8-580/{last-eight-turns.png,last-eight-turns.pdf,line-density.csv,last-eight-turns.csv,profile-summary.json}. Figure inspected; footer spacing corrected after first visual review. No inset/no septum modeled.
Old16failure near584MeV remains unclassified retrospectively because original failed state was not saved. New diagnostics distinguish support/RF causes but the requested580MeV stop does not reproduce the old failure. No physics boundaries/tolerances changed; do not claim the numerical584MeV cause fixed. All current flushing unit/integration tests and manual validations pass. No commits or pushes.

## Old OPAL comparison completed
User requested same test with old OPAL. Study tmp/old-opal-comparison-20261023: OPAL2022.1 LF2/FFT8^3/4096/2mA, same maps/cavities/sample offsets, bounded140000steps then offline580MeV reference window. Return0 in181.99s. Comparisonlast8turns178..185 has maxcentroiddifference1.0583mm andold/newrmsratio.8311..1.1125; old4096survivevsOPALX4049. Initial4095commonparticles verifiednm-level aftercoordinateconversion; oldforcedreferenceID0excludedfrombothplots, small collectivecontributiondifference remains. Bare-reference controlmax0.327mm/3.63keV. Samebins/physicalcharge/noareanormalization. Figures reviewed; REPORT.md/summary.json/CSV give full provenance and limits. Does not resolve old16failure or establish convergence.
