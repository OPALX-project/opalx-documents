# BeamBeam recovery and master merge (2026-11-20)

## Current handoff — PR #300, 22 November 2026

The maintained notes now live in `/Users/adelmann/git/opalx-documents/prs/300`.
Start at [README.md](README.md); update notes here, not the old-path redirects.
Code/scripts/data/LaTeX remain in `/Users/adelmann/git/opalx-beambeam`.
Commit `4231c717f` was pushed to `origin/271-implement-interation-point-element`;
older “no push” statements record earlier authorization, not current Git state.

The latest Lumi Track-12 and full Experiment 4 comparisons are complete.
Next investigate primary preparation/waist and witness birth timing; the legacy
Experiment 4 setup differs from narrow rigid/exact-timed Track-12, and does
not yet validate production physics accuracy. Quantitative results and limits
are in the index. This documentation relocation is uncommitted in both repos.
No code, physics, numerical settings or data changed. Historical entries below
preserve original paths and execution-time state; `sandbox/...` paths refer
to the source checkout. The relocation plan below is now completed.

Relocation validation: ten authored notes moved, one index added, ten old-path
redirects retained; all 59 local Markdown/figure targets resolve. Whitespace
checks cover both repositories and all eleven new maintained documents.
Only Markdown files changed. No tests/runs were repeated for this document-only
move, and no commit/push was performed in either repository. The documents
checkout remains on its pre-existing branch; unrelated contents are untouched.

## Documentation relocation — 2026-11-22 (in progress)

User identified this work as PR300 and requests authored BeamBeam Markdown
notes moved to /Users/adelmann/git/opalx-documents/prs/300 and updated there.
Plan: move ten notes preserving history; create PR index/current summary;
update stale lifecycle/status/path claims; retain short old-path redirects.
Generated run REPORT.md files stay with data except the authored cutoff study;
AGENTS/build/project docs, LaTeX/code/scripts/data stay in source checkout.
No commit/push authorized for this relocation. Source commit4231c717f already
pushed to271-implement-interation-point-element. Destination repository clean
on existingcodex/ffa26-core-course-archive branch; do not switch branch or
touch unrelated documents. No destination-specific AGENTS found; parent
/Users/adelmann/AGENTS.md read. Manuscript skill/LOCAL_EXTENSION read; preserve
technical claims/history, add dated status corrections rather than rewrite logs.
Next: move explicitfiles (destination currentlyempty), verify preservedbytes,
update links/status, add redirects and validatecrosslinks/gitdiffs inbothrepos.

## Local commit — 2026-11-22

User authorized localcommit, no push. Created4231c717f oncodex/beambeam-recovery:
fix(beambeam): cut off witness fields outside the longitudinal solve window.
30files include cutoffsource, boundary/CIC anddeletion/H5 tests, LaTeXnote,
audits andthreeLumi validation control/script/statusdirectories. Generateddata,
PDF, untrackedAGENTS/HANDOFF/PYTHONinventoryexcluded. RemoteBBthreechangedfiles
SHA256matchlocalexactly. SeparateLumi~/opalxmaster4trackededits backeduplocally
toignored sandbox/lumi-experiment4-cutoff-20261122/unrelated-lumi-master.patch
andbase/status; unrelatedmaster notaltered/merged/committed. Itsuntrackedolder
experimentfolders remainremote andoutofscope. Commitmsgfullbody /tmp/opalx-beambeam-cutoff-commit-message.txt.
FinalCTest4/4pass withPRTE_MCA_rmaps_default_mapping_policy=slot:OVERSUBSCRIBE
PRTE_MCA_hwloc_default_binding_policy=none (defaultmappingfailsbeforetests).
ExplicitCPU n1 MultiContainer19tests,n2deletion/H5,n1/n2/n4fieldservices pass;
5syntheticPythonchecks,clangformatdryrun,diffcheckpass. NO pushperformed.

## Source evolution / witness timing diagnosis — 2026-11-22

Currentrequest comparewhypositronoscillationsmissingExp4vTrack12; NOcommit/push.
Re-read actualdecks, sourcekickcode, explicitbirthparserdocs, GaussianCORRX/Y
defaults0. Newreproscript sandbox/lumi-experiment4-cutoff-20261122/compare_models.py
analyzes existingCPU2primaryH5 andnewGPU1witnessH5; Track12sourcefree-driftprediction
fromfixedinput(no primaryGPUhistory). Resultsmodel-comparison/summary.json,
primary_evolution_and_births.png, CSVs. PrimaryCPUnearIP435.529/444.206um vs
Track12input1.91903/1.92068um(nearzero divergence,BBRIGIDtrue). Exp4uncorrelated
entrancewaist sigma1.944um,sigma_xprime2.67445mrad,L.17m ->unforcedsigma454.66um:
alreadyexplainsmostexpansion; no focusing/correlations tocreatewaistatIP.
BBRIGID suppresseskicksonly, NOTdrift! FlagalonewouldnotfixExp4divergence.
Exp4simultaneousbirths-16.747ps, primarycentroids±5.0206mm then. Track12births
-3.002..+1.999ps, correlatedbirthz-.9..+.5994mm, pxpy0,pz1.732mc; notallbornIP.
GPUpositronmedianradius2.127um(firstsample)->2.471mm atoverlap; inputvTmedian
.498533c predicts2.503mm drift. sigmaZ/c2.001ps; witnessesmostlyfarcorebefore
arrival. Strongmodel/initialconditionexplanation but noisolatedcausalablation;
mesh16cubedvs256x256x128also differs. GPUold/newprefixidenticalroundoff: notcutoff.
No newtracking/source/deck/LaTeXchanges; onlyanalysis/statefiles. SeeSTATUSlastsection.

## Lumi full loss-producing Experiment4 — 2026-11-22 (completed)

FINAL: cutoff23928245 COMPLETED0:0,477.98s,26576steps,t1600.001ps;
old23928246 FAILED28:0(exit-status156),471.36s, reproduces CICoutsideguard
afterstep25565. Bothsmall-g (attempts tomovecutoffdev-g failed/notscheduled;
bothstartedregularqueuebeforelastupdate). Exact5inputs/binaryhashesverified.
GPUcutofffinal643e-/731e+, losses654/566,49lossintervals/species, zeroduplicate/
reappearing/newIDs,nonfinite,causalityviolations; ballisticdeltaP0 atlosses and
same-sideoutsidewindow, driftresidual<=1.28e-15m. No repeatedpositronoscillations:
oneID706reversespxonce; oldGPUandCPUcaseslikewise. GPUold/newcommon4940snapshots
maxlabdr1.249e-15m,maxdp2.167e-15mc. CPUcutoffvsGPUcutoffNOTidentical:
maxdr0.454151mm,maxdp0.00150841mc,twointermediateloss-timingcountdifferences
(e-step26339CPUoneextra,p-step26379GPUoneextra); finalcountsmatch. CPUoldvsGPUold
alreadydiffers7.8886um/0.00150841mc beforeabort: notattributedtocutoff.
DetailedSTATUSandanalysisplots/CSV in sandbox/lumi-experiment4-cutoff-20261122/.
comparison/{all_trajectories.png,positron_oscillations.png,summary.json};
cutoff/loss-audit for full audit. Allpostprocessinglocalh6; 5syntheticaudittests
pass; gitdiffcheck/bashsyntax/ASTpass. Remote3sourcehashesstillmatch; nojobsleft.
NOcommit/push. Preservedpreviousoutputs; noLaTeXreferenceupdated.

Current user request: run full Experiment4 onLumi withcutoff, compareprevious,
showtrajectories/positronoscillations. NOcommit/push. Prepared exactlocaln1 deck
and4inputfiles, verified5hashes. Remote newcampaign
/flash/project_465002453/bb-experiment4-cutoff-20261122/{cutoff,old}.
Submitted23928245 cutoff and23928246 saved-oldbinary, each1GPU small-g4CPUOMP1
--info4, scripts/stdout/stderr runlocal. Existing verifiedbinaryfromTrack12:
bb-cutoff-track12-20261122/bin/opalx(f44bf287...) vs pre-cutoff/opalx(31e97e63...).
No source/buildchanges. Oldcontrol mayabort atwindowexit aspreviousCPUdid;
preservepartialdata, comparecommonstepsonly. Bothdecks identical, 10kevolving
primaries/1297species/16cubed/550+25001+1025steps. NotrigidTrack12!
Local sandbox/lumi-experiment4-cutoff-20261122 hasSTATUS.md,submit.sh,analyze.py.
Next: monitorjobs, fetchcompleted/failedoutputs withrsync-rz no-perms/owner/group,
runanalyze.py in~/.venv-h6 withcampaign-localMPLCONFIGDIR; audits perID,
all_trajectories.png/positron_oscillations.png andCPUcomparisons. Analysis notyet
executed. Oldlocalbaseline issue612-20261121-n1 (abort25566), cutofflocal
cutoff-20261122-n1(completes26576). InitialSSHdelayminutesrecovered; noauthissue.

## Lumi Figure6(b) cutoff rerun — 2026-11-22 (completed)

FINAL: GPU build/n1 23927919, n2 23927942, cutoffTrack12 23927947 and saved-old
binary control23928050 all COMPLETED0:0. Local analysis with --control succeeds;
all5 input hashes, immutable witness IDs and output clocks match. All12 survive,
finite, maxdistance<1.65mm fromIP. Original->cutoff maxlabdr0.302419nm,
maxdp1.271378e-6mc; unchangedoldexe repeat vsoriginal maxdr0.982497nm,
maxdp2.734897e-6mc. Consistent with ordinary GPU/run-to-run variation, not
MonteCarlo resampling; onlyone repeat so no statistical/tolerance claim.
MSOL relL2x/s and CAIN errors unchanged6significantdigits. Times original469.86s,
cutoff472.25s, oldrepeat475.05s. All1501steps. GPU n1/n2 cutoff/reentry/nonuniform
CIC regressions pass. Track12 staysinsidewindow, not a physicaltruncation test.
Summary/plot: sandbox/lumi-cutoff-20261122/track12/cutoff-comparison/summary.json
and previous_vs_cutoff.png. Repro scripts/provenance/finalreport in campaign
STATUS.md. Remote source hashes verified unchanged after alljobs; exactlythree
intended trackedfiles dirty (plus untrackedbuild-hip). No commit/push. Previous
Figure6b data/PNG and LaTeX figure reference preserved. Allrequested work done.

User requests exact Figure6b Track12 repeat on Lumi with new uncommitted cutoff,
then direct comparison. No commit/push. Read opalx-git-cli skill; remote checkout
on branch271-implement-interation-point-element at e24dc9218, tracked tree clean
before task; only untracked build-hip. Master~/opalx out of scope. squeue empty.
Remote runroot /flash/project_465002453/bb-cutoff-track12-20261122 newly created.
Old executable saved as pre-cutoff/opalx with verified baseline SHA
31e97e63d5208ef210c4188b717b48ccd739fba37874f38735e08754372d1307.
Exact baseline deck/input copied without changes from old runroot
/flash/project_465002453/bb-validation-e24dc9218-20261120/track12; all5 input
hashes match local baseline manifest (primary625621de..., decke4f99f25...).
Local control/provenance/scripts in sandbox/lumi-cutoff-20261122/:
build.sh, unit-mpi2.sh, track12/submit.sh, STATUS.md, ignored cutoff.patch and
source.sha256. Patch contains ONLY src/SpaceCharge/BeamBeamFieldServices.h,
src/SpaceCharge/CartesianPIC3D/CartesianPIC3DAlgorithm.cpp and
unit_tests/SpaceCharge/TestBeamBeamFieldServices.cpp. Prior local ID/H5 test,
LaTeX and unrelated changes are NOT transferred. Patch checked/applied in clean
remote checkout, all source/input hashes verified, scripts copied run-local.
Build uses existing build-hip incrementally, targets opalx_exe
and TestBeamBeamFieldServices -j20; copies new executable to runroot/bin/opalx.
Build1GPU+unitn1 -> unit2GPU -> production1GPU. All ReleaseHIP/GFX90A,
LUMI25.03/AMD6.3.4/Cray-MPICH8.1.32, GPUawareMPI1/GPUIPC0, existing ROCR selector.
All scripts/Slurm logs run-local, --info4, oneMI250400k256x256x1281501steps.
Build23927919 completed successfully (dev-g1GPU20CPUs), all source/input hashes match.
Patch applied remotely after clean-tree/apply-check gates; remote tracked
changes exactlythree intended files. GPU n1 three applicable field-service
tests PASS, including new cutoff/reentry/nonuniformCIC. Expected MPI4-only skip.
MPI2 GPU job23927942 completed exit0, three applicable tests PASS on both
ranks (new cutoff and nonuniformCIC included). Production Track12 job23927947
submitted small-g1GPU4CPUs/OMP1/--info4, exact baselineinput. Source remote now
intentionally dirty with cutoff changes; no commit/push. SSH initialization
can take~20s; connection works.
Fetch outputs/postprocess locally with ~/.venv-h6. Compare raw H5 by immutableID,
clock and allphase components; don't assume bitwise GPU repeatability. If needed
old saved binary supports additional run-to-run control. Preserve baseline PNGs
and old results; do not overwrite Figure6b before showing comparison.
Local analyze.py prepared/--help tested. Baseline integrity verifies all6504 H5
records/species, sixpersistentIDs, globalstep1500, finitephase, no sample outside
window; maxdistance1.641816mm (electrons),1.638786mm (positrons) fromIP4mm.
Allfive baseline local input hashes verified. New analysis checks same hashes,
completed/timing, rawH5 byID/exactclock, bothcomparisonCSV pairIDs, then calls
existing CAIN/MSOL comparison and writes overlay/delta plots. No tolerance
inferred; expected ordinary gather path because all particles well inside10mm.
23927947 confirmed R on nid005026, step>=300 at2m22s. New HIP exeSHA
f44bf28796a8134cc96d8a3afbb5e8a62a90adf1be72c152dd28123266da73c3;
patchSHAae3484a4948b94604485dc967b05afd657ae28e1235979ceb50b620d7a4c1595.
GPU n2 distinct PCI c9:00/d9:00; ROCR masks respected, onevisible perrank.
Build+unit logs fetched. rsync -az Mac directory chmod failed23 after receiving
data; retry -rz --no-perms --no-owner --no-group succeeded. Use that for final
fetch, excluding bin/,pre-cutoff/,STATUS.md, and track12/input/primary_fixed.fromfile.
Copy local baseline primary to new track12/input after fetch and verify hash.
Do NOT overwrite local baseline. analyze.py hashes ID-sorted phase/clock/frame
metadata bytes, not just maxdifference0; no acceptance tolerance invented.
LATEST:23927947 COMPLETED0:0, all1501steps, real472.25s vsbaseline469.86s;
Slurm8m01s. Build23927919 completed2m20s; MPI2 job23927942 completed15s.
Final fetch succeeded; local baseline primary copied into new input/ and5 hashes
verified. analyze.py completed after fixing Matplotlib \mathbf{r}/\mathbf{p}
braces (plotting-only error). All13,008 actual H5 witness records match IDs/clocks;
phase finite, six/species throughstep1500, allinsidewindow(max|s-IP|1.642mm).
NOT bitwise/numerically equal: maxlabdr3.0241853377e-10m, maxdp1.271377691e-6mc,
RMSdr3.759127627e-11m. New MSOL relL2x0.0085373835853, s0.0011730230273;
old0.0085373794866/0.0011730220798. Runtime472.25s old469.86s. Overlay viewed:
curves overlap, differences small but not called identical or attributed blindly.
Source hashes rechecked after fullrun; remote trackedchangesonly3expectedfiles.

ADDITIONAL CONTROL:old-repeat job23928050 submitted using SAVED OLD binary
SHA31e97e63... and exact baselineinputs, small-g1GPU4CPUs/OMP1/--info4.
Remote /flash/project_465002453/bb-cutoff-track12-20261122/old-repeat.
Local script sandbox/lumi-cutoff-20261122/old-repeat.sh, copied to run/submit.sh.
Control purpose: old-binary repeatability/environment variation versus code
change; no tolerance inferred. No jobpending exceptthisone. Main23927947done.
Next: monitor23928050, fetch completed old-repeat with rsync -rz --no-perms
--no-owner --no-group (exclude bin/pre-cutoff/STATUS/largeprimary). Copy local
baselineprimary to controlinput. Re-run analyze.py --control
sandbox/lumi-cutoff-20261122/old-repeat; it compares baseline->old-repeat and
old-repeat->cutoff rawH5 byIDs and labnorms. Finalcomparisonreport/plot in
track12/cutoff-comparison/. Keep original Fig6b unchanged. No commit/push.

## Hard longitudinal witness cutoff — 2026-11-22 (implemented and locally validated)

User authorizes zero BeamBeam contribution outside IP+/-10mm and checking
existing cases. No commit/push. Change only passive gather: source deposition,
primary kicks and lifecycle unchanged. Closed endpoints gather; outside finite
witnesses get exact E=B=0, no deletion/wrapping/clamping, re-entry supported.
Nonfinite coordinates and bad in-window CIC stencils remain collective errors.
CartesianPIC3DAlgorithm::gatherFields keeps old gather if all targets inside;
otherwise fills E/B halos on all ranks and performs masked device CIC using
IPPL's existing weights/gatherFromField. One integer status MPI reduction,
no full-array host copies or particle selection allocations. Mixed-path E/B
gathers are fused; possible backend rounding differences are tested without
relaxing existing tolerances. Hard force discontinuity intentionally changes
witness physics outside window; omitted impulse/window convergence unresolved.
Docs: BeamBeamFieldServices.h Doxygen plus sandbox/note/bb-note.tex cutoff
paragraph (manuscript-writing skill, concise verified claims only). Configured
/Users/adelmann/git/physics-manual-opalx does not exist, so manual sync pending.
New TestBeamBeamFieldServices case exercises +/-10mm, nextafter outside,
all-outside, re-entry, empty local ranks, R/P/ID retention and nonfinite guard.
GCC build passes. Field-service tests n1/n2 CTest PASS; manual n4 PASS, including
non-slab mirror. New masked/nonuniform cached-field test matches ordinary IPPL
CIC at inside-only probes, with both E and B checked. Closed endpoints,
nextafter outside, all-outside, re-entry, IDs/R/P and nonfinite guard PASS.
Initial new fixture defaulted to PERIODIC; corrected fixture to BC::NO to match
PartBunch OPEN, not a production behavior change. No tolerance relaxation.
Relinked prior ID/H5 tests; final CTest four entries PASS and Python audit5/5 PASS.
Some intermediate default MPI launches failed before tests (slots/mapper);
direct --oversubscribe --bind-to none launches and final ordinary CTest pass.

Full Experiment4 n1/n2 both complete26576 steps to1.600001ns, now past former
step25566 abort. Both final643 electrons/731 positrons; removed654/566 across
49 H5 loss intervals/species. No duplicate/replacement/reappearing IDs, no
nonfinite components, no superluminal displacement. All outside-window
same-side intervals have exact deltaP=0. Ballistic survivor deltaP at losses=0,
max position residual1.3422e-15m n1 /1.2579e-15m n2. Repeated positron
oscillations remain absent (n1 one reverses once; n2 none near overlap).
Primary deposition/lifecycle unchanged; cutoff is approximation, not accuracy
claim. Window/timestep/mesh convergence and GPU validation remain open.

Exp2 local2000-primary16x16x32 full1501-step case compared against isolated
pre-cutoff reference executable: all13008 actual H5 witness records have
bitwise-identical phase space/IDs/clock; analysis_equal true,13012 reconstructed
reference-grid samples. Reference built using exact HEAD algorithm TU before
new static archive; sources not reverted. Build script/source/hash metadata in
tmp/cutoff-validation-20261122/ (task-local .gitignore prevents accidental staging).
Exp3 full160step exact1297+1297 births PASS; witness R/P/IDs bitwise equal to
former local-20261120-221523-66s1bzsm, primaryz max3.47e-18m difference only.
Exp1 all four manufactured field smokes1000primary8x8x16 complete; finite metrics,
zero uncovered probes; large coarse-grid errors are not an acceptance gate.

Detailed companion report: sandbox/experiment-4/results/cutoff-20261122-study/REPORT.md.
Run outputs/manifests/timing/plots: experiment4 results/cutoff-20261122-n{1,2};
Track12 results: experiment2 cutoff-20261122-{n1,reference}; Exp3 cutoff-20261122-n1;
Exp1 cutoff-20261122-smoke. Executable SHA256
65a9eb7cc7b947b81d0dff36c6517fc41cb5c0a8bd73465e9edc74278788eb8a.
Both MPI4 and fresh n1/n2 tests rerun after final nonuniform-test addition.
LaTeX note updated (cutoff + bounded CPU results) and PDF rebuild passes;
manuscript skill used for concise claims/caveats. Doxygen updated. Physics
manual checkout absent, sync pending. New audit outside-ballistic checks and
two additional synthetic tests documented. Diff/clang-format/whitespace pass.
No processes pending, no commit or push. Prior uncommitted unit/H5 regression
and unrelated files preserved. Next: user review; assess the expanded primary,
legacy injection clock and window convergence before production conclusions.

## Experiment4 loss/oscillation audit — 2026-11-21 (blocked before losses)

User requests rerun of loss-producing full Experiment4 and check #612's
trajectory discontinuities/positron oscillations. No commit/push. Prior
uncommitted witness-deletion unit regression must be preserved. Rebuilt current
build_gcc/src/opalx (opalx_exe target); build_openmp has unchanged AppleClang
LossDataSink compile failure. Current full deck is dynamic-window staged case:
10k evolving Gaussian primaries, 1297+1297 simultaneous FROMFILE witnesses,
IP0.17m, 32cm element, 15cm radius, 16^3 mesh, DT1ps/1fs/1ps,
550+25001+1025 requested steps. It differs substantially from Exp2 rigid,
deterministic, exact-timed Track12 and cannot alone prove identical oscillations.
Prepared results/issue612-20261121-n1 through normal launcher --full
--prepare-only. Only generated-deck change: C0PSDUMPFREQ=0 to avoid bulky primary
dumps (witness output/physics unchanged). First mpiexec launch returned213
before OPALX started, slots-filled message; retry uses --oversubscribe
--bind-to none. Also prepared n2 with C0PSDUMPFREQ=100 (sparse primary output).
Both physical decks otherwise unchanged. Both runs aborted exit156 at step25566,
approximately591.001ps: CartesianPIC3DAlgorithm::gatherFields rejects witness
CIC stencil outside solved local storage. Last completed step25565=590.001ps;
last H5 step25559=584.001ps. All1297+1297 witnesses remain: NO losses occurred.
Thus post-deletion jumps could NOT be tested. Neither run reaches Completed
or the ballistic tail; no processes remain running.

