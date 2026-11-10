"""Sequential reproducible baseline mesh sequence; preserve completed runs."""
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CASES=[('xy128-z512',(128,64,512)),('xy256-z512',(256,128,512)),
       ('xy128-z1024',(128,64,1024)),('xy128-z2048',(128,64,2048))]

for name,mesh in CASES:
    subprocess.run([sys.executable,str(ROOT/'run_study.py'),name,'--mesh',*map(str,mesh),'--run'],cwd=ROOT,check=True)
