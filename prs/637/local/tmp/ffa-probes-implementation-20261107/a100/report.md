# FFA probe A100 validation: passed

Both authorized GPU jobs completed successfully on Gwendolen / merlin-g-100:

- Build/native tests355069: COMPLETED, exit0:0, elapsed27m45s.
- Unchanged school integrations355070: COMPLETED, exit0:0, elapsed10m40s for both runs.

The preceding355067/355068 attempts failed during setup, before native tests: first an incorrect submission working directory, then IPPL's hard-coded Kokkos launcher path with a source-directory override. Both concrete causes were fixed in the isolated job setup. Logs are retained under remote-final/evidence/attempt1 andattempt2; these are not probe source failures or successful validation runs. No production/dependency source change or tolerance change was made for GPU validation.

## Native tests actually executed

CTest2/2targets passed in11.05s; JUnit records failures0, disabled0, skipped0.

| Target/process | Cases run | Passed | Skipped |
|---|---:|---:|---:|
| TestCyclotronProbe, one MPI process |12|12|0|
| TestCyclotronProbeMPI, first MPI process |12|12|0|
| TestCyclotronProbeMPI, second MPI process |12|12|0|

The new FfaStationsPreserveNativeFrameAndHistoryWithoutRadialSummaries test appears as RUN/OK once in the one-rank target and twice in the two-rank target (105ms /198ms per process). Thus it actually ran and passed on each rank. All native tests use self-contained C++; their CTest commands directly launch the C++ executables through mpiexec. Python scripts in the job only verify provenance outside CTest.

Native-test rank-to-GPU mapping was not captured. These results establish one/two MPI processes executing the CUDA build in a two-A100 allocation; allocation alone is not evidence that each process selected a distinct GPU. The separate school runs below record explicit device assignments.

Evidence: remote-final/evidence/tests.log, junit.xml andtest-commands.log; parsed per-process counts in native-log-audit.json.

## Matched school output

Used the unchanged corrected16-cell linked-final CPU input: one particle,12MeV nominal,16explicit stations, NONE space charge,10,000 nominal steps at2.1043771043771044e-10s. CPU reference is native-16-cell-linked-final-hdf5-r1, executableSHA58bd5db212d2dc3e62c8fdf62a51fb2dca456580eabf9452c595ea448777f9d5.

InputSHA256:31fee815416edc19edc318000be8a6dee28f1c2bc5df57f230cd189ede3729ea.
Particle-fileSHA256:65ca902e9907a3a48563ec34729429e71ea68433a6055ceef92b6caa60fa16d7.
The inert positive FFA STEP=1e-30mm also exercises the parser's geometry-only validation and absence of unused histogram allocation.

Both one- and two-rank GPU runs record exactly57hits across all16stations, with matching station counts, stable IDs, bunch numbers and native reference-turn labels. One particle survives with charge1.0000000000000001e-19C, identical to CPU. No FFA histogram/peak files are produced.

| Maximum absolute GPU minus CPU difference | One rank | Two ranks |
|---|---:|---:|
| Probe position component [m] |6.9234e-13|6.9234e-13|
| Probe momentum component [p/(mc)] |1.0897e-13|1.0897e-13|
| Probe time [s] |1.5120e-19|1.5120e-19|
| Final particle coordinate component [m] |7.3815e-12|7.3815e-12|
| Final reference coordinate component [m] |1.7387e-13|1.7387e-13|
| Final reference momentum component [p/(mc)] |4.5797e-16|4.5797e-16|
| Final time [s] |0|0|

These differences are consistent with accumulated floating-point roundoff. GPU accepted-step counts are36,256 versus CPU36,245 because floating-point boundary decisions can change tiny accepted subdivisions. Both reach the identical nominal final time2.104377104377088e-6s. No bitwise CPU/GPU schedule or state equivalence is claimed.

The two GPU runs have identical measured probe numeric records and final numeric fields (id,x,y,z,px,py,pz,q,TIME,GlobalTrackStep,SPOS,RefPartR,RefPartP). This is a checked result for those fields, not an assertion about file bytes or runtime metadata. See gpu-rank-equivalence.json andgpu-school-audit.json; audit_gpu.py reproduces the output audit without rerunning simulations.

## Explicit GPU assignment

The school wrapper selected one inherited CUDA_VISIBLE_DEVICES token per OMPI local rank and set KOKKOS_DEVICE_ID=0 within that single-device view before exec. Successful runs therefore used the recorded assignment:

| School rank | Device token | Physical GPU UUID | PCI bus |
|---|---|---|---|
|0|0|GPU-5f9879f3-2745-d8dd-af12-fb57a4460c1f|00000000:07:00.0|
|1, two-rank run|1|GPU-ddaf526c-0266-266a-8606-0f82d8aa1f8d|00000000:B7:00.0|

Raw rank/PID/device records are in remote-final/gpu-school/r1/gpu-mapping-rank0.json andr2/gpu-mapping-rank{0,1}.json. The two-rank school case has one macro-particle globally, so the empty-rank path is exercised; the native16-station test separately performs real particle-history migration.

## Provenance and preservation

Source snapshot790abac196432fcfca893ad73d0e045de4efca21768a32fa6cfc33a53ba47afa, base ec4319acb1d3cf676f2581f4c86c3e691ce2e22d. All1072manifest files were verified before build and after native tests. The source is an uncommitted feature snapshot, not a claimed committed revision. Parent independently confirmed current intended C++ files match; subsequent README/documentation changes are outside the GPU code result.

Toolchain: sharedRelease CUDA;SERIAL, AMPERE80, GCC14.3.0, CUDA13.2.1/NVCC13.2.78, OpenMPI5.0.10_slurm, CMake4.4.0, A100-SXM4-40GB, driver595.91.07, OMP1.

Fresh IPPL3.4.0 d6216553e39dcf4405849c027517cc3401fefee5. GPU uses declared release-testing preset Kokkos5.2.2 8e15454876298832f013ebcaf08d53825b5bda40; CPU cache uses5.2.0, a recorded toolchain difference. heFFTe6e16996e5a3eb65c60fd62fd4d93c4b2df833033, GTest6910c9d9165801d8827d628cb72eb7ea9dd538c5, H5hutb5c74f760bc9919d409f46b5472e9eedf9a764d5. Post-run dependency working trees are clean.

GPU executableSHA256:efaa5402dc8e5aadc13dcb264f94d3e8f24e358adde52e4d64ae615c0ecad13c.
Shared libopalxSHA256:32c6b741a6404414f21c9a5da0428c051e358a780690e0a9b5cd693270b3c789.
All four binary hashes are in remote-final/evidence/binaries.sha256.

The original remote checkout /data/user/adelmann/opalx-dev/opalx-probe-615 remains tracked-clean at a9d38caa4f88433a5de1508b3d5c7d01bdfea95a with its prior untracked slurm/tmp files; its existing build/dependency source trees were not modified. All new source/build/output work used /data/user/adelmann/opalx-dev/ffa-probes-20261107/790abac19643.

Terminal raw evidence archive validation-evidence.tgz SHA256064ed62706d7c26b1093eacc63fd972d50673c259d46faa4375f01865e5e2695 was verified after retrieval and extracted under remote-final/. No jobs remain active for this task. No commits/pushes were made. No further validation or performance work was run.
