from pathlib import Path
import subprocess,os,json,hashlib
root=Path('/Users/adelmann/git/opalx');r=Path(__file__).resolve().parent;rows=[]
for threads in [1,4]:
 for target in ['UnifiedValidationSpaceChargeConfig','UnifiedValidationFFT2D5Frames','UnifiedValidationFFT2D5Numerics']:
  log=r/f'{target}-omp{threads}.log'
  with log.open('w') as f:p=subprocess.run([str(root/'build-omp'/target)],cwd=r,env=dict(os.environ,OMP_NUM_THREADS=str(threads),OPENBLAS_NUM_THREADS='1'),stdout=f,stderr=subprocess.STDOUT)
  rows.append(dict(target=target,omp_threads=threads,returncode=p.returncode,log=str(log)))
(r/'checks.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2));assert all(x['returncode']==0 for x in rows)
binary=root/'build-omp/src/opalx';srcdiff=subprocess.check_output(['git','diff','HEAD','--','src'],cwd=root)
(r/'source.patch').write_bytes(srcdiff)
meta=dict(branch=subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),binary=str(binary),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),source_patch_sha256=hashlib.sha256(srcdiff).hexdigest(),source_changes='Committed fd6 FFT2D5 frame/Poisson/workspace fixes restored in current branch; no experimental modes.',configuration=str(root/'build-omp/CMakeCache.txt'))
(r/'validated-build.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