Added scripts/audit_loss_trajectories.py and three passing synthetic tests:
valid deletion/permutation, deliberate unphysical jump, deliberate renumbering.
Actual data:2470 snapshots/species/run, zero duplicate/new/reappearing IDs,
zero nonfinite components, zero displacements above c*dt+1pm. No ID remapping.
Positron px reversals near overlap: n1 one particle reverses once; n2 none.
No repeated oscillations. Accepted Lumi Track12 has5–30 reversals/positron,
but source, witnesses, timing and mesh differ: NOT a controlled equivalence.
Sparse n2 primary at567.050ps: sigma_x435.529um, sigma_y444.206um, versus
entrance parameter1.944um (~224x expansion in x). Full witnesses injected
simultaneously16.747ps before nominal overlap, unlike exact Track12 births.

Read-only diagnosis: mesh z fixed IP+/-10mm, only x-y expands; gather tries
ALL witnesses, including those leaving z window while primary is still active.
Guard checks all3 dimensions. Failure log: witness tails~18.6mm behind source,
source centroid~6.9mm beyondIP; witnesses extend upstream of field window.
Needs explicit outside-longitudinal-window policy, NOT disabling guard or
changing IDs. No production fix implemented; request next user direction.

Outputs: sandbox/experiment-4/results/issue612-20261121-n{1,2}/loss-audit/
summary.json, loss_trajectory_audit.png, per-ID/loss CSVs; n2 primary_envelope.csv.
REPORT.md/manifests mark abort, actual input hashes recorded. Source9102c9cd1;
executable SHA256978765cd6bdebc16abec89964472b157dff55992f4515d85ab319b0fe2e41ad3.
Reproduce: ~/.venv-h6/bin/python sandbox/experiment-4/scripts/audit_loss_trajectories.py
RUN --ranks N --track12-reference
sandbox/lumi-validation-20261120/track12/results/track12_pointwise_comparison.csv
Use run-local MPLCONFIGDIR=.plot-cache, OMP_NUM_THREADS=1. No commit/push;
prior uncommitted unit regression preserved. Broader #612 remains unresolved.

## Witness deletion regression — 2026-11-21

User requested regression only; do not commit or push. Changed
unit_tests/PartBunch/TestMultiContainerPartBunch.cpp and its CMakeLists.txt.
Three containers (primary, electron/positron witnesses), eight particles per
rank, two selective deletion rounds, including empty electron rank1. Check
exact surviving ID-to-(R,P) associations, unique global ID coverage/counts,
unchanged primary, and all three H5 snapshots via normal DataSink diagnostics.
No physics/production code changes or tolerance changes. Dedicated MPI2 CTest
entry added; single-rank coverage is in TestMultiContainerPartBunch.
build_openmp failed before new test compilation in unchanged LossDataSink.h
std::less<SetStatistics> with AppleClang/libc++. Existing build_gcc (GCC15.2,
Kokkos SERIAL) successfully rebuilt both targets. CTest n1 full 19-case
TestMultiContainerPartBunch suite and focused TestWitnessDeletionMPI2 both PASS
(0.52s each). Run with:
  cmake --build build_gcc --target TestMultiContainerPartBunch TestWitnessDeletionMPI2 -j4
  ctest --test-dir build_gcc -R '^(TestMultiContainerPartBunch|TestWitnessDeletionMPI2)$' --output-on-failure
Initial reader used H5hut's retained previous-step view, causing an incorrect
population assertion; test now clears the read view before querying each
snapshot's global count. No production fix required. Exact survivor mappings
and population checks pass: n1 primary8/8/8, electron8/5/4, positron8/5/4;
n2 primary16/16/16, electron16/5/4, positron16/10/8. H5 checks compare all six
components and IDs against the independently constructed pre-deletion oracle.
Diff reviewed; git diff --check and clang-format --dry-run --Werror pass.
No GPU/full Experiment4 trajectory validation claimed; #612's broader physical
trajectory/oscillation questions are not resolved by this isolated regression.
An optional CTest --repeat run failed in the MPI launcher before any tests
started ("All nodes ... already filled"). Immediate normal CTest rerun passed
both entries again; this was not an ID/H5 assertion failure. Final LastTest.log
records passing n1/n2 runs.
No commit or push. Next: user review/authorization.

## LaTeX refresh — 2026-11-21

Follow-up: Figure6 now stacks historical A100 as6(a) and Lumi Track12 as6(b),
with subfigure labels, mesh/revision captions and updated figure provenance.
Uses the existing Lumi result PNG directly; no plots/data regenerated. PDF
rebuilt successfully (16pages), Figure6 confirmed onpage9 and visually inspected
with pdftoppm. No undefined references/overfull boxes; whitespacecheck passes.
No commit/push. Source-only changes remain sandbox/note/bb-note.tex.

Updated sandbox/note/bb-note.tex with verified Lumi checkout/run paths, Slurm
job IDs, run-local scripts/logs, MPI transport settings and local analysis
commands. Replaced obsolete Merlin operational instructions, retained historical
A100 figures/results with explicit labeling. Briefly added current Track-12
metrics and ID semantics; corrected old aperture-sized fixed-mesh description
to the implemented 20mm longitudinal/dynamic transverse domain and post-emission
coverage repair. No scientific source changes. Manuscript skill used to keep
the update compact; PDF shrank from17to15pages. latexmk succeeds, no undefined
references or overfull boxes; git diff --check passes. No commit/push this turn.

## AFK authorization / published commit / Lumi campaign (latest)

FINAL: requested workflow completed. Track12 fetch73489 and local analysis3715
finished successfully. All12witnesses survive toglobal1500,6504actualrecords per
species, finite allphase values, persistentIDs. Fullcomparison13012rows.
MSOL relativeL2 x0.853738%,s0.117302%, yRMS1.73728um (referenceyzero).
CAIN relativeL2 x9.482848%,s2.967314%, yRMS14.76368um. PositronCAINxrelative
107.906% withabsoluteRMS5.76585um; late firstkicks~0.797MSOLratio, so do not
claim uniform few-percent agreement or new mesh convergence. Runtime469.86s.
Plot inspected: localcampaign/track12/results/track12_cain_vs_opalx.png.
Operational source/run paths, jobIDs, launch workaround and results consolidated
in sandbox/lumi-validation-20261120/STATUS.md. Scripts/analysis retained there;
generated outputs ignored, notcommitted. Sourcecommit e24dc9218 pushed to271;
tracked local source clean. No tasks need monitoring now; no production retry.
Known unrelated unchanged master GCC bend exactzero test stillfails1.39e-17.
Next optional user-directed work: finer mesh/convergence or rank-independent
input-row provenance (separate from immutable particleIDs). Do not start alone.

PRODUCTION COMPLETE:23901513 finished1501steps; completed marker and populated
timing.dat verified. `/usr/bin/time -p` real469.86s. Fetch exec session73489: rsync-rz
remote track12/ to localcampaign/track12/, excluding alreadyverified54MBprimary
file and cores. Next run local compare_timed_track12.py; validate finite all12,
finalstep1500,stableIDs,13012comparison rows. No further remote compute needed.

CURRENT: all smoke fetch/analysis COMPLETE. analyze_smokes.py succeeded for all4;
actual HIP exe SHA31e97e63d5208ef210c4188b717b48ccd739fba37874f38735e08754372d1307.
Exp1 all861probes covered, coarse ErelativeL2 0.5239/0.5186/0.5889/0.6238;
B at0sigma is ill-conditioned (40.09 relative). Exp2 historical maxdP2.64e-9mc,
maxdR2.38e-15m. Exp3 firstelectron Pnorm1.322336mc, exact1297+1297births,
finite allsnapshots and stableIDs. Exp4 complete lifecycle. Preparation manifests
preserved separately; manifests now identify actual LumiHIPjob/exe.
Fetch root rsync-a had mode escalation error only on directory; rerun rsync-rz
succeeded. All outputs analyzed successfully. No missing/partial H5.

Production Track12 job23901513 SUBMITTED and RUNNING on nid005078 small-g,
1MI250,400k fixedprimaries,256x256x128,1501steps,--info4. Remote dir:
/flash/project_465002453/bb-validation-e24dc9218-20261120/track12.
smokes-validated-locally marker created only after successful local analysis.
Next: monitor23901513 tocompletion (do not resubmit),fetch results/logs locally,
run compare_timed_track12.py --run-dir localcampaign/track12 with ~/.venv-h6.
Existing local campaign/track12 contains prepared inputs only; rsync remote
outputs there with -rz (avoid preserveperms). Then inspect comparisonmetrics,
trajectoryplot, all12surviving/finite/complete1501steps, timing.dat. Summarize
results and known master BendFieldModel exactzero fail. Source commit already
pushed; no new source changes after e24dc9218. Session11372 status poll finished.

FRESHEST: smoke23901410 SUCCESS in58s, all n2 unit gates and all four scientific
smokes completed (`smokes-completed`). Actual distinctGPU PCI IDs confirmed by
overlap probe: rank0 d1:00.0,rank1 d6:00.0, eachseesoneGPUasordinal0.
Fetch exec10073 in progress: rsync exp1..4 to each experiment's
results/lumi-e24dc9218-smoke, then root scripts/logs/fingerprint to local
sandbox/lumi-validation-20261120. Exp3 source H5~120MB, transfer compressed;
exp4/root may not have arrived yet. Wait for fetch completion before analysis.
New local reproducible analyzer:
`~/.venv-h6/bin/python sandbox/lumi-validation-20261120/analyze_smokes.py`.
It records actualHIPexehash/job from execution-fingerprint.txt, preserves original
preparation manifests, runs all4local analyses, checks probe coverage and witness
ID persistence, and prints first-witness momenta. Review those before creating
remote smokes-validated-locally marker and submitting track12/submit.sh.
Do NOT rerun build or smokes. No production job submitted yet.

NEWEST: smoke23901330 failed in HIP init (rank1 no device), because historical
HIP_VISIBLE_DEVICES=localrank double-filtered Slurm's per-task ROCr mask.
Wrapper now unsets HIP mask when ROCR mask exists. Retry23901382 passed emitted
ID/migration+BeamBeam on2ranks but hung/aborted in Cray GPU IPC import during
FieldServices (HSA_STATUS_ERROR_INVALID_ARGUMENT in hsa_amd_ipc_memory_attach).
Cancelled ONLY task-owned23901382 after verified hang; unrelated3jobs untouched.
Set MPICH_GPU_IPC_ENABLED=0, keeping MPICH_GPU_SUPPORT_ENABLED=1.
Retry23901410 now passes ALL n2 gates (emitted10,BeamBeam22,FieldServices3,
Diagnostics11) and runs scientific smokes. Submitted script saved remotely as
submitted-smoke-23901410.sh. New local scripts reflect Slurm mask+IPC fix.
Hardware PCI probe (task-only, overlap, no kernels) exec98441 may still run;
remote gpu-binding-23901410.txt records actual device mapping if job survives.
Do not mistake ROCR_VISIBLE_DEVICES=0 on both ranks for equal physical GPUs:
Slurm/cgroup masks can re-enumerate, so verify PCI IDs before claiming2devices.

LATEST update: build23901108 SUCCESS, completed10m51s. All binaries built;
one-GPU emitted-file10tests, FieldServices and Diagnostics11tests passed;
`build-and-unit.completed` exists. After slot release, smoke23901330 submitted
successfully (dev-g,2GPUs). It runs n2 unit gate then all4scientific smokes.
Track12 still NOT submitted; must validate fetched smoke outputs locally first.
Current polling exec session28126 for smoke status. Build-log fetch session83549
may still be running. Local scripts now in sandbox/lumi-validation-20261120.
Smoke script writes execution-fingerprint.txt (actual SHA,exe hash,Slurm job).

Update: all transfer87914 completed successfully. track12/submit.sh recopied
successfully; select-gpu.sh chmodded executable. Smoke submission attempt afterok
failed with QOSMaxSubmitJobPerUserLimit (user already has3unrelated long runs
plus our build). No smoke job exists yet. DO NOT cancel unrelated jobs. Wait for
build23901108 to finish, then retry smoke submission without stale dependency
if success marker exists. Build was at78% after3m49s, compiling HIP OPALX source.

User conditionally authorized commit+push after resolving witness ID concern,
then isolated Lumi checkout, all four smokes and full Track-12. No further user
choice needed for these scoped steps. IDs DO NOT change in the experiment-3
histories: both species n1/n2 have zero duplicate or disappearing IDs across all
38 dumps. Birth IDs differ by MPI size due rank-strided allocator. No allocator
change required. Strengthened timed-file test verifies per-row ID persistence
through later emission batches and actual migration on 1/2/4 ranks (all10 tests
pass each). Fixed test mesh/layout lifetime so borrowed objects outlive container.

Published merge/fix commit `e24dc92185198c5f65718e057400e6c6398dce56` to
`origin/271-implement-interation-point-element` (normal fast-forward, no force).
Local branch remains `codex/beambeam-recovery`. Restored numbered experiment
sources/inputs, comparison script and diagnosis note are committed. Generated
results, root HANDOFF/AGENTS, PDF, and local campaign directory are not committed.
Raw CAIN input CRLF/whitespace preserved byte-for-byte, not reformatted.
Broader GCC suite147/148 passes; only unchanged master TestBendFieldModel exact
zero assertion differs by1.39e-17. Do not alter master tolerance/code without
permission. Relevant tests pass; Python helpers7/7 and9/9 plus2optional skips.

Lumi isolated checkout (verified exact SHA):
`/flash/project_465002453/opalx-beambeam-recovery-20261120`.
Existing dirty master `~/opalx` untouched. New run root:
`/flash/project_465002453/bb-validation-e24dc9218-20261120`.
Build job23901108 (dev-g,1GPU,20CPUs) running; script/logs build.sh,
build-23901108.out/.err in run root. HIP/GFX90A Release; verified LUMI25.03,
AMD6.3.4, cray-mpich8.1.32. Build reads existing master's link flags but writes
only new checkout's build-hip. Script builds all binaries then runs emitted-file,
field-service and diagnostic tests n1, creating build-and-unit.completed only
after success. No need for network connection to keep job running.

Local run scripts/input prep under `sandbox/lumi-validation-20261120`.
Prepared Track-12 standard400k deterministic primaries,256x256x128,1501steps,
12 witnesses,dt6.0041537135667364fs. User informed; oneMI250, --info4.
Track12 script checks smokes-validated-locally marker before running.
Smoke script n2 unit gate then n1 scientific exp1four separations,exp2three steps,
exp3full1297+1297 birth schedule160steps,exp4primary-only1607steps.

IN-FLIGHT transfers: exec session87914 copies prepared run dirs in sequence
(experiment1..4 then54MB track12) to run root. It may still be running; poll it.
Script upload session62308 finished with final error because track12 directory
had not arrived yet. select-gpu.sh and smoke.sh DID arrive. Recopy track12
submit.sh after transfer87914 completes. Local script copies are under campaign
directory. Do not resubmit build job; monitor23901108.

Next: check build completion/fix in-scope HIP compile issues if any; after all
inputs arrive submit smoke.sh with --dependency=afterok:23901108, --chdir runroot,
--output=smoke-%j.out --error=smoke-%j.err. If successful fetch scientific output
and analyze LOCAL with ~/.venv-h6 (remote venv lacks pandas, do not install).
Only after local validation create smokes-validated-locally remotely and submit
track12/submit.sh from its own directory with logs there. Fetch completed
witness H5 and run compare_timed_track12.py locally for CAIN/manufactured results.
Do not claim GPU tests completed until verified. Keep checking current task.

## Coverage repair (latest, supersedes diagnosis-only status)

User authorized mesh coverage repair/collective guard and tests, no commit/push.
Implemented AfterEmission transverse coverage check and primary-only repeat
solve with owned saved pre-emission step/activity state. Added collective local
CIC stencil guard in CartesianPIC3DAlgorithm and regression for one-rank-only
bad position, plus internal Doxygen contract updates. No upstream edits, units,
longitudinal window or tolerances changed. Adds device reduction+MPI collective
per witness gather and extra solves on post-emission envelope growth.
GCC build and FieldServices n1/n2/n4 pass (including 4-rank non-slab test).
Exp2 smokes n1 `local-20261120-221513-ly7dacao`, n2
`local-20261120-221600-mz9s5nhy`: historical comparisons pass manifest/ID/clock
checks, max dR 3.34e-16m and dP 3.71e-10mc.
Exp3 n1 `local-20261120-221523-66s1bzsm`, n2
`local-20261120-221540-ptq9gur7`: complete exact1297+1297 births, finite all
snapshots. First electron now P=(1.07882,-0.75428,0.12566)mc; 2 extra solves n1.
October exp3 invalid gathers mean no historical trajectory acceptance claim.
Cross-rank exp3 emitted IDs differ by Step#10, so strict full-trajectory
comparison is rejected rather than remapping IDs. Full details/reproduction:
`sandbox/experiment-3/FIRST_WITNESS_DIAGNOSIS.md`.
Changes remain uncommitted/unpushed; merge still pending. Need review of
cross-rank identity/provenance before any trajectory-equivalence claim or Lumi run.

## First-electron diagnosis (latest)

See `sandbox/experiment-3/FIRST_WITNESS_DIAGNOSIS.md`. First emission is finite,
fields initially zero, fractional dt 0.774 ps. AfterEmission gathers at source-frame
x=1.108 mm on a mesh extending only to x=32 micrometres. CIC indices (268,-27,8)
on 16^3 field cause invalid memory reads; B~1e16 T, then first kick P~5865 mc.
Mesh envelope/solve happens before emission, so new witnesses are absent from
coverage. Positron also gathers invalid values. Not a parser/Boris defect.
Temporary trace instrumentation removed; logs preserved in experiment-3
`local-20261120-220751-7r4c2c0s`. No repair implemented, no commit/push.
Next: user authorization to repair coverage + collective guard + n1/n2 tests.

## Parser follow-up (supersedes the parser diagnosis below)

User authorized header-driven explicit/legacy support, rebuild and experiment
2/3 smoke comparisons; no commit/push. Direct inspection shows the merged
checkout ALREADY retained explicit seven-column parsing and birth semantics.
The earlier claim that the merged parser was legacy-only was incorrect: it
came from reading a branch-versus-master diff rather than the working source.
Do not repeat that diagnosis or attribute the experiment-3 anomaly to parsing.

Changes this follow-up: recognize named commented headers (including after a
count); regression for reordered uppercase `PZ t Z PY X PX Y` verifying positions,
momenta and exact birth boundary; Doxygen clarification. Legacy positional
unit-annotated headers/bins remain supported. No units, time conventions, kernels,
reduction order or tolerances changed. Added reproducible ID/clock-matched smoke
comparison in `sandbox/scripts/compare_smoke_phase_space.py`.

GCC rebuild passes (using existing build_gcc because build_openmp's unchanged
master AppleClang issue remains). CTest parser/BeamBeam/field services 4/4;
parser 10/10 on two MPI ranks. MPI launch needed oversubscription/unbinding;
the initial launch failed before test execution due slot allocation. Clang-format
and whitespace checks pass.

Fresh experiment 2: `local-20261120-215028-srkxwbb9`; comparison with October
smoke has identical IDs/clocks/counts/species/charges, max position delta
3.34e-16 m, max momentum delta 3.71e-10 mc.
Fresh experiment 3: `local-20261120-215037-l382c82p`; 1297+1297 exact births,
finite state, IDs/clocks match, BUT first electron's unphysical ~5865 mc
momentum persists. This is not a validated physics smoke pass. Primary Gaussian
coordinates also differ from October (compiler/backend/RNG provenance must be
separated from merge effects). Comparison CSV/JSON products are in each new run.
Next: diagnose first emitted electron's birth/gather/kick and establish a
same-primary deterministic comparison. No commit, push or Lumi job submitted.

Current goal: recover the BeamBeam branch and its numbered experiments, merge
`origin/master` with master winning, validate the merge locally, and use Lumi
for subsequent accelerator runs.

- Clean worktree: `/Users/adelmann/git/opalx-beambeam`, branch
  `codex/beambeam-recovery`, based on
  `origin/271-implement-interation-point-element` at `2bfbd3502`.
- `origin/master` has been merged with `--no-commit --no-ff`; the merge is still
  uncommitted. Conflicts in the workflows, `ParallelTracker`,
  `CartesianPIC3DAlgorithm`, and `MeshGenerator` are resolved. Master PROBE,
  FFT2D5, and periodic-box behavior is retained alongside BeamBeam interaction
  dispatch and fixed-domain handling.
- BeamBeam fixed domains now suppress ORB while master's periodic-box fixed
  domains may still rebalance. Focused one- and two-rank tests pass after this
  resolution.
- The branch's original missing brace in
  `unit_tests/Distribution/TestEmittedFromFile.cpp` is fixed.
- GCC 15 build in `build_gcc` completed. Relevant focused tests: 15/15 pass
  after the ORB resolution. Python experiment helpers: experiment 1, 7/7;
  experiment 2, 9/9 plus two optional skips. Targeted changed C++ is clean
  under clang-format 21 and both staged/unstaged diffs pass whitespace checks.
- AppleClang 21 stops in unchanged master `LossDataSink.h`; do not change this
  master-derived compatibility issue without user permission.
- Numbered experiment smoke/default-workflow runs completed locally under the
  `20261120` result directories. Experiments 2--4 reproduce counts, dump
  cadence, birth schedule, finite-state, and lifecycle manifest invariants.
  Experiment 1's nonzero-separation coarse field errors change by less than
  0.004 absolute; exact-overlap magnetic relative error is ill-conditioned.
