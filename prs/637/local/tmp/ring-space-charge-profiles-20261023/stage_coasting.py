"""Stage a 10-turn coarse PIC case using maintained fixed samples; does not run it."""
from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parent
source=Path('/Users/adelmann/git/regression-tests-x/RegressionTests/Cyclotron-SC-Midpoint')
target=root/'coasting10';target.mkdir(exist_ok=False)
text=(source/'Cyclotron-SC-Midpoint.in').read_text()
text=text.replace('PSDUMPFREQ=0','PSDUMPFREQ=1000000000').replace('STATDUMPFREQ=1000000000','STATDUMPFREQ=100').replace('ASCIIDUMP=TRUE','ASCIIDUMP=FALSE')
text=text.replace('72 MeV cyclotron: 12-step MIDPOINT space-charge regression','72 MeV cyclotron: ten-turn coarse PIC radial profiles')
text=text.replace('MYCYCL: RING=(', 'RADIAL: PROBE, XSTART=1900, XEND=4700, YSTART=0, YEND=0, STEP=0.1, OUTFN="radial";\nMYCYCL: RING=(RADIAL,')
text=text.replace('TABLEPRINTFREQ=1','TABLEPRINTFREQ=1000').replace('MAXSTEPS=12','MAXSTEPS=20000').replace('SCFIELDUPDATE="MIDPOINT"','SCFIELDUPDATE="MIDPOINT", TURNS=10')
(target/'coasting.in').write_text(text)
for name in ['gauss.dat','bfield.dat']:shutil.copy2(source/name,target/name)
manifest={'source':str(source),'particles':262144,'mesh':[32,32,32],'charge_C':3.9486673247778873e-11,'current_A':.002,'rf_Hz':50.65e6,'turns':10,'dt_s':1.6452780519907864e-10,'solver':'OPEN','greens':'STANDARD','sc_update':'MIDPOINT','hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir()}}
(target/'input-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(target)
