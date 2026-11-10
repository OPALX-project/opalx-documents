"""Job-only mask selector using a typed CUDA-runtime metadata child probe."""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys

rank=int(os.environ['OMPI_COMM_WORLD_RANK'])
local_rank=int(os.environ['OMPI_COMM_WORLD_LOCAL_RANK'])
inherited=os.environ.get('CUDA_VISIBLE_DEVICES')
assert inherited is not None,'Allocation must provide CUDA_VISIBLE_DEVICES'
tokens=[part.strip() for part in inherited.split(',') if part.strip()]
assert local_rank<len(tokens),(local_rank,tokens)
selected=tokens[local_rank]
os.environ['CUDA_VISIBLE_DEVICES']=selected
os.environ['KOKKOS_DEVICE_ID']='0'
os.environ.pop('KOKKOS_MAP_DEVICE_ID_BY',None)
probe=Path(__file__).with_name('cuda_metadata_attempt2')
def runtime_path(binary):
    linked=subprocess.check_output(['ldd',str(binary)],text=True)
    paths=re.findall(r'libcudart\.so[^\s]*\s+=>\s+(\S+)',linked)
    assert len(paths)==1,(paths,linked)
    path=Path(paths[0]).resolve()
    assert path.is_file(),str(path)
    return path
opal_runtime=runtime_path(sys.argv[1]);probe_runtime=runtime_path(probe)
assert opal_runtime==probe_runtime,(str(opal_runtime),str(probe_runtime))
result=subprocess.run([str(probe)],text=True,capture_output=True,check=False)
if result.returncode:
    raise RuntimeError('CUDA metadata probe failed: '+result.stdout+result.stderr)
metadata=json.loads(result.stdout)
assert metadata['runtime_device_count']==1,metadata
assert metadata['cuda_runtime_version']==metadata['compiled_cudart_version'],metadata
assert re.fullmatch(r'GPU-[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',metadata['gpu_uuid']),metadata
record={'rank':rank,'local_rank':local_rank,'pid':os.getpid(),'host':socket.gethostname(),
        'inherited_cuda_visible_devices':inherited,'selected_cuda_visible_device':selected,
        'cuda_runtime_library':str(opal_runtime),'probe_cuda_runtime_library':str(probe_runtime),
        'uuid_api':'cudaGetDeviceProperties(logical0).uuid, compiled against installed headers',
        'probe_binary_sha256':hashlib.sha256(probe.read_bytes()).hexdigest(),
        'kokkos_logical_device_id':0,'executable':sys.argv[1],**metadata}
path=Path(os.environ['AUDIT_GPU_MAP_DIR'],Path(sys.argv[1]).name+'-rank'+str(rank)+'.json')
path.write_text(json.dumps(record,indent=2)+'\n')
print('Confirmed CUDA runtime GPU mapping '+json.dumps(record),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
