# Active Physics diagnostic output isolation

Status: two-file implementation and source review complete; root coordinates builds and test execution. No staging, commits or pushes.

Active generated CSVs now live in unique owned temporary directories:

- muon_angular_spectrum_mu_minus.csv
- muon_angular_spectrum_mu_plus.csv
- pion_rest_costheta.csv
- pion_boosted_energy_box.csv

MuonDecaySpectrumTest::runAngularCase creates a local TemporaryDirectory before its existing CSV write; both sign cases use that helper. Each PionDecaySpectrumTest case likewise creates a local owner around its output. writeSpectrumCsv opens and closes the stream within the call, so directory cleanup occurs only after the CSV has been consumed by the writer and the path logged. These diagnostics are now removed at case exit, and header comments describe that lifetime. No numerical setup, particle counts, seeds, histograms, assertions or tolerances changed. SpectrumTestSupport.h is unchanged; there are no new scripts or external data dependencies.

Audit of other registered Physics targets: TestLinearCompton, TestLinearBreitWheeler and TestMuonDecay have no file outputs. TestLinearComptonSpectrum and TestLinearBreitWheelerSpectrum remain disabled and untouched. Their external reference CSV concerns are outside this isolation change. Standalone LinearComptonSpectrumBenchmark and LinearBreitWheelerBenchmark intentionally take user-selected output paths and are unchanged. No CMake registration changed.

Checks: LLVM21 clang-format --dry-run --Werror and scoped git diff --check pass. No builds/tests started by this worker. Relevant targets: TestMuonDecaySpectrum and TestPionDecaySpectrum.

Source hashes:

- unit_tests/Physics/TestMuonDecaySpectrum.cpp: e565496913675ed80dfd0d572c7ed501ac7ab7e6e3c461520033b1655d4d8f5a
- unit_tests/Physics/TestPionDecaySpectrum.cpp: 31f90098b2ca1a6b80600f7488fa210feb245f051648ca653d8a8b4ba692ec9a
