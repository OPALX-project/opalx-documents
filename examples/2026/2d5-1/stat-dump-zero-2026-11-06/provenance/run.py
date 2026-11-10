from pathlib import Path
import os,subprocess,time,json,hashlib,sqlite3
r=Path('/psi/home/adelmann/opalx-dev/dba');s=r/'validation-stat0-20261106';exe=r/'build/gwendolen-cuda/src/opalx.parallel-geometry-20261106'
assert hashlib.sha256(exe.read_bytes()).hexdigest()=='981ce971edc5485c78f48525e517d8242ddbfd456e8e18ea5cf5f51ca1126c43'
original=(r/'validation-parallel-geometry-20261106/gpu-1-after/case.in').read_text();assert original.count('STATDUMPFREQ=10')==1
for frequency,profile in [(10,False),(0,False),(0,True)]:
 d=s/f'stat{frequency}{"-profile" if profile else ""}';d.mkdir(exist_ok=False)
 (d/'case.in').write_text(original.replace('STATDUMPFREQ=10',f'STATDUMPFREQ={frequency}'))
 args=['mpirun','-np','1','--map-by','slot','--bind-to','none',str(r/'validation-mpi-z-20261106/gpu_rank.sh')]
 if profile:args.append(str(r/'validation-parallel-geometry-20261106/profile_rank.sh'))
 args.extend([str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'validation-a100-20261105/assets/dba-initial-state.h5')])
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,stat_dump_frequency=frequency,profiled=profile,ranks=1,returncode=rc,wall_seconds=time.monotonic()-t,binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),job=os.environ['SLURM_JOB_ID']),indent=2)+'\n');assert rc==0
 if profile:
  with (d/'export.log').open('w') as f:subprocess.run(['nsys','export','--type','sqlite','--force-overwrite=true','--output',str(d/'trace-rank0.sqlite'),str(d/'trace-rank0.nsys-rep')],stdout=f,stderr=subprocess.STDOUT,check=True)
