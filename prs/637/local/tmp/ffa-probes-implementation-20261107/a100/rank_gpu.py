"""Bind each school integration rank to one allocated CUDA device and record it."""
import json,os,pathlib,socket,subprocess,sys
rank=int(os.environ['OMPI_COMM_WORLD_RANK'])
local_rank=int(os.environ['OMPI_COMM_WORLD_LOCAL_RANK'])
inherited=os.environ.get('CUDA_VISIBLE_DEVICES')
if inherited is None:
    # A missing mask is usable only when the allocation exposes exactly its
    # requested GPUs; otherwise refuse to choose from unrelated devices.
    query=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True)
    tokens=[line.strip() for line in query.splitlines() if line.strip()]
    assert len(tokens)==2,'Ambiguous allocated GPU inventory without visibility mask'
else:
    tokens=[token.strip() for token in inherited.split(',') if token.strip()]
assert tokens and local_rank<len(tokens),(local_rank,tokens)
selected=tokens[local_rank]
query=subprocess.check_output(['nvidia-smi','--id='+selected,'--query-gpu=uuid,pci.bus_id','--format=csv,noheader'],text=True).strip()
assert len(query.splitlines())==1,query
uuid,pci_bus_id=[part.strip() for part in query.split(',')]
os.environ['CUDA_VISIBLE_DEVICES']=selected
os.environ['KOKKOS_DEVICE_ID']='0'
os.environ.pop('KOKKOS_MAP_DEVICE_ID_BY',None)
record={'rank':rank,'local_rank':local_rank,'pid':os.getpid(),'host':socket.gethostname(),'inherited_cuda_visible_devices':inherited,'selected_cuda_visible_device':selected,'gpu_uuid':uuid,'pci_bus_id':pci_bus_id,'kokkos_logical_device_id':0,'executable':sys.argv[1]}
pathlib.Path('gpu-mapping-rank'+str(rank)+'.json').write_text(json.dumps(record,indent=2)+'\n')
print('Explicit rank GPU mapping '+json.dumps(record),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
