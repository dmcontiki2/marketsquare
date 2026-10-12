"""rig_front.py -- plays nginx for the rig: serves the app's static files exactly as the live server does
(index.html = marketsquare.html, /static/ms.js ...) and passes every other request to the backend on :8000,
so the security gate sees the same routes it sees in production. One origin: http://127.0.0.1:8080."""
import os, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
RIG = '/home/claude/rig'; BEA = 'http://127.0.0.1:8000'
STATIC = {'/': ('marketsquare.html', 'text/html; charset=utf-8'), '/index.html': ('marketsquare.html', 'text/html; charset=utf-8'),
          '/static/ms.js': ('ms.js', 'application/javascript'), '/static/ms.css': ('ms.css', 'text/css'),
          '/static/ms_gate.js': ('ms_gate.js', 'application/javascript'), '/static/ts_report.js': ('ts_report.js', 'application/javascript'),
          '/dashboard.html': ('dashboard.server.html', 'text/html; charset=utf-8'),
          '/service-worker.js': ('assets/service-worker.js', 'application/javascript')}
TYPES = {'.js': 'application/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
         '.json': 'application/json', '.html': 'text/html; charset=utf-8', '.webmanifest': 'application/manifest+json', '.woff2': 'font/woff2'}
class H(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *a): pass
    def _file(self, path, ctype):
        try: raw = open(path, 'rb').read()
        except Exception: return False
        self.send_response(200); self.send_header('Content-Type', ctype); self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw); return True
    def _go(self):
        p = self.path.split('?', 1)[0]
        if self.command == 'GET':
            if p in STATIC and self._file(os.path.join(RIG, STATIC[p][0]), STATIC[p][1]): return
            if p.startswith('/static/') or p.startswith('/assets/'):
                f = os.path.normpath(os.path.join(RIG, p.lstrip('/')))
                if f.startswith(RIG) and os.path.isfile(f) and self._file(f, TYPES.get(os.path.splitext(f)[1], 'application/octet-stream')): return
        n = int(self.headers.get('Content-Length') or 0); body = self.rfile.read(n) if n else None
        hdr = {k: v for k, v in self.headers.items() if k.lower() not in ('host', 'connection', 'content-length', 'accept-encoding')}
        req = urllib.request.Request(BEA + self.path, data=body, method=self.command, headers=hdr)
        try:
            r = urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            r = e
        except Exception as e:
            raw = b'{"detail":"rig backend unreachable"}'
            self.send_response(502); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        raw = r.read()
        self.send_response(r.status if hasattr(r, 'status') else r.code)
        for k, v in r.headers.items():
            if k.lower() in ('transfer-encoding', 'connection', 'content-length', 'content-encoding'): continue
            self.send_header(k, v)
        self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = _go
if __name__ == '__main__':
    ThreadingHTTPServer(('127.0.0.1', 8080), H).serve_forever()
