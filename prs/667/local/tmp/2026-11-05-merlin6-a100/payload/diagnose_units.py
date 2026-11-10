from pathlib import Path
import subprocess,json,re,os
O=Path(__file__).resolve().parent;B=O.parent/'build/gwendolen-cuda/unit_tests/SpaceCharge/TestFFT2D5Algorithm';D=O/'unit-individual';D.mkdir(exist_ok=True)
listing=subprocess.check_output([str(B),'--gtest_list_tests'],text=True);names=[];suite=None
for line in listing.splitlines():
 if re.match(r'^FFT2D5AlgorithmTest\.',line):suite=line.strip()
 elif suite and line.startswith('  '):names.append(suite+line.strip().split()[0])
assert len(names)==11;rows=[]
for name in names:
 with (D/(name.split('.')[-1]+'.log')).open('w') as f:p=subprocess.run(['srun','--ntasks=1',str(B),'--gtest_filter='+name],stdout=f,stderr=subprocess.STDOUT)
 rows.append(dict(name=name,returncode=p.returncode,slurm_job_id=os.environ['SLURM_JOB_ID']));(O/'unit-individual.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
