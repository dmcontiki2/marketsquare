#!/usr/bin/env python3
"""prove_trust_badge_one_rule.py -- TRUST-BADGE-ONE-RULE-1 (David, 12 Oct 2026), executed, not read.

Runs the REAL scoring functions of a given bea_main.py against a COPY of the live database (never the live file) and
proves two things:
  1. the Bee Lady case: after the Edit screen's read and the buyer's panel, in either order, every advert of a seller
     who has a Local Market advert carries the Local Market score;
  2. order-independence for EVERY seller: whichever trust screen is opened last, each advert's badge is the same.
Run ON THE SERVER:   venv/bin/python prove_trust_badge_one_rule.py /path/to/bea_main.py
Exit 0 = proved, 1 = the fault reproduces. No mail, no network: outbound calls are cut before the module loads."""
import os, sys, sqlite3, subprocess, shutil, types, logging, io, contextlib, itertools

SRC = sys.argv[1] if len(sys.argv) > 1 else "/var/www/marketsquare/main.py"
LIVE = "/var/www/marketsquare/marketsquare.db"; COPY = "/tmp/tb_proof.db"; BASE = "/tmp/tb_proof_base.db"

pid = subprocess.check_output(["systemctl", "show", "marketsquare", "-p", "MainPID", "--value"]).decode().strip()
for kv in open("/proc/%s/environ" % pid, "rb").read().split(b"\0"):
    if b"=" in kv:
        k, v = kv.split(b"=", 1); os.environ[k.decode()] = v.decode(errors="ignore")
for k in list(os.environ):                      # no key that could reach the outside world survives into this process
    if any(t in k.upper() for t in ("RESEND", "SMTP", "SMS", "PAYSTACK", "OPENAI", "ANTHROPIC", "HIGGS", "CF_", "CLOUDFLARE",
                                    "GEMINI", "GROK", "XAI", "WEBHOOK", "R2_", "AWS", "TELEGRAM")) and not k.upper().startswith("MS_"):
        os.environ[k] = ""
import socket
def _no_net(*a, **k): raise OSError("network is cut inside the proof")
socket.create_connection = _no_net; socket.socket.connect = lambda *a, **k: _no_net()

src_db = sqlite3.connect("file:%s?mode=ro" % LIVE, uri=True); dst = sqlite3.connect(BASE)
with dst: src_db.backup(dst)
src_db.close(); dst.close()

logging.disable(logging.CRITICAL)
os.chdir("/var/www/marketsquare"); sys.path.insert(0, "/var/www/marketsquare")
import database
database.DB_PATH = COPY
shutil.copyfile(BASE, COPY)
mod = types.ModuleType("main"); mod.__file__ = "/var/www/marketsquare/main.py"; sys.modules["main"] = mod
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    exec(compile(open(SRC, encoding="utf-8").read(), "/var/www/marketsquare/main.py", "exec"), mod.__dict__)
database.DB_PATH = COPY
assert database.DB_PATH == COPY

def fresh(prep=None):
    shutil.copyfile(BASE, COPY)
    if prep:
        c = sqlite3.connect(COPY)
        with c: prep(c)
        c.close()

def badges(email):
    c = sqlite3.connect(COPY)
    out = dict(c.execute("select id, trust_score from listings where lower(seller_email)=? order by id", (email,)).fetchall())
    c.close(); return out

def front_cat(category, service_class):
    """What ms.js sends as ?category= for an advert (normCat + _elTrustCat, AUD-047)."""
    rc, sc = (category or "").lower(), (service_class or "").lower()
    if rc in ("local_market", "local market"): return "LocalMarket"
    if rc.startswith("services"): return "Services-Casuals" if "casual" in (sc + " " + rc) else "Services-Technical"
    if rc.startswith("adventures"): return "Adventures-Accommodation" if "accom" in (rc + " " + sc) else "Adventures-Experiences"
    return category

def call(fn, *a):
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return fn(*a)
    except Exception as e:
        return {"_error": repr(e)[:120]}

