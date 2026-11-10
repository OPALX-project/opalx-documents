import json,os,pathlib,socket,subprocess,sys
rank=int(os.environ['OMPI_COMM_WORLD_RANK']);local_rank=int(os.environ['OMPI_COMM_WORLD_LOCAL_RANK'])
inherited=os.environ.get('CUDA_VISIBLE_DEVICES')
if inherited is None:
    raw=subprocess.check_output(['nvidia-smi','--query-gpu=uuid','--format=csv,noheader'],text=True)
    tokens=[line.strip() for line in raw.splitlines() if line.strip()]
    assert len(tokens)==2,'Ambiguous GPU inventory without allocation mask'
else:tokens=[x.strip() for x in inherited.split(',') if x.strip()]
assert local_rank<len(tokens),(local_rank,tokens)
selected=tokens[local_rank]
raw=subprocess.check_output(['nvidia-smi','--id='+selected,'--query-gpu=uuid,pci.bus_id','--format=csv,noheader'],text=True).strip()
assert len(raw.splitlines())==1,raw
uuid,pci=[part.strip() for part in raw.split(',')]
os.environ['CUDA_VISIBLE_DEVICES']=selected;os.environ['KOKKOS_DEVICE_ID']='0';os.environ.pop('KOKKOS_MAP_DEVICE_ID_BY',None)
record={'rank':rank,'local_rank':local_rank,'pid':os.getpid(),'host':socket.gethostname(),'inherited_cuda_visible_devices':inherited,'selected_cuda_visible_device':selected,'gpu_uuid':uuid,'pci_bus_id':pci,'kokkos_logical_device_id':0,'executable':sys.argv[1]}
name=pathlib.Path(sys.argv[1]).name
pathlib.Path(os.environ['AUDIT_GPU_MAP_DIR'],name+'-rank'+str(rank)+'.json').write_text(json.dumps(record,indent=2)+'\n')
print('Explicit rank GPU mapping '+json.dumps(record),flush=True)
os.execv(sys.argv[1],sys.argv[1:])
