from pathlib import Path
import subprocess,json,sys
record=Path(__file__).resolve().parent
name=sys.argv[1];args=json.loads((record/'configure-commands.json').read_text())[name]
with (record/(name+'-configure.log')).open('w') as stream:subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT,check=True)
with (record/(name+'-build.log')).open('w') as stream:subprocess.run(['cmake','--build','/Users/adelmann/git/opalx/'+name,'--target','opalx_exe','--parallel','4'],stdout=stream,stderr=subprocess.STDOUT,check=True)
print(name+' complete',flush=True)
