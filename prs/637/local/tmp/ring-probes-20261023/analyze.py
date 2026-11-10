"""Verify and plot the PSI Ring PROBE demonstration; run with ~/.venv-h6/bin/python."""
from pathlib import Path
from io import StringIO
import json,os,re
import numpy as np
import pandas as pd
import h5py
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-ring-probe-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
root=Path(__file__).resolve().parent

def stat_frame(path):
    h,b=re.split(r'&data\b.*?&end',path.read_text(),maxsplit=1,flags=re.S)
    names=[re.search(r'\bname\s*=\s*([^,\s]+)',c).group(1) for c in re.findall(r'&column\b(.*?)&end',h,re.S)]
    lines=[line for line in b.splitlines() if line.strip() and not line.lstrip().startswith('!')]
    return pd.read_csv(StringIO('\n'.join(lines[len(re.findall('&parameter',h)):])),sep=r'\s+',names=names)

def probe_frame(path):
    if not path.exists():return pd.DataFrame()
    with h5py.File(path) as file:
        parts=[pd.DataFrame({name:group[name][:] for name in ['id','turn','bunchNumber','time','x','y','z','px','py','pz','q','m']})
               for key,group in file.items() if key.startswith('Step#')]
    df=pd.concat(parts,ignore_index=True).sort_values('time').reset_index(drop=True)
    df['radius_mm']=1000*np.hypot(df.x,df.z)
    df['energy_MeV']=(np.sqrt(1+df.px**2+df.py**2+df.pz**2)-1)*df.m*1000
    return df

summary={'runs':{},'limitations':['Single proton; no space charge; one MPI rank and one OpenMP thread.',
    'Existing SINGLEGAP map/transport model retained; not a new machine calibration.',
    'The long coasting case exhibits a pre-existing large particle/reference separation; controls reproduce it exactly.']}
all_hits={}
for case,base in [('coasting-10turns','coasting'),('acceleration-590MeV','acceleration')]:
    run=root/case;control=root/(case+'-control')
    stat=stat_frame(run/(base+'.stat'));offstat=stat_frame(control/(base+'.stat'))
    np.testing.assert_array_equal(stat.to_numpy(),offstat.to_numpy())
    stat.to_csv(run/'statistics.csv',index=False)
    columns=[c for c in ['mean_x','mean_y','mean_s'] if c in stat]
    offset=np.linalg.norm(stat[columns].to_numpy(),axis=1)
    entry={'final_energy_MeV':float(stat.energy.iloc[-1]),'final_time_us':float(stat.t.iloc[-1]/1000),
           'final_path_m':float(stat.s.iloc[-1]),'statistics_records':len(stat),'probes':{}}
    with h5py.File(run/(base+'.h5')) as on,h5py.File(control/(base+'.h5')) as off:
        keys=sorted(on,key=lambda key:int(key.split('#')[1]));assert keys==sorted(off,key=lambda key:int(key.split('#')[1]))
        for key in keys:
            for name in ['id','x','y','z','px','py','pz']:
                np.testing.assert_array_equal(on[key][name][:],off[key][name][:])
            for name in ['TIME','SPOS','GlobalTrackStep','RefPartR','RefPartP']:
                np.testing.assert_array_equal(on[key].attrs[name],off[key].attrs[name])
        entry['phase_space_records_compared']=len(keys)
        entry['accepted_steps']=int(on[keys[-1]].attrs['GlobalTrackStep'][0])
        entry['final_particle_reference_offset_m']=float(np.linalg.norm([on[keys[-1]][n][0] for n in ['x','y','z']]))
    entry['all_saved_transport_and_statistics_identical_to_probe_off']=True
    for name in ['radial0','radial90','extraction']:
        df=probe_frame(run/(name+'.h5'));all_hits[(case,name)]=df
        hist=np.loadtxt(run/(name+'.hist'))
        peaks=np.array([float(x) for x in (run/(name+'.peaks')).read_text().splitlines() if x and not x.startswith('#')])
        assert hist.sum()==len(df)
        if df.empty:
            assert len(peaks)==0
            entry['probes'][name]={'hits':0};continue
        np.testing.assert_allclose(peaks,df.groupby('turn').radius_mm.mean().to_numpy(),rtol=1e-14,atol=1e-10)
        assert np.all(np.diff(df.time)>0)
        if name=='radial0': assert abs(df.z).max()<1e-12
        if name=='radial90':assert abs(df.x).max()<1e-12
        if name=='extraction':
            start=np.array([4.16616,-1.22685]);end=np.array([4.25,-1.2413]);d=end-start
            offset2=df[['x','z']].to_numpy()-start
            frac=(offset2@d)/(d@d);assert np.all((frac>=0)&(frac<=1))
            distance=abs(offset2[:,0]*d[1]-offset2[:,1]*d[0])/np.linalg.norm(d)
            assert distance.max()<1e-12
            entry['extraction_max_plane_residual_m']=float(distance.max())
        df.to_csv(run/(name+'-hits.csv'),index=False)
        entry['probes'][name]={'hits':len(df),'first_reference_turn':int(df.turn.min()),'last_reference_turn':int(df.turn.max()),
            'min_radius_mm':float(df.radius_mm.min()),'max_radius_mm':float(df.radius_mm.max()),
            'min_energy_MeV':float(df.energy_MeV.min()),'max_energy_MeV':float(df.energy_MeV.max())}
    log=(run/'run.log').read_text()
    if case.startswith('acceleration'):
        assert 'EKINSTOP reached after complete gap kick' in log
        assert 590<=entry['final_energy_MeV']<592
    else:assert 'completed directed turn 10' in log
    summary['runs'][case]=entry
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.labelsize':10,'axes.titlesize':11,
    'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':220,'pdf.fonttype':42})