- Critical blocker: master replaced the explicit seven-column timed-pair
  parser with the legacy six-column parser. Experiment 3 therefore silently
  interprets `x y z px py pz birth_time` as `x px y py t pz`, and the first
  electron receives an unphysical momentum near `5.8e3 mc`. Restoring the
  branch's explicit timed parser modifies master-derived
  `EmittedFromFile.{h,cpp}` and requires user permission under the master-wins
  rule. Rerun experiments 2 and 3 after that fix; do not accept the current
  smoke result.
- LaTeX inventory: the only manuscript source below `sandbox` is
  `sandbox/note/bb-note.tex` (1,041 lines, 17-page PDF). Its five external PNG
  assets and two inline TikZ figures are present. `latexmk -pdf` succeeds.
- Lumi is reachable. Existing source is `~/opalx` ->
  `/flash/project_465002453/opalx`, with a Release HIP/GFX90A build at
  `~/opalx/build`; it is a dirty master checkout and must remain untouched.
  Existing run root is `~/runOPALX-beambeam` ->
  `/flash/project_465002453/runOPALX-beambeam`. Relevant Slurm setup uses
  account `project_465002453`, `standard-g`/`dev-g`, MI250 GPUs,
  `MPICH_GPU_SUPPORT_ENABLED=1`, and one `srun` rank per visible GPU.
- No commit or push has been made. Do not submit a Lumi physics run until the
  timed parser is repaired and the local smoke comparison passes.

Next step: obtain permission to restore the explicit timed-pair parser, rebuild,
rerun the focused parser tests and experiments 2/3, then prepare an isolated
Lumi checkout/run directory and HIP smoke job. Review and stage only intended
experiment sources/docs; generated local results remain uncommitted.

# OPALX CPU/A100 12-witness validation

## CI recheck — GH200 blocked by runner failure, 2026-10-22

PR300 head confirmed6ee221cdb44b73dac54ec506795ffb2f1d9dc3bc via GitHub REST.
GH200 API pipeline2972522404 failed; push pipeline2972522833 skipped by design.
Debug build17353137637 and Release build17353137638 logs show compilation
completed with0 compiler errors (3 warnings), opalx executable produced, then
artifact-upload/cleanup phase failed with custom executor exit22/system failure.
Debug unit17353137639, Release units17353137640/641 and regression17353137642
all SKIPPED. Neither one- nor two-rank GH200 diagnostic test ran for this SHA;
therefore workaround effectiveness on GH200 remains UNCONFIRMED, not failed.
Do not confuse this with previous d30b42d49 runtime HDF5 assertion.

MI300 pipeline2972526106: Debug17353166927 and Release17353166928/929 logs each
138/138 passed, including both diagnostic writers (Debug2.91/2.96s; Release
2.76/2.77s and2.75/3.16s). Unit jobs fail only on CDash connection/submission.
Regression17353166930 passed359/359 and published results, then executor exit22.
OpenMP pipeline2972526077: Debug17353166665 and Release17353166666/667 each
138/138 passed including both writers; jobs fail only on CDash connection.
Regression17353166668 passed359/359, then publication clone failed with missing
objects from opal-live-doc promisor remote. These are infrastructure/publication
failures, not test assertion failures. CDash current index has no PR300 entries;
actual GitLab job logs are the evidence, since submissions failed.
All six GitHub workflows passed (CPU Serial/OpenMP, CUDA/HIP/SYCL, clang).
GPU GitHub checks are compilation-only; four BeamBeam smoke tests remain disabled.
No source/CI edits, commits, pushes, job reruns or monitoring changes this turn.
Next action: authorize retry of GH200 failed build jobs to unblock runtime tests
after CSCS runner recovery; do not claim all-architecture green meanwhile.

## GH200 workaround committed/pushed — 2026-10-21

User authorized committing/pushing the validated workaround and checking PR300
CI. Committed only writer .cpp/.h and its gtest as
6ee221cdb44b73dac54ec506795ffb2f1d9dc3bc:
"fix: pause HDF5 error recording during BeamBeam append probes".
Push to origin/271-implement-interation-point-element succeeded, advancing
707228352 -> 6ee221cdb. No physics/CI/dependency edits. Tracked tree clean;
existing untracked notes/sandbox not committed. Repeated post-push checks via
GitHub connector and direct REST show no Actions runs or commit-status contexts
for this SHA yet (combined state pending). GitLab GH200 project82981356 returns
no pipelines for this SHA. git ls-remote confirms remote branch6ee221cdb, while
GitHub PR300 REST/connector still show previous head707228352 at check time.
CI/PR propagation has not yet appeared; do not claim GH200 tests ran or passed.
No manual reruns/triggers and no new recurring monitor created. GH200 suite
configuration includes both TestBeamBeamDiagnosticsWriter (one-rank) and
TestBeamBeamDiagnosticsWriterMPI2 (explicit two-rank) in Debug and Release;
job allocation labels are not the individual test rank count.
Next check this exact SHA for GH200 Debug and both Release unit jobs, confirm
both writer registrations from logs/CDash when available. Do not mix prior
GH200 failures at d30b42d49 or merge707228352 with the new workaround results.

## GH200 diagnostic HDF5 workaround — validated locally, uncommitted, 2026-10-21

User authorized pushing only the existing master merge first. Push succeeded:
origin branch advanced d30b42d49 -> 707228352. Subsequent fix MUST remain
uncommitted/unpushed. Actual GH200 Debug trace17347346177 and its build artifact
17347346175 confirm bundled HDF5 2.2.0, shared library, assertion in
H5E__push_stack(cls_id>0) during corrupt-file test; rank0 abort leaves rank1 waiting.
Local Debug isolated corrupt-file test passes before changes. No remote GH200
execution access established; Merlin6 SSH name currently does not resolve.
Underlying cause of invalid HDF5 error-class ID is not yet established.
Targeted mitigation uses supported H5Epause_stack/H5Eresume_stack around the
rank0 native read-only append probe for HDF5>=1.14.5. H5E_BEGIN_TRY alone only
disables printing, not the failing stack construction. Pause prevents recording;
return codes and collective failure agreement remain mandatory. Nested pause
state and callbacks restored; older installed HDF5 keeps prior fallback.
Changed writer .cpp/.h and gtest only; no physics, GPU kernel, tolerances, CI,
or dependency source changes. Added pause-state/nested-pause regression coverage.
Focused Debug rebuild at -j4 succeeded. Final CTest subset: 5/5 passed in7.31s:
TestDiagnosticOutput, TestBeamBeamDiagnosticsWriter and MPI2 (11 gtests each),
TestBeamBeamFieldServices and MPI2. Logs /tmp/pr300-gh200-hdf5-final-{build,tests}.log.
Regression sensitivity checked by temporarily removing ONLY pause/resume from
the probe: new empty-error-stack expectations fail at one and two MPI ranks
(rank0 records7 entries for non-HDF5 input and12 for truncated header). Restored
workaround, rebuilt, reran final green suite. Red logs
/tmp/pr300-gh200-hdf5-red-{test,mpi2}.log. This demonstrates suppression coverage,
not a local reproduction of the architecture-specific invalid-class assertion.
Nested-pause test covers successful and rejected appends, no leaked pause;
existing tests retain callback restoration, byte preservation, no handle leaks,
recovery after repair, scalar/vector content and two-stage output checks.
Clang-format21.1.8 passes ALL PR-changed C++ files against origin/master;
git diff --check passes and final three-file diff reviewed. No physics, numerics,
floating-point order, GPU memory movement, MPI collective order or tolerance
changes. No tests disabled. Git HEAD and remote branch both707228352; fix is
unstaged/uncommitted/unpushed. Existing untracked files untouched except this note.
GH200 CI confirmation remains pending; old-HDF5 fallback not rebuilt here.
Next: user review/authorization before committing/pushing this workaround, then
verify actual GH200 Debug/Release one/two-rank diagnostic jobs. Do not claim the
underlying HDF5 error-class initialization/lifetime cause has been established.

## Master merge and CI check — completed locally, 2026-10-21

User requests fresh PR300 CI check and merge master. Current pushed PR head
d30b42d49171de2483ac4ad51bc2bf288ce20a55. Fetched origin/master at
41d65389d326a584aa438d80a88788ca7e82db95. Local merge commit 707228352;
only conflicts were CartesianPIC3DAlgorithm.cpp includes and .h member additions.
Resolved by retaining both upstream algorithm include/P3M warning state and
branch BeamBeam diagnostic members/includes; no hand changes to numerical code.
Upstream brings P3M/Dirichlet/rest-frame/load-balancing work, muon-decay sign,
negative SBEND geometry and H5 particle-ID fixes. Keep existing BeamBeam OPEN
restriction/frozen model and new diagnostics guards. Full build_openmp Debug
build succeeded at -j4, dependency updates disconnected; logs
/tmp/pr300-master-merge-{configure,build}.log. All 138 unit CTest entries passed
in 164.77s with OMP_NUM_THREADS=1 and CTest -j1; log
/tmp/pr300-master-merge-tests.log. Both diagnostic-writer registrations passed.
New P3MRestFrameParallel test skips under the default one-rank registration;
explicit mpiexec -n2 passed GhostPartnerUsesRestFrameSeparation on both ranks.
Rank-specific four-rank load-balancing coverage was not exercised. Clang-format
21.1.8 passed PR-changed C++ files against origin/master; staged diff check passed.
No push authorized for this new merge; leave it local. Existing untracked files
must remain excluded. Initial tracked tree was clean.

CI for d30b42d4: all six GitHub workflows succeeded (GPU checks compile-only).
MI300 pipeline2970878026 entirely SUCCESS including regression17340344979;
Debug136/136 including both writer registrations previously confirmed.
Latest CSCS GH200 pipeline2971789234 has builds green but all three unit jobs
17347346177/178/179 FAILED at diagnostic writer; MPI2 times out after rank0
aborts. Debug trace shows HDF5 H5Eint.c:1622 H5E__push_stack assertion cls_id>0
in FailedHdf5OpenIsCheckedWithoutAssertions. This is a real runtime failure,
NOT the previously reported publication timeout. Regression17347346180 running.
Latest OpenMP pipeline2971789333: all unit jobs succeed; regression17347347019
reports359/359 tests passed, then SLURM time limit during opal-live-doc publication
(exit137). No test failure inferred from that publication failure. No CI reruns
or additional source fixes to these external failures are part of this merge task.

## MI300 fix confirmed in Debug CI — 2026-10-21 08:28 UTC

Read-only recheck: PR300 head remains d30b42d49171de2483ac4ad51bc2bf288ce20a55.
MI300 Debug unit job17340344976 SUCCEEDED, 136/136 tests passed, publication
successful. Actual trace confirms checkout d30b42d4 and MPICH_GPU_IPC_ENABLED=0.
CDash build4351917 confirms TestBeamBeamDiagnosticsWriter passed2.63s (test
541753865, srun -n1) and TestBeamBeamDiagnosticsWriterMPI2 passed2.96s (test
541753866, srun -n2). Both executable paths are build-d30b42d4-debug. The two
previously failing diagnostic registrations now pass on MI300 Debug.
Release jobs17340344977/17340344978 also succeeded, each136/136; CDash
4351907/4351913. MI300 regression17340344979 still running; do not claim full
pipeline/all architectures green yet. GitHub CPU Serial/OpenMP and clang-format
passed; GPU CUDA/HIP/SYCL compilation workflows remain in progress. CSCS
GH200/OpenMP combined statuses pending. No edits beyond this local note,
no commits/pushes/reruns and no new recurring monitor created.

## MI300 diagnostics fix committed/pushed — 2026-10-21 08:00 UTC

User explicitly authorized commit/push and a fresh CI check. Committed only the
three reviewed writer/test files as d30b42d49171de2483ac4ad51bc2bf288ce20a55:
"fix: guard BeamBeam diagnostic append against corrupt HDF5 files".
Pushed to origin/271-implement-interation-point-element; GitHub PR300 head
confirmed at this SHA. The successful push could not update the local tracking
ref inside the sandbox; a subsequent authorized fetch refreshed it successfully.
Tracked worktree clean; existing untracked notes/sandbox files not committed.
Follow-up check: clang-format passed; all five GitHub architecture workflows
are in progress. MI300 project83033814 pipeline2970878026 is running for this
exact SHA. Debug build17340344974 and Release build17340344975 running;
Debug unit job17340344976, Release unit jobs17340344977/17340344978 and
regression17340344979 created, awaiting builds. Debug unit job includes both
TestBeamBeamDiagnosticsWriter and TestBeamBeamDiagnosticsWriterMPI2; neither
has a result yet. The secondary push-triggered pipeline2970877944 is skipped
by design; API-triggered2970878026 is the actual architecture pipeline.
GH200 pipeline2970877886 pending. Do not interpret prior bbfd68364 failures as
results of this fix. No reruns, CI changes or additional test disabling performed.

## MI300 Debug diagnostics fix — validated locally, uncommitted, 2026-10-21

User authorizes investigation/fix, clang and relevant one/two-rank validation;
NO COMMIT. Baseline bbfd6836450c9cd579d96686139d7b5d43ca3f28. Root-cause
inspection found H5hut open_file() error message indexes H5_O_MODES[flags & 0xff].
Collective MPI flag0x40 plus append0x08 gives72, outside the nine-entry table.
Confirmed source both locally (H5hut b5c74f760bc9919d409f46b5472e9eedf9a764d5)
and in the actual MI300 Debug build artifact. This precedes OPALX's handle check.
The GitLab web trace.json endpoint is readable (REST trace returned401) and
confirms IPC disabled, failures at corrupted-file reopen, no stack trace.
Implemented an OPALX-side read-only native-HDF5 append-target preflight on rank0,
followed by all-rank failure agreement before H5hut. No dependency source edits,
physics/kernel changes, tolerance changes or CI changes. Probe is not protection
against concurrent external file changes. Extended existing corrupted-file test
with signature-only/truncated input, scalar/vector rejection, byte preservation
and recovery after restoring valid output, plus error-handler restoration and
open-file handle count checks. Local build_openmp switched from
Release to Debug with dependency updates disconnected; rebuilt selected tests
at -j4. Logs /tmp/pr300-mi300-debug-{configure,build,final-build}.log.
Standalone unmodified H5hut UBSan reproduction at one and two MPI ranks confirms
"index 72 out of bounds for type 'const char *const[9]'" in h5_file.c:482
(macro expansion of the error-message expression at line485). No GPU/Kokkos
code is involved in that reproducer. Source, executable and logs n1.log/n2.log
are in /tmp/pr300-h5-open-ubsan.0rr1e4. Dependency checkout remains clean.
Final Debug CTest run: 5/5 passed in7.35s, covering TestDiagnosticOutput,
TestBeamBeamDiagnosticsWriter (10 gtests each at1/2ranks), and
TestBeamBeamFieldServices at1/2ranks. Gaussian/witness gathering passed;
the retained four-rank-only mirror gtest skipped as designed. Test log:
/tmp/pr300-mi300-debug-final-tests.log. Clang-format21.1.8 --dry-run --Werror
passed for all PR-changed C++ files against master b379e7a5b7276e386519f5daa14af0de99c34854;
git diff --check passed and final diff reviewed. Changed only writer .cpp/.h
and its gtest; no tests disabled. No commit or push. Existing untracked files
preserved. The build_openmp configuration is now Debug, not Release.
Limitations: MI300 itself has not been rerun with this uncommitted fix. This
targeted adapter workaround prevents the reported corrupt-append failure; it
does not repair H5hut's underlying error formatter for all other open/create
failures or concurrent external file changes. Extra read-only open/close and
status collective affect diagnostics I/O only, not numerical work or kernels.
Next: user review/authorization before commit/push and subsequent MI300 CI check.

## PR300 CI check — 2026-10-21 07:40 UTC

Read-only check of current head bbfd6836450c9cd579d96686139d7b5d43ca3f28.
MI300 pipeline 2970743990 (project 83033814): Release unit jobs 17339312709
and 17339312710 succeeded, each 136/136 (CDash builds 4351812/4351813).
The new TestBeamBeamDiagnosticsWriterMPI2 actually ran with srun -n 2 and
passed in 2.78/2.94 seconds respectively; single-rank writer also passed.
Debug job 17339312708 FAILED: CDash build 4351821 has 134 passed, 2 failed.
Both TestBeamBeamDiagnosticsWriter and TestBeamBeamDiagnosticsWriterMPI2
segfault in BeamBeamDiagnosticsIOTest.FailedHdf5OpenIsCheckedWithoutAssertions.
CDash test IDs 541694220/541694221 contain the actual output: scalar readback,
filesystem failure/retry and HDF5 write failure/retry pass before the crash.
The failing case deliberately corrupts an HDF5 file and expects OpalException
on reopening. No stack trace is available here; the exact crashing frame is
not established. This occurs at both one and two ranks, not only MPI2.
MI300 CI still sets MPICH_GPU_IPC_ENABLED=0. FieldServices and FieldServicesMPI2
pass in Debug and both Release jobs, so this is distinct from the previous
Gaussian SIGBUS symptom. MI300 regression job 17339312711 is still running.
Direct GitLab trace access returned HTTP401; used actual CDash GraphQL test
output instead. Executable paths contain build-bbfd6836-{debug,release}.
GitHub CPU Serial/OpenMP and clang-format succeeded; CPU OpenMP log confirms
new MPI2 writer passed. GPU CUDA/HIP/SYCL compilation workflows still running.
CSCS OpenMP Debug/Release-one-rank each passed136/136 including MPI2 writer;
Release-four-rank allocation and regressions still running. GH200 builds still
running; runtime jobs not started. No source/CI edits, reruns, commits or pushes.
Next: report Debug failure; await authorization before implementing a fix.

## PR300 audit remediation — committed and pushed, 2026-10-21

On subsequent explicit user authorization, showed the commit message first,
then committed the 23 reviewed source/test files as bbfd6836450c9cd579d96686139d7b5d43ca3f28
(fix: harden BeamBeam diagnostics and complete API documentation) and pushed to
origin/271-implement-interation-point-element (PR300). HEAD and upstream match;
tracked worktree is clean. Local notes and sandbox files remain untracked and
were not included. Subsequent CI findings are recorded above.

User authorized fixing audit findings, Doxygen cleanup, clang/tests, NO COMMIT.
Implemented lazy rank-zero animation with checked output and nonfatal disabling
on I/O failure; strict diagnostic-step parsing; HDF5 scoped handles, unconditional
checks and synchronized error reporting; corrected element/field-service/writer
Doxygen and explicit-vs-legacy emitted reference-position documentation. Removed
unused animation constant and timer. Kept public physics model, numeric kernels,
tolerances, entry diagnostic solves/snapshots and charge validation unchanged.
New MPI collectives are confined to HDF5 diagnostic status checks, not solver
execution. Added focused gtests for invalid output limits, animation I/O and
side-effect-free interaction creation, HDF5 append/readback and failed preparation
on all ranks, close/destructor lifecycle; added MPI2 writer registration.
Validation complete:
- CMake configured build_openmp with FETCHCONTENT_UPDATES_DISCONNECTED=ON to
  avoid fetching dependency changes. Fixed a CMake list-quoting issue in the new
  test registration during configuration. Rebuilt the library and all nine
  selected test executables successfully using at most four build CPUs. Existing
  unrelated missing-override warnings remain; no new compiler errors.
- All 11 selected CTest registrations passed in 4.61 seconds: TestEmittedFromFile,
  TestDiagnosticOutput, TestBeam, TestBeamBeamDiagnosticsWriter (1/2 MPI ranks),
  TestBeamBeam, TestCartesianPIC3DAlgorithms, TestCartesianPIC3DFields,
  TestBeamBeamFieldServices (1/2 MPI ranks), TestOpalDrift. The retained
  MirrorFieldZHandlesNonSlab3DDecomposition gtest skipped as designed because it
  requires four ranks. Gaussian/witness and overlap checks passed at 1/2 ranks.
- Additional manual MPI2 run of ConstructingInteractionDoesNotTouchAnimationOutput
  passed on both ranks. Tests use OMP_NUM_THREADS=1. Sandbox MPI launch failed
  before execution ("All nodes ... already filled"); approved outside-sandbox
  reruns succeeded. No four-rank registrations reintroduced and no GPU runs.
- Ten new gtests cover parser bounds/errors, animation open/error/no-construction
  side effects, HDF5 scalar append/readback, vector and two-stage readback,
  coordinated filesystem failure/retry, actual HDF5 open/write failures, and
  close/destructor lifecycle. Writer tests exercise all cases at 1/2 ranks.
- clang-format 21.1.8 --dry-run --Werror passed for all PR-changed tracked C++
  source/tests plus both new files. git diff --check passed; source diff reviewed.
- Targeted Doxygen XML generation completed with no warnings in the audited
  BeamBeam element, field-service, animation, HDF5-writer and DiagnosticOutput
  headers. Existing warnings elsewhere in the partial-input audit are not claimed
  fixed. Configuration: /tmp/opalx-pr300-audit.8Ic1F8/Doxyfile.

Logs: /tmp/pr300-audit-cleanup-{configure,build,tests,animation-mpi2}.log.
The reviewed edits, including new src/Utilities/DiagnosticOutput.h and
unit_tests/Utilities/TestDiagnosticOutput.cpp, are now in the commit above.
Existing untracked sandbox/notes preserved. Next: await user direction.

## PR300 source audit — 2026-10-21

Scope: user requested Doxygen/coding-quality audit; test coverage explicitly
left out for now. Reviewed PR head a203a4d50df04455069ca2b7ade4c85836401e10
against master b379e7a5b7276e386519f5daa14af0de99c34854. No source changes,
build/test execution, commits or pushes. Frozen-field approximation accepted.

Findings to address on authorization:
- BeamBeamInteraction unconditionally constructs BeamBeamWindowAnimation;
  its ofstream truncates data/collision_ascii_frames.txt on every MPI rank even
  with VISUALIZE disabled. Construct lazily on the writer rank only.
- H5BeamBeamDiagnosticsWriter uses PAssert for file/property failures (the
  checked local IPPL header disables PAssert on AMD HIP); use unconditional
  runtime error checks. Raw handles lack exception cleanup; its instance
  destructor calls potentially throwing close(). Only static scalar writing is
  currently used by the production BeamBeam caller; distinguish that active
  path from the unused instance API when fixing lifetimes.
