"""Check that cached evidence replots offline without modifying copied inputs."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    selection=json.loads((ROOT/'plot_selection.json').read_text())
    temporary=Path(tempfile.mkdtemp(prefix='opalx-sacr-offline-',dir='/private/tmp'))
    data=temporary/'analysis';reference=temporary/'reference';out=temporary/'figures'
    data.mkdir();reference.mkdir()
    files=['analyze_fields.py','fields_comparison.csv','field_summary.csv',
           'mesh_and_control_changes.csv','cases_manifest.json',
           'native_profiles_comparison.csv']
    for name in files:shutil.copy2(ROOT/name,data/name)
    for name in ['tube_reference.py','fields_reference.csv']:
        shutil.copy2(STUDY/'reference'/name,reference/name)
    before={str(p.relative_to(temporary)):sha(p) for p in [*data.iterdir(),*reference.iterdir()]}
    command=[sys.executable,str(data/'analyze_fields.py'),'--replot','--output-dir',str(out),
             '--transverse-cases',*selection['transverse'],
             '--longitudinal-cases',*selection['longitudinal'],
             '--field-cases',*selection['direct_fields']]
    completed=subprocess.run(command,capture_output=True,text=True,check=True)
    unchanged=all(sha(temporary/path)==digest for path,digest in before.items())
    images={p.name:sha(p)==sha(ROOT/p.name) for p in out.glob('*.png')}
    result=dict(passed=unchanged and bool(images) and all(images.values()),
                scope='Offline cached-data replot; no OPALX/H5 needed',
                inputs_unchanged=unchanged,identical_pngs=images,
                copied_input_count=len(before),temporary_directory=str(temporary),
                stdout=completed.stdout,stderr=completed.stderr)
    (ROOT/'offline_replot_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result['passed']:raise RuntimeError('Offline replot check failed')

if __name__=='__main__':main()
