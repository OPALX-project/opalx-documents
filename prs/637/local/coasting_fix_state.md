# Coasting particle/reference separation fix

Goal: diagnose and fix the 22.998 m particle/reference separation after ten coasting PSI Ring turns before any FFA work.
Workspace: /Users/adelmann/git/opalx-master; branch 615-probe-command-does-not-work.
Existing PROBE implementation and manual edits are retained. No pushes authorized.

Evidence inspected directly:
- Particle field callbacks use OrbitThreader::query(s,local-z extent) when DeviceExternalField does not support the lattice (including mapped cyclotron sectors).
- The reference always queries the current spatial midpoint through TrackReferenceStep.
- Threader return period is 13.1899853903 m; TRACK's first turn is about 13.189732 m. A repeated ownership map is not exact for TRACK or for particles off the threaded orbit.
- Existing ten-turn output is near roundoff through ~3 turns, then develops centimetre excursions at s~47.5 m and finally 22.998475 m. Probe OFF reproduces all saved states exactly.

Implementation plan:
1. Freeze pre-fix executable and reproduce densely enough to locate the first missed kick.
2. Add a conservative host-side angular-wedge candidate predicate for cyclotron sectors using transformed current bunch bounds. Sector kernels remain the final radial/vertical/half-open support test.
3. Replace only cyclotron sector membership in the path-index candidate set; preserve other element selection and use prepared callback order for this spatial sector path.
4. Unit-test conservative geometry and real device field evaluation when a stale map omits the sector, including seam/rotation/bunch-extent and empty-rank cases.
5. Rebuild and validate ten turns on one rank with probes OFF/ON, a dedicated multi-rank check, RF acceleration, and relevant existing unit/regression cases.
6. Document changed selection, accuracy/execution implications, evidence, and remaining risks. Review diff; no tolerance widening or reference rebaselining.

Numerical implications: field formulas, SI units, physical support and step schedule stay unchanged; correcting candidate omissions changes magnetic kicks and particle trajectories. Callback order/extra candidate frame round trips can change rounding. Bounds are conservative only; roundoff slack must not alter actual field boundaries. Host bounds/descriptor math; existing Kokkos device field kernels, no new particle transfers or MPI collectives.
Completed:
- New CyclotronSectorCandidates.h conservative transformed-AABB angular-wedge selection, integrated for RING sector callbacks in ParallelTracker; prepared callback ordering retained across ranks. No upstream dependency source changes.
- Two new unit tests in TestCyclotronSector cover wedges/seams/rotations/finite bounds, omitted-sector recovery with preserved non-sector candidates, misalignment, real Kokkos field evaluation, and empty MPI rank. Added two-rank CTest target.
- Dense baseline first excursion >1e-8 m: t=415.432708 ns, s=46.173825 m, transverse offset 0.196862 mm. Final baseline offset 22.99847541899688 m.
- Fixed ten-turn final offset 1.1865415943696464e-11 m; maximum 1.2326600192976955e-11 m. Reference position/time/path statistics exactly unchanged from baseline. Energy spread over the fixed run ~3.15e-10 MeV (roundoff; no field/integrator change).
- Fixed probe OFF/ON and dedicated two-rank ON statistics identical at every step. Both radial probes record ten crossings; extraction has none.
- Six CTest targets pass: CyclotronSector, CyclotronSectorMPI, TrackReferenceStep, DeviceExternalField, CyclotronProbe, CyclotronProbeMPI.
- Extended tools/check_cyclotron_probe.py to ten-turn coasting, 1 nm accumulated-separation guard, twenty chord crossings; bound resolves the old first error by >1e5 and allows roundoff. HDF5/ASCII coasting and RF passivity and all four rejection contracts pass. Initial harness rerun caught a test-only TURNS=1 substring replacement (became FS00 for TURNS=10); fixed with numeric regex and reran all checks successfully.
- Full RF acceleration to 590.3268 MeV: all 546 saved particle/reference/time/step states exactly match pre-fix output.
- Existing Cyclotron-SC-Midpoint and Cyclotron-SC-Prestep fixtures: all 17 existing final-stat bounds pass for each. No numerical references or tolerances changed.
- Updated /Users/adelmann/git/opalx-manual/physics/cyclotron.qmd; source validator passes 58 chapters; edited page rendered; HTML validator passes 64 pages.
- git diff --check clean; reviewed helper geometry and tracker scope. Existing probe modifications preserved; FFA work deferred.

Artifacts: tmp/coasting-fix-20261023/{summary.json,coasting-fix.png,coasting-fix.pdf,run_case.py,analyze_fix.py,coast_data.py,check_rf.py,check_space_charge.py}; frozen opalx-before and all input/output/launch manifests retained. Scripts use ~/.venv-h6 Python and existing maintained input fixtures. Integration report: integration-verified/report.json.
Remaining limits: validated on CPU OpenMP, single proton long runs and short PIC cases; no CUDA run or convergence/absolute orbit accuracy claim. Broad-phase cost scales with sector count, eight host corner transforms per sector per callback. No API/field/step changes. No commits or pushes.
Next: report completed coasting fix; FFA remains second step.
