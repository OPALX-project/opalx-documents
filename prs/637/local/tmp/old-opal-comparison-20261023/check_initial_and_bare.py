from pathlib import Path
import json,h5py,numpy as np,pandas as pd
root=Path(__file__).resolve().parent;new=root.parent/'ring-space-charge-profiles-20261023/accelerating-pic-8-580'
a=pd.read_csv(new/'bunch.dat',sep=r'\s+',skiprows=1).to_numpy();a[:,0]-=.696695032;a[:,4]+=1.91415387
with h5py.File(root/'smoke/acceleration.h5') as f:
 g=f['Step#0'];ids=g['id'][:];b=np.column_stack([g[n][:] for n in ['x','px','z','pz','y','py']]);b[:,2:4]*=-1
 residual=np.max(abs(b-a[ids]),axis=0)
initial={'common_physical_particle_samples':len(ids),'legacy_id0_not_in_phase_space_dump':True,'maximum_coordinate_residual_m':float(residual[::2].max()),'maximum_momentum_residual':float(residual[1::2].max())}
old=pd.read_csv(root/'old-bare/acceleration-trackOrbit.dat',sep=r'\s+',comment='#',names=['id','x','px','y','py','z','pz']);old=old[old.id=='ID0'].reset_index(drop=True)
dt=6/(50.65e6*720);p=old[['px','py','pz']].to_numpy();old['energy_MeV']=(np.sqrt(1+np.sum(p*p,axis=1))-1)*938.27208816
rows=[]
with h5py.File(new/'acceleration.h5') as f:
 for key,g in f.items():
  t=float(g.attrs['TIME'][0]);step=round(t/dt)
  if abs(step*dt-t)>1e-14:continue # terminal time is localized, not a full timestep
  o=old.iloc[step];r=np.array([o.x,-o.z,o.y]);p=np.array([o.px,-o.pz,o.py]);nr=g.attrs['RefPartR'];np_=g.attrs['RefPartP']
  rows.append({'step':step,'time_s':t,'position_error_m':float(np.linalg.norm(r-nr)),'momentum_error':float(np.linalg.norm(p-np_)),'energy_error_MeV':float(o.energy_MeV-(np.sqrt(1+np.sum(np_**2))-1)*938.27208816)})
df=pd.DataFrame(rows).sort_values('step');df.to_csv(root/'bare-reference-errors.csv',index=False)
report={'initial_samples':initial,'bare_reference_maxima':df[['position_error_m','momentum_error','energy_error_MeV']].abs().max().to_dict(),'matched_snapshot_count':len(df)}
(root/'initial-bare-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