fails = []
# ── 1. the Bee Lady case ────────────────────────────────────────────────────────────────────────────
c = sqlite3.connect(COPY); c.row_factory = sqlite3.Row
lm_multi = [r[0] for r in c.execute("""select lower(seller_email) e from listings where seller_email is not null and seller_email != ''
    group by e having sum(lower(trim(category)) in ('local_market','local market')) > 0 and count(distinct category) > 1""")]
c.close()
print("sellers with a Local Market advert AND adverts in another category:", len(lm_multi))
for e in lm_multi:
    c = sqlite3.connect(COPY); c.row_factory = sqlite3.Row
    rows = c.execute("select id, category, service_class from listings where lower(seller_email)=? order by id", (e,)).fetchall(); c.close()
    lm_score = int(mod._trust_evidence(database.get_db(), e, "local_market")["score"])
    others = [r for r in rows if (r["category"] or "").lower() not in ("local_market", "local market")]
    for order in ("panel-then-edit", "edit-then-panel"):
        fresh()
        for r in others:
            steps = [(mod.seller_public_credentials, (r["id"],)), (mod.trust_score_breakdown, (e, front_cat(r["category"], r["service_class"])))]
            for fn, a in (steps if order == "panel-then-edit" else steps[::-1]):
                res = call(fn, *a)
                if isinstance(res, dict) and res.get("_error"): fails.append("call failed: %s %s" % (fn.__name__, res["_error"]))
        b = badges(e)
        ok = all(v == lm_score for v in b.values())
        print("  %s: Local Market score %d, badges %s -> %s" % (order, lm_score, sorted(set(b.values())), "same on every advert" if ok else "DIFFERENT"))
        if not ok: fails.append("%s: adverts of one Local Market seller carry %s" % (order, sorted(set(b.values()))))
    ed = call(mod.trust_score_breakdown, e, front_cat(others[0]["category"], others[0]["service_class"])) if others else {}
    print("  Edit screen answers: score %s under the %s set" % (ed.get("score"), ed.get("category_key")))
    if others and ed.get("score") != lm_score: fails.append("the Edit screen shows %s, the advert %s" % (ed.get("score"), lm_score))

# ── 2. order-independence, every seller ─────────────────────────────────────────────────────────────
c = sqlite3.connect(BASE); c.row_factory = sqlite3.Row
sellers = {}
for r in c.execute("select id, lower(seller_email) e, category, service_class from listings where seller_email is not null and seller_email != '' order by id"):
    sellers.setdefault(r["e"], []).append(r)
users = {r[0] for r in c.execute("select lower(email) from users")}
c.close()
multi = {e: ls for e, ls in sellers.items() if len({(r["category"], r["service_class"] or "") for r in ls}) > 1 and e in users}
print("sellers with adverts in more than one category or service class:", len(multi))
moved = 0
for e, ls in multi.items():
    reps = {}
    for r in ls: reps.setdefault((r["category"], r["service_class"] or ""), r)
    steps = [("profile", mod.trust_score_breakdown, (e, None))]
    for (cat, sc), r in reps.items():
        steps.append(("panel #%d" % r["id"], mod.seller_public_credentials, (r["id"],)))
        steps.append(("edit #%d" % r["id"], mod.trust_score_breakdown, (e, front_cat(cat, sc))))
    finals = {}
    for name, order in (("forward", steps), ("reverse", steps[::-1])):
        fresh()
        for _, fn, a in order: call(fn, *a)
        finals[name] = badges(e)
    if finals["forward"] != finals["reverse"]:
        moved += 1
        diff = {i: (finals["forward"][i], finals["reverse"][i]) for i in finals["forward"] if finals["forward"][i] != finals["reverse"][i]}
        print("  MOVES with the screen opened last: %s...%s adverts %s" % (e[:3], e[e.find("@"):], diff))
print("sellers whose badge depends on which screen was opened last:", moved)
if moved: fails.append("%d seller(s): the badge depends on the last screen opened" % moved)

for p in (COPY, BASE):
    try: os.remove(p)
    except OSError: pass
print("\nPROVED: one rule, one writer -- every screen leaves the same badge" if not fails else "\nFAULT REPRODUCES:\n  - " + "\n  - ".join(fails))
sys.exit(1 if fails else 0)
