#!/usr/bin/env python3
"""GI-0041 (David, 19 Oct 2026: "Yes for GI-0041"). One-off, run once:
 (b) move draft #543 to the Google account she signed in with (bekezelansingo23@gmail.com);
 (c) archive the duplicate drafts #564 (= #563) and #558 (= #557);
 (a) one letter to each person whose Quick draft is saved and waiting, with her own sign-in link.
Publishes nothing. Usage: gi0041.py --dry | --do"""
import sys, os, sqlite3, datetime, json
sys.path.insert(0, "/opt/marketsquare-src/scripts")
from quick_draft_backfill import _load_service_env
DB = "/var/www/marketsquare/marketsquare.db"
MOVE = (543, "bekezelansingo@gmail.com", "bekezelansingo23@gmail.com")
ARCHIVE = {564: 563, 558: 557}
LETTERS = [543, 545, 546, 555, 556, 557, 559, 563, 566]
DO = "--do" in sys.argv
now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def row(c, i):
    return c.execute("select id,listing_status,seller_email,title,published_at from listings where id=?", (i,)).fetchone()

c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
# guards: every row still a draft, never published, owners as recorded
for i in [MOVE[0]] + list(ARCHIVE) + LETTERS:
    r = row(c, i); assert r and r["listing_status"] == "draft" and not r["published_at"], (i, dict(r) if r else None)
assert row(c, MOVE[0])["seller_email"] in (MOVE[1], MOVE[2])
for d, k in ARCHIVE.items():
    assert row(c, d)["seller_email"] == row(c, k)["seller_email"], (d, k)
assert c.execute("select count(*) from users where lower(email)=?", (MOVE[2],)).fetchone()[0] == 1

if DO:
    bk = "/root/backup_gi0041_%s.db" % datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    d = sqlite3.connect(bk); c.backup(d); d.close(); print("backup", bk)
    with c:
        c.execute("update listings set seller_email=?, updated_at=? where id=? and listing_status='draft'", (MOVE[2], now, MOVE[0]))
        for d_ in ARCHIVE:
            c.execute("update listings set listing_status='archived', status_changed_at=?, updated_at=? where id=? and listing_status='draft'", (now, now, d_))
    print("moved", MOVE[0], "->", MOVE[2]); print("archived", list(ARCHIVE))

_load_service_env()
sys.path.insert(0, "/var/www/marketsquare"); os.chdir("/var/www/marketsquare")
import main as B
assert B._JWT_SECRET, "MS_JWT_SECRET empty -- refusing (QUICK-RETURN-GUARD-1)"
from datetime import timezone, timedelta

def letter(em, lid, title):
    tok = B._pyjwt.encode({"email": em, "purpose": "signin",
                           "exp": datetime.datetime.now(timezone.utc) + timedelta(days=7),
                           "iat": datetime.datetime.now(timezone.utc)}, B._JWT_SECRET, algorithm=B._JWT_ALGO)
    assert B._pyjwt.decode(tok, B._JWT_SECRET, algorithms=[B._JWT_ALGO])["email"] == em
    link = B.APP_URL + "/?signin=" + tok + "&draft=" + str(int(lid))
    safe = (title or "your listing").replace("<", "&lt;").replace(">", "&gt;")
    subject = "Your TrustSquare listing is saved — one tap to put it live"
    html = ("<div style='font-family:Inter,Arial,sans-serif;max-width:460px;margin:auto'>"
        "<h2 style='color:#0c1a2e;margin-bottom:6px'>Your listing is saved</h2>"
        "<p style='color:#0c1a2e;font-size:16px;margin-top:0'><b>" + safe + "</b></p>"
        "<p>You made this advert on TrustSquare and saved it. Nobody can see it yet — it goes live "
        "when you publish it. It is free.</p>"
        "<p><a href='" + link + "' style='display:inline-block;background:#C8873A;color:#fff;"
        "text-decoration:none;padding:13px 24px;border-radius:8px;font-weight:700'>Open my listing &rarr;</a></p>"
        "<p>The button signs you in and opens your listing. Check it, then tap <b>Publish</b>.</p>"
        "<p style='color:#6b7280;font-size:13px'>Tap it within 3 days on the phone you will use. Any other time, "
        "open <a href='" + B.APP_URL + "'>trustsquare.co</a> and sign in with <b>" + em + "</b> — "
        "your listing is waiting on that address.</p>"
        "<p style='color:#6b7280;font-size:12px'>We are writing once because your listing is still waiting. "
        "If you don't want it, ignore this letter — nothing is public and we will not write about it again.</p></div>")
    plain = ("Your TrustSquare listing is saved: " + (title or "") + "\n\nNobody can see it yet -- it goes live when "
             "you publish it. It is free.\n\nOpen it, check it and tap Publish:\n" + link +
             "\n\nTap it within 3 days. Any other time, open " + B.APP_URL + " and sign in with " + em +
             ".\n\nWe are writing once because your listing is still waiting. If you don't want it, ignore this letter.")
    return subject, html, plain

out = []
for lid in LETTERS:
    r = row(c, lid); em = r["seller_email"].strip().lower()
    s, h, p = letter(em, lid, r["title"])
    st = B._send_html_email(em, s, h, p) if DO else "dry"
    out.append({"id": lid, "to": em, "status": st}); print(lid, em, st)
if DO:
    json.dump({"at": now, "permission": "David, 19 Oct 2026: Yes for GI-0041", "sent": out},
              open("/root/gi0041_sent_%s.json" % now[:10], "w"), indent=1)
