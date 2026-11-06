"""Summarize Nsight Systems CUDA evidence without treating API waits as CPU work."""
from pathlib import Path
import json
import pandas as pd
p=Path(__file__).resolve().parent/'gpu-proof'
k=pd.read_csv(p/'stats_cuda_gpu_kern_sum.csv')
t='Total Time (ns)';n='Instances';name='Name'
# Preserve all rows; classification is an aid to reading the raw trace summaries.
def group(s):
 s=str(s).lower()
 if 'heffte::cuda::' in s:return 'heFFTe CUDA rearrangement/scaling'
 if any(x in s for x in ['cufft','vector_fft','regular_fft','bluestein']):return 'cuFFT'
 if 'ippl::fft::' in s:return 'IPPL FFT device copies'
 if 'fft2d5' in s or any(x in s for x in ['scattertogridfunctor','gatherfromgridfunctor','poissoncouplingfunctor','copyslicefieldfunctor']):return 'FFT2D5 Kokkos kernels'
 return 'Other CUDA kernels'
k['category']=k[name].map(group)
k.to_csv(p/'kernels-classified.csv',index=False)
g=k.groupby('category').agg(total_ns=(t,'sum'),launches=(n,'sum'))
g['gpu_kernel_time_percent']=100*g.total_ns/k[t].sum()
print(g.to_string())
print('\nTop CUDA kernels:')
print(k.head(20).to_string(index=False))
print('\nCUDA API:')
a=pd.read_csv(p/'stats_cuda_api_sum.csv');print(a.head(15).to_string(index=False))
(p/'summary.json').write_text(json.dumps({'kernel_launches':int(k[n].sum()),'summed_kernel_time_s':float(k[t].sum()/1e9),'categories':g.reset_index().to_dict('records')},indent=2)+'\n')
