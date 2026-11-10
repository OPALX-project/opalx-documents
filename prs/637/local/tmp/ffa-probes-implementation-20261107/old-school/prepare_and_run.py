"""Reproducible old-OPAL probe integration baselines; not a native unit test."""
from pathlib import Path
import argparse, hashlib, json, math, os, re, subprocess, time
HERE=Path(__file__).resolve().parent
SCHOOL=Path('/Users/adelmann/git/FFA25-school')
EXE=Path('/Users/adelmann/OPAL-2022.1/bin/opal')
CASES={
 '16-cell':dict(source='legacy-16-cell.in',radius=4.4,energy=12.,stations=16,spiral=3.142/4),
 '55deg-d-off':dict(source='legacy-16-cell.in',radius=4.163263702279026,energy=12.,stations=16,spiral=math.radians(55.)),
 'fourfold':dict(source='legacy-fourfold.in',radius=4.,energy=3.,stations=4,spiral=math.pi/6),
}

def run(key,steps=10000,scale=1.,radius=None,pr=0.,vertical=0.,pydelta=0.,hdf5=False,label=None):
 case=CASES[key]; radius=case['radius'] if radius is None else radius
 name=key+f'-steps{steps}-scale{scale:g}'+('-'+label if label else '')
 path=HERE/name; path.mkdir(exist_ok=False)
 source=SCHOOL/'migration-audit'/case['source']
 text=source.read_text()
 if hdf5: text='OPTION, PSDUMPFRAME=GLOBAL;\n'+text.replace('ENABLEHDF5=FALSE','ENABLEHDF5=TRUE')
 text,count=re.subn(r'REAL SPIRAL_ANGLE=[^;]+;',f"REAL SPIRAL_ANGLE={case['spiral']:.17g};",text)
 assert count==1
 if key=='55deg-d-off':
  text,count=re.subn(r'REAL BD=[^;]+;','REAL BD=0;',text); assert count==1
 text,count=re.subn(r'MAXSTEPS=5000\*NUM_TURNS',f'MAXSTEPS={steps}',text); assert count==1
 text,count=re.subn(r'REAL STEP_SIZE=0\.01;',f'REAL STEP_SIZE={0.01*scale:.17g};',text); assert count==1
 # Explicitly preserve no-SC original and the original physical probe list.
 (path/'school.in').write_text(text)
 (path/'dist.dat').write_text(f'1\n{radius:.17g} {pr:.17g} 0 {pydelta:.17g} {vertical:.17g} 0\n')
 mass=938.272
 input_p=math.sqrt(case['energy']*(case['energy']+2*mass))
 physical_mass=938.27208816
 bg=input_p/physical_mass
 tangent=bg+pydelta
 actual=physical_mass*(math.sqrt(1+tangent*tangent+pr*pr)-1)
 nominal_bg=input_p/mass
 raw_steps_per_RF=1000/((0.01*scale)/(.3*nominal_bg/math.sqrt(1+nominal_bg*nominal_bg)))
 integer_steps_per_RF=int(raw_steps_per_RF)
 info=dict(case=key,source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
   original_notebook_spiral=case['spiral'],steps=steps,step_size_m=0.01*scale,
   nominal_energy_MeV=case['energy'],actual_energy_MeV=actual,input_mass_MeV=mass,physical_mass_MeV=physical_mass,integer_steps_per_RF=integer_steps_per_RF,raw_steps_per_RF=raw_steps_per_RF,
   initial_old_x_y_z_px_py_pz=[radius,0.,vertical,pr,tangent,0.],
   dt_s=1e-6/integer_steps_per_RF,legacy_turn_period_s=1e-6,
   stations=case['stations'],NPART=1,space_charge='NONE',
   binary=str(EXE),binary_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),
   input_sha256=hashlib.sha256(text.encode()).hexdigest(),distribution_sha256=hashlib.sha256((path/'dist.dat').read_bytes()).hexdigest(),start_unix=time.time())
 command=['/bin/bash','-c','source /Users/adelmann/OPAL-2022.1/etc/profile.d/opal.sh && exec /Users/adelmann/OPAL-2022.1/bin/opal school.in']
 info['command']=command
 with (path/'run.log').open('w') as log:
  process=subprocess.Popen(command,cwd=path,env=dict(os.environ,OMP_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT)
  info['pid']=process.pid; (path/'launch.json').write_text(json.dumps(info,indent=2)+'\n')
  info['returncode']=process.wait()
 info['elapsed_s']=time.time()-info['start_unix']
 info['probe_files']=[p.name for p in sorted(path.glob('*.loss'))]
 info['probe_rows']={p.name:sum(1 for line in p.read_text().splitlines() if line.strip() and not line.startswith('#')) for p in path.glob('*.loss')}
 (path/'launch.json').write_text(json.dumps(info,indent=2)+'\n')
 print(json.dumps(info,indent=2),flush=True)
 return info['returncode']

if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('case',choices=CASES); parser.add_argument('--steps',type=int,default=10000); parser.add_argument('--scale',type=float,default=1.); parser.add_argument('--radius',type=float); parser.add_argument('--pr',type=float,default=0.); parser.add_argument('--vertical',type=float,default=0.); parser.add_argument('--pydelta',type=float,default=0.); parser.add_argument('--hdf5',action='store_true'); parser.add_argument('--label')
 args=parser.parse_args(); raise SystemExit(run(args.case,args.steps,args.scale,args.radius,args.pr,args.vertical,args.pydelta,args.hdf5,args.label))
