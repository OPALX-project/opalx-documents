"""Matched dense-cross-section transverse mesh sequence."""
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
for nx in (64,128,256,512):
    subprocess.run([sys.executable,str(ROOT/'run_study.py'),f'xy{nx}-z512-n16384',
                    '--mesh',str(nx),str(nx//2),'512','--ns','640','--nrad','64',
                    '--nphi','256','--run'],cwd=ROOT,check=True)
