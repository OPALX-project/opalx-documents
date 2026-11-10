"""Compare native radial probes on common turns/time/charge units; no area normalization."""
from pathlib import Path
import os,json
import h5py,numpy as np,pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/old-opal-comparison-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
root=Path(__file__).resolve().parent;new=root.parent/'ring-space-charge-profiles-20261023/accelerating-pic-8-580';old=root/'old-full'
assert json.loads((old/'launch.json').read_text())['returncode']==0
trace=pd.read_csv(old/'acceleration-trackOrbit.dat',sep=r'\s+',comment='#',names=['id','x','px','y','py','z','pz']);trace=trace[trace.id=='ID0'].reset_index(drop=True)
p=trace[['px','py','pz']].to_numpy();trace['energy_MeV']=(np.sqrt(1+(p*p).sum(axis=1))-1)*938.27208816
step=int(np.flatnonzero(trace.energy_MeV.to_numpy()>=580)[0]);old_stop=step*6/(50.65e6*720)
frames={};residuals={};raw_counts={}
for label,path in [('OPAL 2022.1',old),('OPALX',new)]:
 parts=[]
 with h5py.File(path/'radial.h5') as f:
  for key,g in f.items():
   if key.startswith('Step#'):parts.append(pd.DataFrame({n:g[n][:] for n in ['id','turn','time','x','y','z','q']}))
 df=pd.concat(parts,ignore_index=True);raw_counts[label]=len(df)
 if label=='OPAL 2022.1':
  df['turn']-=1;df=df[df.time<=old_stop].copy();df['radius_mm']=np.hypot(df.x,df.y)*1000;residuals[label]=float(abs(df.y).max())
 else:df['radius_mm']=np.hypot(df.x,df.z)*1000;residuals[label]=float(abs(df.z).max())
 df=df[df.turn.between(178,185)&(df.id!=0)].copy()
 assert not df.duplicated(['id','turn']).any(),label
 np.testing.assert_allclose(df.q,3.9486673247778873e-11/4096,rtol=1e-10,atol=0)
 frames[label]=df
rows=[]
for label,df in frames.items():
 for turn,g in df.groupby('turn'):
  r=g.radius_mm.to_numpy();rows.append({'code':label,'turn_zero_based':int(turn),'particles':len(g),'charge_pC':float(g.q.sum()*1e12),'mean_radius_mm':float(r.mean()),'rms_radius_mm':float(r.std()),'min_radius_mm':float(r.min()),'max_radius_mm':float(r.max())})
summary=pd.DataFrame(rows);summary.to_csv(root/'turn-comparison.csv',index=False)
pivot=summary.pivot(index='turn_zero_based',columns='code');delta=pd.DataFrame({'turn':pivot.index,'old_minus_new_mean_radius_mm':pivot.mean_radius_mm['OPAL 2022.1']-pivot.mean_radius_mm.OPALX,'old_over_new_rms':pivot.rms_radius_mm['OPAL 2022.1']/pivot.rms_radius_mm.OPALX,'old_particles':pivot.particles['OPAL 2022.1'],'new_particles':pivot.particles.OPALX});delta.to_csv(root/'differences.csv',index=False)
lo=np.floor(min(d.radius_mm.min() for d in frames.values())*10)/10;hi=np.ceil(max(d.radius_mm.max() for d in frames.values())*10)/10
edges=np.arange(lo,hi+.100001,.1);centres=.5*(edges[:-1]+edges[1:]);densities=pd.DataFrame({'radius_mm':centres})
for label,df in frames.items():
 densities[label]=np.histogram(df.radius_mm,bins=edges,weights=df.q*1e12)[0]/np.diff(edges)
 assert abs(np.sum(densities[label]*np.diff(edges))-df.q.sum()*1e12)<1e-8