- OPALX_SC_FIELD_H5_STEPS parser returns true on invalid/out-of-range input,
  causing unbounded per-step diagnostic output. Validate the complete value,
  reject invalid input or fail closed, and document the supported semantics.
- New element headers retain drift descriptions and lack substantive class
  Doxygen (especially OpalBeamBeam/BeamBeamRep).
- BeamBeamFieldServices configure/domain/charge-result lifecycle contracts and
  depositCharge's new optional global charge output need precise documentation:
  frames, units, collective calls, policy restrictions and invalidation.
- H5 writer class comment describes one-file physical-density two-stage output;
  active producer instead uses per-quantity static writing with normalized
  primary rho. Document both APIs separately, including normalization/units.
  EmittedFromFile initial-reference-position doc also needs explicit-vs-legacy
  format qualification: only explicit-birth records use mean file position.
- Lower-priority cleanup: unused transformBackTimer_m and
  postWindowVisualizationSteps_m; copied slice comments/scaffolding; consider
  making entry-transition diagnostic snapshots/extra solve explicitly opt-in
  while preserving the charge validation independently.

Checks: source diff whitespace check passed. Targeted Doxygen XML generation
completed using temporary /tmp/opalx-pr300-audit.8Ic1F8/Doxyfile; warnings include
inherited symbols and missing context, so the raw 700-line log is NOT a count of
PR defects. New-header warnings were checked against source. No runtime failure
reproductions or numerical validation claimed. Next: await direction on fixes.

## Remove inactive four-rank registrations — 2026-10-21

User requested removal of four-rank unit tests with clear rationale. Removed
the two already-disabled explicit MPI4 CTest registrations from Distribution
and SpaceCharge CMakeLists; retained all test source for manual diagnostics and
the enabled single-/two-rank coverage. Documented history, scope, coverage gap,
manual revalidation and distinction from MI300 IPC/GH200 publication issues in
ci/cscs/cscs-ci-cd.md. No physics, tolerances or CSCS job allocation changes.
Subsequently committed/pushed on explicit user request as a203a4d50
(test: remove disabled four-rank BeamBeam registrations). Only the three
reviewed tracked files included; tracked tree clean and upstream synchronized.
Smoke tests unchanged; local notes/sandbox remain untracked. Relevant existing binaries passed all three retained
CTest registrations (TestEmittedFromFile and FieldServices at one/two ranks).
CMake reconfiguration completed successfully (refreshing dependency checkouts).
Generated CTest JSON confirms 134 registrations, zero disabled, no MPI4 entries,
and retained commands at ranks 1/1/2. Sandbox MPI launch initially failed with
"All nodes ... already filled"; the identical CTest subset outside the sandbox
passed 3/3. Tests used existing binaries: no C++ source changed or rebuild needed
for this registration-only change. Diff reviewed and git diff --check passed.

## All-architecture CI monitoring — terminal, 2026-10-21

User requests periodic PR300 checks and success verdict for all architectures.
Reactivated existing heartbeat check-pr-300-mi300-ipc-off-tests at two-minute
interval, renamed Check PR 300 CI on all architectures; now tracks exact head
6a9d4d7a8ccfb96386d272b2869d98fa1479389b. Initial status: clang passes, GitHub
CPU Serial/OpenMP, GPU CUDA/HIP/SYCL in progress, CSCS MI300 2969388752,
GH200 2969388617 and OpenMP 2969388891 pending. Must include regression outcomes
and distinguish compile-only GPU coverage. Four BeamBeam smokes remain disabled.
Requested changes already committed/pushed; no further changes to commit. Quiet
while unchanged; report failures and final verdict, then pause on completion.
23:15 Zurich check: PR head unchanged; GitHub CPU Serial and clang passed,
CPU OpenMP/CUDA/HIP/SYCL still running. MI300 builds/all three unit jobs pass;
latest CDash Debug 4348808, Release1 4348799, Release4 4348801 each 134 passed,
0 failed, 2 disabled. MI300 regression still running. CSCS OpenMP Release unit
jobs pass, Debug/regression running; GH200 builds running. No new failures;
no notification during normal progress.
23:37 Zurich check: MI300 pipeline 2969388752 is fully successful, including
regression job 17330220441; GitHub commit status cscs/cscs-ci-mi300 is success.
GitHub CPU Serial/OpenMP, HIP compilation and clang pass. CUDA/SYCL workflows
still running; GH200 builds and CSCS OpenMP regression still running. No failures
so far. Continue monitoring remaining architectures without checkpoint notices.
23:51 Zurich check: all three CSCS architectures now have successful Debug and
Release unit jobs. GH200 and OpenMP regression jobs remain running; MI300 remains
fully successful. GitHub SYCL compilation has also passed; CUDA workflow is the
only remaining GitHub workflow. PR head unchanged; no failures or action needed.
23:53 Zurich: CSCS OpenMP regression 17330221298 succeeded, completing all six
jobs in pipeline 2969388891; combined OpenMP status now success. Only GitHub CUDA
and GH200 regression remain in progress. No failures.
00:05 Zurich (Oct 21): all six GitHub workflows now succeeded, including CUDA
compilation. Only GH200 regression 17330219618 remains running. Public GitHub
REST returned 403; connected GitHub tools successfully verified unchanged head,
all workflow results, and combined statuses. Use the connected tools for further
GitHub polling. MI300 and OpenMP pipelines remain fully successful.
00:27 Zurich final: all expected jobs terminal at unchanged 6a9d4d7a8.
All six GitHub workflows passed (GPU workflows compile-only). MI300 and OpenMP
six-job pipelines passed. GH200 builds and all three unit jobs passed, but
regression job 17330219618 failed during publication, NOT during tests:
raw job log reports "Summary: 359 / 359 tests passed" at 21:57:41 UTC and
"Regression tests finished (run_tests exit code 0)" at 21:57:45 UTC.
Then opal-live-doc checkout/update processed 178569 files until 22:26:45 UTC;
termination at 22:27:02, runner reports probable SLURM timelimit, exit 137.
Thus numerical regression checks passed but overall CI is NOT all green.
Log: https://gitlab.com/cscs-ci/ci-testing/webhook-ci/mirrors/6151408209445194/694321096757981/-/jobs/17330219618/raw
CDash current nine unit builds each show 134 passed, zero failed, two disabled:
MI300 4348808/4348799/4348801; GH200 4348867/4348863/4348862;
OpenMP 4348812/4348805/4348804. GH200 Debug command explicitly uses
build-6a9d4d7a-debug. Four new BeamBeam GitHub smokes remain intentionally disabled.
Next: request authorization to fix/bound publication checkout/update, not physics
or tolerances; do not rerun/change CI without direction. Pause completed monitor.

## Temporary beam-beam smoke disable — 2026-10-20

User requests temporary smoke disable following missing-input diagnosis.
Comment out only the four BeamBeam matrix entries in cpu-serial.yml; retain
three existing smoke cases, all unit tests and launch/comparison logic. Inline
comment specifies re-enable after regression-tests-x/pr-300 inputs reach default
branch. No physics changes. YAML comparison confirms no other workflow changes;
git diff --check passed. User subsequently authorized commit/push: committed
6a9d4d7a8ccfb96386d272b2869d98fa1479389b and pushed to PR300 branch, remote tip
verified identical and tracked tree clean. Next: verify all architecture CI
results on this exact SHA. A green run excludes these four temporarily disabled
smokes; do not claim they were validated. No permission to disable other tests
or alter physics to make CI green.

## Final-cleanup CI and smoke-test diagnosis — 2026-10-20

Status-only user request at head 8bd7c8fb9. Normal six-job MI300 pipeline
2969311485: both builds and all three unit jobs success; regression job
17329692808 still running. CDash Debug 4348743, Release1 4348732 and Release4
4348735 each show 134 passed, 0 failed, 2 disabled. No extra diagnostic job.
GitHub CPU Serial run 39493305702: build/unit and three old smoke tests pass;
all four BeamBeam smoke jobs fail before launching OPALX. Retrieved actual logs
via GitHub connector (public curl job-log endpoint previously unavailable).
Jobs RigidSource 118879682895, TimedBirths 118879682671, OffsetKick 118879682722,
WitnessMPI 118879682743 all fail at find with missing RegressionTests/BeamBeam-*
directory. .github/workflows/cpu-serial.yml clones regression-tests-x default
branch with no ref; remote master has none of those four folders, remote pr-300
has all four. This is test-input branch integration, not a physics/IPC failure.
Recommend integrate regression-tests-x/pr-300 into default branch, or explicitly
pin a validated regression-tests commit while it is under review; do not skip
tests or loosen tolerances. Existing CSCS regression configuration also uses
master, so its success does not demonstrate these four new cases ran.
No source/CI changes, reruns, commits or pushes authorized/performed this turn.

## Retain MI300 workaround / remove temporary diagnostics — 2026-10-20

User requests permanent MI300 IPC-off CI default, no PR restrictions or extra
diagnostic runs; commit/push authorized, no physics changes. Move IPC=0 to
MI300 entry-point variables for all refs; delete paired diagnostic job/script
and temporary rules/suffix/automatic phase logging. Keep optional C++ markers
unchanged and off by default. Promote validated four-CPU/OMP=1 settings into
MI300 test templates so removing PR rules does not inflate allocations. Keep
normal six-job matrix/failure propagation. Document evidence, scope, potential
performance impact and revalidation conditions in existing CI guide. Deleted
diagnostic script remains recoverable from Git. Recursive YAML resolution
validates six normal jobs on all refs; IPC-off is present only in MI300,
not GH200/OpenMP. Shell syntax checks pass for all three architecture pipelines;
no dangling script/job/PR-specific/suffix references. Five-file diff reviewed,
git diff --check passes. Full local CPU suite without diagnostics passed all
134 enabled tests (two original MPI4 tests remain disabled); log
/tmp/opalx-mi300-workaround-final-ctest.log. No C++ changes. Next: commit/push
and confirm remote normal MI300 matrix starts. Prior MI300 suite was green;
this final cleanup commit still needs its own remote run. Committed/pushed as
8bd7c8fb90993cd0259a9eb1f67e98a3ffe6047d; remote tip verified identical,
tracked tree clean. Existing unrelated untracked files preserved. Monitoring
heartbeat remains paused; no new recurring monitoring requested.

## MI300 repeat/full-suite status check — 2026-10-20

PR head remains cd128ab10. Pipeline 2969182428 builds both successful.
Repeated isolated baseline: CDash 4348629/test 540997605, rank0 SIGBUS after
17.13 s, same last markers on both ranks before solver construction/FFT warmup.
Repeated IPC-off: CDash 4348630/test 540997606 passes 8.12 s, all phases and
assertions completed both ranks. This reproduces the earlier fail/pass pair;
supports an IPC-sensitive issue but does not establish library bug ownership.
Full IPC-off Release one-rank job 17328719917/build 4348635 and four-rank job
17328719918/build 4348636 both pass 134 enabled tests, 0 failures, 2 disabled.
MPI2 FieldServices tests 540998975/541000289 both pass from cd128ab1 binary;
four-rank job name is allocation, these explicit registrations still run -n 2.
Final heartbeat check 20:31 UTC: Debug full-suite job 17328719916 succeeded;
CDash 4348643 confirms 134 passed, 0 failed, 2 disabled (423 s). Regression job
17328719920 succeeded at 20:30:48 UTC; PR head unchanged. All standard MI300
unit/regression jobs with IPC disabled are now successful. Overall pipeline
still contains the intentionally failing inherited-IPC diagnostic; do not claim
the default configuration is fixed. Regression success verified via GitLab job
status, not a separately retrieved case-by-case regression report. Two-minute
heartbeat check-pr-300-mi300-ipc-off-tests paused after completion.
Status-only task: no source/CI edits, commits or pushes.

## Repeat MI300 diagnostics and full IPC-off suite — in progress, 2026-10-20

User authorizes CI-only changes, commit and push. Restore Release build, all
three standard MI300 unit jobs and NightlyBuildX regression job on PR300; scope
IPC-off env/phase logging/four CPUs total to exact __CSCSCI__pr300 only. Keep
paired diagnostic unchanged in its own process/job; full suites depend only
on builds and use when:always so baseline failure does not suppress coverage.
Add IPC-disabled CDash suffix and environment logging in ROCm unit template.
No physics, source tests, dependencies, tolerances or test selection changes.
One-rank jobs allocate four CPUs since they also launch MPI2 registrations;
four-rank job allocates one CPU/rank. OpenMP remains one thread/rank.
Validation: recursive local YAML include/extends/reference resolution passes;
seven PR300 jobs versus six standard jobs on master/PR301; IPC-off only on
full-suite jobs; four-CPU test allocation budgets, build-only needs and
when:always checked. ROCm/diagnostic scripts pass bash -n. git diff --check
passes and three-file diff reviewed. Both local diagnostic variants pass;
all 134 enabled CPU tests pass in 17.49 s, original two MPI4 tests still disabled.
Logs: /tmp/opalx-mi300-repeat-diagnostic.log and
/tmp/opalx-mi300-full-ipc-disabled.log. No C++ files changed (clang not applicable).
Committed and pushed cd128ab10ba32f099bbe5099f235da5b2bc5474f; local and remote
tips verified identical, tracked tree clean. CSCS MI300 pipeline 2969182428
created for this SHA/ref, pending. Next: inspect repeated diagnostic and full IPC-off
remote results. Local CPU success does not validate HIP IPC.

## MI300 diagnostic results — 2026-10-20

Read-only CI check at PR head 11e1e8391: GitLab pipeline 2969102201 contains
only Debug build (success) and diagnostic job 17328082331 (failed as designed
because baseline fails). CDash baseline build 4348595/test 540966122 fails
SIGBUS rank 0 in 15.74 s; IPC-off build 4348596/test 540966123 passes in 8.06 s.
Both execute only GaussianFieldsAndPassiveWitnessGather, same Debug binary,
two ranks, same Slurm allocation. Baseline IPC env unset; second run logs 0.
Both ranks select distinct HIP devices 0/1; CRAY MPICH 8.1.32.110, HIP 6.3.42134,
HSA_XNACK=1; MPICH_GPU_SUPPORT_ENABLED remains unset in both.
Baseline last markers on both ranks: before solver construction/FFT warmup;
neither after-marker nor before first solve is reached. IPC-off reaches every
phase, both numerical assertions and successful teardown on both ranks.
This strongly implicates an IPC-sensitive communication/memory interaction,
not the witness gather specifically; asynchronous work means these markers
are not an exact faulting-kernel backtrace. One pair does not prove MPI-library
ownership versus application/dependency lifetime/synchronization issues.
Suggested next step (not performed/authorized by status request): repeat paired
diagnostics and validate full MI300 suite with IPC disabled before treating it
as a reliable platform workaround. Restore normal coverage before merging.
Other current CI: CPU Serial/OpenMP build+unit and clang pass; CSCS Zen all
three unit jobs pass, regression running; GH200 builds running. Four GitHub
BeamBeam smoke jobs fail; no new log diagnosis performed in this check.
Evidence: https://my.cdash.org/tests/540966122 and
https://my.cdash.org/tests/540966123 . No source/CI changes, commit or push.

## MI300 diagnostic CI implementation — in progress, 2026-10-20

User authorizes phase markers, isolated Gaussian MPI2 baseline and IPC-off runs,
commit and push; no physics changes. Restrict temporary MI300 coverage to these
two runs on exact verified mirror ref __CSCSCI__pr300, retaining Debug build.
Other refs/platforms unchanged. New dedicated CTest dashboard runs both variants
even if baseline fails, submits separate entries and keeps XML artifacts. Markers
are opt-in logging only (no fences), record phase/MPI/device environment. New
script ci/cscs/mi300-beambeam-diagnostics.cmake, edits cscs-mi300.yml, existing CI
guide and TestBeamBeamFieldServices.cpp. First compile caught incorrect MPI
constant spelling, corrected to MPI_MAX_LIBRARY_VERSION_STRING.
Validation complete: Release/OpenMP target builds with -j4; normal one-/two-rank
tests pass (0.21/0.17 s), both isolated variants pass. Decoded saved XML confirms
exactly one gtest case, complete phase markers on both ranks and the intended
IPC environment. Increased dashboard output limits to 1 MiB because CTest's
1024-byte passing-output default hid the markers. Raw per-variant logs retained.
Synthetic failing baseline confirms second variant runs and overall job fails;
unrelated test excluded. YAML parse/rule checks preserve six normal jobs for
master/other PRs and select Debug build + diagnostic for __CSCSCI__pr300.
clang-format 21.1.8 and git diff --check pass. HIP device-id branch awaits remote
compilation; no local GPU validation. Four commit targets only, preserve all
untracked sandbox/local notes. Committed and pushed as
11e1e8391d0528e3173735453470e67fc19c5c5b; remote tip verified identical, tracked
tree clean. Immediate GitHub status query is pending with no CSCS status entries
yet. Next: inspect remote MI300 diagnostic pipeline/results when published.
Remove temporary PR-specific coverage override before merge. This supersedes
earlier investigation ideas below: baseline preserves GPU support/IPC settings,
second changes only IPC; no fences/barriers or physics modifications added.

## MI300 bus-error investigation — 2026-10-20

Diagnostic request only: no source/CI/dependency changes or remote job submission.
At PR head 5a82b9ad1, CDash Debug build 4348313: single-rank FieldServices
test 540845363 passes, Gaussian case 3089 ms. Same executable at two ranks,
test 540845364, fails after 12.29 s: overlap case passes, Gaussian starts,
rank zero receives SIGBUS, rank one is subsequently terminated. Release
tests 540835900/540836100 reproduce at 11.00/11.02 s on different nodes.
No backtrace or phase markers: cannot yet identify the crashing operation.
The test runs a Poisson warmup during construction and a full primary solve
before creating/migrating eight witnesses from rank zero, then gathers,
solves again, and gathers again. Do not infer it reached witness gathering.

Two ranks add IPPL migration, GPU-buffer MPI, halo exchange and distributed
FFT transfers; ParticleSpatialLayout::update returns before migration when
nRanks < 2. Gaussian uses 32768 particles and 48^3 mesh on both AMD backends;
passing overlap case has 64 particles/rank and 8^3 mesh. Message sizes and
allocation/reuse patterns differ substantially. Leading hypothesis is
GPU-aware MPI/IPC/buffer lifetime or synchronization; empty-rank receive/gather
handling and FFT communication remain candidates, not established diagnoses.
Local IPPL source has raw HIP archive allocation rounded to 64 KiB and buffer
retention specifically for MPI registration-cache safety; this does not prove
which IPPL revision the remote job used or that the remaining fault is in IPPL.

MI300 CI sets HSA_XNACK=1, but does not explicitly export
MPICH_GPU_SUPPORT_ENABLED or use a rank-to-GPU wrapper in the observed command.
They may be supplied by the uenv/Kokkos; inspect actual rank environment and
device selection rather than declaring GPU support/binding absent. The MI250
pass is user-reported; exact commit, dependency versions, rank count, filter,
GPU binding, MPI/GTL and ROCm versions have not been supplied for comparison.

Next MI300 diagnostics: run Gaussian alone versus complete fixture at two ranks;
record versions/env/GPU IDs; repeat with MPICH_GPU_SUPPORT_ENABLED=1 and
MPICH_GPU_IPC_ENABLED=0 (diagnostic host staging, not a production fix).
If needed add rank-tagged phase markers with fences around construction/warmup,
first solve, witness migration, each gather and second solve, and collect a
Debug core/backtrace. Fence-enabled success alone does not identify a culprit.
Keep all physics tolerances and the frozen-field model unchanged.
References: https://my.cdash.org/tests/540845364 ;
https://docs.cscs.ch/software/communication/cray-mpich/ ;
https://cpe.ext.hpe.com/docs/latest/mpt/mpich/intro_mpi.html .

## Origin/master merge — validated, 2026-10-20

User requested merging master into PR #300. Starting tracked tree is clean at
`d1194f64d`, matching origin/271-implement-interation-point-element. Fetched
origin/master at `b379e7a5b`. Plan: merge, review resolutions, rebuild
build_openmp with at most four CPUs, and run local single-/multi-rank tests.
Preserve untracked sandbox content and disabled MPI4 tests. No push requested.
Nine conflicts resolved and staged. Retain both additive BEAMBEAM/end-field
registrations, Beam attributes/tests, and PartBunch metadata. ParallelTracker
resolves decay followers to their chain root while preserving secondary
ORBITTHREADER=FALSE primary-map sharing. Secondary daughters can precede their
roots; upstream TrackRun still rejects a daughter as container zero.
No physics-kernel/tolerance changes
in the resolution. All PR-modified C++ files pass clang-format 21.1.8.
The old build_openmp directory is absent. Fresh Release configuration uses
Homebrew LLVM 21 and explicit libomp include/library paths (automatic OpenMP
detection initially failed); dependencies are being fetched. Evidence logs:
/tmp/opalx-merge-20261020-{configure,format}.log. Merge not committed yet.
Fresh configuration succeeded: IPPL 704932fdaa390f883524cf53588c92386294add4,
Kokkos 5.2.2 (8e15454876298832f013ebcaf08d53825b5bda40), LLVM 21.1.8.
Full build running with -j4; /tmp/opalx-merge-20261020-build.log. CTest inventory
has 136 registrations. Prepared a temporary mixed decay/map-sharing smoke deck
at /tmp/opalx-merge-20261020-smoke/decay-map-sharing.in (four steps, no HDF5).
All 62 PR-modified C++ files pass formatting; diff against master has no
whitespace errors. Upstream itself includes one trailing blank line in
unit_tests/AbsBeamline/EndFieldModel/CMakeLists.txt, left unchanged.

Full Release/OpenMP build passed at -j4. Existing upstream missing-override
warnings in AsymmetricEnge/ScalingFFAMagnet and two visitor test fixtures are
unchanged from master. Initial sandbox MPI launches reported no CPU slots;
rerunning outside the sandbox passed all 134 enabled CTest registrations in
57.09 s, including BeamBeamFieldServices at one/two ranks (0.49/0.17 s).
The two MPI4 registrations remain disabled. Logs and JUnit XML are
/tmp/opalx-merge-20261020-ctest.{log,xml}.

