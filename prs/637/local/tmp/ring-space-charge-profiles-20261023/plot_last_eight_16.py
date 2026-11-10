"""Plot completed accelerating PIC probe data. No smoothing or inset."""
from pathlib import Path
import json,os
import h5py,numpy as np,pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-extraction-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent;root=Path(__file__).resolve().parent/'profiles-16';root.mkdir(exist_ok=True)
run=root.parent/'accelerating-pic-16'
record=json.loads((run/'launch.json').read_text())
assert record.get('returncode')==0,'Run is incomplete or failed'
assert 'EKINSTOP reached after complete gap kick' in (run/'run.log').read_text(),'Energy target not reached'
parts=[]
with h5py.File(run/'radial.h5') as f:
 for key,g in f.items():
  if not key.startswith('Step#'):continue
  parts.append(pd.DataFrame({n:g[n][:] for n in ['id','turn','time','x','y','z','q']}))
data=pd.concat(parts,ignore_index=True);data['radius_mm']=np.hypot(data.x,data.z)*1000
turns=sorted(data.turn.unique())[-8:];assert len(turns)==8
selected=data[data.turn.isin(turns)].copy()
assert np.abs(selected.z).max()<1e-11
assert not selected.duplicated(['id','turn']).any(),'More than one passage per particle/turn'
summary=selected.groupby('turn').agg(particles=('id','size'),charge_C=('q','sum'),mean_radius_mm=('radius_mm','mean'),minimum_radius_mm=('radius_mm','min'),maximum_radius_mm=('radius_mm','max'),first_time_s=('time','min'),last_time_s=('time','max'))
# Report partial coverage explicitly rather than silently normalizing it away.
summary['fraction_of_launch']=summary.particles/32768
summary.to_csv(root/'last-eight-turns.csv')
assert (summary.particles==32768).all(), 'Partial probe coverage: inspect last-eight-turns.csv before plotting'
np.testing.assert_allclose(summary.charge_C,3.9486673247778873e-11,rtol=1e-10,atol=0)
lo=np.floor(selected.radius_mm.min()*10)/10;hi=np.ceil(selected.radius_mm.max()*10)/10
edges=np.arange(lo,hi+.100001,.1);centres=(edges[1:]+edges[:-1])/2
profiles=pd.DataFrame({'radius_mm':centres})
for turn in turns:
 df=selected[selected.turn==turn]
 profiles[f'turn_{turn}_pC_per_mm']=np.histogram(df.radius_mm,bins=edges,weights=np.abs(df.q)*1e12)[0]/np.diff(edges)
profiles['sum_pC_per_mm']=profiles.iloc[:,1:].sum(axis=1)
profiles.to_csv(root/'line-density.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':True,'axes.spines.right':True,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(11,5.7),layout='constrained')
colors=plt.get_cmap('tab10').colors
for i,turn in enumerate(turns):
 y=profiles[f'turn_{turn}_pC_per_mm'];ax.plot(centres,np.where(y>0,y,np.nan),lw=1.1,color=colors[i],label=f'Turn {turn}')
ax.plot(centres,np.where(profiles.sum_pC_per_mm>0,profiles.sum_pC_per_mm,np.nan),color='black',lw=1.5,label='Sum of final 8 turns')
ax.set(yscale='log',xlabel=r'$r$ (mm)',ylabel=r'Radial line density (pC/mm)',title='PSI Ring · 2 mA · final eight probe passages')
ax.set_ylim(bottom=max(1e-6,profiles.sum_pC_per_mm.max()*1e-5));ax.grid(alpha=.18,which='major')
ax.legend(frameon=False,ncol=3,fontsize=9)
fig.text(.5,.005,'16³ mesh · 32,768 macroparticles · coarse PIC · no vertical RF focusing',ha='center',fontsize=9)
fig.savefig(root/'last-eight-turns.png',dpi=240);fig.savefig(root/'last-eight-turns.pdf')
with h5py.File(run/'acceleration.h5') as f:
 g=f[max(f,key=lambda k:int(k.split('#')[1]))]
 final={'particles':len(g['id']),'time_s':float(np.asarray(g.attrs['TIME']).ravel()[0]),'steps':int(np.asarray(g.attrs['GlobalTrackStep']).ravel()[0])}
report={'turns_zero_based':[int(t) for t in turns],'bin_width_mm':.1,'final':final,'per_turn':summary.reset_index().to_dict(orient='records'),'all_eight_full_particle_count':bool((summary.particles==32768).all()),'launch':record,'limitations':['Coarse mesh/particles/timestep; not a converged extraction-density prediction.','Single transported bunch; repeated-turn probe sum does not include inter-turn neighbouring-bunch space charge.','Initial Gaussian is not demonstrated matched; thin gap preserves vertical momentum without RF vertical focusing.','No septum geometry modeled; no septum annotation or inset.']}
(root/'profile-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
