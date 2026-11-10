# Read-only implicit-writer reachability audit

Scope: unchanged registered AbsBeamline/Elements fixtures with input stems or DataSink construction, after the initial isolation edits. No source edits or builds performed in this audit.

## One missed active output

TestRFCavity.cpp IdealRFCavityTest::FullAutophaserRespectsVetoAndFindsCrest and ::FullAutophaserAdjustsGradientToDesignEnergy reach CavityAutophaser::getPhaseAtMaxEnergy with veto=false. CavityAutophaser.cpp156 constructs a filename from OpalData::getAuxiliaryOutputDirectory() and cavity.getName()+"_AP.dat", then opens an ofstream. The current name ideal therefore attempts shared data/ideal_AP.dat. It is cavity-name-derived, so changing only the input filename would not isolate it. Root notified before the final Linux source snapshot.

Small explicit-path option: give IdealRFCavityTest an owned TemporaryDirectory and set the cavity's name to (directory.path()/"ideal").string(). ElementBase::setName is public. Util::combineFilePath uses filesystem path composition, so an absolute cavity name directs the AP data into the owned directory. Current assertions do not depend on the literal cavity name. No process working-directory mutation or production change is needed. Root owns any resulting source edit.

## Safe current reachability

- DataSink::init constructs StatWriter/LBalWriter objects. SDDSWriter constructor only records the filename/mode and checks filesystem existence; it does not open the file. Default destruction does not write.
- PartBunch constructor allocates domain, containers and attributes and logs through Inform. It does not invoke DataSink or filesystem writers.
- ParticleContainer::createParticles creates/initializes attribute slots and logs counts; it does not invoke any diagnostic writer.
- PartBunch::gatherLoadBalanceStatistics (PartBunch.cpp225) only fills its count buffer and performs an MPI allreduce. Despite its name it never calls LBalWriter::write. Its only current caller is DataSink::dumpSDDS, which the reviewed unchanged fixtures do not call.
- TestMultipoleT, TestMultipoleTStraight and TestMultipoleTCurvedConstRadius use initialise/apply/finalise, plus non-writing DataSink construction. Their fixed unit_test input stem is not a generated artifact in these tests.
- TestVariableRFCavity follows the same non-writing field path. Its BorrowedBunchTracker test constructs/registers a cavity via visitVariableRFCavity; the constructor and visitor do not execute tracking or prepareSections/save writers.
- TestOpalBeamlinePlacement invokes prepareSections. OpalBeamline::prepareSections only sorts and resolves geometry; it does not call save3DLattice/save3DInput. Its non-writing DataSink construction is safe.
- TestRFCavity's basic FakeFieldmap fixture injects field state directly and never calls the mapped initialise(bunch) branch that can write errormsg.txt on a frequency mismatch. IdealRFCavityTest::initialise returns through the ideal branch before that warning-file code. Direct trackOnAxisParticle calls use the default null output stream. Only the full autophaser cases above open an AP file.

The protected CyclotronSector/RF cases use existing process-specific map paths. Disabled Physics CSV-reference tests remain unregistered and unchanged; standalone benchmarks intentionally accept user-selected output paths and are outside this unit-test isolation change.
