"""Pin build, source and independent validation evidence for the fixed model."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
REPO=Path('/Users/adelmann/git/opalx')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

sources=['src/SpaceCharge/FFT2D5/FFT2D5Algorithm.h','src/SpaceCharge/FFT2D5/FFT2D5Algorithm.hpp',
    'src/SpaceCharge/SpaceChargeConfig.h','src/SpaceCharge/SpaceChargeConfig.cpp',
    'src/SpaceCharge/SpaceChargeConfigBuilder.cpp','src/Structure/FieldSolverCmd.h',
    'src/Structure/FieldSolverCmd.cpp','unit_tests/SpaceCharge/TestFFT2D5Numerics.cpp',
    'unit_tests/SpaceCharge/TestSpaceChargeConfig.cpp','docs/validation/fft2d5/longitudinal-model.md',
    '.github/workflows/cpu-serial.yml']
units=[]
for name in ['TestFFT2D5Numerics','TestFFT2D5Algorithm','TestSpaceChargeConfig']:
    xml=ROOT/'checks'/(name+'.xml');r=ET.parse(xml).getroot()
    cases=r.findall('.//testcase');skips=sum(c.find('skipped') is not None for c in cases)
    assert int(r.attrib['failures'])==int(r.attrib['errors'])==0
    binary=REPO/'build-omp/unit_tests/SpaceCharge'/name
    units.append(dict(name=name,tests=len(cases),passed=len(cases)-skips,skipped=skips,
        binary_sha256=sha(binary),xml_sha256=sha(xml),log_sha256=sha(xml.with_suffix('.log'))))
ranklog=ROOT/'checks/rank2-guard/opalx-rank2.log'
assert 'FFT2D5 supports only one MPI rank.' in ranklog.read_text()
gate=dict(date='2026-11-02',units=units,total_passed=sum(x['passed'] for x in units),
    total_skipped=sum(x['skipped'] for x in units),
    expected_skip='Rank-specific Numerics test in one-rank suite; separately verified native rank2 rejection.',
    native_rank2_guard=dict(expected_rejection=True,returncode=156,log_sha256=sha(ranklog)),
    build_target='opalx_exe (opalx is the static library)',build_log_sha256=sha(ROOT/'build.log'),
    binary=json.loads((ROOT/'binary-archives.json').read_text()),
    source_sha256={path:sha(REPO/path) for path in sources},
    independent_native_audit=str(ROOT/'audit-api/checks.json'),
    native_regression=str(ROOT/'regression-checks/correct/physics-validation.json'),
    native_regression_controls=str(ROOT/'regression-checks/regression-controls.json'),
    legacy_tracking_regressions=str(ROOT/'checks/legacy-regression-checks.json'),
    ci='Local workflow includes native field validator; YAML parsed. Remote GitHub Actions not run.',
    limits='CPU OpenMP, FFT2D5 one rank, straight frozen uniform-round pipe field. No general curved/free-space or new-mode tracking validation.')
(ROOT/'checks/gates.json').write_text(json.dumps(gate,indent=2)+'\n')
print(json.dumps(dict(passed=gate['total_passed'],skipped=gate['total_skipped'],rank2_guard=True)))
