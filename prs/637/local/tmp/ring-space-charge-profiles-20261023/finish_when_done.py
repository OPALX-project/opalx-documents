"""Complete this one launched study by plotting after successful termination."""
from pathlib import Path
import json,subprocess,sys,time
root=Path(__file__).resolve().parent
while True:
 try: record=json.loads((root/'accelerating-pic/launch.json').read_text())
 except (OSError,json.JSONDecodeError):time.sleep(10);continue
 if 'returncode' in record:break
 time.sleep(20)
if record['returncode']!=0:raise SystemExit('Accelerating PIC failed; inspect preserved run.log')
subprocess.run([sys.executable,str(root/'plot_last_eight.py')],check=True)
