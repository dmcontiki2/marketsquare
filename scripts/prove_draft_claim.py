#!/usr/bin/env python3
"""prove_draft_claim.py -- DRAFT-CLAIM-1 (Goal run 39, 14 Oct 2026): EXECUTE POST /listings/{id}/claim-draft and the
Google login_hint against the real bea_main.py, on a throwaway COPY of a database (never the live file).

Run: python3 scripts/prove_draft_claim.py [path-to-db-to-copy]   (default: a fresh empty schema from the server's init)
"""
import os, sys, tempfile, sqlite3, shutil
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO); sys.path.insert(0, REPO)
os.environ.setdefault("MS_API_KEY", "k"); os.environ.setdefault("MS_ADMIN_KEY", "adm")
os.environ.setdefault("MS_JWT_SECRET", "test-only-" + os.urandom(8).hex())
for k in ("RESEND_API_KEY", "PAYSTACK_SECRET_KEY", "PAYSTACK_WEBHOOK_SECRET"):
    os.environ.pop(k, None)
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k["check_dir"] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
import database
tmp = tempfile.mkdtemp(); DB = os.path.join(tmp, "dc.db")
src = sys.argv[1] if len(sys.argv) > 1 else ""
if src:
    s = sqlite3.connect(src); d = sqlite3.connect(DB); s.backup(d); s.close(); d.close()
database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(tmp, "flights.db")
import bea_main as b
from fastapi import Response, HTTPException
fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok: fails.append(msg)
def x(sql, *p):
    c = database.get_db(); cur = c.execute(sql, p); c.commit(); r = cur.lastrowid; c.close(); return r
def q(sql, *p):
    c = database.get_db(); r = c.execute(sql, p).fetchall(); c.close(); return r
def sess(em):
    r = Response(); b._establish_user_session(em, r)
    for k, v in r.raw_headers:
        if k.decode().lower() == "set-cookie" and v.decode().startswith("ts_user="):
            return v.decode().split(";", 1)[0].split("=", 1)[1]
    raise SystemExit("no ts_user cookie minted")
A, B, C = "qa-dc-a@example.com", "qa-dc-b@example.com", "qa-dc-c@example.com"
for e in (A, B, C):
    x("DELETE FROM users WHERE email=?", e)
x("INSERT INTO users (email, aa_free_used, aa_sessions_remaining) VALUES (?,0,0)", A)        # typed in Quick, never proven
x("INSERT INTO users (email, aa_free_used, aa_sessions_remaining, auth_provider) VALUES (?,0,0,'google')", B)  # her Google account
x("INSERT INTO users (email, aa_free_used, aa_sessions_remaining, last_seen) VALUES (?,0,0,'2026-10-01T00:00:00Z')", C)  # somebody real
def mk(owner, status="draft", pub=None):
    return x("INSERT INTO listings (title, price, category, city, seller_email, listing_status, published_at, created_at, updated_at, is_demo) "
             "VALUES ('QA claim test','R1','Services','Pretoria',?,?,?,datetime('now'),datetime('now'),0)", owner, status, pub)
d1 = mk(A); d2 = mk(C); d3 = mk(A, "live", "2026-10-14 07:00:00"); d4 = mk(B)
tok = lambda i: b._purpose_token("draft", i, days=7)
sB = sess(B)
try:
    b.claim_quick_draft(d1, 1, None, tok(d1)); check(False, "no session -> 401")
except HTTPException as he:
    check(he.status_code == 401, "no session -> 401")
check(b.claim_quick_draft(d1, 1, sB, None).get("reason") == "not_this_phone", "no draft cookie -> not_this_phone")
check(b.claim_quick_draft(d1, 1, sB, tok(d2)).get("reason") == "not_this_phone", "another draft's cookie -> not_this_phone")
check(b.claim_quick_draft(d1, 1, sB, "123.abc").get("reason") == "not_this_phone", "forged cookie -> not_this_phone")
check(b.claim_quick_draft(d2, 1, sB, tok(d2)).get("reason") == "other_account", "draft on a proven (signed-in) address -> other_account")
x("UPDATE listings SET listing_status='draft', published_at=NULL WHERE id=?", d3)
x("INSERT INTO listings (title, price, category, city, seller_email, listing_status, published_at, created_at, updated_at, is_demo) "
  "VALUES ('QA live','R1','Services','Pretoria',?, 'live', '2026-10-14 07:00:00', datetime('now'), datetime('now'), 0)", "qa-dc-d@example.com")
dD = mk("qa-dc-d@example.com")
check(b.claim_quick_draft(dD, 1, sB, tok(dD)).get("reason") == "other_account", "address that ever published -> other_account")
x("INSERT INTO listings (title, price, category, city, seller_email, listing_status, published_at, created_at, updated_at, is_demo) "
  "VALUES ('QA was live','R1','Services','Pretoria',?, 'draft', '2026-10-13 07:00:00', datetime('now'), datetime('now'), 0)", A)
dP = q("SELECT MAX(id) AS m FROM listings")[0]["m"]
check(b.claim_quick_draft(dP, 1, sB, tok(dP)).get("reason") == "not_a_draft", "a once-published (paused) advert -> not_a_draft")
x("DELETE FROM listings WHERE id=?", dP)
check(b.claim_quick_draft(d4, 1, sB, tok(d4)).get("reason") == "already_yours", "her own draft -> already_yours")
r = b.claim_quick_draft(d1, 1, sB, tok(d1))
check(r.get("claimable") is True and r.get("from", "").endswith("@example.com") and "qa-dc-a" not in r.get("from", ""), "check=1 offers it, address masked: %s" % r)
check(q("SELECT seller_email FROM listings WHERE id=?", d1)[0]["seller_email"] == A, "check=1 moves nothing")
r = b.claim_quick_draft(d1, 0, sB, tok(d1))
check(r.get("moved") is True, "claim moves it")
check(q("SELECT seller_email FROM listings WHERE id=?", d1)[0]["seller_email"] == B, "draft now waits on her Google address")
check(b.claim_quick_draft(d1, 0, sB, tok(d1)).get("reason") == "already_yours", "second claim is a no-op")
x("INSERT INTO passkeys (email, cred_id, public_key, alg, created_at) VALUES (?, 'qa-dc-cred', x'00', -7, datetime('now'))", "qa-dc-e@example.com")
dE = mk("qa-dc-e@example.com")
check(b.claim_quick_draft(dE, 1, sB, tok(dE)).get("reason") == "other_account", "address with a passkey -> other_account")
# Google login_hint
class _R: headers = {}; cookies = {}
os.environ.setdefault("GOOGLE_CLIENT_ID", "x")
try:
    if b._oauth_ready("google"):
        loc = b.auth_oauth_start("google", None, "/", "bekezela@gmail.com").headers["location"]
        check("login_hint=bekezela%40gmail.com" in loc, "Google start carries login_hint")
        loc = b.auth_oauth_start("google", None, "/", "not an email<script>").headers["location"]
        check("login_hint" not in loc, "a non-address hint is dropped")
        loc = b.auth_oauth_start("google", None, "/").headers["location"]
        check("login_hint" not in loc, "no hint, no login_hint")
    else:
        print("  [--] Google not configured in this environment; login_hint not executed here")
except Exception as e:
    check(False, "Google start: %r" % e)
shutil.rmtree(tmp, ignore_errors=True)
print("FAIL %d" % len(fails) if fails else "PASS -- DRAFT-CLAIM-1")
sys.exit(1 if fails else 0)
