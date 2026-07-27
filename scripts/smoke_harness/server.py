import http.server, urllib.parse, os
class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        m = {'/listings':'listings.json','/demo-listings':'demo-listings.json',
             '/demo-sellers':'demo-sellers.json','/geo/countries':'geo.json','/health':'health.json',
             '/':'index.html'}
        if p in m:
            body=open(m[p],'rb').read()
            self.send_response(200); self.send_header('Content-Type','application/json' if p!='/' else 'text/html')
            self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body); return
        if p.startswith('/static/') and os.path.exists(p[1:]):
            return super().do_GET()
        self.send_response(200); self.send_header('Content-Length','2'); self.end_headers(); self.wfile.write(b'{}')
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8471),H).serve_forever()
