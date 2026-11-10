from pathlib import Path
import os,subprocess,json,time,hashlib
root=Path('/psi/home/adelmann/opalx-dev/dba');study=root/'validation-row-profile-20261106';exe=root/'build/gwendolen-cuda/src/opalx'
for name,pattern,count,skip in [('line-density','regex:.*SliceDensitySumFunctor.*',1,10),('geometry','regex:.*preparePathGeometryAndProjections.*',2,20)]:
 d=study/f'ncu-{name}';d.mkdir(exist_ok=False);(d/'case.in').write_text((root/'validation-r2c-rows-20261106/gpu-1-rows/case.in').read_text())
 args=['mpirun','-np','1','--map-by','slot','--bind-to','none',str(root/'validation-mpi-z-20261106/gpu_rank.sh'),'ncu','--section','SpeedOfLight','--section','Occupancy','--section','MemoryWorkloadAnalysis','--kernel-name-base','demangled','--kernel-name',pattern,'--launch-skip',str(skip),'--launch-count',str(count),'--replay-mode','kernel','--force-overwrite','--export',str(d/'kernel'),'--csv','--log-file',str(d/'metrics.csv'),str(exe),'case.in','--info','1','--2D5BatchSize','64','--restart',str(root/'validation-a100-20261105/assets/dba-initial-state.h5')]
 t=time.monotonic()
 with (d/'case.out').open('w') as f:rc=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT).returncode
 (d/'run.json').write_text(json.dumps(dict(command=args,returncode=rc,elapsed_s=time.monotonic()-t,job=os.environ['SLURM_JOB_ID'],binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()),indent=2))
 if rc: print('NCU FAILED',name,rc,flush=True)