colors={'radial0':'#0072B2','radial90':'#009E73','extraction':'#D55E00'}
fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
run=root/'acceleration-590MeV';stat=stat_frame(run/'acceleration.stat')
ax=axes[0,0]
ax.scatter(stat.ref_x,stat.ref_z,s=3,color='#bbbbbb',alpha=.6,label='Reference samples',rasterized=True)
for name,coords in [('radial0',([1.9,4.7],[0,0])),('radial90',([0,0],[1.9,4.7])),('extraction',([4.16616,4.25],[-1.22685,-1.2413]))]:
    df=all_hits[('acceleration-590MeV',name)]
    ax.plot(*coords,color=colors[name],lw=1.3)
    ax.scatter(df.x,df.z,s=8 if name!='extraction' else 30,color=colors[name],label=name,marker='o' if name!='extraction' else 'D')
ax.set(xlabel='Laboratory X [m]',ylabel='Laboratory Z [m]',title='(a) PSI Ring and probe crossings',aspect='equal',xlim=(-5,5),ylim=(-5,5))
ax.legend(loc='lower left',frameon=False,fontsize=8,ncol=2);ax.grid(alpha=.15)
ax=axes[0,1]
for name in ['radial0','radial90']:
    df=all_hits[('acceleration-590MeV',name)]
    ax.plot(df.turn,df.radius_mm,lw=1.2,color=colors[name],label=name)
df=all_hits[('acceleration-590MeV','extraction')]
ax.scatter(df.turn,df.radius_mm,color=colors['extraction'],marker='D',s=28,zorder=5,label='extraction')
ax.set(xlabel='Reference turn (zero-based)',ylabel='Crossing radius [mm]',title='(b) Radial scan: 189 crossings per radial probe')
ax.legend(frameon=False);ax.grid(alpha=.18)
ax=axes[1,0]
hist=np.loadtxt(run/'extraction.hist');first=(run/'extraction.hist').read_text().splitlines()[0]
info=first.split(') ')[1].split();minimum=float(info[0]);width=float(info[-2]);centers=minimum+(np.arange(len(hist))+.5)*width
ax.bar(centers,hist,width=.85*width,color=colors['extraction'],alpha=.85)
for row in df.itertuples():ax.annotate(f'turn {row.turn}',(row.radius_mm,1),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
ax.set(xlabel='Crossing radius [mm]',ylabel='Crossings per 1 mm bin',title='(c) Old manual extraction probe: final three turns',ylim=(0,1.35),xlim=(4338,4367))
ax.yaxis.set_major_locator(MaxNLocator(integer=True));ax.grid(axis='y',alpha=.18)
ax=axes[1,1]
ax.plot(stat.t/1000,stat.energy,color='#333333',lw=1.4)
ax.axhline(590,color=colors['extraction'],ls='--',lw=.9,label='590 MeV target')
ax.plot(stat.t.iloc[-1]/1000,stat.energy.iloc[-1],'o',ms=4,color=colors['extraction'])
ax.set(xlabel='Time [µs]',ylabel='Kinetic energy [MeV]',title=f'(d) Full RF acceleration: {stat.energy.iloc[-1]:.4f} MeV')
ax.legend(frameon=False);ax.grid(alpha=.18)
fig.suptitle('PSI Ring cyclotron · one proton · no space charge',fontsize=14)
fig.savefig(root/'ring-probes.png');fig.savefig(root/'ring-probes.pdf');plt.close(fig)
coast=stat_frame(root/'coasting-10turns/coasting.stat')
fig,ax=plt.subplots(figsize=(7,3.8),layout='constrained')
offset=np.linalg.norm(coast[['mean_x','mean_y','mean_s']].to_numpy(),axis=1)
ax.semilogy(coast.t/1000,np.maximum(offset,1e-16),color='#D55E00',lw=1.4)
ax.set(xlabel='Time [µs]',ylabel='Particle/reference separation [m]',title='Coasting anomaly reproduced identically with probes OFF')
ax.grid(alpha=.2);fig.savefig(root/'coasting-anomaly.png');plt.close(fig)
print(json.dumps(summary,indent=2))
