"""Plot manufactured-density unit-test CSV and isolate the even curvature field.
Input is emitted by SmoothGaussianSlicesConvergeWithoutParticleNoise when
OPALX_FFT2D5_FORCE_CSV is set. Current FFT2D5 has flat slice solves; do not label
agreement with the straight field as physical curvature validation.
"""
from pathlib import Path
import argparse,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/opalx-2d5-matplotlib')
import numpy as np,pandas as pd
from scipy.constants import epsilon_0
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('csv',nargs='?',type=Path,default=root/'smooth-gaussian-force.csv');args=parser.parse_args()
data=pd.read_csv(args.csv);out=root;out.mkdir(exist_ok=True)
unit=1e-9/(4*np.pi*epsilon_0*.001)
plt.rcParams.update({'font.family':'serif','mathtext.fontset':'stix','font.size':11,'pdf.fonttype':42})
colors=['#0072B2','#E69F00','#009E73','#76519a'];markers=['s','^','o','d']
fig,axs=plt.subplots(1,2,figsize=(10.5,4.4),layout='constrained')
meshes=sorted(data.mesh.unique())
for mesh,col,marker in zip(meshes,colors,markers):
 part=data[(data.mesh==mesh)&(data.radius_m==0)].sort_values('x_over_sigma')
 axs[0].plot(part.x_over_sigma,part.Ex_V_per_m/unit,color=col,marker=marker,mfc='white',ms=3.5,lw=1.5,label=rf'OPALX ${mesh}^2$')
axs[0].plot(part.x_over_sigma,part.straight_Ex_V_per_m/unit,'k--',lw=1.8,label='Gaussian analytic slice')
axs[0].set(xlabel=r'$x/\sigma_\perp$',ylabel=r'$E_x/[\lambda/(4\pi\epsilon_0\sigma_\perp)]$',title='Smooth Gaussian density: numerical convergence',xlim=(-3,3))
rows=[]
for (mesh,radius),part in data[data.radius_m>0].groupby(['mesh','radius_m']):
 lookup=part.set_index('x_over_sigma')
 for x in sorted(lookup.index):
  if x<0 or -x not in lookup.index:continue
  plus=lookup.loc[x];minus=lookup.loc[-x]
  even=.5*(plus.Ex_V_per_m+minus.Ex_V_per_m)
  expected=.5*(plus.qiang_delta_Ex_V_per_m+minus.qiang_delta_Ex_V_per_m)
  rows.append(dict(mesh=mesh,radius_m=radius,x_over_sigma=x,even_Ex_V_per_m=even,qiang_delta_Ex_V_per_m=expected,
    even_Ex_scaled=even/(unit*.001/radius),qiang_delta_Ex_scaled=expected/(unit*.001/radius)))
even=pd.DataFrame(rows);even.to_csv(out/'smooth_curvature_even_field.csv',index=False)
# Compare all meshes at mirrored probes ±sigma. Scaling by the known 1/R
# factor exposes whether the physical leading term is present at each radius.
point=even[even.x_over_sigma==1]
radii=sorted(point.radius_m.unique())
for mesh,col,marker in zip(meshes,colors,markers):
 part=point[point.mesh==mesh].sort_values('radius_m')
 axs[1].plot(part.radius_m,part.even_Ex_scaled,color=col,marker=marker,mfc='white',ms=5,lw=1.3,label=rf'OPALX ${mesh}^2$')
part=point[point.mesh==max(meshes)].sort_values('radius_m')
axs[1].plot(part.radius_m,part.qiang_delta_Ex_scaled,'k--',lw=1.8,label='Qiang: leading curvature term, Eq. (98)')
axs[1].set_xscale('log')
axs[1].set(xticks=radii,xticklabels=[f'{r:g}' for r in radii],
 xlabel=r'Bend radius $R$ [m]',ylabel=r'$[E_x(\sigma)+E_x(-\sigma)]/[2\lambda/(4\pi\epsilon_0 R)]$',
 title='Curvature contribution at mirrored probes',xlim=(.75,135))
for ax in axs:
 ax.axhline(0,color='.6',lw=.7);ax.grid(alpha=.18);ax.minorticks_on();ax.tick_params(which='both',direction='in',top=True,right=True);ax.legend(fontsize=8)
fig.savefig(out/'frame-consistency-comparison.png',dpi=350);fig.savefig(out/'frame-consistency-comparison.pdf')
print(even[even.x_over_sigma==1].to_string(index=False))