# Shared bin charge-density L1 difference, divided by the mean total charge.
a=densities['OPAL 2022.1'].to_numpy();b=densities.OPALX.to_numpy();l1=float(np.sum(abs(a-b)*np.diff(edges))/(.5*np.sum((a+b)*np.diff(edges))))
densities.to_csv(root/'summed-line-densities.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
colors={'OPAL 2022.1':'#D55E00','OPALX':'#0072B2'}
fig,axes=plt.subplots(2,1,figsize=(10,8),layout='constrained',gridspec_kw={'height_ratios':[1.5,1]});fig.get_layout_engine().set(rect=(0,.04,1,.96))
for label in frames:
 y=densities[label];axes[0].plot(centres,np.where(y>0,y,np.nan),color=colors[label],lw=1.3,label=label)
axes[0].set(yscale='log',xlabel='Radius (mm)',ylabel='Summed radial density (pC/mm)',title='Final eight complete passages: turns 178–185 (zero-based)');axes[0].legend(frameon=False);axes[0].grid(alpha=.18)
for label in frames:
 d=summary[summary.code==label];axes[1].errorbar(d.turn_zero_based,d.mean_radius_mm,yerr=d.rms_radius_mm,fmt='o-',ms=4,capsize=3,color=colors[label],label=label)
axes[1].set(xlabel='Turn (zero-based)',ylabel='Mean radius ± rms (mm)');axes[1].set_xticks(range(178,186));axes[1].grid(alpha=.18)
fig.suptitle('OPAL 2022.1 LF2 vs OPALX Boris/PIC · 8³ mesh · 2 mA launch')
fig.text(.5,.008,'Same 4,095 non-reference samples; ID0 excluded from both curves · common 0.1 mm bins · no area normalization',ha='center',fontsize=8)
fig.savefig(root/'comparison.png',dpi=220);fig.savefig(root/'comparison.pdf');plt.close(fig)
fig,axes=plt.subplots(4,2,figsize=(11,11),layout='constrained');fig.get_layout_engine().set(rect=(0,.03,1,.97))
for turn,ax in zip(range(178,186),axes.flat):
 selected={label:d[d.turn==turn] for label,d in frames.items()};lo=min(d.radius_mm.min() for d in selected.values())-1;hi=max(d.radius_mm.max() for d in selected.values())+1;e=np.arange(np.floor(lo*10)/10,np.ceil(hi*10)/10+.10001,.1);x=.5*(e[:-1]+e[1:])
 for label,d in selected.items():
  y=np.histogram(d.radius_mm,bins=e,weights=d.q*1e12)[0]/np.diff(e);ax.plot(x,np.where(y>0,y,np.nan),lw=1,color=colors[label],label=label)
 ax.set(yscale='log',title=f'Turn {turn}',xlabel='Radius (mm)',ylabel='pC/mm');ax.xaxis.set_major_locator(MaxNLocator(4));ax.grid(alpha=.15)
axes[0,0].legend(frameon=False,fontsize=8);fig.suptitle('Individual final-turn radial density profiles · 580 MeV window');fig.savefig(root/'per-turn-comparison.png',dpi=220);fig.savefig(root/'per-turn-comparison.pdf');plt.close(fig)
report={'old_run':json.loads((old/'launch.json').read_text()),'old_580_reference_crossing':{'step':step,'time_s':old_stop,'energy_MeV':float(trace.energy_MeV.iloc[step])},'turns_zero_based':list(range(178,186)),'shared_particle_ids_exclude':[0],'counts_by_turn':summary.to_dict(orient='records'),'difference_metrics':{'maximum_absolute_mean_radius_difference_mm':float(abs(delta.old_minus_new_mean_radius_mm).max()),'minimum_old_over_new_rms':float(delta.old_over_new_rms.min()),'maximum_old_over_new_rms':float(delta.old_over_new_rms.max()),'summed_density_L1_over_mean_charge':l1},'probe_plane_maximum_residual_m':residuals,'initial_and_bare':json.loads((root/'initial-bare-summary.json').read_text()),'limitations':['Native LF2 and Boris/PIC stepping and space-charge ordering are not identical.','OPALX uses the explicit MIDPOINT split and one GAMMAZ bin; legacy uses its native cyclotron FFT self-field path.','Legacy forces reference ID0; OPALX original ID0 was a sampled particle. Excluding ID0 from profiles does not undo its small self-field contribution difference.','Legacy deletion criteria/cadence have not been matched to OPALX default 10-sigma removal; the observed loss difference cannot be assigned uniquely to the self-field solver.','Legacy probe plane interpolation differs; residuals are measured, not assumed zero.','Old run completed a bounded140000steps; data beyond first580MeV reference crossing are excluded offline.','Very coarse8³ mesh/4096samples; these are reproducibility diagnostics, not converged machine predictions.','Both track one bunch, with no neighbouring-turn self fields.']}
(root/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['difference_metrics'],indent=2));print(delta.to_string(index=False))
