"""Common-time, common-axis energy/rms/normalized-emittance comparison."""
from pathlib import Path
import os,json
import h5py,numpy as np,pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/old-opal-comparison-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent;old=root/'old-full/acceleration.h5';new=root.parent/'ring-space-charge-profiles-20261023/accelerating-pic-8-580/acceleration.h5'
def moments(r,p):
    """Population projected moments, p in beta*gamma; emittance in mm mrad."""
    dr=r-r.mean(axis=0);dp=p-p.mean(axis=0)
    rr=np.mean(dr*dr,axis=0);pp=np.mean(dp*dp,axis=0);rp=np.mean(dr*dp,axis=0)
    return np.sqrt(rr)*1e3,np.sqrt(np.maximum(rr*pp-rp*rp,0))*1e6,float(np.mean(np.sqrt(1+np.sum(p*p,axis=1))-1)*938.27208816)
rows=[];dt=6/(50.65e6*720)
with h5py.File(old) as a,h5py.File(new) as b:
    indices={round(float(g.attrs['TIME'][0])/dt):key for key,g in a.items() if len(g['id'])>1000}
    for key,g in sorted(b.items(),key=lambda item:int(item[0].split('#')[1])):
        t=float(g.attrs['TIME'][0]);step=round(t/dt)
        if step not in indices:continue
        h=a[indices[step]]
        if abs(float(h.attrs['TIME'][0])-t)>1e-14:continue
        ref=g.attrs['RefPartP'];longitudinal=ref/np.linalg.norm(ref)
        vertical=np.array([0.,1.,0.]);vertical-=vertical.dot(longitudinal)*longitudinal;vertical/=np.linalg.norm(vertical)
        radial=np.cross(vertical,longitudinal);basis=np.stack([radial,vertical,longitudinal],axis=1)
        for label,f in [('OPAL 2022.1',h),('OPALX',g)]:
            mask=f['id'][:]!=0
            r=np.column_stack([f[n][:][mask] for n in ['x','y','z']]);p=np.column_stack([f[n][:][mask] for n in ['px','py','pz']])
            if label=='OPAL 2022.1':
                r=r[:,[0,2,1]]*np.array([1,-1,1]);p=p[:,[0,2,1]]*np.array([1,-1,1]);r=r@basis;p=p@basis
            rms,emit,energy=moments(r,p)
            row={'code':label,'time_us':t*1e6,'step_from_time':step,'particles_excluding_id0':len(r),'mean_energy_MeV':energy}
            for i,axis in enumerate('xyz'):row[f'rms_{axis}_mm']=rms[i];row[f'emit_{axis}_mm_mrad']=emit[i]
            rows.append(row)
df=pd.DataFrame(rows);df.to_csv(root/'common-frame-moments.csv',index=False)
colors={'OPAL 2022.1':'#D55E00','OPALX':'#0072B2'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
fig,axes=plt.subplots(4,2,figsize=(11,11),layout='constrained',sharex=True);fig.get_layout_engine().set(rect=(0,.04,1,.96))
for label,color in colors.items():
    d=df[df.code==label];t=d.time_us
    axes[0,0].plot(t,d.mean_energy_MeV,color=color,lw=1.25,label=label)
    axes[0,1].plot(t,d.particles_excluding_id0,color=color,lw=1.25,label=label)
    for i,axis in enumerate('xyz'):
        axes[i+1,0].plot(t,d[f'rms_{axis}_mm'],color=color,lw=1,label=label)
        axes[i+1,1].plot(t,d[f'emit_{axis}_mm_mrad'],color=color,lw=1,label=label)
axes[0,0].set(ylabel='Mean kinetic energy (MeV)',title='Energy');axes[0,0].legend(frameon=False)
axes[0,1].set(ylabel='Particles (ID0 excluded)',title='Population')
for i,(axis,name) in enumerate(zip('xyz',['radial','vertical','longitudinal'])):
    axes[i+1,0].set(ylabel=rf'$\sigma_{axis}$ (mm)',title=f'RMS {axis}: {name}')
    axes[i+1,1].set(ylabel=rf'$\varepsilon_{{n,{axis}}}$ (mm mrad)',title=f'Projected normalized emittance {axis}')
for ax in axes.flat:ax.grid(alpha=.18)
for ax in axes[-1]:ax.set_xlabel('Time (µs)')
fig.suptitle('OPAL 2022.1 vs OPALX · common moving axes · 8³ mesh · 2 mA')
fig.text(.5,.008,'Snapshots every 1,000 steps (164.53 ns); ID0 excluded from both · final localized endpoint omitted to match times',ha='center',fontsize=8)
fig.savefig(root/'energy-rms-emittance.png',dpi=220);fig.savefig(root/'energy-rms-emittance.pdf')
last=df.groupby('code',sort=False).tail(1).copy();last.to_csv(root/'last-common-time-moments.csv',index=False)
report={'snapshot_pairs':len(df)//2,'last_common_time_us':float(df.time_us.max()),'axis_convention':{'x':'radial/transverse','y':'vertical','z':'longitudinal along OPALX reference momentum'},'emittance_definition':'sqrt(var(r)*var(p)-cov(r,p)^2), p=beta*gamma; population moments','source_frames':'Legacy global phase space rotated into OPALX reference axes; OPALX reference-coordinate snapshots used directly','limitations':['Snapshots are 1000 steps apart; fast envelope oscillations are under-sampled.','Last matched time precedes the localized580MeV terminal state; no mismatched endpoint comparison.','Projected emittances depend on the stated shared frame; raw lab-frame legacy stat values are not overlaid.','ID0 exclusion does not undo different reference charge contribution during tracking.'],'last_common_rows':last.to_dict(orient='records')}
(root/'moments-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(last.to_string(index=False));print('pairs',len(df)//2)