All four short beam-beam cases passed all 49 existing reference-stat assertions,
using the comparator directly from .github/workflows/cpu-serial.yml and original
.rt tolerances. WitnessMPI ran with two ranks; the other cases with one.
Mixed secondary-root primary-map sharing plus an earlier-listed decay daughter
completed four steps at one and two ranks. Logs confirm daughter BE follows BM
and BM reuses the primary map. Evidence is in
/tmp/opalx-merge-20261020-smoke/. No additional Python script, numerical tolerance,
dependency-source change, or HDF5 output was introduced. These are local CPU
checks, not validation of the previous MI300 failure. Merge committed as
`5a82b9ad1fb8188718360af763bb60a54838bb21`, parents d1194f64d and b379e7a5b.
Final remerge-diff reviewed, tracked tree clean, origin/master is an ancestor.
On explicit user request, refreshed remote refs and rechecked all 62 PR-modified
C++ files with clang-format 21.1.8 plus git diff --check: passed. Pushed
5a82b9ad1 to origin/271-implement-interation-point-element on 2026-10-20.
Local and remote tips match; tracked tree clean. CI has not yet been checked
for this push (especially the previously unresolved MI300 case).

## LUMI reproduction guidance — 2026-10-09

Latest inspected MI300 Debug build 4263886 (source d1194f64, ROCm 6.3.3):
TestBeamBeamFieldServicesMPI2 fails in 12.22 s with rank-zero Bus error during
GaussianFieldsAndPassiveWitnessGather; the preceding overlap case passes.
Single-rank registration passes in 8.54 s. Log:
https://my.cdash.org/tests/522600661 . User has built on LUMI and requested
interactive launch instructions, not remote execution. Consulted official LUMI
interactive, partition, GPU binding and programming-environment documentation.
Recommend dev-g salloc, two MPI ranks/two GPU GCDs, at most four CPU cores,
OMP=1, matching build modules and MPICH_GPU_SUPPORT_ENABLED=1. Run the complete
TestBeamBeamFieldServices binary first, then Gaussian-only at two/one ranks.
LUMI-G uses MI250X/gfx90a, not MI300/gfx942: success there does not clear the
MI300-specific failure. No LUMI job submitted, source edit, commit or push.

## Origin/master merge — validated, 2026-10-08

Fetched `origin/master` at `245202d0b` and merged it into
`271-implement-interation-point-element` from `260b2825b`. The six textual
conflicts were additive registration sites for the branch's `BEAMBEAM` and
master's new `BOX` element; both entries were retained without changing the
master `BOX` implementation. Existing untracked documentation and numbered
experiment directories were left untracked and untouched by Git.

The Release/OpenMP `build_openmp` tree rebuilt successfully with `-j4`; the
configure output confirms Kokkos 5.2.0. Full CTest passed all 121 enabled tests
in 42.58 s, with the two explicitly disabled MPI4 registrations not run.
Manual four-rank runs of `TestBeamBeam` (21/21 per rank) and
`TestBeamBeamFieldServices` (3/3 per rank, `OMP_NUM_THREADS=1`) passed. The
merge resolution has no physics, units, boundary-condition, discretization,
tolerance, or reduction-order change. No push was performed.

## Full local unit-test audit — complete, 2026-10-07

User reports remaining timeout and requests all local unit tests. Source HEAD
260b2825b, tracked tree clean. Reconfigure build_openmp with dependency updates
disconnected (retain fetched dependency revisions), full Release/OpenMP rebuild
at -j4, then full CTest with OMP=1 and serial scheduling so MPI2 stays within
four-CPU limit. Keep two MPI4 registrations disabled as requested. Logs under
tmp/unit-tests-20261007/. No production edits, commit/push or new exclusions.
Latest CDash index already lists CPU Debug 4250836 with 119 passed, zero failed,
two disabled; determine whether reported timeout is an older submission.

Current CI inspection confirms Zen Debug FieldServices passes in 6.83 s and
MPI2 in 3.98 s (build 4250836). Latest CPU Release and GH200 Debug/Release
also show 119 passed, zero failed, two disabled. MI300 Debug build 4250833
(source build-260b2825) still fails FieldServicesMPI2 in 12.21 s: rank-zero
Bus error in GaussianFieldsAndPassiveWitnessGather, then peer terminated;
this is not a timeout. Log: https://my.cdash.org/tests/519353052.
Local inventory is 121 registrations: 119 enabled and the two MPI4 disabled.

Full Release/OpenMP rebuild completed successfully with -j4 (no compiler
warning/error diagnostics). Full CTest run with OMP_NUM_THREADS=1, BLAS thread
limits=1, serial scheduling and MPI binding disabled passed all 119 enabled
registrations in 68.42 s; zero failures/timeouts, the two MPI4 tests remain
disabled. BeamBeamFieldServices passed at one rank in 0.68 s and two ranks in
0.26 s, both within the unchanged 30 s timeout. Configure/build/CTest logs and
JUnit XML are in tmp/unit-tests-20261007/. This validates local macOS Release,
not local Debug or MI300; remote Zen Debug is green as recorded above. Tracked
tree remains clean; no production changes, commit or push. Remaining known CI
issue is the MI300 MPI2 bus error, which requires a separate diagnosis.

Supplemental two-rank runs also pass all four BunchStateHandler AggressiveSync
cases and FFT2D5 Configuration_MultipleRanksRejected, which skip at one rank;
each run used OMP=1 and a 30 s launcher timeout. Logs are in the same directory.
Remaining individual gtest skips: the external PSI cyclotron map benchmark
(OPALX_COF_CYCLOTRON_MAP not supplied), and the explicitly four-rank mirror-field
case. Slowest full-suite registration was TestMultiVariateGaussian at 2.20 s.

## Merge-brace repair — complete, 2026-10-06

On explicit user request, restored the closing brace and blank separator between
ParallelTracker::visitBeamBeam and visitFieldmapElement. Clang-format 21.1.8
passes all 62 PR-modified C++ files; ParallelTracker.cpp syntax-only compilation
with existing build flags and -Werror=inconsistent-missing-override passes.
Whitespace/diff reviewed; no full executable rebuild or runtime suite rerun for
this syntax-only repair. Committed as 260b2825b (Fix missing BeamBeam visitor
brace after master merge) and pushed to origin/271-implement-interation-point-element.
Tracked tree clean; unrelated untracked files unchanged. CI result still pending.

## Post-pull formatting check — 2026-10-06

User requested pull and recheck. Fast-forwarded branch 9e3d4f4a4 -> 2b1fffe33
(merge of master), refreshed origin/master to 33d444649. Clang-format 21.1.8
checks 62 PR-modified C++ files: 61 pass, ParallelTracker.h fails. Inspection
shows merge omitted the closing brace after visitBeamBeam's call (line 521),
so visitFieldmapElement begins inside it at line 522. This is a C++ syntax defect,
not merely formatting. No source edits/commit/push during this check; tracked
tree remains clean. Next step requires fixing the missing brace, rechecking
formatting and compilation, then an authorized commit/push.

## Reduce CPU Gaussian regression cost — locally validated, 2026-10-06

User requested aggressive CPU-case cost reduction, not MI300 debugging. Plan:
reduce the host-only Gaussian quadrature and mesh, retaining the 3% analytic
E/B bound, source-charge checks, both solves and passive-witness MPI migration.
Keep the device test configuration unchanged. Check local one-/two-rank results
with one OpenMP thread and record timings/accuracy. Production physics code,
30-second timeout and disabled MPI4 registrations remain unchanged. No commit
or push requested. Original fast-target rebuild and CPU 1/2-rank baseline pass:
Gaussian case 1030/562 ms (OMP=1). First candidate 16 samples/axis, 16 mesh
cells/axis and +/-4 mm transverse box took 38 ms but failed the unchanged 3%
bound (E 4.47%, B 4.51%); rejected. Now testing 24 cells/axis with the same
16 samples/axis and tighter box. This retains the original rest-frame grid
spacing while reducing mesh cells and source particles eightfold. The 24-cell/
16-sample candidate still narrowly failed (E 3.08%, B 3.12%, CPU 110/61 ms), so
retain the smaller mesh but increase quadrature to 24 samples/axis for margin.

Final change in unit_tests/SpaceCharge/TestBeamBeamFieldServices.cpp: host-only
24^3 source particles (13,824 vs 32,768), 24^3 mesh (13,824 vs 110,592 cells),
transverse half-width 4 mm and lab longitudinal half-width 2 mm. Grid spacing
is unchanged; all source nodes/probes remain inside the isolated open domain.
Total source charge, units, gamma, witness positions, deposition/gather checks,
two solves and 3% E/B bounds unchanged. Fixture sampling/discretization changes;
production algorithms and MPI call order do not. Device builds retain 32 samples,
48^3 mesh and original domain via OPALX_DEVICE_COMPILATION. Added gtest XML
properties for measured relative L2 E/B errors.

Fresh fast-target test-TU build against existing Release libraries passes.
Local Release OMP=1 CTests pass at one/two MPI ranks: Gaussian 110/62 ms versus
1030/562 ms baseline (~9x faster); whole CTests 0.74/0.26 s including startup.
Single-rank XML errors E=0.023258877554178603, B=0.023584753656340746, both below
unchanged 0.03. Formatting and diff checks pass; diff reviewed. Logs/XML under
/tmp/opalx-field-services-{baseline,small,small24,cpu24}*. No GPU or full Debug
library rebuild performed; Eiger Debug runtime needs CI confirmation. No MPI4
run (still disabled). Subsequently committed and pushed on user request as
`9e3d4f4a4` (Reduce CPU BeamBeam Gaussian regression cost) to
`origin/271-implement-interation-point-element`. Tracked tree clean. Zen CI
confirmation remains pending; no claim of a passing remote Debug run yet.

## Latest CDash CPU/OpenMP failure — 2026-10-06

Read-only follow-up: PR300 build 4249788 (Eiger OpenMP Debug, build-492bd6c0)
has one failure: TestBeamBeamFieldServices times out at 30.20 s. Its overlap
case passes in 269 ms, then GaussianFieldsAndPassiveWitnessGather starts and
does not finish before CTest's 30 s limit. Command/environment confirm one MPI
rank and OMP_NUM_THREADS=1. No assertion failure or crash is logged. The separate
MPI2 registration passes in 24.97 s. Runtime-budget pressure is plausible, not
proven; a longer diagnostic run/profiling is needed to distinguish slow execution
from a stall before changing the short-test design. Keep the user's 20–30 s
regression budget and do not loosen numerical tolerances without evidence.
CPU failure: https://my.cdash.org/tests/519010178

CPU Release jobs 4249789/4249782 each have 116 passed, zero failed, two disabled.
GH200 jobs 4249945/4249948/4249946 also each have 116 passed, zero failed, two
disabled. MI300 jobs 4249805/4249806/4249815 each have 115 passed, one failed,
two disabled. Latest MI300 Debug MPI2 still reports rank-zero Bus error during
the Gaussian case (11.65 s), https://my.cdash.org/tests/519025735. This differs
from the CPU timeout; do not claim the CPU shows the same memory fault.
Dashboard job-name rank suffixes do not override the explicit MPI2 registration.
No source changes or new tests executed during this inspection.

## CDash warning cleanup — 2026-10-06

User requested only the additional warning cleanups. Removed both obsolete
`OPALX_ENABLE_TESTS` entries from CMakePresets.json and added `override` to
ParallelTracker::visitBeamBeam, matching the existing base signature and adjacent
visitors. No API, physics, MPI/GPU execution or tolerance change. The MI300 MPI2
runtime crash remains unresolved and is outside this cleanup. Validation passes:
`cmake --list-presets`, local CMake reconfiguration, `git diff --check`, and a
Clang syntax-only compile of ParallelTracker.cpp using its existing build flags
plus `-Werror=inconsistent-missing-override`. No full rebuild, runtime tests or
remote HIP build performed for these non-behavioral edits. Committed on user
request as `492bd6c08` and pushed to `origin/271-implement-interation-point-element`,
including the preceding cleanup commit `0ce36c622`. Tracked working tree is clean;
untracked experiments and notes remain local.

## CDash PR300 MI300 failure inspection — 2026-10-06

Read-only diagnosis of https://my.cdash.org/builds/4235183 (build-95138109):
configuration/build succeed, but field-services MPI2 and MPI4 crash during
GaussianFieldsAndPassiveWitnessGather after the overlap case passes on all ranks.
Rank zero reports Bus error/core dumped; Slurm terminates peers (exit 143).
No assertion failure, stack trace or precise crashing operation is reported.

Latest linked build https://my.cdash.org/builds/4235386 uses build-0047fa17:
both explicit MPI4 tests now correctly Disabled; MPI2 still crashes identically
(11.16 s), https://my.cdash.org/tests/516291439. Single-rank field-services,
FFT2D5Algorithm/Numerics and all three self-field-clear diagnostics pass. This is
AMD MI300/ROCm 6.3.3, Kokkos 5.2.2/HIP, not the earlier Merlin CUDA launch failure.
Do not infer that the removed deep-copy workaround caused it. Need isolated
Gaussian-case reproduction and backtrace on MI300 to distinguish solver,
particle migration, gather and MPI/GPU-memory handling; current logs cannot.

Other reported issues: 20 build warning entries repeat the missing override on
ParallelTracker::visitBeamBeam and associated base-method notes. One configure
warning is the CI preset still supplying removed OPALX_ENABLE_TESTS=ON.
No source/test/CI changes, commits or pushes during this inspection.

## Record outstanding deletions — 2026-10-05

On user request, committed the 101 already-deleted tracked sandbox/test files as
`0ce36c622` (Record sandbox cleanup and remove obsolete test scaffold). No further
files were removed from disk. Only deletions were staged; the untracked experiment
directories and other untracked files remain local and untouched. Deletions are
recoverable from Git history. Verified no pending tracked changes/deletions remain;
the staged whitespace check passed. No simulation rerun for this bookkeeping-only
change. Not pushed.

## Disable four-rank unit tests — 2026-10-05

User requested disabling all four-rank unit tests. Set CTest `DISABLED TRUE` on
`TestBeamBeamTimedBirthsMPI4` and `TestBeamBeamFieldServicesMPI4`, the only explicit
four-rank registrations. Keep their source and registrations for later reuse;
single-rank tests and `TestBeamBeamFieldServicesMPI2` remain enabled. No physics
or numerical changes. CMake reconfiguration and `git diff --check` pass. CTest
discovery confirms both MPI4 cases disabled and single-/two-rank cases enabled;
`ctest --test-dir build_openmp --output-on-failure -R 'MPI4$'` skips both without
launching MPI. Generated test commands confirm these are the only four-rank
registrations in this build (`OPALX_DEFAULT_TEST_PROCS=1`). Committed on user
request as `0047fa17a` (Disable four-rank BeamBeam unit tests); only the two CMake
files are included. Other pending changes remain untouched. Pushed on user
request to `origin/271-implement-interation-point-element` at `0047fa17a`.

## Remove unused integration-test scaffold — 2026-10-05

User requested removal of the top-level `test/` directory, which no longer
registered tests. Removed its two CMake files, the top-level subdirectory entry,
the now-unused `OPALX_ENABLE_TESTS` option and its README row. Gtest coverage in
`unit_tests/` and external `regression-tests-x` are unchanged. Historical test
reports are retained as history. No physics, numerical or MPI behavior changes.
Validation: `cmake -S . -B build_openmp` passes; `ctest --test-dir build_openmp -N`
discovers 118 tests. No remaining scaffold references in active CMake, README or
CI files; `git diff --check` passes. No executable rebuild or test execution was
needed for this configuration-only removal. No commit/push.

## Decision: remove self-field clear workaround for now — 2026-10-05

User decided to remove the `Kokkos::deep_copy` workaround. Source inspection
confirms `src/SpaceCharge/SpaceChargeFrames.h::clearSelfFields` is back to the
original E/B vector assignments. Removal was user-managed; this follow-up only
updates the handoff, with no commit or push. This decision supersedes the earlier
recommendation below to retain the workaround.

- The isolated original-assignment, fenced-assignment and deep-copy cases all
  passed locally and on Merlin6 A100 (job 354325, four CPUs, CUDA 12.9.1).
  They did not reproduce the earlier full-binary host-null-call failure.
- Root cause remains unresolved: NVCC multi-translation-unit lambda linkage is
  a hypothesis, not a demonstrated IPPL assignment defect or host-memory capture.
  Original evidence: `tmp/beambeam-cross-architecture-20261002/diagnose-354310.log`.
- Earlier full CPU/A100 suites, scientific comparisons and the latest A100
  FFT2D5Numerics control used the workaround. They do not validate the full
  executable after its removal. Next validation: rebuild and rerun the affected
  full FFT2D5 tests on A100 plus CPU/MPI checks, using at most four CPUs.
  If the crash recurs, preserve the binary, toolchain and logs for a controlled
  assignment/deep-copy/fenced-assignment comparison in that exact link layout.
- Diagnostic caveat: `SelfFieldClearTest.DeepCopy` currently calls production
  `clearSelfFields`, rather than an independent deep-copy implementation. After
  removal it therefore tests assignment too. Before using this as an A/B test
  again, preserve an explicit deep-copy reference helper or rename/restructure
  the case; do not interpret its current name as evidence of distinct paths.

## Isolated self-field clear tests — complete, 2026-10-05

User requested isolated tests and execution on Merlin6/gwendolen. Adding a
three-process gtest/CTest diagnostic: original IPPL assignment, assignment with
matching fences, and current deep_copy. Two compilation units; counts 0/3/257;
verify live-only writes, spare-capacity sentinel preservation, R/P unchanged and
no reallocation. No production/dependency source modifications. Built and ran
locally and in the existing remote validation checkout on one A100. No commit
or push performed.

Local three-process CTest passes (1.03 s), including all 0/3/257-particle cases.
Used TestSelfFieldClear/fast after stopping only this task's initial dependency
rebuild; diagnostic TUs link the existing validated libraries. Remote helper
files SHA256 match; remote SpaceChargeFrames is identical to local. Original
remote CMakeLists saved under self-field-clear-20261005/CMakeLists.before.txt;
only new diagnostic registrations added, no production/dependency edits.
First Slurm submission with ntasks-per-core=2 rejected before allocating; retry
uses one task/four CPUs/one GPU and rejects any actual allocation above four CPUs.

Merlin job354325 COMPLETED exit0, elapsed1:52, actual AllocCPUS=4, node merlin-g-100,
gmerlin6/gwendolen. CUDA12.9.1, GCC14.3.0, OpenMPI5.0.10. All three isolated cases
PASS (8.72s total including MPI/CUDA startup); unchanged existing FFT2D5Numerics
control PASS (8.48s). Original assignment also passes: this is now a functional
comparison test, NOT a reproducer of the earlier host-null-call failure.
The multi-TU/link-layout explanation remains plausible but unproven. These tests
alone do not justify removing the previously validated OPALX workaround.
Next diagnostic if requested: controlled A/B in the formerly failing full
FFT2D5 executable/link configuration, preserving both binaries and toolchains.

Run locally: `ctest --test-dir build_openmp -V -R '^TestSelfFieldClear' -j1`.
Each CTest launches exactly one gtest filter in a fresh process; alternatively
use `--gtest_filter=SelfFieldClearTest.OriginalAssignment`, `.FencedAssignment`,
or `.DeepCopy` with the TestSelfFieldClear executable. No HDF5/Python analysis.
New files: unit_tests/SpaceCharge/TestSelfFieldClear.cpp, SelfFieldClearTestOps.h,
SelfFieldClearTestOps.cpp; added registrations in the already-dirty CMakeLists.txt.
Evidence locally: tmp/self-field-clear-20261005/{local-ctest.log,job-354325.log,
tests-354325.log,build-354325.log,fft2d5-control-354325.log,run_a100.sh}.
Remote: /psi/home/adelmann/opalx-dev/opalx-beambeam-validation-20261002/
self-field-clear-20261005/; executable in build_a100/unit_tests/SpaceCharge/.

## SpaceChargeFrames/IPPL reassessment — 2026-10-05

- Review only; no OPALX/IPPL production or test source changed, committed, or pushed.
- Audited `/Users/adelmann/git/ippl` at `edb8794cd` (local
  FFTDirichletPeriodicPoissonSolver branch) and OPALX's fetched IPPL at `a7e505730`.
  Relevant constant-assignment and live-view semantics agree in both versions.
- `ParticleAttrib::operator=(T)` captures a view and value by value, not a host
  object/reference. `localNum_mp` is read on the host to form the range. The
  direct vector overload is confirmed by the retained Merlin backtrace.
- `getView()` spans only live particles, whereas `size()` reports capacity.
  The proposed deep_copy therefore clears the same particle range without a
  host field array, new allocation, or physics/tolerance change.
- Reclassify the proposal as a validated OPALX workaround for a host-side CUDA
  launch failure, not proof of an invalid IPPL memory capture. The null call in
  diagnose-354310.log resembles the already documented NVCC multi-TU lambda
  issue; an assignment-specific multi-TU reproducer is still required to prove
  that root cause. Existing IPPL HaloCells named functors provide a precedent.
- Two-argument Kokkos deep_copy adds global pre/post fences (four for two
  non-null fills), unlike the asynchronous attribute assignments. It also
  bypasses the NVCC extended lambda via Kokkos's named ViewFill functor. Those
  two effects have not been experimentally isolated in the original failure.
- Recommendation: retain the tested OPALX workaround for the release unless a
  replacement passes the affected A100 binary; prefer a separately validated
  named-functor IPPL assignment implementation for the general long-term fix,
  preserving asynchronous semantics. Do not claim all GPUs/master must fail.
- Test follow-up: keep nonzero-to-zero/R-P preservation and MainApi coverage;
  add empty-live-range/overallocated-storage and multi-TU CUDA assignment tests
  if implementing the dependency-level fix. No new CUDA run in this review.
- Fresh existing-build checks: FFT2D5Algorithm, FFT2D5Numerics and field-services
  at 1/2/4 ranks all pass (5 CTests, 2.84 s, OMP_NUM_THREADS=1). Initial sandboxed
  MPI launch failed before execution; unsandboxed rerun passed without code edits.

## V1 merge-readiness reassessment — 2026-10-04

