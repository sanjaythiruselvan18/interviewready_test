"""Run the included browser build with a local demo backend. Python 3.12+."""
import os, sys, subprocess, time, webbrowser
from pathlib import Path
root=Path(__file__).resolve().parent
if not (root/'mobile/dist/index.html').exists():
    raise SystemExit('Browser build is missing. In mobile/, run npm ci and npx expo export --platform web.')
env=os.environ.copy();env['DEMO_MODE']='true';env['DATABASE_PATH']=str(root/'demo.db');env['ALLOWED_ORIGINS']='http://localhost:8081';env['PORT']='8000'
processes=[]
try:
    processes.append(subprocess.Popen([sys.executable,str(root/'server/app.py')],env=env))
    processes.append(subprocess.Popen([sys.executable,'-m','http.server','8081','--bind','127.0.0.1','--directory',str(root/'mobile/dist')]))
    time.sleep(1)
    if any(p.poll() is not None for p in processes):raise SystemExit('Could not start. Check whether ports 8000 or 8081 are already in use.')
    print('\nInterviewReady demo: http://localhost:8081\nPress Ctrl+C to stop.\n',flush=True)
    webbrowser.open('http://localhost:8081')
    while all(p.poll() is None for p in processes):time.sleep(1)
except KeyboardInterrupt:pass
finally:
    for p in processes:p.terminate()
    for p in processes:p.wait()
