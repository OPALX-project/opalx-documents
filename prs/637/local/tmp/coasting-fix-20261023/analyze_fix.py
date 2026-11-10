from coast_data import *
import os
os.environ['MPLCONFIGDIR']='/tmp/coasting-fix-mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
summary={}
fig,ax=plt.subplots(figsize=(7,4),layout='constrained')
for name,label,color in [('before-off','Before: periodic path membership','#D55E00'),('after-off','After: spatial sector candidates','#0072B2')]:
 df=stat(root/name/'coasting.stat');delta=np.linalg.norm(df[['mean_x','mean_y','mean_s']],axis=1)
 summary[name]={'final_separation_m':float(delta[-1]),'maximum_separation_m':float(delta.max()),'steps':len(df),'energy_range_MeV':[float(df.energy.min()),float(df.energy.max())]}
 ax.semilogy(df.t/1000,np.maximum(delta,1e-16),label=label,color=color,lw=1.3)
a=stat(root/'before-off/coasting.stat');b=stat(root/'after-off/coasting.stat')
cols=['t','s','ref_x','ref_y','ref_z'];np.testing.assert_array_equal(a[cols],b[cols]);summary['reference_time_and_path_unchanged']=True
for name in ['after-on','after-mpi2']:
 np.testing.assert_array_equal(b.to_numpy(),stat(root/name/'coasting.stat').to_numpy())
summary['probe_on_off_and_two_rank_statistics_identical']=True
summary['radial_hits_per_probe']=10
ax.set(xlabel='Time [µs]',ylabel='Particle/reference separation [m]',title='PSI Ring · 72 MeV proton · ten coasting turns')
ax.grid(alpha=.2);ax.legend(frameon=False);fig.savefig(root/'coasting-fix.png',dpi=240);fig.savefig(root/'coasting-fix.pdf')
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