Read-only assessment requested, assuming updated manuals and accepting frozen-field
approximation. Fresh GitHub API: PR300 open, non-draft, mergeable/unstable; head
9822ef85e, base ce813d3cd, no labels; all7 head checks skipped (compile-ci absent).
Local HEAD98e3426d9 additionally contains cleanup; migration and short tests remain
uncommitted. SpaceChargeFrames.h CUDA clearSelfFields fix and FFT2D5 regression
still uncommitted; prior CPU/A100 passing evidence includes that dirty fix.
External regression-tests-x four BeamBeam cases, README and makeReference.sh edits
also unpublished locally. Publish those fixtures before enabling the OPALX matrix.
Remaining release steps: form exact tested candidate, publish short regressions,
add fast full interaction lifecycle/copy-boundary coverage, run enabled CI and
CPU/CUDA/MPI gates on final SHA, finalize scoped validation claims/review.
Single-pass/multiple-interaction guard is already published; no model redesign or
full-production convergence campaign required for a restricted initial release.
Rechecked source guard, lifecycle/helper tests, four short decks, and retained
full-suite/comparison logs. Fresh7 focused CTests PASS2.87s includingMPI2/4 with
existing local PRTE slot:OVERSUBSCRIBE/bind-none settings, <=4ranks,1thread/rank.
First launch without those settings failed before test execution with MPI slot
allocation errors, not numerical assertions. Full CPU/CUDA suite not rerun today.
CAIN agreement remains qualified: standard x/s relativeL2 9.48%/2.97%; weak y and
individual relative errors can be large. Like-for-like analytic0.854%/0.117% and
CPU/A100 reproducibility are distinct evidence. No code/CI/remote mutations,
commits or pushes in this assessment; only this task-state entry updated.

## Note layout update — 2026-10-04

Updated sandbox/note/bb-note.tex reproduction appendix for experiment-1 through4.
Added experiment map, current local launchers, inputs/scripts/results conventions,
legacy-data/deletion caveat and explicit historical-versus-current profile warning.
Rebased all obsolete study commands; Track12 remote preparation now writes directly
to RUN_ROOT/production instead of assuming generated files alongside scripts.
Documented unimplemented --merlin6 and historical remote checkout; example builds
and MPI thread counts respect four CPUs. Scientific body/numerical results unchanged.
Validation: all5 figures and17 referenced script/input paths exist;11 command blocks
pass bash -n; no obsolete workspace paths remain. LaTeX draft-mode compilation
passes without generating/replacing the existing PDF; temporary logs in
/tmp/opalx-note-tex-check.7ouSaY. No simulations, remote submissions or commit/push.

## Raw-output disk cleanup — 2026-10-03

User explicitly chose deletion rather than compression: outputs can be rerun.
Removed34 H5 files listed in tmp/sandbox-cleanup-20261003/deleted-raw-output-files.txt:
12 experiment2 timing_pairs/timing_pairs_100 primary c0 snapshots;20 experiment4
track-e-p/data field/density/potential dumps;2 shared-data field-debug conversions.
No new archive; reruns needed to regenerate deleted diagnostics. All witness
trajectories, plots, tables, inputs, scripts and recent local runs left untouched.
Measured allocated usage (du -sk): experiment2 1263820 ->926140 KiB;
experiment4 1552088 ->312592 KiB. Reclaimed1577176 KiB (1.50 GiB).
Updated Experiments.md to distinguish original preservation from this cleanup.
No source/model changes, simulations, commit or push.

## Shared script cleanup — 2026-10-03

User approved the audited cleanup: keep the two shared launchers and optional
spherical-model dependency; move three cylinder/field-dump diagnostics into
experiment-4/scripts; archive the six legacy GUI/debug/movie scripts.
Archive: tmp/sandbox-cleanup-20261003/shared-legacy-scripts.tar.gz; SHA-256
4ce5f674fd202342dcf87d005a091daf669d598a2ce285278a0cbd67fe8793fd.
All six entries compared byte-for-byte with working copies before deletion.
Moved diagnostics change only repository-root depth (parents[2] -> parents[3]);
input/output defaults and numerical behavior stay unchanged. Updated Experiments.md
and marked PYTHON_SCRIPTS.md as historical to avoid stale active-tool instructions.
No OPALX-IMPACT, regression, physics, or unrelated worktree changes; no commit/push.
Validation passed: all three relocated diagnostic CLIs and four launcher --help
checks; correct repository roots and existing default input directories; optional
spherical-model import; AST parsing of all31 active Python scripts;18 scientific
helper tests (7 experiment1 +11 experiment2); git diff --check. Shared directory
contains exactly the three retained files. No simulations needed for path-only
relocation. Next step: await user review/commit authorization.

Latest documentation follow-up: deleted sandbox/requirements-h6.txt as requested.
Merged the two remaining Markdown files in sandbox/results into the top-level
sandbox/BEAMBEAM_PHYSICS_AND_VALIDATION.md. Preserved historical physics/numerical
content; consolidated useful README environment/archive/provenance material,
replaced obsolete workspace commands with links to Experiments.md and current
helper paths, and noted restored OPALX-IMPACT/current remote-interface status.
Updated Experiments.md and ignore rules. No simulation/source changes or commit.

Latest layout follow-up: moved sandbox/results/note back to sandbox/note as
explicitly requested. Preserved all three files (.tex/.pdf/.aux), rebased the
five LaTeX figure paths, updated Experiments.md and ignore rules. No commit.

## Numbered experiments — implementation/validation, 2026-10-03

User requests restoring OPALX-IMPACT unchanged; organizing non-regression studies
as experiment-1 etc with Experiments.md; run.sh locally runs/analyzes, Python in
scripts/, generated plots/reports in results/. Merlin6 A100 dispatch can wait.
No commit/push authorized. Four CPUs maximum. No physics kernel changes.
Plan:1 analytic/PIC fields (old reduced-order-model);2 exact-timed Track12;
3 full-population exact-timed CAIN;4 current32cm production/lifecycle plus old
track-e-p decks preserved as historical variants. OPALX-IMPACT remains separate
at its original path, untouched. Short gtest/external regression architecture
unchanged. Older Python scientific checks stay with their corresponding scripts.
Migration tool and SHA-256 move manifest under tmp/sandbox-cleanup-20261003/;
original output bytes preserved in each experiment's results/legacy tree.
Restored23 OPALX-IMPACT files verified against both cleanup manifests, unchanged.
Moved2135 experiment files with hashes checked; old paths mapped in
tmp/sandbox-cleanup-20261003/experiment-moves.json. Rebased42 live scripts and
note figure paths. Source/inputs under numbered scripts/inputs; original outputs
in results/legacy unchanged. Shared utilities in sandbox/scripts; note and physics
report in sandbox/results. Index: sandbox/Experiments.md. .gitignore now exposes
experiment source/config/reference files while ignoring generated results; new
paths are untracked until explicitly staged, not yet a committed migration.

New run.sh wrappers use sandbox/scripts/run_experiment.py: unique results runs,
logs/plots/REPORT.md, input/source/executable hashes, exit-code propagation,
overwrite rejection, max4 CPU threads; --prepare-only and --analyze-only.
--merlin6 rejects safely with status2; no remote job or SSH. Old wrapper entry
points forward to run.sh and no longer invoke C++ regression tests.

Actual runs so far:
- Experiment1 smoke and default20k/32x32x64: all4 separations simulated/analyzed.
  Default evidence results/local-20261003-145221-_6b5ez25.
- Experiment2 smoke and full1501-step local2k/16x16x32: complete13,012 CAIN samples
  compared and plotted, results/local-20261003-144939-gk78rfhp. Coarse local profile
  is not physics acceptance. The empty c0 H5 is intentional dump suppression;
  generic diagnostics now require a nonempty particle container but allow empty c0.
- Experiment3 original deck bus-error on first witness gather. Set existing
  ORBITTHREADER=FALSE on both witnesses, matching Track12 and production; original
  input preserved at results/legacy/opalx/gamma_gamma_pairs_timed.original.in.
  No kernel, field/source parameters, birth timing, or timestep changes. Full
  10k primary +1297+1297 run passed with1,2,4 threads and exact birth counts.
  Four-thread evidence results/local-20261003-145203-jmqk_pwq.
- Experiment4 default primary lifecycle smoke completed1607steps/32particles;
  generic diagnostic now handles single-container unsuffixed H5, requires
  Inactive->Active->Completed and expected final step/count. Input distributions
  plotted separately; default smoke does NOT track witnesses. Full staged
  production is available via --full, but not yet executed in this task.
- Scientific helper tests7+11 PASS. Safe --merlin6 rejection checked all4 wrappers;
  existing-output overwrite rejection checked. Shell syntax/diff whitespace PASS.
Completed default4thread lifecycle rerun, results/local-20261003-145251-5jbi7f9y;
asserted Inactive->Active->Completed,1607steps,32 primary particles. Full production
--full --prepare-only completed at results/local-20261003-145421-z4diiy2c, both
FNAME input paths verified, no long full-production simulation. Final CTests6/6
PASS in2.66s includingMPI2/4.37 Python sources AST-parse; shell syntax and git
diff --check pass. All5 note figures resolve. Legacy2056-file hashes and restored
23 OPALX-IMPACT hashes pass. All4 experiment directories have precisely
inputs/,scripts/,results/,run.sh. No active tool sessions or remote jobs remain.
No staging/commit/push. Existing unrelated source/test changes remain untouched.
Next user choice: review/commit migration together with the previously pending
short-test registration, or implement/test future Merlin6 submission separately.

## Ignored-output cleanup — 2026-10-03

User now authorizes inspecting ignored/untracked sandbox outputs, retaining those
related to remaining experiments and deleting unrelated/retired material.
Read current filesystem and surviving script/note references; no nested AGENTS.
Keep ALL active track12, track-e-p, track-e-p-new, reduced-order-model and
cain-opalx-reduced-order-model outputs, CAIN reference, note and figure assets,
shared gamma_gamma and boosted_gaussian data. Also keep timing_pairs and
timing_pairs_100: retained plot_older_timing_histogram.py still reads the former.
Retired attic fits/scans have no incoming dependency from current timed/analytic
drivers or the note; their source was already archived/removed in the prior step.

Selection:458 ignored files,2,180,023,225 bytes, comprising355 attic leftovers,
14 OPALX-IMPACT leftovers,84 deleted BeamBeam-1/2 field/geometry dumps,2 obsolete
broad-regression metrics,2 editor undo files for deleted decks and1 empty frame
list. No tracked files selected. Retain2140 existing files (3,535,479,760 bytes).
Full per-file content hashes/reasons saved to
tmp/sandbox-cleanup-20261003/ignored-manifest.json. Supplemental archive created:
tmp/sandbox-cleanup-20261003/obsolete-ignored-outputs.tar.gz. Extracted and
SHA-256 verified all458 entries against original content before deleting exact
selected paths. ALL2140 retained files hash-verified unchanged after deletion.
Removed only empty retired directory trees (attic, OPALX-IMPACT, compare-e-fields,
duplicate-slide directory and empty root bytecode directory). Kept regression/
figures as an output destination used by retained tools. Updated sandbox index.
No source changes, no staging, commit, push, or remote action. Final validation:
15/15 retained workflow checks PASS in1.318s;6/6 focused CTests PASS in2.77s
including2/4-rank field and4-rank birth tests. git diff --check PASS. Sandbox
reduced from5.3GiB to3.3GiB; supplemental archive is about1.3GiB outside sandbox.
Tracked Git changes unchanged except the intentional sandbox README update.

## Sandbox cleanup executed — 2026-10-03

Later follow-up: user authorized removing remaining root BeamBeam examples.
Archived and SHA-256 verified BeamBeam-1.in, BeamBeam-2.in, beambeam-1.h5,
BeamBeam-2.h5 and BeamBeam-static-1V.h5, then deleted those five files only.
Recovery archive: tmp/sandbox-cleanup-20261003/root-beambeam-examples.tar.gz
(about32 MiB). The two tracked input deletions are unstaged/uncommitted; three
H5 files were ignored. Legacy beambeam_analysis.py still contains historical
BeamBeam-2 GUI defaults; active tests/studies do not depend on these five files.

Follow-up: user authorized staging all deletions and committing. Created local
commit98e3426d9, "Remove archived sandbox studies and generated clutter";
exactly705 deletions, no other changes. Documentation/source/test modifications
remain unstaged; archive remains local. Nothing pushed.

User authorized deleting category-4 generated clutter, archiving other category-4
items and deleting them. Applied to tracked files from the reviewed inventory;
ignored/untracked run data remain untouched, so historical directories can still
contain local outputs. No commit, staging, push or remote change.

- Archive: tmp/sandbox-cleanup-20261003/sandbox-category4.tar.gz (about82 MiB).
  Includes ALL705 removed files:70 generated-clutter files and635 other category-4
  files, including all196 preexisting local modifications. Original tracked
  inventory, Git status, per-file SHA-256, protected reference/figure hashes and
  exact removal list are in manifest.json and archive-files.txt beside the tar.
  archive-sha256.txt records the compressed archive hash. Keep these local files;
  they are NOT published or backed up remotely by this action.
- Extracted the archive to a temporary verification directory and checked every
  archived file against its working-tree hash before removal. First deletion pass
  stopped on a symlink whose target had just been removed; resumed safely using
  lstat/readlink validation against the verified archive. All705 targets removed.
  All102 retained tracked sandbox files plus CAIN reference and five note figures
  were hash-identical immediately after removal, before documentation updates.
- Removed tracked attic, compare-e-fields, OPALX-IMPACT, broad regression wrapper,
  historical timing_pairs and old root-level Track12 scripts/decks/input copies,
  obsolete root outputs/plots, static-1V deck, old gamma_gamma_pairs-2/-3 decks,
  bytecode, LaTeX auxiliary output, and duplicate slide renders. Kept shared
  analysis helpers still used by retained tools and all timed workflow sources.
- Updated sandbox index, physics-note archive pointer, Track12 and analytic
  README pointers and legacy input inventory to describe the archive/removal.
- Six focused CTests initially failed before execution due to local OpenMPI slot
  detection. Reran with documented PRTE oversubscribe/unbind settings, OMP1 and
  ctest -j1 (at most4 ranks):6/6 PASS, including MPI2/MPI4 field and4-rank births.
  Retained manual analytic/input/timed workflow checks:15/15 PASS in1.432s.
  git diff --check PASS; reviewed five documentation diffs and removal manifest.
  Final audit:705 selected targets absent, all196 preexisting sandbox edits in
  archive. No physics/source-code changes made by this cleanup.

## Sandbox cleanup inventory — 2026-10-03

Current request: classify needed content first (tests, e+/e-, analytic example,
removable). Audit only; no sandbox deletion, relocation, commit, or push.
Inspected tracked inventory, active READMEs, CMake, script dependencies, input
paths, and LaTeX figure references. No simulations required for this inventory.

- 807 tracked sandbox files; 568 under attic. On-disk sandbox is approximately
  5.5 GB including ignored/untracked outputs, not the size of the tracked diff.
  All 196 existing tracked sandbox modifications are under attic/models; preserve.
- Working-tree unit_tests/test/.github contain no sandbox path dependency after
  the UNCOMMITTED short-regression replacement. Committed HEAD still registers
  run_manufactured_regression.py, scan_first_kick_fields.py, and
  run_witness_gather_mpi_regression.py; preserve their dependency closure until
  replacement tests are committed. Four new external regression cases have no
  sandbox paths. Existing manual Python study checks are not the short CI suite.
- Keep e+/e- sources: track12particles/track12particles.py and opalx/timed source
  scripts/templates/configs/launchers; TestParticleOrbit.dat; track-e-p/fort98.txt,
  witness inputs and converters; cain-opalx-reduced-order-model source pipeline;
  track-e-p-new source decks and diagnostics. Legacy production-deck variants need
  explicit pruning separately, not blanket removal of track-e-p.
- TestParticleOrbit.dat is essential but ignored by root .gitignore line49.
  Preserve it locally; do not treat ignored/untracked reference data as junk.
- Analytic example interpreted from active index as reduced-order-model:
  preserve parameters, convergence matrix, source scripts, template and launcher.
  It also loads track12particles.py for cross-checks. Retain
  python/boosted_gaussian_witness.py while track12's optional legacy path uses it;
  it is NOT the authoritative anisotropic model.
- Keep BEAMBEAM_PHYSICS_AND_VALIDATION.md, operational READMEs, requirements-h6.txt,
  note/bb-note.tex and its referenced figures, and the original reference PPTX.
  Note figures live in track-e-p/data, reduced-order-model/outputs, and historical
  timed A100 run directories; preserve those exact assets before pruning outputs.
- Removal candidates: tracked bytecode/cache and LaTeX auxiliary files; duplicate
  slide renders; obsolete root BeamBeam outputs/plots; compare-e-fields generated
  figures; historical timing_pairs{,_100} and obsolete root track12 decks; attic
  only AFTER an archive retaining dirty local work and scientific provenance.
  Keep selected accepted CPU/A100 baseline inputs/hashes/metrics/logs/timings.
- OPALX-IMPACT plus regression/ and run_sandbox_regressions.py belong to an older
  broad manual workflow, not new gtest/regression-tests-x coverage. Archive as a
  coherent optional study, not partially delete its input dependencies.
- sandbox/Drift-Experiment is absent in this checkout. Latest CPU/A100 evidence
  exists outside sandbox at tmp/beambeam-cross-architecture-20261002; leave it.
- Next: user reviews the classification before any cleanup. Update stale sandbox
  test instructions when the replacement registration is committed; decide an
  archive destination before removing historical scientific material.

## Implementation requested — single-interaction guard and text-only regressions

User authorizes a separate commit for the single-interaction scope guard; leave
the two CUDA/self-field files uncommitted. Also agrees to short regressions,
but NO new Python scripts and NO HDF5: use gtest or existing .in/.local/.rt/.stat
regression architecture. No push authorized. Four CPUs maximum.

In progress: manager rejects a second stateful interaction atomically; tracker
rejects RING/TURNS with an interaction. Tests cover ordinary lattices, rejection,
same-name occurrences, recovery, and tracker setup. Initial tracker test hung
because the fixture had no input file and existing save3DInput parsing loops on
an unopened stream; stopped only its MPI launcher (37003), added the fixture
input. No unrelated parser changes. Next: rerun 1/2/4-rank guard tests and commit
only its four files; implement text-only/gtest regressions separately.

NightlyBuildX stat runner currently has absolute tolerances and no container-file
selector, whereas OPALX embedded smoke comparator uses relative tolerances.
Use existing .local launchers to select a witness .stat under the canonical case
name, without editing numerical output; CI must honor those launchers. Resolve
the tolerance convention explicitly, don't silently reinterpret existing cases.

### Implementation progress / verification

- Guard committed locally as 9822ef85e (four files only). No push or Merlin commit.
  Full21-case TestBeamBeam passed; five scope tests also passed on2/4 MPI ranks.
  Source numerical kernels and the frozen-field approximation are unchanged.
- Separate UNCOMMITTED regression work: new deterministic Gaussian analytic E/B
  plus passive-charge/gather gtest (32768 primary quadrature points,48^3 mesh,
  3% discretization tolerance), new12-identity timed-birth gtest with exact
  boundary and fractional steps; registered2/4-rank field and4-rank birth CTests.
  BeamBeam field and emission tests have30s timeouts and one thread/rank.
- Removed automatic registration of the old3 sandbox Python/HDF5 integrations.
  Historical study files remain untouched. No new Python script or HDF5 fixture.
- External fixtures in /Users/adelmann/git/regression-tests-x are UNCOMMITTED:
  BeamBeam-OffsetKick, BeamBeam-TimedBirths, BeamBeam-WitnessMPI, BeamBeam-RigidSource.
  Each512-source case has its own .in/.local/.rt/text inputs and canonical
  .stat reference selected verbatim from c1,c2,c1,c0 respectively. Steps4/8/4/4,
  ranks1/1/4/1. Reference data generated with existing makeReference.sh, one rank.
  Same four-rank witness baseline checked against the one-rank reference.
  README records provenance, units, tolerances, reference regeneration and scope.
  Existing makeReference.sh changed only to omit nonexistent unsuffixed .stat
  from its copy list for multi-container runs (avoids spurious copy/checksum errors).
- OPALX cpu-serial workflow has new matrix entries and uses these existing .local
  launchers with30s timeout. Existing embedded comparator understands the
  [tolerance: absolute] description marker, uses NightlyBuildX avg semantics,
  rejects nonfinite checked values, empty assertions/output and incomplete
  trajectories. Other cases retain their previous relative comparison semantics.
- Initial fixture wrongly reused one emitted distribution for both species and
  produced inconsistent timed trajectories. Separate DWE/DWX distribution
  instances made repeat and verbose-reference runs agree; no production-code fix
  or tolerance relaxation was made. Shared-distribution behavior is not diagnosed
  exhaustively; keep this as a remaining configuration risk, not a physics claim.
- NightlyBuildX5539fa31b56d4952d923e6641557d6683c68725a:49/49 assertions PASS.
  Same49 assertions PASS using the exact existing inline CI comparator.
  Negative controls: WITNESS_CONTAINERS=NONE fails4 kick checks; BBRIGID=FALSE
  fails7 primary checks. Combined negative-control summary13/24, as expected.
- Seven focused CTests passed in2.91s (prior run3.64s), including MPI.
  Reference-generation wall times0.98–2.03s percase, single-rank Release/OpenMP.
  Reference executable SHA256e16d324edf1f6f7870005457d034cec19558215832517c8b6c37e1d3d54633d0;
  includes preexisting uncommitted CUDA clearSelfFields fix, explicitly documented.
  No new CUDA validation or Serial Debug timing yet. Final build86497 completed
  successfully after CMake caused dependency recompilation; no dependency source edits.
  Final executable hash unchanged. Post-build focused CTests7/7 PASS in3.90s;
  existing NightlyBuildX runner repeated49/49 PASS against that executable.
- Evidence: /tmp/opalx-short-regressions.O6skfg and durable copies under
  tmp/beambeam-short-regressions-20261002/{nightly-49-checks,negative-controls,gtest}.log.
  Source formatting, shell syntax, YAML syntax and reference MD5 checks pass.
  Finished local validation; only guard committed. Regression/CI changes await
  separate commit. No push, upstream merge, CI-label change or remote commit.
  External regression cases must be published before enabling the new CI matrix.

