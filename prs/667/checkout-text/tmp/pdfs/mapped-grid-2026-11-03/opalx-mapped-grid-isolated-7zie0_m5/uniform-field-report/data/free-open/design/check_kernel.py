#!/Users/adelmann/.venv-h6/bin/python
"""Independent Gauss-quadrature checks of the production finite-cell kernels."""
import json
import math
from pathlib import Path
import shlex
import subprocess
import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
REPO = Path('/Users/adelmann/git/opalx')
commands = json.loads((REPO / 'build-omp/compile_commands.json').read_text())
args = shlex.split(next(c['command'] for c in commands if c['file'].endswith('FFT2D5Poisson.cpp')))
out = args.index('-o')
args[out:out+2] = []
args.remove('-c')
args[-1] = str(HERE / 'check_kernel.cpp')
args += ['-L/opt/homebrew/opt/libomp/lib', '-Wl,-rpath,/opt/homebrew/opt/libomp/lib',
         '-o', str(HERE / 'check_kernel')]
subprocess.run(args, check=True, cwd=REPO)

cases = [
    ('cube-self', 0., 0., 0., 2., 2., 2., 0., 1.),
    ('flat-near', .18, .31, .42, .2, .3, .4, 0., 1.),
    ('flat-anisotropic', .0002, .0001, .001, .000078125, .00003125, .001953125, 0., 1.),
    ('curved-anisotropic', .0002, .0001, .001, .000078125, .00003125, .001953125, .5, 1.),
    ('curved-near', .006, .001, .003, .00015, .00003, .002, .5, 1.),
    ('curved-far', .004, .0003, 2., .00015, .00003, .002, .5, 1.),
    ('curved-far-negative', -.004, .0003, -2., .00015, .00003, .002, .5, 1.),
    ('far-isotropic', 40., 30., 20., 1., 1., 1., .001, 1.),
    ('straight-gamma', .004, .0003, .02, .00015, .00003, .002, 0., 10.),
]
payload = ''.join(' '.join(map(str, (kind, *c[1:]))) + '\n' for c in cases for kind in range(3))
output = subprocess.run([str(HERE / 'check_kernel')], input=payload, text=True,
                        capture_output=True, check=True)
values = list(map(float, output.stdout.split()))
nodes, weights = leggauss(100)
weights = weights / 2.
records = []
for ic, case in enumerate(cases):
    name,x,y,s,hx,hy,hs,kappa,gamma = case
    if name == 'cube-self':
        g = (24 * math.log((1+math.sqrt(3))/math.sqrt(2)) - 2*math.pi) / 8
        references = [g,g/3.,0.]
    else:
        xx = x + hx/2 * nodes[:,None,None]
        yy = y + hy/2 * nodes[None,:,None]
        zz = gamma * (s + hs/2 * nodes[None,None,:])
        xi = zz if kappa == 0 else 2*np.sin(kappa*zz/2)/kappa
        r2 = xx*xx + yy*yy + xi*xi
        g = 1/np.sqrt(r2)
        h = xi*xi*g/r2
        w = weights[:,None,None]*weights[None,:,None]*weights[None,None,:]
        references = [np.sum(w*g),np.sum(w*h),np.sum(w*xx*h)]
    for kind,(actual,ref) in enumerate(zip(values[3*ic:3*ic+3], references)):
        records.append(dict(case=name,kind=kind,actual=actual,reference=ref,
                            absolute_error=actual-ref,
                            relative_error=(actual-ref)/ref if ref else actual-ref))
df = pd.DataFrame(records)
df.to_csv(HERE/'kernel_checks.csv',index=False)
print(df.to_string(index=False,float_format=lambda v:f'{v:.12g}'))
assert df.actual.map(math.isfinite).all()
assert df.relative_error.abs().max() < 2.e-6
