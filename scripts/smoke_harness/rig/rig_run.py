"""rig_run.py -- the REAL app, locally: bea_main + the FEA files on one origin (RUL-076 s7.3)."""
import os, sys
sys.path.insert(0, '/home/claude/rig')
os.chdir('/home/claude/rig')
import bea_main
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
app = bea_main.app
@app.get('/')
def _index():
    return FileResponse('/home/claude/rig/marketsquare.html', media_type='text/html')
@app.get('/static/ms.js')
def _js():
    return FileResponse('/home/claude/rig/ms.js', media_type='application/javascript')
@app.get('/static/ms.css')
def _css():
    return FileResponse('/home/claude/rig/ms.css', media_type='text/css')
@app.get('/service-worker.js')
def _sw():
    return FileResponse('/home/claude/rig/assets/service-worker.js', media_type='application/javascript')
@app.get('/dashboard.html')
def _dash():
    return FileResponse('/home/claude/rig/dashboard.server.html', media_type='text/html')
@app.get('/quick.html')
def _quick():
    return FileResponse('/home/claude/rig/quick.html', media_type='text/html')
for sub in ('static', 'assets'):
    p = os.path.join('/home/claude/rig', sub)
    if os.path.isdir(p):
        app.mount('/' + sub, StaticFiles(directory=p), name=sub)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='warning')