## Merge-readiness audit requested — current task

Audit only: assess the beam-beam branch for master, review unit tests, and
recommend regression-tests-x coverage fitting20–30s. Frozen-field approximation
is intentional and remains in scope; replacing it is NOT a merge prerequisite.
No implementation edits, merge, commit, or push authorized by this audit request.
Inspect current source/test/manual/CI contents and current upstream heads;
distinguish validated dirty working-tree state from committed merge candidate.
Four-CPU limit persists. Preserve196 unrelated sandbox changes and two uncommitted
FFT2D5/self-field files.

### Audit findings — 2026-10-02

- Fresh remote master remains ce813d3cd, already merged. Local and PR300 head
  are e7e16a899 (binning-test ownership fix). PR open, mergeable, unstable;
  labels empty and all returned head check runs skipped. Workflows require
  compile-ci. No label, remote branch, commit or push changed by this audit.
- Passing CUDA evidence is for the working tree including the still-uncommitted
  SpaceChargeFrames.h and TestFFT2D5Numerics.cpp changes, not the published head
  alone. Decide whether to include this independently reviewed fix before
  claiming the merge candidate passes CUDA. Do not silently commit it.
- Static control-flow finding: ElementInteractionManager stops at first handled
  SelfField; a discovered BeamBeam owns policy even while inactive. Any Completed
  interaction causes ParallelTracker::computeSpaceChargeFields to return before
  dispatch. Thus multiple BeamBeam elements/repeated passages are not safely
  supported. Fast scoped recommendation: enforce/document one single-pass
  interaction and add a rejection test, rather than broaden the model now.
  No multi-element reproducer was run during this audit.
- Scope vs origin/master: 883 files, +105285/-134; 807 sandbox files (+98818),
  including generated CSV/stat/log/figure studies. Keep studies separately from
  production PR where practical. First relocate the minimal regression drivers,
  templates, generators and oracle dependencies because test/BeamBeam/CMakeLists
  currently executes sandbox code. Do not delete sandbox blindly.
- Published opalx-manual/main/physics/beam-beam/index.qmd still demonstrates
  COPY=TRUE; current parser exposes COPY_TIME (0 disables), BBRIGID and
  WITNESS_CONTAINERS. Update supported frozen/rigid model contract, fixed20mm
  longitudinal window, source-only deposition, passive witnesses, field-copy
  activation, outside-window policy and single-pass restrictions. BBRIGID
  suppresses the source collective kick, not ordinary motion/external fields.
  The user-specified local manual directories do not exist on this host.
- Regression repo fresh master 1b9212466f1a9fb013c987e2fcec484784ff9fa5 inspected
  in /tmp/opalx-regression-audit-20261002; user's local regression checkout left
  unchanged. makeReference.sh collects *_c*.stat, but OPALX cpu-serial workflow
  comparison is hard-coded to <test>.stat and its matrix is explicit. Extend
  runner to select witness files and validate finite/nonempty outputs and at
  least one assertion; add matrix entries. Merely adding directories is not enough.
- Keep existing unit coverage: 17 BeamBeam helper/domain/dispatcher tests,
  field-service copy/charge/B-sign checks and 4-rank non-slab mirror test,
  7 EmittedFromFile tests. Missing targeted runtime coverage: actual entry/exit,
  copy activation at boundary, source kick suppressed with witness kick nonzero,
  source-only deposition, parser errors and unsupported multiple interactions.
  The 4-rank mirror case GTEST_SKIP's under default one-rank CTest; register a
  dedicated four-rank filtered invocation (one thread/rank), not the whole suite.
- Recommended short regression set: manufactured E/B oracle, offset e-/e+
  first-kick, compressed multi-birth short tracking case, deterministic MPI
  gather. Existing first/second/MPI precursors took6.86/4.42/4.71s respectively
  in local final CTest log (~16s total). New birth case runtime is unmeasured;
  target <20s/test, enforce30s, benchmark Serial Debug CI before promising cap.
  Existing TIMEOUT values600/600/300 are not the requested cap. Keep <=4CPUs.
  H5/analytic checks need an explicit checker hook; .rt last/avg alone cannot
  validate particle birth times or field maps. Use per-container .stat for the
  dependency-light smoke tier. Skip optional H5 tests clearly when packages are
  absent; provision dependencies on the designated physics-validation CI runner.
- Preserve existing analytic3%, offset8%/cosine0.999 and MPI5e-4 thresholds
  for unchanged fixtures; justify any new tolerance from discretization and
  architecture variability, never fit to CAIN. Use abs+relative tolerances
  near zero and exact particle counts/step completeness. Full1501-step CAIN
  trajectory remains extended validation, not a20–30s merge gate.
- Audit checks: clang-format21 --dry-run --Werror on all changed src/unit_tests
  C++ files PASS; git diff --check on src/unit_tests/test/CMake files PASS.
  Prior115/115 CPU and112/112 CUDA logs re-read, no full suite rerun this turn.
  Only this task-state file updated. Next: user chooses implementation scope;
  prioritize exact tested commit, single-pass guard, minimal fixtures/runner,
  missing behavior tests, docs, then enabled CI on the final merge candidate.

## Completed validation — 2026-10-02 (supersedes earlier stop/status instructions)

### Final results

Commit update: at the user's explicit request, ONLY the binning test device-view
ownership fix was committed as e7e16a899 (Fix CUDA view ownership in binning tests).
SpaceChargeFrames.h and the FFT2D5 regression remain uncommitted and unchanged.
Index is empty; nothing pushed. Validation artifacts below describe the tested
three-file working-tree state, not the binning-only commit in isolation.

The agreed handover benchmark has now been reproduced on local OpenMP and
Merlin A100. Both builds, complete test suites, dedicated MPI checks, smoke,
and all three full1501-step studies completed. No compute jobs remain active.
This completes cross-architecture reproduction, NOT exact CAIN model matching;
the original CAIN deck remains deferred as requested. Do not describe the
CAIN agreement as uniformly a few percent.

- Merge27dc0ed52 already incorporates origin/master ce813d3cd. No push performed.
- Three new uncommitted CUDA fixes: SpaceChargeFrames.h uses resident-view zero
  fills; TestBinning.cpp owns device-view handles by value; TestFFT2D5Numerics.cpp
  adds zero-field/R/P-preservation regression. No dependency edits, public API
  changes, units/model/tolerance changes. Clearing now synchronizes before return.
  Full diff reviewed, clang-format21 dry-run and scoped git diff --check PASS.
  Patch artifact: tmp/beambeam-cross-architecture-20261002/cuda-regression-fixes.patch.
  Commit/push still requires approval.196 pre-existing sandbox modifications remain.
- Local115/115 CTests PASS, A100112/112 CTests PASS. Three optional Python CTests
  skipped remotely for missing h5py; all three equivalent GPU integrations
  executed and analyzed locally with original criteria, PASS. Nine additional
  1/2/4-rank command groups PASS on EACH architecture; GPU PCI identity distinct.
- All full cases:12 witnesses,13000 measured post-birth records plus8H5 births
  and4input births,13012 CAIN comparison rows, finalstep1500. Completeness checks
  validate identities, exact clocks, finite6D phase space, input hashes and
  reconstructed analyzer metrics. No interpolation or tolerance fitting.
- CPU-small100k64x64x128 runtime1719.49s; identical A100-small79.34s.
  A100-standard400k256x256x128 runtime216.72s.
- CPU/A100 exact-input/source comparison,13000 measured samples: maximum
  absolute x/y/s difference=0.0342513/0.327577/0.00690831nm. Overall relativeL2
  x/y/s=2.64145e-8/1.16598e-5/1.71363e-9; px/py/pz=8.43357e-8/1.80553e-5/5.62899e-9.
  Worst per-witness/component relativeL2=0.000490959 (0.0490959%,electronTe-5 py).
- Standard A100 vs retained eef599761 baseline: maximum position difference
  0.0258307nm; largest overall relativeL2=4.29681e-6 (py), largest per-witness
  relativeL2=2.38131e-5 (positronpair6 py). Historical source PARTICLE hashes
  match; code revisions differ intentionally. Old wrapped deck recorded zero wraps.
- CAIN overall relativeL2 x/s: CPU-small8.20705749%/3.00523168%,
  GPU-small8.20705751%/3.00523173%, GPU-standard9.48283635%/2.96731387%.
  Standard rigid analytic reference x/s errors0.85375362%/0.11730212%.
  Remaining CAIN limits: standard yrelativeL2=96.1769% (14.7642um RMSE),
  positron xrelativeL2=107.904% (5.76577um RMSE). Solver/model differences and
  weak-component ratios are not resolved by this reproduction; original deck
  comparison is deferred. No changes to force CAIN fitting were made.
- Current source819-file SHA256:
  a90ded645880351cc23c56c4e95b19610ebeacac73eb27854d1749d57cbd49ab.
  CPU executable SHA256:b447f17c74e3d06ea7bd5eb6190f03866c48465b5b5b9d5fd8615a226aecb0fd.
  GPU executable SHA256:8dd495e0334be99cbe05ed09abedd42f092feb923456233db035e79acbb1bb91.
- Evidence root: tmp/beambeam-cross-architecture-20261002/.
  architecture-comparison/comparison.json and cpu_a100_comparison.{png,pdf};
  historical-standard-comparison/historical_baseline_comparison.json;
  {cpu-small,gpu-small,gpu-standard}/results/{track12_comparison,completion_validation}.json;
  final-comparisons.log ends ALL_COMPLETION_AND_COMPARISON_CHECKS_FINISHED.
  Plot visually inspected; all labels/curves readable.
- Smoke locations: local tmp/beambeam-cross-architecture-20261002/gpu-smoke/
  (results/smoke_validation.json), remote
  /psi/home/adelmann/opalx-dev/opalx-beambeam-validation-20261002/runs/smoke/.
  Remote source snapshot and both older dirty checkouts preserved.

The chronological execution notes below are superseded by these final results.

### Merlin connection restored (latest turn)

LATEST: job354309 built all CUDA targets, then CTest110/112 PASS (262.35s),
exit8 due to TestBinning and TestFFT2D5Numerics. No MPI/study job submitted.
TestBinning crashes in HistogramGetBinIterationPolicy: two test functors use
decltype(DualView::view_device()), a const reference to a host view handle,
inside device kernels. Changed both to value-type Histo_t::dview_type.
Diagnostic job354310 (1CPU,1GPU) reproduced standalone FFT2D5 MainApi crash:
GDB null call inside Kokkos parallel_for for IPPL ParticleAttrib<Vector>::operator=,
called from FFT2D5Algorithm::solve through clearSelfFields. No GPU reset/error
recovery performed. Changed OPALX SpaceChargeFrames.h clearSelfFields to explicit
Kokkos::deep_copy of active E/B views; same exact zero values, no units/model/
tolerance change; fills synchronize before return (previous assignment launches
were asynchronous). No dependency changes. Added nonzero-to-zero regression
also checking R/P unchanged with independent host snapshots in FFT2D5 tests.
These three files are uncommitted; commit/push needs permission. clang-format21
applied and diff whitespace check passes. Local full rebuild (4workers) PASS;
all115 CTests PASS79.94s, nine1/2/4-rank test groups, eight Python workflow tests,
comparison self-check (including undo exclusion), historical self-check PASS.
Logs: October evidence/build-after-cuda-fixes.log and local-after-cuda-fixes/.
Three patched files synced and SHA256 equality verified. Remote retry354311
COMPLETED exit0: retest_a100.sh,1task4CPUs1GPU32GiB; log retest-354311.log,
rebuild-354311.log,ctest-354311.log. All112 CTests PASS260.27s; both initial
failures fixed without tolerance changes. Preserves original failed-run logs.
MPI job354312 stopped at resource guard before testing: Slurm core allocation
rounded request4CPUs to8. Cluster CR_CORE_MEMORY,CR_ONE_TASK_PER_CORE and enforced
GPU/core binding. Retry354313 uses --ntasks-per-core=2 --gres-flags=disable-binding;
actual AllocCPUS=4 confirmed. All nine1/2/4-rank CUDA groups PASS, including the
formerly failing4-rank field-services path; each run verifies distinct runtime
GPU PCI IDs. Job354313 completed exit0,72s. All five integration executions
and all three LOCAL analysis checks PASS: E/B manufactured relativeL2
0.02416083112834292/0.025045768608445387; offset E ratio0.948799,
direction0.999948; 1/2/4-rank witness field/kick relative differences <=8.30e-16,
charge-symmetry relative px-kick <=9.48e-12. Original thresholds unchanged.
Fetched outputs: October/gpu-integrations, analysis gpu-integration-analysis.log.
Smoke354314 COMPLETED exit0 (5s,actual2CPUs), fetched as October/gpu-smoke.
check_smoke.py PASS: both species, strict3-step schedule, finite coordinates/
momenta, exact clocks/input hashes and source file-map equality to new CPU
fingerprint. Evidence gpu-smoke/results/smoke_validation.json.
All pre-study gates now PASS. run_full_a100.sh submits sequential gpu-small
and gpu-standard1501-step executions,1task1CPU requested(2allocated),1GPU.
Job354315 COMPLETED exit0,4m58s,actual2CPUs. BOTH full cases reached finalstep1500.
GPU-small fetched to October/gpu-small; compare_timed_track12 + strict
validate_completed_run PASS:13000 mandatory measured rows +8H5 births +4input
births,12identities,13012comparison rows. CAIN relativeL2 x0.08207057509134894,
s0.030052317278269833,y0.9472245791920055 (NOT uniformly few-percent).
CPU run now ACTIVE, tool session18564; launcher run_cpu_small.sh,4OpenMP threads,
driver cpu-small-driver.log, simulation cpu-small/track12_timed.out. Remote
compute ended before launch. Expected~30min; do not run heavy local analysis
or remote computation concurrently. CPU launcher automatically analyzes and
strictly validates afterward. GPU-standard and full/MPI logs fetching locally
(scp session74550); analysis of standard and cross-architecture comparison
deferred until CPU run/analysis exits. Current source SHA a90ded... (above).
CPU COMPLETED,session18564 exit0:1501steps,1719.49s, strict validator PASS all
13000 postbirth+8H5 birth+4input birth records,12identities,13012comparison rows.
GPU-standard
fetch finished. New untracked finish_comparisons.sh performs standard analyzer,
strict completion, exact-input/source CPU/GPU comparison, historical standard
baseline comparison, then plot_architecture_comparison.py (PNG/PDF overlay+
absolute-error envelopes). finish_comparisons.sh now RUNNING; log final-comparisons.log.
Plot script uses pandas and existing font cache,1thread. No remote compute active.
No local CPU study concurrently; start run_cpu_small.sh once GPU jobs finish.
Fresh prepared-only source SHA is
a90ded645880351cc23c56c4e95b19610ebeacac73eb27854d1749d57cbd49ab;
pre-fix prepared fingerprint preserved as prepared-fingerprint-before-cuda-fixes.json.
Expected CPU fingerprint recopied remote; no full trajectory has started.
Next: remote rebuild/full CTest, then MPI and integration executions, smoke,
local/full matched studies. Old tests below are pre-fix, not current acceptance.
Never start heavy remote work while local four-worker build/tests are active.
Previous canonical source SHA below now identifies the PRE-FIX executable only.

SSH works again. merlin-g-100 is MIXED, not drained; user's queue was empty.
Preserving both existing remote checkouts, including the extensively dirty old
validation tree. Fresh source snapshot of committed27dc0ed52 prepared at
`/psi/home/adelmann/opalx-dev/opalx-beambeam-validation-20261002` (archive, not a Git
checkout; copied generated revision header identifies commit). Reuses verified
clean, matching IPPL/Kokkos/Heffte/H5hut source dependencies through FetchContent
overrides; no dependency code edits. Build script/evidence locally under
tmp/beambeam-cross-architecture-20261002/build_a100.sh. Requests1task×4CPUs,1A100,
32GiB, then serial full CTest. Script rejects allocations above4CPUs.
Job354307 failed configure because IPPL hardcodes the Kokkos launcher below its
FetchContent path despite source overrides. Fixed build-directory symlinks only.
Job354308 cancelled during configuration after noticing the fresh cache needed
both OPALX_ENABLE_UNIT_TESTS and OPALX_ENABLE_TESTS. Both now explicitly ON.
Job354309 is the active retry. Allocation requests remain1task,4CPUs,1A100,32GiB;
354307/354308 confirmed cpu=4. Logs: remote build-test-<jobid>.log.
354309 configured successfully (CUDA/SERIAL,112 unit executables expected) and
is compiling dependencies. No source changes. New remote runs/gpu-small and
runs/gpu-standard contain exact local prepared inputs; runs/smoke is a derived
3-step case. No trajectory job started yet. Local helper scripts: gpu_rank.py
(rank-isolated GPU plus runtime PCI identity), test_a100_mpi.sh (1/2/4-rank
three-test groups, checks distinct PCI IDs), prepare_smoke.py, run_a100_case.sh,
check_smoke.py. These are untracked run artifacts, not changes to physics code.
Provenance audit found27 ignored Emacs undo-tree histories in local src/cmake
were included by the earlier fingerprint helper, but absent from clean archive.
Excluded ONLY filename suffix .~undo-tree~ from new fingerprints, explicitly
recorded the exclusion; user backups and historical executed-run fingerprints
untouched. Old prepared-only fingerprint retained beside new evidence. Canonical
source SHA256 (819 build/source files):
2bffe8a2ef8320756da709e534ba3717c7a7bfc1ad139a81c67d8df38d8e9517.
Updated helper at tmp/beambeam-cross-architecture-20260919/compare_architectures.py;
prepared CPU fingerprint refreshed; check_smoke compares exact source-file maps
and hashes against that fingerprint. No physics/build-source changes.
Remote audit PASS:819 files equal, canonical SHA matches. Added synthetic
fingerprint exclusion check to comparison self-check (run after GPU compute
releases CPUs). Prepared new local run_cpu_small.sh, not started. Live SSH shell
tool session7541 at new remote source root; use write_stdin for compact job/log
checks. Current job354309 at~97% (~80min elapsed): libopalx, opalx_exe and
TestBeamBeam built successfully; remaining space-charge/unit executables
compiling. No compiler errors. Runtime CTest/MPI/study gates not yet executed.
Remote ctest -N confirms112 unit executables (three optional integrations skipped).
Allocated A100 query succeeds; driver595.91.07. No runtime GPU test result yet.
Next: inspect job exit and full CTest; only on success submit test_a100_mpi.sh
with ntasks4,cpus-per-task1,gpus-per-node4,mem32G,account/partition gwendolen,
cluster gmerlin6. Check per-rank physical PCI uniqueness. Then run smoke via
run_a100_case.sh smoke (1task,1CPU,1GPU), fetch and run local check_smoke.py.
Only after smoke passes start full cases, serializing CPU/GPU work. Remote
case script records fingerprints and refuses existing simulation outputs.
Additional GPU validation without package installation: unchanged local CTest
input decks copied to remote integrations/{manufactured-field-regression,
witness-reference-offset-regression,witness-gather-mpi-regression}. The updated
test_a100_mpi.sh executes those five probe runs (manufactured1,offset1,witness
ranks1/2/4) after the nine unit groups; then fetch integrations and run local
check_gpu_integrations.py. It reuses established analysis functions and original
thresholds (3% manufactured E/B,8% offset magnitude,.999 direction,5e-4 MPI),
not a new physics criterion. Pending: test that new wrapper against copied CPU
fixtures after remote CPU budget frees; don't write into old CTest outputs.
System Python3 lacks h5py: optional Python integration skips on Merlin, per user.
GPU build/tests not yet complete; matched full studies still await CUDA gates.
Older DNS-blocker entries below are superseded by this successful connection.

User explicitly requested: resume, merge newest upstream master, redo all tests,
then continue the original cross-architecture/CAIN goal. Merlin work is authorized
again. Four CPUs maximum remains in force; serialize heavy builds, tests and
studies. No push requested.

- Starting branch: `271-implement-interation-point-element`, HEAD `fefd25341`.
- Latest fetched `origin/master`: `ce813d3cd` (closed-orbit finder PR553).
- Current dirty state is196 tracked modifications, all under
  `sandbox/attic/models/spherical-rest-gaussian`; preserve these and untracked
  studies. Previous604 deletions and timed-study edits were committed by later
  user work; September dirty-state descriptions below are historical.
- Merge completed as `27dc0ed522385acf747ad3e41f9c390e7e550d8b`; parents
  fefd253418ca00c34519e9c9182177c7e98bc09e and ce813d3cddd7c220632d549701c83a7f825ffb04.
  MERGE_HEAD cleared, index empty, no push. Six conflicts resolved
  (.gitignore, ParallelTracker.cpp/h, Beam.cpp/h, RelativisticFieldComposer.cpp).
  Tracker retains upstream terminal-step/time-centering flow with exactly one
  first drift, source-plane cleanup and element self-field/diagnostics/emission
  hooks; both beam attributes coexist. Mirrored-primary parity and units unchanged;
  upstream CUDA const views/materialized accumulation retained. Upstream combined
  momentum/gamma reduction can change rounding; check MPI without relaxing tolerances.
  Dirty path-list SHA256 remains aeb257e3fc7921ff9c2493c892299d67941fc63354d15748087b14094d13339b.
  Added attribute-independence regression in unit_tests/Structure/TestBeam.cpp.
  Configure and full four-worker build succeeded with new reference LAPACK/Fortran
  dependency. Logs: /tmp/opalx-{configure,build}-20261002.log. All 115 CTests pass
  (112 unit executables + 3 integrations; 75.13s). Additional BeamBeam17,
  FieldServices2 and ParticleBinTraversal4 tests pass on each of 1/2/4 MPI ranks.
  Eight Python workflow tests and strict comparison synthetic self-check pass.
  Driver/evidence: tmp/beambeam-cross-architecture-20261002/validate_local.sh and
  adjacent ctest.log, mpi-*/Test*.log, analysis-tests.log, comparison-self-check.log.
  Manufactured E/B relativeL2: 0.019913387623442268/0.019522103250674643.
  Witness MPI field/kick relative differences <=4.04512e-7 (unchanged 5e-4 gate).
  PR-source clang-format21 check passed; upstream trailing whitespace on two lines
  (README.md, CMakePresets.json) corrected; staged diff whitespace check passes.
