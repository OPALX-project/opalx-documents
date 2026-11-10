from pathlib import Path
import subprocess,json,sqlite3,time,hashlib,os
r=Path('/psi/home/adelmann/opalx-dev/dba');s=r/'validation-longitudinal-batch-20261106';d=s/'gpu-1-profile';d.mkdir(exist_ok=False);exe=r/'build/gwendolen-cuda/src/opalx';(d/'case.in').write_text((s/'gpu-1-after/case.in').read_text())
args=['mpirun','-np','1','--map-by','slot','--bind-to','none',str(r/'validation-mpi-z-20261106/gpu_rank.sh'),'nsys','profile','--trace=cuda,nvtx','--sample=none','--cpuctxsw=none','--gpu-metrics-devices=none','--force-overwrite=true','--output',str(d/'trace'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'validation-a100-20261105/assets/dba-initial-state.h5')]
t=time.monotonic()
with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
(d/'run.json').write_text(json.dumps(dict(command=args,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()),indent=2));assert rc==0
with (d/'export.log').open('w') as f:subprocess.run(['nsys','export','--type','sqlite','--output',str(d/'trace.sqlite'),str(d/'trace.nsys-rep')],stdout=f,stderr=subprocess.STDOUT,check=True)
c=sqlite3.connect(d/'trace.sqlite');rows=c.execute("select s.value,count(*),sum(k.end-k.start)/1e6 from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName where s.value like '%SliceDensitySumFunctor%' group by s.value").fetchall();assert sum(x[1] for x in rows)==100,rows
(d/'density-launches.json').write_text(json.dumps(dict(density_kernels=rows,total_kernels=c.execute('select count(*) from CUPTI_ACTIVITY_KIND_KERNEL').fetchone()[0]),indent=2))
