import jwt, time, sqlite3, json, urllib.request
DB = '/home/claude/rigdata/marketsquare.db'
JWT = 'rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt'
REVIEW = 'rigsecret_rigsecret_rigsecret_rigsecret'
ORIGIN = 'http://127.0.0.1:8080'
def user_token(email): return jwt.encode({"scope": "user", "sub": email, "exp": int(time.time()) + 86400}, JWT, algorithm="HS256")
def admin_token(): return jwt.encode({"scope": "admin", "sub": "master", "name": "rig-admin", "exp": int(time.time()) + 86400}, JWT, algorithm="HS256")
def review_token(): return jwt.encode({"scope": "review", "exp": int(time.time()) + 86400}, REVIEW, algorithm="HS256")
def sql(q, *p):
    c = sqlite3.connect(DB, timeout=20); c.row_factory = sqlite3.Row
    r = [dict(x) for x in c.execute(q, p).fetchall()]; c.commit(); c.close(); return r
def standin(path='/__standin/state', body=None):
    req = urllib.request.Request('http://127.0.0.1:8999' + path, data=(json.dumps(body).encode() if body is not None else None),
                                 method='POST' if body is not None else 'GET', headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=20).read())
def api(method, path, body=None, headers=None):
    req = urllib.request.Request('http://127.0.0.1:8000' + path, data=(json.dumps(body).encode() if body is not None else None),
                                 method=method, headers=dict({'Content-Type': 'application/json'}, **(headers or {})))
    try:
        r = urllib.request.urlopen(req, timeout=30); return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
