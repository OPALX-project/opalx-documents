exec(open('/Users/adelmann/git/opalx/tmp/zerosc-audit/check.py').read().split("f=np.load")[0])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path('/Users/adelmann/git/opalx/tmp/zerosc-audit')
df=pd.read_csv(root/'bend-10m-100steps-local-original/analysis/series.csv')
rows=[]
for s in np.linspace(0,10,101):
 ph=s/R;r=np.sqrt(R*R+2*R*a*np.cos(ph)+a*a)
 u=(2*R*a*np.cos(ph)+a*a)/(r+R);p=-p0*a*np.sin(ph)/r
 us=a*np.cos(ph)-a*a*np.sin(ph)**2/(R+np.sqrt(R*R-a*a*np.sin(ph)**2))
 ps=-p0*a*np.sin(ph)/R
 rows.append((s,em(u,p),em(us,ps)))
ref=pd.DataFrame(rows,columns=['s_m','exact_time','exact_station']);ref.to_csv(out/'references.csv',index=False)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,4.5),layout='constrained')
for code,color in [('Local original','#0072B2'),('PyORBIT','#D55E00')]:
 d=df[(df.code==code)&(df['mode']=='ZeroSC')&(df.steps==100)]
 ax.plot(d.s_m,d.emit_n_u_m*1e6,color=color,label=code+' (100 steps)')
 if code=='PyORBIT':
  err=np.abs(d.emit_n_u_m.to_numpy()*1e6-ref.exact_station.to_numpy());print('Py station maximum absolute error',err.max(),'fraction peak',err.max()/ref.exact_station.max())
ax.plot(ref.s_m,ref.exact_time,'k:',lw=2,label='Exact: common time (OPALX convention)')
ax.plot(ref.s_m,ref.exact_station,'--',color='#009E73',lw=1.7,label='Exact: common station (PyORBIT convention)')
ax.set(xlabel='$s$ (m)',ylabel=r'$\epsilon_{n,u}$ (mm mrad)',xlim=(0,10),ylim=(0,None),title='Zero space charge: different sampling conventions')
ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.grid(alpha=.2);ax.legend(fontsize=9)
fig.savefig(out/'zero-sc-conventions.png',dpi=300)
