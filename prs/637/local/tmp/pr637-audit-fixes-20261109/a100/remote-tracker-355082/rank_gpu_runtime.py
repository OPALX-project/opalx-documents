"""Select one allocated mask token and confirm the executable's CUDA runtime UUID."""
import ctypes
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import uuid

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
linked=subprocess.check_output(['ldd',sys.argv[1]],text=True)
paths=re.findall(r'libcudart\.so[^\s]*\s+=>\s+(\S+)',linked)
assert len(paths)==1,(paths,linked)
runtime_path=Path(paths[0]).resolve()
assert runtime_path.is_file(),str(runtime_path)
runtime=ctypes.CDLL(str(runtime_path))
runtime.cudaGetErrorString.argtypes=[ctypes.c_int]
runtime.cudaGetErrorString.restype=ctypes.c_char_p

def checked(name,*args):
    function=getattr(runtime,name)
    function.restype=ctypes.c_int
    status=function(*args)
    if status:
        error=runtime.cudaGetErrorString(status)
        raise RuntimeError(name+' failed: '+(error.decode() if error else str(status)))

runtime.cudaGetDeviceCount.argtypes=[ctypes.POINTER(ctypes.c_int)]
count=ctypes.c_int()
checked('cudaGetDeviceCount',ctypes.byref(count))
assert count.value==1,(count.value,selected)
class CudaUUID(ctypes.Structure):
    _fields_=[('bytes',ctypes.c_ubyte*16)]
runtime.cudaDeviceGetUuid.argtypes=[ctypes.POINTER(CudaUUID),ctypes.c_int]
physical=CudaUUID()
checked('cudaDeviceGetUuid',ctypes.byref(physical),0)
physical_uuid='GPU-'+str(uuid.UUID(bytes=bytes(physical.bytes)))
runtime.cudaRuntimeGetVersion.argtypes=[ctypes.POINTER(ctypes.c_int)]
version=ctypes.c_int()
checked('cudaRuntimeGetVersion',ctypes.byref(version))
record={'rank':rank,'local_rank':local_rank,'pid':os.getpid(),'host':socket.gethostname(),
        'inherited_cuda_visible_devices':inherited,'selected_cuda_visible_device':selected,
        'gpu_uuid':physical_uuid,'runtime_device_count':count.value,'cuda_runtime_version':version.value,
        'cuda_runtime_library':str(runtime_path),'uuid_api':'cudaDeviceGetUuid(logical device0)',
        'kokkos_logical_device_id':0,'executable':sys.argv[1]}
path=Path(os.environ['AUDIT_GPU_MAP_DIR'],Path(sys.argv[1]).name+'-rank'+str(rank)+'.json')
path.write_text(json.dumps(record,indent=2)+'\n')
print('Confirmed CUDA runtime GPU mapping '+json.dumps(record),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
