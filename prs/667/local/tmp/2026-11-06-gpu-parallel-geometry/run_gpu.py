from pathlib import Path
import subprocess,os,json,time,hashlib,sys,sqlite3
r=Path('/psi/home/adelmann/opalx-dev/dba');s=r/'validation-parallel-geometry-20261106';n=int(sys.argv[1]);assert n in [1,2,3]
for profile in [False,True]:
 for mode in ['before','after']:
  exe=r/'build/gwendolen-cuda/src'/('opalx.pre-parallel-geometry-20261106' if mode=='before' else 'opalx.parallel-geometry-20261106')
  d=s/f'gpu-{n}-{mode}{"-profile" if profile else ""}';d.mkdir(exist_ok=False)
  (d/'case.in').write_text((r/'validation-longitudinal-batch-20261106/gpu-1-after/case.in').read_text())
  args=['mpirun','-np',str(n),'--map-by','slot','--bind-to','none',str(r/'validation-mpi-z-20261106/gpu_rank.sh')]
  if profile:args.append(str(s/'profile_rank.sh'))
  args.extend([str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(r/'validation-a100-20261105/assets/dba-initial-state.h5')])
  t=time.monotonic()
  with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
  (d/'run.json').write_text(json.dumps(dict(command=args,ranks=n,profiled=profile,mode=mode,returncode=rc,wall_seconds=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),source_base_commit='a8ce134afa4e79c97e1611635e029579564ada35'),indent=2));assert rc==0
  if profile:
   summary=[]
   for rep in sorted(d.glob('*.nsys-rep')):
    db=rep.with_suffix('.sqlite')
    with rep.with_suffix('.export.log').open('w') as f:subprocess.run(['nsys','export','--type','sqlite','--force-overwrite=true','--output',str(db),str(rep)],stdout=f,stderr=subprocess.STDOUT,check=True)
    c=sqlite3.connect(db);q="select s.value,count(*),sum(k.end-k.start)/1e6,avg(k.end-k.start)/1e6,min(k.end-k.start)/1e6,max(k.end-k.start)/1e6,min(k.start) from CUPTI_ACTIVITY_KIND_KERNEL k join StringIds s on s.id=k.demangledName where s.value like '%preparePathGeometryAndProjections%' group by s.value"
    rows=sorted(c.execute(q).fetchall(),key=lambda x:x[6]);assert len(rows)==(2 if mode=='before' else 3),rows
    assert all(x[1]==100 for x in rows[:-1]),rows
    assert 100 <= rows[-1][1] <= (200 if n>1 else 100),rows  # MPI refreshes projections after migration.
    summary.append(dict(rank=int(rep.stem.split('rank')[-1]),kernels=[dict(name=x[0],calls=x[1],total_ms=x[2],average_ms=x[3],min_ms=x[4],max_ms=x[5],first_start_ns=x[6]) for x in rows]))
   (d/'geometry-kernels.json').write_text(json.dumps(summary,indent=2)+'\n')