- Post-commit configure/relink succeeded; executable embeds 27dc0ed52. Final full
  rerun: 115/115 CTests (63.09s), all nine MPI command groups, eight Python tests,
  comparison synthetic self-check and historical-baseline self-check all PASS.
  Logs, manufactured CSV and MPI JSON copied into the October evidence directory.
  Executable SHA256: 67dc081a88a50f0095d800e9667f9a7d30916daa98d23bdff3db38c39f7a910a.
  Physics/build source manifest: f4eb04b84b0ba8e3410f4990ecf711427ed2a3b9513bb4c5a37daf5df2ae5f28.
- Original-goal continuation: new isolated inputs prepared under
  tmp/beambeam-cross-architecture-20261002/cpu-small (100k,64x64x128) and
  gpu-standard-inputs (400k,256x256x128), all1501steps. Small physical inputs match
  September case byte-for-byte; standard deck matches retained A100 baseline.
  CPU provenance JSON explicitly says PREPARED ONLY; no new full trajectory run
  or GPU execution is claimed. Keep original both-build-gates-before-studies order.
- Current next step requires Merlin connectivity: SSH still cannot resolve
  merlin-l-001.psi.ch outside sandbox; user asked about PSI VPN/changed hostname.
  No remote job submitted. Once accessible, inspect node/jobs and isolated checkout,
  transfer merged source safely, configure/build CUDA with four CPUs, run full
  remote test suite and 1/2/4-rank gates, then exact-matched CPU/GPU cases above.
  Do NOT use old submission defaults (unit4x10,production4x4 CPUs): enforce <=4
  total CPUs, e.g. build1x4, MPI4x1, study1x4; serialize heavy work. No push.
- Merlin SSH currently fails resolving `merlin-l-001.psi.ch`, including outside
  the sandbox; no remote job was started. Continue local work while unavailable.
- Plan: merge upstream with preserved study edits; inspect/resolve integration;
  configure/build `build_openmp` with at most4 workers; run full CTest and relevant
  1/2/4-rank tests plus analysis tests; finalize merge; rebuild/validate matching
  CUDA source when connected; rerun matched CPU/GPU Track-12 studies and compare.
- Also retain the later spherical-Gaussian field-amplitude warning at the end of
  this file. Assess evidence after current manufactured-field regressions; do not
  equate that old spherical setup with the validated anisotropic Track-12 case.

Everything below records the September work and its evidence unless updated.

## Current status (GPU stopped; local simulation complete)

LATEST USER OVERRIDE: stop Merlin6 GPU work because of hardware problems. Confirmed jobs354238/354239/354240/354241 all CANCELLED at10:40:07local, elapsed00:00:00; none started, no replacements, squeue shows no user jobs. NO resubmission, automatic restart, hardware reset, or continued remote monitoring without new user direction. Remotecheckout/artifacts/inputfiles preserved. Local four-thread simulation and automatic analysis have exited successfully.

- Local work is complete; broader cross-architecture goal is NOT complete and is blocked by stopped/unavailable GPU work. No scheduler recovery is being pursued. The GPU blocker has persisted across the original goal turn and two continuations; all meaningful local validation is now finished.
- Local current source builds and passes all 94 unit-test executables, all 3 integration CTests, and relevant MPI tests on 1/2/4 ranks. C++ clang-format 21 and Git diff checks pass.
- Local 100k-primary, 64×64×128 study completed all1501steps (last global step1500), no reported errors, wall1748.84s. Launcher/automatic analyzer session64740 exited0. Strict completeness PASS: actual H5 contains13008 rows (13000 mandatory post-birth +8 optional birth-time states), analyzer adds4 absent input births, all12 identities/13012 reference rows match. Hashes, actual clocks, finite six-component phase space, exact CSV reconstruction and exact report metrics verified. Initial validator incorrectly assumed all12 births absent; fixed only checker semantics, no simulation data/physics/tolerance change. Synthetic optional-birth and missing/duplicate/wrong-step guards pass.
- Full59MB local run preserved in tmp/beambeam-cross-architecture-20260919/cpu-small-completed; recursive byte comparison against original case passes. Report: tmp/beambeam-cross-architecture-20260919/CPU_RESULTS.md. Evidence: preserved results/completion_validation.json. No local simulation, analyzer or test sessions remain active.
- Local overall CAIN relativeL2: x8.2070576%,s3.0052317%,y94.7227146%. Analytic rigid two-Gaussian reference: x3.4245493%,s0.3643556%; its yreference is zero (absolute yRMSE6.60931um). Positron CAIN xrelativeL2=115.569576%,xRMSE6.17536um; do not claim uniform few-percent agreement. This coarse100k64×64×128 case is not an exact same-input regression against the old400k256×256×128 A100 baseline.
- Merlin initially compiled all CUDA targets successfully. Latest small ORB adapter fix is synced but still needs final CUDA rebuild/retest.
- EXTERNAL BLOCK: sole eligible A100 node merlin-g-100 is MIXED+DRAIN after UCX I/O abort and NVML GPU loss during a four-rank test. No new A100 study has run.
- Recovery chain354238/354239/354240/354241 was cancelled per user request, before any job started. No remote tasks queued/running; no replacements. Preserved ledger: build_a100/recovery-job-chain.txt.
- Last authorized node check08:34:34UTC: SSH worked but compute node remained MIXED+DRAIN. User subsequently stopped GPU work; do not keep monitoring or restart it.
- User explicitly requested finishing the merge. Local merge commit35a1825481d6584ae3fa4a9ab3b86a96c47bf20a created; MERGE_HEAD cleared and index clean. No push requested or performed. Three study-script edits and604 pre-existing sandbox deletions remain unstaged; unrelated untracked files untouched.

## User intent and scope

LATEST RESOURCE CONSTRAINT: user permits only4CPUs. Local study uses4OpenMP threads. Use -j4 maximum for future builds and bound BLAS/OpenMP analysis to4. GPU workflow was cancelled before resource-adjusted execution. If explicitly resumed later, require build1×4CPU, GPUgate4MPI×1CPU, studies1×<=4CPU; verify Slurm allocations and submitted scripts, serialize work to avoid exceeding4 total workers. No permission to resubmit now.

Analyzer now bounds BLAS/MKL/Accelerate/NumExpr pools to an explicitly supplied positive OMP_NUM_THREADS before h5py/NumPy import. The direct launcher used OMP_NUM_THREADS=4 for analysis; no simulation/baseline input or physics change. All8workflowtests pass after completion (1.493s); subprocess checks confirm oversized limits clamp and smaller limits remain unchanged. Importing this helper after NumPy has initialized is not a retroactive pool cap; importing entrypoints must set limits at startup. Existing h6 has no threadpoolctl; no package installed.

Synchronize local branch with origin/master; compile local OpenMP and Merlin A100; reproduce the established 12-particle CAIN benchmark and check CPU/A100 agreement. User explicitly clarified that CAIN uses a different solver, some percent deviation is expected, and the existing handover results are good. Original CAIN deck exists but is deferred. Do NOT change physics to force exact CAIN agreement. Finite-emittance/opposing-only experiments are deferred and NOT completion gates.

Preserve unrelated studies and ignore unrelated untracked sandbox files for Git. No upstream IPPL/Kokkos source edits. No public API/default physics changes, no tolerance relaxation. Use /Users/adelmann/.venv-h6/bin/python locally.

## Git and preserved state

- Local branch: 271-implement-interation-point-element, initial HEAD efedfcc310edcb0b5ac0a03f901ef4d71809b8f6.
- Fetched origin/master45e126f3a; merge completed in35a1825481d6584ae3fa4a9ab3b86a96c47bf20a (parents efedfcc310edcb0b5ac0a03f901ef4d71809b8f6 and45e126f3a8e7023e31e878b20d1634dc813c71cb). All13 conflicts resolved. Commit includes tested C++ integration and3 obsolete RETIRE_TIME template fixes, but not the separate timed-study script edits/untracked study tests or README.
- Preserve604 pre-existing tracked deletions:600 absent sandbox/Drift-Experiment files and4 sandbox/attic files. Never stage these accidentally.
- Other user untracked directories/files are out of scope.
- Original Merlin /psi/home/adelmann/opalx-dev/opalx untouched: HEAD3f272ecef, pre-existing unfinished merge and staged changes.
- Isolated Merlin checkout: /psi/home/adelmann/opalx-dev/opalx-beambeam-validation.
- Previous stale/empty local build preserved as build_openmp.pre-master-20260919.

## Implemented integration

Master replaced PartBunch-owned fields with SpaceChargeSolver/CartesianPIC3D. Ported BeamBeam through internal BeamBeamFieldServices, retaining same-sign reflected primary (+Ex,+Ey,-Ez), reversed pz, one solve/bin, rigid primary, witness migration/gather and nonshrinking fixed interaction mesh. Solver owns frame conversions; source bounds use temporary rotations; witness gather is collective even with locally empty ranks.

Important review fixes:
- Ordinary tracker solve frames match master, including translation needed for absolute cathode/image plane R0Z. Collective-element dispatch receives a separate rotation-only context.
- BeamBeam permits configured nonzero ORB frequency because CartesianDomainUpdater already suppresses redistribution for every fixed domain. Ordinary fixed-domain validation remains unchanged. Regression tests frequency1, threshold0, zero redistributions and unchanged configuration.
- Rho diagnostics capture normalized primary density before OPEN overwrites rho with potential; optional transition snapshots only.
- Removed obsolete RETIRE_TIME from3 tracked integration templates; fixed obsolete FieldContainer argument in TestEmittedFromFile.
- Migrated all17 BeamBeam tests; new field-service/mirror and absolute-plane tests. No numerical tolerance changes.
- Study preparation supports isolated directories and input hashes; analyzer uses actual OPEN coordinates and inferred IP, rejecting nonfinite data.

Out-of-scope review limitations: witness/source axes assumed parallel (satisfied here); dropping below MINBINEMITTED could leave stale AfterEmission fields (not reached by fixed100k/400k cases).

Local read-only FieldMirror audit found no port-introduced signature/buffer defect: coordBool matches pinnedIPPL ippl::Vector<bool,Dim>, serialization fences beforeMPI, distinct send archives remain pool-held throughWaitall. GPU path does pass CudaSpace pointers directly toMPI and has no automatic runtime support check/host fallback; CUDA-aware MPI/UCX is therefore a hard prerequisite distinct from Heffte’s GPU-aware option. Verify environment only ifuserlaterresumesGPUwork; no speculative source edits or remote probing now.

## Builds and validation evidence

Local: build_openmp, LLVM21.1.8, Homebrew CMake4.1.2, libomp, Release/OPENMP, tests ON. Explicit libomp CMake paths required.
- IPPL a7e505730a76dd1edc7d0c8b96fb4223d9f84cfb
- Kokkos5.2.0 d9397f95a04a0334d327647e64ab7f1882ca0664
- Current CPU exe SHA256:39d1cc1ff994beeb10a4b7e404769a290c5322a59c895230bfcbd771ef6759a1
- Current full source manifest (includes unit tests):d943398d8e4fb1966b2279ed2edbf3b8b8ed5d77178f39a7f7588329db3c0e18
- Study helper source-content hash (different file set):f5a68ded84196f8412727d8fb5693bd2cfa14c4bf00f002059b5baa698c6b0c8
- Final94/94 unit pass: /tmp/opalx-all-unit-tests-orb-final-20260919.log (30.76s).
- All3 integration pass: /tmp/opalx-integration-orb-fixed-20260919.log (14.81s).
- Fresh pre-commit full CTest97/97 passes (30.12s), including3 integration tests/MPI witness gather: tmp/beambeam-cross-architecture-20260919/pre-merge-commit-ctest.log. All physics-source hashes match the completed CPU run. Clang-format21 dry-run on changed C++ against merge parent and index whitespace check passed immediately before commit.
- Final FieldServices n1/n2/n4: /tmp/opalx-beambeam-orb-validation.n10BHJ/n{1,2,4}/validation.log.
- BeamBeam17 tests n2/n4: /tmp/opalx-beambeam-mpi-validation.2fJPOJ/.
- Absolute translated-plane regression6/6: /tmp/opalx-absolute-plane-regression.MQgfut/validation.log. Non-vacuous wrong-frame signal hundredsV/m: /tmp/opalx-absolute-plane-signal.kbKR2k/signal.log.
- Local MPI needs oversubscribe/unbind: PRTE_MCA_rmaps_default_mapping_policy=slot:OVERSUBSCRIBE PRTE_MCA_hwloc_default_binding_policy=none; OMP_PROC_BIND=false.
- CartesianPIC3DFields/Algorithms fixture is serial-only (undecomposed layout); use dedicated BeamBeam tests for multi-rank validation.

Merlin: GCC14.3, CUDA12.9.1, OpenMPI5.0.10_slurm, CMake4.4; AMPERE80, Heffte GPU-aware MPI OFF; same IPPL/Kokkos.
- Full CUDA build job354236 succeeded with compute ldd check at08:17:06UTC (302.60s), BEFORE latest ORB fix.
- Previous CUDA exe SHA:d03f731ad306d252a23fd652bb289ee85de7de3c3c337c7e4f905b9cd1c421d8; do not use as final patched fingerprint.
- GPU gate354237 passed14/15 command groups:11 single-rank, both2-rank,4-rankBeamBeam.4-rankFieldServices aborted in UCX ucp_worker.c:668 / MPI_Recv/Waitall, not an assertion; GPU lost and node drained. Actual per-rank GPU UUIDs verified distinct.
- Only account/partition gmerlin6/gwendolen and node merlin-g-100 (8A100) eligible; no alternative partition/node.
- Login RHEL8 vs compute RHEL9 caused build-environment mismatches: CUDAToolkit_rt_LIBRARY must point to /usr/lib64/librt.so.1 on compute, Python3_EXECUTABLE=/usr/bin/python3 (3.9.25). Remote optional Python integration skipped for missing h5py/numpy/pandas; local tests cover it.
- Switching builds between OS hosts triggers dependency rebuilds due missing system-header prerequisites, e.g. bits/atomic_wide_counter.h. Keep final build on compute environment.
- Earlier task jobs354230 failed stale librt,354231 canceled dependent,354233 failed Python loader. Login build groups2847198 and3406570 stopped by verified task-only SIGINT; evidence preserved. No unrelated processes/GPU reset/admin changes.
- Remote logs under isolated checkout: build-a100-final.log, build-a100-orb.log, build_a100/gpu-unit-tests-354237/, compute-cache-repair-354236/.

## Completed / prepared studies

CPU completed: /tmp/opalx-track12-validation-20260919/cpu-small
-100k deterministic primaries,64×64×128,1501steps;1MPIrank,4OMPthreads.
- Launch: tmp/beambeam-cross-architecture-20260919/run_cpu_small.sh
- Log: track12_timed.out; provenance: results/execution_fingerprint.json.
- Script completed compare_timed_track12.py after simulation; analysis log results/comparison_stdout.log.
- Preserve the completed run; no restart is required or running.
- Source particle SHA:3fafe74b7dca39b95f814d569316d71b4239656df848764c2823d90ca423dfff

GPU inputs, not executed:
 /psi/home/adelmann/opalx-dev/opalx-beambeam-validation-runs-20260919/gpu-small
 /psi/home/adelmann/opalx-dev/opalx-beambeam-validation-runs-20260919/gpu-standard
- gpu-small physical input files byte-identical to CPU case.
- gpu-standard400k,256×256×128,1501steps.
-400k source SHA625621deae71b5e66522dfc8b9c17d02a75bf9db3e7cd6a0d70f5e94aa59ccd5
-standard deck SHAe4f99f25112525f8e238d3c1c51a5c5d1b449d71de783102574f8f93d716dbc6
- Reference sandbox/TestParticleOrbit.dat SHA c06ac966cf09d673f0550904aee6805210ea696c13a848ca00c84fa58ecc3b06.
- Six e-/e+ pairs;13000 mandatory post-birth samples plus12 birth states. Current CPU H5 contains8 of those birth states;4 are added from input. Exact dt=1.8um/c, finalglobal1500, first post-birth steps1/168/334/501/668/834. No interpolation or unwrapping for current OPEN runs.

## Comparisons and established baseline

Helpers in tmp/beambeam-cross-architecture-20260919/:
- compare_architectures.py: fingerprint / compare / self-check. Match actual GlobalTrackStep/TIME and identity; validate same physical input hashes and complete13000 mandatory post-birth records. Optional exact-birth H5 snapshots are validated/counted separately and excluded from architecture metrics. No invented default tolerance.
- validate_completed_run.py --run-dir CASE --output NEW_JSON: strict single-run completeness/provenance/CSV/report verifier. Passed currentCPUcase, including13008 actual H5 rows and4 input births.
- compare_historical_baseline.py --new-run-dir <fetched gpu-standard> --output-dir <new path>: strict13012 CSV keys/clock, six phase-space components, overall/species/pair metrics; self-check passes.
- README.md and HISTORICAL_BASELINE_COMPARISON.md explain usage.

Historical same-resolution case:
 sandbox/track12particles/opalx/timed/a100_1rank_400k_256x256x128_aspect_eef599761/
- Exact same standard deck/source hashes; old executable predates OPEN fix but report records ZERO wraps for all12.
- Overall CAIN xL2=9.482836%,sL2=2.967314%; manufactured xL2=0.853754%,sL2=0.117302%.
- CAIN xRMSE30.4471um,sRMSE24.3946um. Species caveat: positron xL2=107.904188% but xRMSE5.76577um; do not describe every trajectory as uniformly few-percent agreement.
- Retained results/track12_pointwise_comparison.csv and track12_comparison.json (JSON SHA5ac1949e50724f160c267f5e66edf478cd27b9ce720755c00fd2da12fe976200).
- Policy: sandbox/BEAMBEAM_PHYSICS_AND_VALIDATION.md:255–271. Fine-grid results: sandbox/track12particles/opalx/README.md:115–139 (x9.545%,s2.9774% vs CAIN).
- Existing5e-4 ceiling applies to MPI field/kick regression, not an explicit CPU/A100 trajectory threshold.

Optional source-model audit/controls under tmp/cain-model-audit-20260919 are PREPARED ONLY and deferred by user. Do not launch or require original deck/opposing-only mode now.

## Next steps

Latest user-requested note comparison completed read-only: sandbox/note/bb-note.tex/PDF Section5 accurately reproduces the retained400k4096×256×128 four-A100 JSON. Full comparison saved in tmp/beambeam-cross-architecture-20260919/NOTE_COMPARISON.md. Note's sub-percent result is vs manufactured model, notCAIN. Current coarseCPU manufactured x/s errors3.4245%/0.36436% vs0.6004%/0.09708% historical (5.70×/3.75× larger); CAIN8.2071%/3.0052% vs9.5453%/2.9774%. Current first-kick ratios0.2521–0.9873 vs0.9295–0.9749, later births under-kicked; charge symmetry remains~5.4e-10. Different particles/grid/domain/backend preclude a merge or architecture regression claim. Fresh fieldCTest E/B1.9913%/1.9522% vsnote2.10%/2.20%; MPI rank differences~4.05e-7 vsnote<1.5e-15, stillbelowexisting5e-4criterion. No note/source edits, new simulations, remote work, commits or tolerance changes in this comparison.

1. Await user direction. Local simulation/analysis/integrity checks and relevant tests are finished; plots inspected, final whitespace checks pass. Last workflow8/8 rerun1.531s saved to tmp/beambeam-cross-architecture-20260919/cpu-workflow-tests.log.
2. Merlin cancellation is already verified: task-owned chain354238/354239/354240/354241 stopped before execution. Do not monitor, resubmit, or restart automatically.
3. Only if the user later resumes GPU work after recovery: final CUDA rebuild/loader check, GPU unit gate including4-rank mirror, then gpu-small/gpu-standard. Fetch outputs and run exact architecture and historical comparisons, respecting4CPU maximum.
4. Merge is complete locally as35a182548. Preserve3 remaining unstaged timed-study script edits and604 user sandbox deletions; deletion-list SHA256 stayed1e33917deb4f5028b7d00d9573a60bf1683256656dfc92dd8ead385eac67f135 across commit. No push or further commit without permission.
5. Goal is blocked, not complete: no new GPU comparisons exist, and user explicitly stopped GPU work. New user direction/external recovery is required; do not use automatic goal continuation to override that stop.

Detailed prior chronological history: tmp/beambeam-cross-architecture-20260919/HANDOFF_HISTORY_0832.md.

## Spherical-rest-Gaussian rerun (2026-09-19)

- Working directory: `sandbox/attic/models/spherical-rest-gaussian`.
- Preserved July OPALX/MSOL data and plots in `atic/baseline-2026-07-07` before overwriting.
- Fixed Python repository-root discovery and moved-config CAIN paths. Removed obsolete BeamBeam input attributes `RETIRE_TIME` and `IP_S` for the compiled API.
- Current `build_openmp/src/opalx` reports embedded revision `efedfcc310edcb0b5ac0a03f901ef4d71809b8f6`.
- Fresh 10-step 400k run, MSOL run, 152 MSOL contour frames, 20 OPALX contour frames, and density alignment plots completed.
- Fresh 20,000-step run completed in 599.079 s; BeamBeam solve active for 7,859 steps. Final populations: primary 98,987/400,000, electron witnesses 5/6, positron witnesses 3/6.
- Absolute initial C0 field regression: E-rms changed from 2.673752e9 V/m (July) to 7.490261e13 V/m, ratio 2.8014e4, with identical charge and longitudinal RMS. Normalized density shape remains visually similar.
- Old/new best negative-charge MSOL track metrics: x RMSE 2032.85 -> 2291.25 um; longitudinal RMSE 364.27 -> 10774.16 um. First-10-ps x RMSE 136.42 -> 203.04 um; longitudinal RMSE 27.41 -> 985.39 um.
- Current witness H5 IDs become primary-like IDs after losses. `compare_tracks_20000.py` now assigns surviving trajectories by minimum displacement between adjacent dumps.
- Main unresolved issue: current BeamBeam field amplitude is physically wrong by roughly four orders of magnitude; diagnose field-domain/unit scaling before using these results as validation.
