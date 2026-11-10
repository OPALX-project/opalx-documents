"""Reproduce uniform-round pipe fields and matched numerical/physical controls."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parent
sys.path.insert(0,str(STUDY/'opalx'))
from run_opalx import run

def main():
    source=STUDY/'common/triangle-ns16384-nr16-np32.json'
    runs=ROOT/'opalx/runs'
    for name,mesh,width,b,mode in [
        ('fixed64',(64,64,64),.02,.02,'CIRCULAR_UNIFORM'),
        ('fixed128',(128,128,128),.02,.02,'CIRCULAR_UNIFORM'),
        ('fixed256',(256,256,256),.02,.02,'CIRCULAR_UNIFORM'),
        ('fixed-wide256',(256,256,128),.04,.02,'CIRCULAR_UNIFORM'),
        ('physical-b10mm',(128,128,128),.02,.01,'CIRCULAR_UNIFORM'),
        ('legacy128',(128,128,128),.02,None,'CIRCULAR')]:
        run(name,mesh,source,width,mode,b,runs)

if __name__=='__main__':main()
