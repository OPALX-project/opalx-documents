"""Verify flushed crossing records and plot final eight complete passages; no inset."""
from pathlib import Path
import json,os,sys
import h5py,numpy as np,pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-extraction-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent;run=root/'accelerating-pic-8-580';out=root/'profiles-8-580';out.mkdir(exist_ok=True)
record=json.loads((run/'launch.json').read_text());assert record.get('returncode')==0
assert 'EKINSTOP reached after complete gap kick' in (run/'run.log').read_text()
parts=[]
with h5py.File(run/'radial.h5') as f:
 for key,g in f.items():
  if key.startswith('Step#'):parts.append(pd.DataFrame({n:g[n][:] for n in ['id','turn','time','x','z','q']}))
data=pd.concat(parts,ignore_index=True);data['radius_mm']=np.hypot(data.x,data.z)*1000
with h5py.File(run/'acceleration.h5') as f:
 g=f[max(f,key=lambda k:int(k.split('#')[1]))];survivors=set(g['id'][:]);final={'particles':len(survivors),'time_s':float(g.attrs['TIME'][0]),'steps':int(g.attrs['GlobalTrackStep'][0]),'reference_energy_MeV':float((np.sqrt(1+np.sum(g.attrs['RefPartP']**2))-1)*938.27208816)}
# Every final survivor must occur once in each chosen full passage. An unfinished
# last passage is excluded rather than confused with a turn's physical losses.
complete=[]
for turn,df in data.groupby('turn'):
 assert not df.id.duplicated().any(),f'duplicate particle crossing in turn{turn}'
 if survivors.issubset(set(df.id)):complete.append(int(turn))
turns=complete[-8:];assert len(turns)==8
selected=data[data.turn.isin(turns)];assert abs(selected.z).max()<1e-11
summary=selected.groupby('turn').agg(particles=('id','size'),charge_C=('q','sum'),mean_radius_mm=('radius_mm','mean'),minimum_radius_mm=('radius_mm','min'),maximum_radius_mm=('radius_mm','max'))
summary['fraction_of_launch']=summary.particles/4096
np.testing.assert_allclose(summary.charge_C,summary.particles*(3.9486673247778873e-11/4096),rtol=1e-10)
summary.to_csv(out/'last-eight-turns.csv')
lo=np.floor(selected.radius_mm.min()*10)/10;hi=np.ceil(selected.radius_mm.max()*10)/10
edges=np.arange(lo,hi+.100001,.1);centres=.5*(edges[:-1]+edges[1:]);profiles=pd.DataFrame({'radius_mm':centres})
for turn in turns:
 df=selected[selected.turn==turn];profiles[f'turn_{turn}_pC_per_mm']=np.histogram(df.radius_mm,bins=edges,weights=abs(df.q)*1e12)[0]/np.diff(edges)
profiles['sum_pC_per_mm']=profiles.iloc[:,1:].sum(axis=1);profiles.to_csv(out/'line-density.csv',index=False)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(11,5.9),layout='constrained')
fig.get_layout_engine().set(rect=(0,.06,1,.94))
for i,turn in enumerate(turns):
 y=profiles[f'turn_{turn}_pC_per_mm'];ax.plot(centres,np.where(y>0,y,np.nan),lw=1,color=plt.get_cmap('tab10')(i),label=f'Turn {turn}')
y=profiles.sum_pC_per_mm;ax.plot(centres,np.where(y>0,y,np.nan),'k-',lw=1.5,label='Sum of final 8 complete turns')
ax.set(yscale='log',xlabel=r'$r$ (mm)',ylabel='Radial line density (pC/mm)',title='PSI Ring · 2 mA launch · 580 MeV reference stop')
ax.grid(alpha=.18);ax.legend(ncol=3,frameon=False,fontsize=9)
fig.text(.5,.005,f'8³ mesh · 4,096 launched · {len(survivors):,} surviving · coarse PIC · 0.1 mm bins',ha='center',fontsize=9)
fig.savefig(out/'last-eight-turns.png',dpi=240);fig.savefig(out/'last-eight-turns.pdf')
report={'turns_zero_based':turns,'final':final,'per_turn':summary.reset_index().to_dict(orient='records'),'probe_records':len(data),'complete_turns':complete,'excluded_incomplete_turns':sorted(set(map(int,data.turn.unique()))-set(complete)),'lost_particles':4096-len(survivors),'limitations':['Very coarse PIC; no mesh or timestep convergence claim.','One bunch successive turns; no neighbouring-bunch/turn space charge.','Thin RF gaps preserve vertical momentum; no vertical RF focusing.','No septum model or inset.'],'launch':record}
(out/'profile-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
